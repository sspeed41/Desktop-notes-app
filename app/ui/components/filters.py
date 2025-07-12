"""
Filter sidebar component for WiseDesktopNoteApp
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QCheckBox, QFrame, QScrollArea, QPushButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.settings import COLORS, FONTS
from app.data.models import Track, Series, Driver, Tag, TrackType, SessionType


class FilterSection(QFrame):
    """Individual filter section widget"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("filterSection")
        self.setup_ui(title)
    
    def setup_ui(self, title: str):
        """Setup the section UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Section header
        header = QLabel(title)
        header.setFont(QFont(FONTS["primary"], 12, QFont.Bold))
        header.setObjectName("sectionHeader")
        layout.addWidget(header)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(4)
        
        layout.addWidget(self.content_widget)
    
    def add_checkbox(self, text: str, data=None) -> QCheckBox:
        """Add a checkbox to the section"""
        checkbox = QCheckBox(text)
        checkbox.setObjectName("filterCheckbox")
        if data:
            checkbox.setProperty("data", data)
        self.content_layout.addWidget(checkbox)
        return checkbox
    
    def add_button(self, text: str, data=None) -> QPushButton:
        """Add a button to the section"""
        button = QPushButton(text)
        button.setObjectName("filterButton")
        button.setCheckable(True)
        if data:
            button.setProperty("data", data)
        self.content_layout.addWidget(button)
        return button


class FilterSidebar(QWidget):
    """Filter sidebar with racing-specific filters"""
    
    filters_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metadata = {}
        self.filter_checkboxes = {}
        self.filter_buttons = {}
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup the sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(24)
        
        # Sidebar title
        title = QLabel("Filters")
        title.setFont(QFont(FONTS["primary"], 18, QFont.Bold))
        title.setObjectName("sidebarTitle")
        layout.addWidget(title)
        
        # Scroll area for filters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setObjectName("filterScroll")
        
        # Filter content widget
        filter_widget = QWidget()
        filter_layout = QVBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(20)
        
        # Track Type filter
        self.track_type_section = FilterSection("Track Type")
        self.track_type_buttons = QButtonGroup(self)
        self.track_type_buttons.setExclusive(False)
        
        for track_type in TrackType:
            button = self.track_type_section.add_button(track_type.value, track_type)
            self.track_type_buttons.addButton(button)
            button.toggled.connect(self.on_filter_changed)
        
        filter_layout.addWidget(self.track_type_section)
        
        # Session Type filter
        self.session_type_section = FilterSection("Session Type")
        self.session_type_buttons = QButtonGroup(self)
        self.session_type_buttons.setExclusive(False)
        
        for session_type in SessionType:
            button = self.session_type_section.add_button(session_type.value, session_type)
            self.session_type_buttons.addButton(button)
            button.toggled.connect(self.on_filter_changed)
        
        filter_layout.addWidget(self.session_type_section)
        
        # Tracks filter (will be populated with metadata)
        self.tracks_section = FilterSection("Tracks")
        filter_layout.addWidget(self.tracks_section)
        
        # Series filter
        self.series_section = FilterSection("Series")
        filter_layout.addWidget(self.series_section)
        
        # Drivers filter
        self.drivers_section = FilterSection("Drivers")
        filter_layout.addWidget(self.drivers_section)
        
        # Tags filter
        self.tags_section = FilterSection("Tags")
        filter_layout.addWidget(self.tags_section)
        
        filter_layout.addStretch()
        
        # Clear filters button
        clear_button = QPushButton("Clear All Filters")
        clear_button.setObjectName("clearButton")
        clear_button.clicked.connect(self.clear_all_filters)
        filter_layout.addWidget(clear_button)
        
        scroll.setWidget(filter_widget)
        layout.addWidget(scroll)
    
    def apply_theme(self):
        """Apply X/Twitter-inspired theme"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
            
            #sidebarTitle {{
                color: {COLORS['text_primary']};
                padding-bottom: 10px;
                border-bottom: 2px solid {COLORS['border']};
            }}
            
            #filterSection {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                padding: 16px;
            }}
            
            #sectionHeader {{
                color: {COLORS['text_primary']};
                font-weight: bold;
                margin-bottom: 8px;
            }}
            
            #filterCheckbox {{
                color: {COLORS['text_primary']};
                font-size: 13px;
                padding: 4px 0px;
            }}
            
            #filterCheckbox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid {COLORS['border']};
                background-color: {COLORS['background']};
            }}
            
            #filterCheckbox::indicator:checked {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
            
            #filterButton {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 16px;
                padding: 6px 12px;
                text-align: left;
                color: {COLORS['text_primary']};
                font-size: 13px;
                min-height: 24px;
            }}
            
            #filterButton:hover {{
                background-color: {COLORS['hover']};
                border-color: {COLORS['secondary']};
            }}
            
            #filterButton:checked {{
                background-color: {COLORS['primary']};
                color: white;
                border-color: {COLORS['primary']};
            }}
            
            #clearButton {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                color: {COLORS['text_primary']};
                font-weight: bold;
            }}
            
            #clearButton:hover {{
                background-color: {COLORS['error']};
                color: white;
                border-color: {COLORS['error']};
            }}
            
            #filterScroll {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                background-color: transparent;
                width: 6px;
                border-radius: 3px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border']};
                border-radius: 3px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
    
    def set_metadata(self, metadata: dict):
        """Set the metadata and populate dynamic filters"""
        self.metadata = metadata
        
        # Clear existing dynamic filters
        self.clear_dynamic_filters()
        
        # Populate tracks
        if 'tracks' in metadata:
            for track in metadata['tracks']:
                checkbox = self.tracks_section.add_checkbox(track.name, track)
                checkbox.stateChanged.connect(self.on_filter_changed)
        
        # Populate series
        if 'series' in metadata:
            for series in metadata['series']:
                checkbox = self.series_section.add_checkbox(series.name, series)
                checkbox.stateChanged.connect(self.on_filter_changed)
        
        # Populate drivers (limit to top 20 for space)
        if 'drivers' in metadata:
            for driver in metadata['drivers'][:20]:
                checkbox = self.drivers_section.add_checkbox(driver.name, driver)
                checkbox.stateChanged.connect(self.on_filter_changed)
        
        # Populate tags
        if 'tags' in metadata:
            for tag in metadata['tags']:
                checkbox = self.tags_section.add_checkbox(tag.label, tag)
                checkbox.stateChanged.connect(self.on_filter_changed)
    
    def clear_dynamic_filters(self):
        """Clear dynamically populated filters"""
        sections = [self.tracks_section, self.series_section, self.drivers_section, self.tags_section]
        
        for section in sections:
            # Remove all widgets from content layout
            while section.content_layout.count():
                child = section.content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
    
    def on_filter_changed(self):
        """Handle filter changes and emit signal"""
        filters = self.get_current_filters()
        self.filters_changed.emit(filters)
    
    def get_current_filters(self) -> dict:
        """Get currently active filters"""
        filters = {
            'track_types': [],
            'session_types': [],
            'track_ids': [],
            'series_ids': [],
            'driver_ids': [],
            'tag_ids': []
        }
        
        # Track types
        for button in self.track_type_buttons.buttons():
            if button.isChecked():
                track_type = button.property("data")
                if track_type:
                    filters['track_types'].append(track_type)
        
        # Session types
        for button in self.session_type_buttons.buttons():
            if button.isChecked():
                session_type = button.property("data")
                if session_type:
                    filters['session_types'].append(session_type)
        
        # Dynamic filters
        self._collect_checkbox_filters(self.tracks_section, 'track_ids', filters)
        self._collect_checkbox_filters(self.series_section, 'series_ids', filters)
        self._collect_checkbox_filters(self.drivers_section, 'driver_ids', filters)
        self._collect_checkbox_filters(self.tags_section, 'tag_ids', filters)
        
        return filters
    
    def _collect_checkbox_filters(self, section: FilterSection, filter_key: str, filters: dict):
        """Helper to collect checkbox filter values"""
        for i in range(section.content_layout.count()):
            widget = section.content_layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                data = widget.property("data")
                if data and hasattr(data, 'id'):
                    filters[filter_key].append(data.id)
    
    def clear_all_filters(self):
        """Clear all active filters"""
        # Clear track type buttons
        for button in self.track_type_buttons.buttons():
            button.setChecked(False)
        
        # Clear session type buttons
        for button in self.session_type_buttons.buttons():
            button.setChecked(False)
        
        # Clear checkboxes in all sections
        sections = [self.tracks_section, self.series_section, self.drivers_section, self.tags_section]
        for section in sections:
            for i in range(section.content_layout.count()):
                widget = section.content_layout.itemAt(i).widget()
                if isinstance(widget, QCheckBox):
                    widget.setChecked(False)
        
        # Emit change signal
        self.on_filter_changed() 