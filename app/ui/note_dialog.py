"""
Session-focused note dialog for creating racing notes
"""

import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QCheckBox,
    QComboBox, QPushButton, QFrame, QListWidget, QListWidgetItem,
    QMessageBox, QButtonGroup, QRadioButton, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.data.models import NoteCreate, NoteCategory, Session, Track, Series, Driver, Tag
from app.settings import COLORS, FONTS
from typing import List, Optional
from app.ui.components.tag_selector import TagSelector

logger = logging.getLogger(__name__)


class SessionSelectionWidget(QFrame):
    """Widget for selecting racing session context"""
    
    session_selected = Signal(object)  # Emits the full session context
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sessions = []
        self.tracks = []
        self.series = []
        self.drivers = []
        self.selected_session = None
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup session selection UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("🏁 Select Racing Session")
        title.setFont(QFont(FONTS["primary"], 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Session selection dropdown
        self.session_combo = QComboBox()
        self.session_combo.setPlaceholderText("Choose session (e.g., Practice at Chicago Street Circuit)")
        self.session_combo.currentTextChanged.connect(self.on_session_changed)
        layout.addWidget(self.session_combo)
        
        # Session context display
        self.context_frame = QFrame()
        self.context_frame.setObjectName("contextFrame")
        self.context_frame.setVisible(False)
        context_layout = QVBoxLayout(self.context_frame)
        context_layout.setContentsMargins(12, 12, 12, 12)
        
        self.context_label = QLabel()
        self.context_label.setFont(QFont(FONTS["primary"], 12))
        self.context_label.setWordWrap(True)
        self.context_label.setObjectName("contextLabel")
        context_layout.addWidget(self.context_label)
        
        layout.addWidget(self.context_frame)
    
    def apply_theme(self):
        """Apply theme to session selection"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            
            QComboBox {{
                background-color: {COLORS['background']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }}
            
            QComboBox:focus {{
                border-color: {COLORS['primary']};
            }}
            
            #contextFrame {{
                background-color: {COLORS['primary']};
                border: none;
                border-radius: 8px;
            }}
            
            #contextLabel {{
                color: white;
                font-weight: bold;
            }}
        """)
    
    def set_metadata(self, tracks, series, drivers, sessions):
        """Set available metadata for session selection"""
        self.tracks = tracks
        self.series = series
        self.drivers = drivers
        self.sessions = sessions
        self.populate_sessions()
    
    def populate_sessions(self):
        """Populate session dropdown with contextual descriptions"""
        self.session_combo.clear()
        
        for session in self.sessions:
            # Find related track and series
            track_name = "Unknown Track"
            series_name = "Unknown Series"
            
            if session.track_id:
                for track in self.tracks:
                    if track.id == session.track_id:
                        track_name = track.name
                        break
            
            if session.series_id:
                for series in self.series:
                    if series.id == session.series_id:
                        series_name = series.name
                        break
            
            # Create descriptive session text
            session_text = f"{session.session} at {track_name} in {series_name} ({session.date})"
            self.session_combo.addItem(session_text, session)
    
    def on_session_changed(self, text):
        """Handle session selection change"""
        if not text:
            self.context_frame.setVisible(False)
            self.selected_session = None
            return
            
        # Get selected session data
        current_data = self.session_combo.currentData()
        if current_data:
            self.selected_session = current_data
            self.update_context_display()
            self.session_selected.emit(current_data)
    
    def update_context_display(self):
        """Update the context display with selected session info"""
        if not self.selected_session:
            return
            
        # Find track and series info
        track_name = "Unknown Track"
        track_type = ""
        series_name = "Unknown Series"
        
        if self.selected_session.track_id:
            for track in self.tracks:
                if track.id == self.selected_session.track_id:
                    track_name = track.name
                    track_type = f" ({track.type})"
                    break
        
        if self.selected_session.series_id:
            for series in self.series:
                if series.id == self.selected_session.series_id:
                    series_name = series.name
                    break
        
        context_text = f"📍 {self.selected_session.session} Session\n🏁 {track_name}{track_type}\n🏎️ {series_name}\n📅 {self.selected_session.date}"
        self.context_label.setText(context_text)
        self.context_frame.setVisible(True)


class NoteDialog(QDialog):
    """Session-focused dialog for creating racing notes"""
    
    note_created = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metadata = None
        self.selected_session = None
        self.selected_tag_ids: List[str] = []  # Store selected tag IDs
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Create Racing Note")
        self.setModal(True)
        self.resize(600, 800)  # Increased height for tag selector
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("✏️ Create New Racing Note")
        title.setFont(QFont(FONTS["primary"], 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Session selection
        self.session_widget = SessionSelectionWidget()
        self.session_widget.session_selected.connect(self.on_session_selected)
        layout.addWidget(self.session_widget)
        
        # Note categorization
        self.setup_categorization(layout)
        
        # Driver selection (for driver-specific notes)
        self.driver_group = QGroupBox("🏎️ Driver (for driver-specific notes)")
        driver_layout = QVBoxLayout(self.driver_group)
        
        self.driver_combo = QComboBox()
        self.driver_combo.setPlaceholderText("Select driver (optional)")
        driver_layout.addWidget(self.driver_combo)
        
        self.driver_group.setVisible(False)
        layout.addWidget(self.driver_group)
        
        # Tag selection
        self.tag_selector = TagSelector()
        self.tag_selector.tags_changed.connect(self.on_tags_changed)
        layout.addWidget(self.tag_selector)
        
        # Note content
        content_label = QLabel("📝 Note Content")
        content_label.setFont(QFont(FONTS["primary"], 14, QFont.Weight.Bold))
        layout.addWidget(content_label)
        
        self.body_edit = QTextEdit()
        self.body_edit.setPlaceholderText("What did you observe about this session? (e.g., Turn 1 entry speed seems critical for lap time...)")
        self.body_edit.setMinimumHeight(150)
        layout.addWidget(self.body_edit)
        
        # All notes are shared by default now
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.save_button = QPushButton("Save Racing Note")
        self.save_button.clicked.connect(self.save_note)
        self.save_button.setEnabled(False)  # Disabled until session selected
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def setup_categorization(self, parent_layout):
        """Setup note categorization options"""
        category_group = QGroupBox("📋 Note Category")
        category_layout = QVBoxLayout(category_group)
        
        self.category_buttons = QButtonGroup()
        
        # General note (default)
        general_radio = QRadioButton("📝 General - Overall session observations")
        general_radio.setChecked(True)
        general_radio.setProperty("category", NoteCategory.GENERAL)
        
        # Track-specific 
        track_radio = QRadioButton("🏁 Track Specific - Corners, elevation, racing line insights")
        track_radio.setProperty("category", NoteCategory.TRACK_SPECIFIC)
        
        # Series-specific
        series_radio = QRadioButton("🏎️ Series Specific - Rules, regulations, car behavior")
        series_radio.setProperty("category", NoteCategory.SERIES_SPECIFIC)
        
        # Driver-specific
        driver_radio = QRadioButton("👨‍💼 Driver Specific - Individual performance, technique")
        driver_radio.setProperty("category", NoteCategory.DRIVER_SPECIFIC)
        
        self.category_buttons.addButton(general_radio, 0)
        self.category_buttons.addButton(track_radio, 1) 
        self.category_buttons.addButton(series_radio, 2)
        self.category_buttons.addButton(driver_radio, 3)
        
        category_layout.addWidget(general_radio)
        category_layout.addWidget(track_radio)
        category_layout.addWidget(series_radio)
        category_layout.addWidget(driver_radio)
        
        # Connect category change
        self.category_buttons.buttonToggled.connect(self.on_category_changed)
        
        parent_layout.addWidget(category_group)
    
    def apply_theme(self):
        """Apply theme"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
            
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 6px;
                padding-top: 6px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
            }}
            
            QRadioButton {{
                font-size: 12px;
                padding: 4px;
            }}
            
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
            
            QTextEdit {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }}
            
            QTextEdit:focus {{
                border-color: {COLORS['primary']};
            }}
            
            QComboBox {{
                background-color: {COLORS['background']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px;
                font-size: 12px;
            }}
            
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 13px;
            }}
            
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
            
            QPushButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['text_secondary']};
            }}
        """)
    
    def set_metadata(self, metadata):
        """Set racing metadata for session and driver selection"""
        self.metadata = metadata
        
        # Set session metadata
        self.session_widget.set_metadata(
            metadata.get('tracks', []),
            metadata.get('series', []),
            metadata.get('drivers', []),
            metadata.get('sessions', [])
        )
        
        # Populate driver dropdown
        self.driver_combo.clear()
        for driver in metadata.get('drivers', []):
            self.driver_combo.addItem(driver.name, driver)
        
        # Set tags for the tag selector
        tags = metadata.get('tags', [])
        self.tag_selector.set_tags(tags)
        
        logger.info(f"Dialog metadata updated: {len(tags)} tags available")
    
    def on_session_selected(self, session):
        """Handle session selection"""
        self.selected_session = session
        self.save_button.setEnabled(True)
    
    def on_category_changed(self, button, checked):
        """Handle category selection change"""
        if checked:
            category = button.property("category")
            # Show driver selection only for driver-specific notes
            self.driver_group.setVisible(category == NoteCategory.DRIVER_SPECIFIC)
    
    def on_tags_changed(self, tag_ids: List[str]) -> None:
        """Handle tag selection changes"""
        self.selected_tag_ids = tag_ids
        logger.debug(f"Dialog selected tag IDs: {tag_ids}")
    
    def save_note(self):
        """Save the racing note"""
        body = self.body_edit.toPlainText().strip()
        if not body:
            QMessageBox.warning(self, "Error", "Please enter note content.")
            return
            
        if not self.selected_session:
            QMessageBox.warning(self, "Error", "Please select a session first.")
            return
        
        # Get selected category
        selected_button = self.category_buttons.checkedButton()
        category = selected_button.property("category") if selected_button else NoteCategory.GENERAL
        
        # Get selected driver (if applicable)
        driver_id = None
        if category == NoteCategory.DRIVER_SPECIFIC:
            current_driver = self.driver_combo.currentData()
            if current_driver:
                driver_id = current_driver.id
        
        # Convert selected tag IDs to UUIDs
        from uuid import UUID
        tag_uuids = [UUID(tag_id) for tag_id in self.selected_tag_ids]
        
        note_create = NoteCreate(
            body=body,
            shared=True,  # All notes are shared now
            session_id=self.selected_session.id,
            driver_id=driver_id,
            category=category,
            tag_ids=tag_uuids  # Include selected tags
        )
        
        logger.info(f"Dialog saving note with {len(tag_uuids)} tags")
        self.note_created.emit(note_create)
        self.accept() 