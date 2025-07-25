"""
Category Filter Widget for dynamic subcategory filtering
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QScrollArea,
    QGroupBox,
    QPushButton,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, pyqtSignal


class CategoryFilterWidget(QWidget):
    filter_changed = pyqtSignal(dict)

    def __init__(self, categories=None, content_type="live"):
        super().__init__()
        self.content_type = content_type
        self.categories = categories or []
        self.active_filters = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(f"{self.content_type.title()} Filters")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # Search filter
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout(search_group)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search content...")
        self.search_input.textChanged.connect(self.on_filter_changed)
        search_layout.addWidget(self.search_input)

        layout.addWidget(search_group)

        # Category filter
        if self.categories:
            category_group = QGroupBox("Categories")
            category_layout = QVBoxLayout(category_group)

            # All categories checkbox
            self.all_categories_cb = QCheckBox("All Categories")
            self.all_categories_cb.setChecked(True)
            self.all_categories_cb.stateChanged.connect(self.on_all_categories_changed)
            category_layout.addWidget(self.all_categories_cb)

            # Individual category checkboxes in scrollable area
            scroll_area = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)

            self.category_checkboxes = {}
            for category in sorted(self.categories):
                cb = QCheckBox(category)
                cb.stateChanged.connect(self.on_category_changed)
                scroll_layout.addWidget(cb)
                self.category_checkboxes[category] = cb

            scroll_area.setWidget(scroll_widget)
            scroll_area.setMaximumHeight(200)
            category_layout.addWidget(scroll_area)

            layout.addWidget(category_group)

        # Content-specific filters
        if self.content_type == "vod":
            self.add_movie_filters(layout)
        elif self.content_type == "series":
            self.add_series_filters(layout)
        elif self.content_type == "live":
            self.add_live_filters(layout)

        # Filter actions
        actions_layout = QHBoxLayout()

        clear_button = QPushButton("Clear All")
        clear_button.clicked.connect(self.clear_filters)
        actions_layout.addWidget(clear_button)

        apply_button = QPushButton("Apply Filters")
        apply_button.clicked.connect(self.apply_filters)
        actions_layout.addWidget(apply_button)

        layout.addLayout(actions_layout)
        layout.addStretch()

    def add_movie_filters(self, layout):
        """Add movie-specific filters"""
        movie_group = QGroupBox("Movie Filters")
        movie_layout = QVBoxLayout(movie_group)

        # Genre filter
        genre_layout = QHBoxLayout()
        genre_layout.addWidget(QLabel("Genre:"))
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(
            [
                "All Genres",
                "Action",
                "Comedy",
                "Drama",
                "Horror",
                "Thriller",
                "Sci-Fi",
                "Romance",
                "Adventure",
                "Animation",
                "Documentary",
                "Family",
                "Fantasy",
                "Mystery",
                "Crime",
            ]
        )
        self.genre_combo.currentTextChanged.connect(self.on_filter_changed)
        genre_layout.addWidget(self.genre_combo)
        movie_layout.addLayout(genre_layout)

        # Year filter
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Year:"))
        self.year_combo = QComboBox()
        years = ["All Years"] + [str(year) for year in range(2024, 1970, -1)]
        self.year_combo.addItems(years)
        self.year_combo.currentTextChanged.connect(self.on_filter_changed)
        year_layout.addWidget(self.year_combo)
        movie_layout.addLayout(year_layout)

        # Rating filter
        self.hd_only_cb = QCheckBox("HD Quality Only")
        self.hd_only_cb.stateChanged.connect(self.on_filter_changed)
        movie_layout.addWidget(self.hd_only_cb)

        layout.addWidget(movie_group)

    def add_series_filters(self, layout):
        """Add series-specific filters"""
        series_group = QGroupBox("Series Filters")
        series_layout = QVBoxLayout(series_group)

        # Status filter
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(
            ["All Status", "Ongoing", "Completed", "New Episodes"]
        )
        self.status_combo.currentTextChanged.connect(self.on_filter_changed)
        status_layout.addWidget(self.status_combo)
        series_layout.addLayout(status_layout)

        # Genre filter for series
        genre_layout = QHBoxLayout()
        genre_layout.addWidget(QLabel("Genre:"))
        self.series_genre_combo = QComboBox()
        self.series_genre_combo.addItems(
            [
                "All Genres",
                "Drama",
                "Comedy",
                "Action",
                "Thriller",
                "Reality",
                "Documentary",
                "News",
                "Sports",
                "Kids",
            ]
        )
        self.series_genre_combo.currentTextChanged.connect(self.on_filter_changed)
        genre_layout.addWidget(self.series_genre_combo)
        series_layout.addLayout(genre_layout)

        layout.addWidget(series_group)

    def add_live_filters(self, layout):
        """Add live TV specific filters"""
        live_group = QGroupBox("Live TV Filters")
        live_layout = QVBoxLayout(live_group)

        # Channel type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.channel_type_combo = QComboBox()
        self.channel_type_combo.addItems(
            [
                "All Types",
                "Entertainment",
                "News",
                "Sports",
                "Movies",
                "Documentary",
                "Kids",
                "Music",
                "International",
                "Local",
            ]
        )
        self.channel_type_combo.currentTextChanged.connect(self.on_filter_changed)
        type_layout.addWidget(self.channel_type_combo)
        live_layout.addLayout(type_layout)

        # Language filter
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(
            [
                "All Languages",
                "English",
                "Spanish",
                "French",
                "German",
                "Italian",
                "Portuguese",
                "Arabic",
                "Hindi",
                "Chinese",
            ]
        )
        self.language_combo.currentTextChanged.connect(self.on_filter_changed)
        lang_layout.addWidget(self.language_combo)
        live_layout.addLayout(lang_layout)

        # Quality filter
        self.hd_channels_cb = QCheckBox("HD Channels Only")
        self.hd_channels_cb.stateChanged.connect(self.on_filter_changed)
        live_layout.addWidget(self.hd_channels_cb)

        self.favorites_only_cb = QCheckBox("Favorites Only")
        self.favorites_only_cb.stateChanged.connect(self.on_filter_changed)
        live_layout.addWidget(self.favorites_only_cb)

        layout.addWidget(live_group)

    def on_all_categories_changed(self, state):
        """Handle all categories checkbox change"""
        is_checked = state == Qt.CheckState.Checked.value

        for cb in self.category_checkboxes.values():
            cb.blockSignals(True)
            cb.setChecked(is_checked)
            cb.blockSignals(False)

        self.on_filter_changed()

    def on_category_changed(self):
        """Handle individual category checkbox change"""
        # Check if all categories are selected
        all_checked = all(cb.isChecked() for cb in self.category_checkboxes.values())
        any_checked = any(cb.isChecked() for cb in self.category_checkboxes.values())

        self.all_categories_cb.blockSignals(True)
        if all_checked:
            self.all_categories_cb.setChecked(True)
        elif not any_checked:
            self.all_categories_cb.setChecked(False)
        else:
            self.all_categories_cb.setCheckState(Qt.CheckState.PartiallyChecked)
        self.all_categories_cb.blockSignals(False)

        self.on_filter_changed()

    def on_filter_changed(self):
        """Collect and emit current filter state"""
        filters = {"search": self.search_input.text().strip(), "categories": []}

        # Get selected categories
        for category, cb in self.category_checkboxes.items():
            if cb.isChecked():
                filters["categories"].append(category)

        # Add content-specific filters
        if self.content_type == "vod":
            filters.update(
                {
                    "genre": self.genre_combo.currentText(),
                    "year": self.year_combo.currentText(),
                    "hd_only": self.hd_only_cb.isChecked(),
                }
            )
        elif self.content_type == "series":
            filters.update(
                {
                    "status": self.status_combo.currentText(),
                    "genre": self.series_genre_combo.currentText(),
                }
            )
        elif self.content_type == "live":
            filters.update(
                {
                    "channel_type": self.channel_type_combo.currentText(),
                    "language": self.language_combo.currentText(),
                    "hd_only": self.hd_channels_cb.isChecked(),
                    "favorites_only": self.favorites_only_cb.isChecked(),
                }
            )

        self.active_filters = filters
        self.filter_changed.emit(filters)

    def apply_filters(self):
        """Explicitly apply current filters"""
        self.on_filter_changed()

    def clear_filters(self):
        """Clear all filters"""
        # Clear search
        self.search_input.clear()

        # Check all categories
        self.all_categories_cb.setChecked(True)

        # Reset content-specific filters
        if self.content_type == "vod":
            self.genre_combo.setCurrentIndex(0)
            self.year_combo.setCurrentIndex(0)
            self.hd_only_cb.setChecked(False)
        elif self.content_type == "series":
            self.status_combo.setCurrentIndex(0)
            self.series_genre_combo.setCurrentIndex(0)
        elif self.content_type == "live":
            self.channel_type_combo.setCurrentIndex(0)
            self.language_combo.setCurrentIndex(0)
            self.hd_channels_cb.setChecked(False)
            self.favorites_only_cb.setChecked(False)

        self.on_filter_changed()

    def get_active_filters(self):
        """Get current active filters"""
        return self.active_filters.copy()

    def update_categories(self, categories):
        """Update available categories"""
        self.categories = categories

        # Clear existing category checkboxes
        for cb in self.category_checkboxes.values():
            cb.deleteLater()
        self.category_checkboxes.clear()

        # Add new category checkboxes
        # This would require rebuilding the UI section - simplified for now
        pass
