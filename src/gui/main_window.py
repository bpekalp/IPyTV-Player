"""
Main Window for IPTV Player Application
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QMenuBar,
    QMenu,
    QStatusBar,
    QLabel,
    QPushButton,
    QLineEdit,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QMessageBox,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon

from .media_player import MediaPlayerWidget
from .login_dialog import LoginDialog
from api.xtream_client import XtreamCodesClient
from parsers.m3u_parser import M3UParser
from parsers.xmltv_parser import XMLTVParser


class DataLoaderThread(QThread):
    data_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)

    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self):
        try:
            self.progress_updated.emit(10, "Loading server info...")
            server_info = self.client.get_server_info()
            if not server_info:
                self.error_occurred.emit("Failed to connect to server")
                return

            self.progress_updated.emit(30, "Loading categories...")
            live_categories = self.client.get_live_categories()
            vod_categories = self.client.get_vod_categories()
            series_categories = self.client.get_series_categories()

            self.progress_updated.emit(60, "Loading content...")
            live_streams = self.client.get_live_streams()
            vod_streams = self.client.get_vod_streams()
            series = self.client.get_series()

            self.progress_updated.emit(100, "Complete!")

            data = {
                "server_info": server_info,
                "live_categories": live_categories,
                "vod_categories": vod_categories,
                "series_categories": series_categories,
                "live_streams": live_streams,
                "vod_streams": vod_streams,
                "series": series,
            }

            self.data_loaded.emit(data)

        except Exception as e:
            self.error_occurred.emit(f"Error loading data: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = None
        self.current_data = {}
        self.init_ui()
        self.show_login_dialog()

    def init_ui(self):
        self.setWindowTitle("IPyTV Player")
        self.setGeometry(100, 100, 1200, 800)

        # Create menu bar
        self.create_menu_bar()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Create left panel (content tree)
        self.create_content_tree()
        splitter.addWidget(self.content_tree)

        # Create right panel (media player and details)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Create tab widget for content sections
        self.content_tabs = QTabWidget()
        right_layout.addWidget(self.content_tabs)

        # Create media player
        self.media_player = MediaPlayerWidget()
        right_layout.addWidget(self.media_player)

        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([300, 900])

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add progress bar to status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        login_action = QAction("Login...", self)
        login_action.triggered.connect(self.show_login_dialog)
        file_menu.addAction(login_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("View")

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)

    def create_content_tree(self):
        self.content_tree = QTreeWidget()
        self.content_tree.setHeaderLabel("Content")
        self.content_tree.itemClicked.connect(self.on_tree_item_clicked)

        # Add main sections
        self.live_tv_item = QTreeWidgetItem(self.content_tree, ["Live TV"])
        self.movies_item = QTreeWidgetItem(self.content_tree, ["Movies"])
        self.series_item = QTreeWidgetItem(self.content_tree, ["Series"])

    def show_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            credentials = dialog.get_credentials()
            self.connect_to_server(credentials)

    def connect_to_server(self, credentials):
        try:
            self.client = XtreamCodesClient(
                credentials["server"], credentials["username"], credentials["password"]
            )

            # Start loading data in background thread
            self.loader_thread = DataLoaderThread(self.client)
            self.loader_thread.data_loaded.connect(self.on_data_loaded)
            self.loader_thread.error_occurred.connect(self.on_loading_error)
            self.loader_thread.progress_updated.connect(self.update_progress)
            self.loader_thread.start()

            self.progress_bar.setVisible(True)
            self.status_label.setText("Connecting...")

        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error", f"Failed to connect: {str(e)}"
            )

    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def on_data_loaded(self, data):
        self.current_data = data
        self.populate_content_tree()
        self.progress_bar.setVisible(False)
        self.status_label.setText("Connected")

    def on_loading_error(self, error_message):
        self.progress_bar.setVisible(False)
        self.status_label.setText("Connection failed")
        QMessageBox.critical(self, "Loading Error", error_message)

    def populate_content_tree(self):
        # Clear existing items
        self.live_tv_item.takeChildren()
        self.movies_item.takeChildren()
        self.series_item.takeChildren()

        # Populate Live TV categories
        for category in self.current_data.get("live_categories", []):
            category_item = QTreeWidgetItem(
                self.live_tv_item, [category.get("category_name", "Unknown")]
            )
            category_item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                {
                    "type": "live_category",
                    "category_id": category.get("category_id"),
                    "data": category,
                },
            )

        # Populate Movies categories
        for category in self.current_data.get("vod_categories", []):
            category_item = QTreeWidgetItem(
                self.movies_item, [category.get("category_name", "Unknown")]
            )
            category_item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                {
                    "type": "vod_category",
                    "category_id": category.get("category_id"),
                    "data": category,
                },
            )

        # Populate Series categories
        for category in self.current_data.get("series_categories", []):
            category_item = QTreeWidgetItem(
                self.series_item, [category.get("category_name", "Unknown")]
            )
            category_item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                {
                    "type": "series_category",
                    "category_id": category.get("category_id"),
                    "data": category,
                },
            )

        # Expand all items
        self.content_tree.expandAll()

    def on_tree_item_clicked(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        item_type = data.get("type")
        category_id = data.get("category_id")

        if item_type == "live_category":
            self.load_live_streams(category_id)
        elif item_type == "vod_category":
            self.load_vod_streams(category_id)
        elif item_type == "series_category":
            self.load_series(category_id)

    def load_live_streams(self, category_id):
        streams = [
            s
            for s in self.current_data.get("live_streams", [])
            if s.get("category_id") == str(category_id)
        ]
        self.display_streams(streams, "live")

    def load_vod_streams(self, category_id):
        streams = [
            s
            for s in self.current_data.get("vod_streams", [])
            if s.get("category_id") == str(category_id)
        ]
        self.display_streams(streams, "vod")

    def load_series(self, category_id):
        series = [
            s
            for s in self.current_data.get("series", [])
            if s.get("category_id") == str(category_id)
        ]
        self.display_streams(series, "series")

    def display_streams(self, streams, stream_type):
        # Clear existing tabs
        self.content_tabs.clear()

        # Create streams list widget
        from .streams_widget import StreamsWidget

        streams_widget = StreamsWidget(streams, stream_type, self.client)
        streams_widget.stream_selected.connect(self.play_stream)

        self.content_tabs.addTab(
            streams_widget, f"{stream_type.title()} ({len(streams)})"
        )

    def play_stream(self, stream_url, stream_info):
        self.media_player.play_stream(stream_url)
        self.status_label.setText(f"Playing: {stream_info.get('name', 'Unknown')}")

    def refresh_data(self):
        if self.client:
            self.loader_thread = DataLoaderThread(self.client)
            self.loader_thread.data_loaded.connect(self.on_data_loaded)
            self.loader_thread.error_occurred.connect(self.on_loading_error)
            self.loader_thread.progress_updated.connect(self.update_progress)
            self.loader_thread.start()

            self.progress_bar.setVisible(True)
            self.status_label.setText("Refreshing...")
