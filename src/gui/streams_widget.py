"""
Streams Widget for displaying and managing streams
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QSplitter,
    QTextEdit,
    QGroupBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QFont


class StreamsWidget(QWidget):
    stream_selected = pyqtSignal(str, dict)

    def __init__(self, streams, stream_type, client):
        super().__init__()
        self.streams = streams
        self.stream_type = stream_type
        self.client = client
        self.filtered_streams = streams.copy()
        self.init_ui()
        self.populate_streams()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Search and filter controls
        controls_layout = QHBoxLayout()

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search streams...")
        self.search_input.textChanged.connect(self.filter_streams)
        controls_layout.addWidget(QLabel("Search:"))
        controls_layout.addWidget(self.search_input)

        # Category filter (if applicable)
        if self.stream_type in ["live", "vod"]:
            self.category_filter = QComboBox()
            self.category_filter.addItem("All Categories")
            self.category_filter.currentTextChanged.connect(self.filter_streams)
            controls_layout.addWidget(QLabel("Category:"))
            controls_layout.addWidget(self.category_filter)

        controls_layout.addStretch()

        # Results count
        self.count_label = QLabel()
        controls_layout.addWidget(self.count_label)

        layout.addLayout(controls_layout)

        # Create splitter for streams list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Streams list
        self.streams_list = QListWidget()
        self.streams_list.itemClicked.connect(self.on_stream_selected)
        self.streams_list.itemDoubleClicked.connect(self.on_stream_double_clicked)
        splitter.addWidget(self.streams_list)

        # Details panel
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)

        # Stream info
        info_group = QGroupBox("Stream Information")
        info_layout = QVBoxLayout(info_group)

        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)

        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(150)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)

        details_layout.addWidget(info_group)

        # Action buttons
        buttons_layout = QHBoxLayout()

        self.play_button = QPushButton("Play Stream")
        self.play_button.clicked.connect(self.play_selected_stream)
        self.play_button.setEnabled(False)
        buttons_layout.addWidget(self.play_button)

        if self.stream_type == "series":
            self.episodes_button = QPushButton("View Episodes")
            self.episodes_button.clicked.connect(self.show_episodes)
            self.episodes_button.setEnabled(False)
            buttons_layout.addWidget(self.episodes_button)

        buttons_layout.addStretch()
        details_layout.addLayout(buttons_layout)

        details_layout.addStretch()
        splitter.addWidget(details_widget)

        # Set splitter proportions
        splitter.setSizes([600, 400])

        self.selected_stream = None

    def populate_streams(self):
        self.streams_list.clear()

        for stream in self.filtered_streams:
            item = QListWidgetItem()

            # Set display text based on stream type
            if self.stream_type == "live":
                title = stream.get("name", "Unknown Channel")
            elif self.stream_type == "vod":
                title = stream.get("name", "Unknown Movie")
            else:  # series
                title = stream.get("name", "Unknown Series")

            item.setText(title)
            item.setData(Qt.ItemDataRole.UserRole, stream)
            self.streams_list.addItem(item)

        self.update_count_label()

    def filter_streams(self):
        search_text = self.search_input.text().lower()

        self.filtered_streams = []
        for stream in self.streams:
            name = stream.get("name", "").lower()
            if search_text in name:
                self.filtered_streams.append(stream)

        self.populate_streams()

    def update_count_label(self):
        self.count_label.setText(f"{len(self.filtered_streams)} streams")

    def on_stream_selected(self, item):
        self.selected_stream = item.data(Qt.ItemDataRole.UserRole)
        self.update_details_panel()
        self.play_button.setEnabled(True)

        if self.stream_type == "series":
            self.episodes_button.setEnabled(True)

    def on_stream_double_clicked(self, item):
        self.on_stream_selected(item)
        self.play_selected_stream()

    def update_details_panel(self):
        if not self.selected_stream:
            return

        # Update title
        title = self.selected_stream.get("name", "Unknown")
        self.title_label.setText(title)

        # Update info text
        info_lines = []

        if self.stream_type == "live":
            info_lines.append(
                f"Category: {self.selected_stream.get('category_id', 'Unknown')}"
            )
            if "epg_channel_id" in self.selected_stream:
                info_lines.append(f"EPG ID: {self.selected_stream['epg_channel_id']}")

        elif self.stream_type == "vod":
            if "plot" in self.selected_stream:
                info_lines.append(f"Plot: {self.selected_stream['plot']}")
            if "genre" in self.selected_stream:
                info_lines.append(f"Genre: {self.selected_stream['genre']}")
            if "release_date" in self.selected_stream:
                info_lines.append(
                    f"Release Date: {self.selected_stream['release_date']}"
                )
            if "rating" in self.selected_stream:
                info_lines.append(f"Rating: {self.selected_stream['rating']}")

        elif self.stream_type == "series":
            if "plot" in self.selected_stream:
                info_lines.append(f"Plot: {self.selected_stream['plot']}")
            if "genre" in self.selected_stream:
                info_lines.append(f"Genre: {self.selected_stream['genre']}")
            if "release_date" in self.selected_stream:
                info_lines.append(
                    f"Release Date: {self.selected_stream['release_date']}"
                )
            if "rating" in self.selected_stream:
                info_lines.append(f"Rating: {self.selected_stream['rating']}")

        self.info_text.setText("\n".join(info_lines))

    def play_selected_stream(self):
        if not self.selected_stream:
            return

        stream_id = self.selected_stream.get("stream_id") or self.selected_stream.get(
            "series_id"
        )
        if not stream_id:
            return

        # Generate stream URL based on type
        if self.stream_type == "live":
            stream_url = self.client.get_stream_url(stream_id, "live")
        elif self.stream_type == "vod":
            stream_url = self.client.get_stream_url(stream_id, "movie")
        else:  # series
            # For series, we'll need to handle episodes differently
            # For now, just emit the series info
            stream_url = ""

        if stream_url:
            self.stream_selected.emit(stream_url, self.selected_stream)

    def show_episodes(self):
        if not self.selected_stream or self.stream_type != "series":
            return

        series_id = self.selected_stream.get("series_id")
        if series_id:
            # This would open an episodes dialog
            # For now, we'll just play the first episode if available
            pass
