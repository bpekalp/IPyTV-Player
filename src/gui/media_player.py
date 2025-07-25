"""
Media Player Widget using VLC
"""

import vlc
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QLabel,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPalette


class MediaPlayerWidget(QWidget):
    position_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.media_player = None
        self.is_paused = False
        self.init_ui()
        self.init_vlc()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Video frame
        self.video_frame = QFrame()
        self.video_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.video_frame.setAutoFillBackground(True)
        palette = self.video_frame.palette()
        palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.black)
        self.video_frame.setPalette(palette)
        self.video_frame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.video_frame)

        # Controls
        controls_layout = QHBoxLayout()

        # Play/Pause button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play_pause)
        controls_layout.addWidget(self.play_button)

        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        controls_layout.addWidget(self.stop_button)

        # Position slider
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.set_position)
        controls_layout.addWidget(self.position_slider)

        # Time label
        self.time_label = QLabel("00:00 / 00:00")
        controls_layout.addWidget(self.time_label)

        # Volume slider
        volume_label = QLabel("Vol:")
        controls_layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        controls_layout.addWidget(self.volume_slider)

        layout.addLayout(controls_layout)

        # Timer for updating position
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

    def init_vlc(self):
        # Create VLC instance
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()

        # Set video output to the widget
        if hasattr(self.media_player, "set_hwnd"):
            self.media_player.set_hwnd(self.video_frame.winId())
        elif hasattr(self.media_player, "set_xwindow"):
            self.media_player.set_xwindow(self.video_frame.winId())
        elif hasattr(self.media_player, "set_nsobject"):
            self.media_player.set_nsobject(int(self.video_frame.winId()))

    def play_stream(self, url):
        if not url:
            return

        media = self.vlc_instance.media_new(url)
        self.media_player.set_media(media)
        self.media_player.play()
        self.play_button.setText("Pause")
        self.is_paused = False

    def toggle_play_pause(self):
        if self.media_player.get_media():
            if self.is_paused:
                self.media_player.play()
                self.play_button.setText("Pause")
                self.is_paused = False
            else:
                self.media_player.pause()
                self.play_button.setText("Play")
                self.is_paused = True

    def stop(self):
        self.media_player.stop()
        self.play_button.setText("Play")
        self.is_paused = False
        self.position_slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")

    def set_position(self, position):
        if self.media_player.get_media():
            self.media_player.set_position(position / 1000.0)

    def set_volume(self, volume):
        if self.media_player:
            self.media_player.audio_set_volume(volume)

    def update_ui(self):
        if not self.media_player.get_media():
            return

        # Update position slider
        media_pos = int(self.media_player.get_position() * 1000)
        self.position_slider.setValue(media_pos)

        # Update time label
        current_time = self.media_player.get_time()
        total_time = self.media_player.get_length()

        if current_time >= 0 and total_time > 0:
            current_str = self.format_time(current_time)
            total_str = self.format_time(total_time)
            self.time_label.setText(f"{current_str} / {total_str}")

    def format_time(self, milliseconds):
        seconds = milliseconds // 1000
        minutes = seconds // 60
        hours = minutes // 60

        if hours > 0:
            return f"{hours:02d}:{minutes%60:02d}:{seconds%60:02d}"
        else:
            return f"{minutes:02d}:{seconds%60:02d}"
