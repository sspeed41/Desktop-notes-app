"""
Note creation panel component for WiseDesktopNoteApp
Extracted from main_window.py for better maintainability
"""

import os
import logging
from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QPushButton, QTextEdit, QComboBox, QGroupBox, QButtonGroup,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QDragEnterEvent, QDropEvent

from app.config import get_ui_config
from app.data.models import NoteCreate, NoteCategory, MediaType, Tag
from app.utils.exceptions import ValidationError, UIError
from app.utils.helpers import get_media_type_from_path
from app.ui.components.tag_selector import TagSelector

logger = logging.getLogger(__name__)


class NoteCreationPanel(QFrame):
    """Right panel for creating new racing notes"""
    
    note_created = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.metadata: Optional[Dict[str, Any]] = None
        self.uploaded_files: list = []  # Store uploaded media files
        self.selected_tag_ids: List[str] = []  # Store selected tag IDs
        
        # Get UI config
        self.ui_config = get_ui_config()
        
        self.setup_ui()
        self.apply_theme()
        
        # Populate with sample data immediately
        self.populate_tracks()
        
        logger.info("NoteCreationPanel initialized")
    
    def setup_ui(self) -> None:
        """Setup the note creation panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Create Racing Note")
        title.setFont(QFont(self.ui_config.fonts["primary"], 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Session selection - track dropdown + horizontal button selections
        session_group = QGroupBox("Racing Session")
        session_layout = QVBoxLayout(session_group)
        session_layout.setSpacing(12)
        
        # Track selection dropdown
        track_label = QLabel("Track:")
        track_label.setFont(QFont(self.ui_config.fonts["secondary"], 12, QFont.Weight.Bold))
        session_layout.addWidget(track_label)
        
        self.track_combo = QComboBox()
        self.track_combo.setPlaceholderText("Select track...")
        self.track_combo.currentTextChanged.connect(self.on_selection_changed)
        session_layout.addWidget(self.track_combo)
        
        series_button_layout = QHBoxLayout()
        series_button_layout.setSpacing(8)
        
        self.series_buttons = QButtonGroup()
        self.series_buttons.setExclusive(True)
        
        cup_btn = QPushButton("CUP")
        cup_btn.setCheckable(True)
        cup_btn.setObjectName("seriesButton")
        cup_btn.clicked.connect(self.on_selection_changed)
        
        xfinity_btn = QPushButton("XFINITY") 
        xfinity_btn.setCheckable(True)
        xfinity_btn.setObjectName("seriesButton")
        xfinity_btn.clicked.connect(self.on_selection_changed)
        
        truck_btn = QPushButton("TRUCK")
        truck_btn.setCheckable(True)
        truck_btn.setObjectName("seriesButton")
        truck_btn.clicked.connect(self.on_selection_changed)
        
        self.series_buttons.addButton(cup_btn, 0)
        self.series_buttons.addButton(xfinity_btn, 1)
        self.series_buttons.addButton(truck_btn, 2)
        
        series_button_layout.addWidget(cup_btn)
        series_button_layout.addWidget(xfinity_btn)
        series_button_layout.addWidget(truck_btn)
        series_button_layout.addStretch()
        
        session_layout.addLayout(series_button_layout)
        
        # Session type selection - horizontal buttons
        session_type_button_layout = QHBoxLayout()
        session_type_button_layout.setSpacing(8)
        
        self.session_type_buttons = QButtonGroup()
        self.session_type_buttons.setExclusive(True)
        
        practice_btn = QPushButton("PRACTICE")
        practice_btn.setCheckable(True)
        practice_btn.setObjectName("sessionTypeButton")
        practice_btn.clicked.connect(self.on_selection_changed)
        
        qualifying_btn = QPushButton("QUALIFYING")
        qualifying_btn.setCheckable(True)
        qualifying_btn.setObjectName("sessionTypeButton")
        qualifying_btn.clicked.connect(self.on_selection_changed)
        
        race_btn = QPushButton("RACE")
        race_btn.setCheckable(True)
        race_btn.setObjectName("sessionTypeButton")
        race_btn.clicked.connect(self.on_selection_changed)
        
        self.session_type_buttons.addButton(practice_btn, 0)
        self.session_type_buttons.addButton(qualifying_btn, 1)
        self.session_type_buttons.addButton(race_btn, 2)
        
        session_type_button_layout.addWidget(practice_btn)
        session_type_button_layout.addWidget(qualifying_btn)
        session_type_button_layout.addWidget(race_btn)
        session_type_button_layout.addStretch()
        
        session_layout.addLayout(session_type_button_layout)
        
        layout.addWidget(session_group)
        
        # Driver selection (optional)
        driver_group = QGroupBox("Driver (Optional)")
        driver_layout = QVBoxLayout(driver_group)
        driver_layout.setSpacing(12)
        
        self.driver_combo = QComboBox()
        self.driver_combo.setPlaceholderText("No driver selected (general note)")
        self.driver_combo.currentTextChanged.connect(self.on_selection_changed)
        driver_layout.addWidget(self.driver_combo)
        
        layout.addWidget(driver_group)
        
        # Note content
        content_label = QLabel("Note Content")
        content_label.setFont(QFont(self.ui_config.fonts["primary"], 14, QFont.Weight.Bold))
        layout.addWidget(content_label)
        
        self.body_edit = QTextEdit()
        self.body_edit.setPlaceholderText("What did you observe about this session? (e.g., Turn 1 entry speed seems critical for lap time...)\n\nYou can drag & drop media files directly here")
        self.body_edit.setMinimumHeight(120)
        
        # Enable drag and drop on the text edit
        self.body_edit.setAcceptDrops(True)
        self.body_edit.dragEnterEvent = self.dragEnterEvent
        self.body_edit.dropEvent = self.dropEvent
        
        layout.addWidget(self.body_edit)
        
        # Tag selection - compact, at bottom of note
        self.tag_selector = TagSelector()
        self.tag_selector.tags_changed.connect(self.on_tags_changed)
        layout.addWidget(self.tag_selector)
        
        # Media files display area
        self.media_frame = QFrame()
        self.media_frame.setObjectName("mediaFrame")
        self.media_frame.setVisible(False)
        media_layout = QVBoxLayout(self.media_frame)
        media_layout.setContentsMargins(12, 12, 12, 12)
        
        media_title = QLabel("Attached Media")
        media_title.setFont(QFont(self.ui_config.fonts["secondary"], 12, QFont.Weight.Bold))
        media_layout.addWidget(media_title)
        
        self.media_list = QLabel("No files attached")
        self.media_list.setFont(QFont(self.ui_config.fonts["secondary"], 10))
        self.media_list.setWordWrap(True)
        self.media_list.setObjectName("mediaList")
        media_layout.addWidget(self.media_list)
        
        layout.addWidget(self.media_frame)
        
        # Save button
        self.save_button = QPushButton("Save Racing Note")
        self.save_button.clicked.connect(self.save_note)
        self.save_button.setEnabled(False)  # Disabled until session selected
        layout.addWidget(self.save_button)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def apply_theme(self) -> None:
        """Apply theme to note creation panel"""
        colors = self.ui_config.colors
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
            }}
            
            QGroupBox {{
                font-weight: bold;
                font-size: 13px;
                border: none;
                margin-top: 6px;
                padding-top: 6px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
            }}
            
            QTextEdit {{
                background-color: {colors['surface']};
                border: 2px solid {colors['border']};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                min-height: 120px;
            }}
            
            QTextEdit:focus {{
                border-color: {colors['primary']};
            }}
            
            QComboBox {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
                border: 2px solid {colors['border']};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                font-weight: 500;
                min-height: 20px;
            }}
            
            QComboBox:focus {{
                border-color: {colors['primary']};
                border-width: 2px;
            }}
            
            QComboBox:hover {{
                border-color: {colors['secondary']};
                background-color: {colors['hover']};
            }}
            
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 13px;
                min-height: 16px;
            }}
            
            QPushButton:hover {{
                background-color: {colors['secondary']};
            }}
            
            QPushButton:disabled {{
                background-color: {colors['border']};
                color: {colors['text_secondary']};
            }}
            
            #seriesButton, #sessionTypeButton {{
                background-color: {colors['surface']};
                color: {colors['text_primary']};
                border: 2px solid {colors['border']};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 11px;
                font-weight: 600;
                min-width: 80px;
            }}
            
            #seriesButton:hover, #sessionTypeButton:hover {{
                background-color: {colors['hover']};
                border-color: {colors['secondary']};
            }}
            
            #seriesButton:checked, #sessionTypeButton:checked {{
                background-color: {colors['primary']};
                color: white;
                border-color: {colors['primary']};
            }}
            
            #mediaFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            
            #mediaList {{
                color: {colors['text_secondary']};
            }}
        """)
    
    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        """Set metadata for the note creation panel"""
        self.metadata = metadata
        self.populate_tracks()
        self.populate_drivers()
        
        # Set tags for the tag selector
        tags = metadata.get('tags', [])
        self.tag_selector.set_tags(tags)
        
        logger.info(f"Metadata updated: {len(tags)} tags available")
    
    def populate_tracks(self) -> None:
        """Populate track dropdown"""
        try:
            self.track_combo.clear()
            
            if not self.metadata:
                # Add sample tracks for development
                sample_tracks = [
                    ("Daytona International Speedway", "Superspeedway"),
                    ("Charlotte Motor Speedway", "Intermediate"),
                    ("Martinsville Speedway", "Short Track"),
                    ("Watkins Glen International", "Road Course"),
                    ("Talladega Superspeedway", "Superspeedway"),
                    ("Bristol Motor Speedway", "Short Track"),
                    ("Sonoma Raceway", "Road Course"),
                    ("Kansas Speedway", "Intermediate"),
                    ("Phoenix Raceway", "Short Track"),
                    ("Circuit of the Americas", "Road Course")
                ]
                
                for track_name, track_type in sample_tracks:
                    track_obj = type('Track', (), {'name': track_name, 'type': track_type})()
                    self.track_combo.addItem(track_name, track_obj)
            else:
                tracks = self.metadata.get('tracks', [])
                for track in tracks:
                    self.track_combo.addItem(track.name, track)
                    
            logger.info(f"Populated {self.track_combo.count()} tracks")
            
        except Exception as e:
            logger.error(f"Error populating tracks: {e}")
            raise UIError(f"Failed to populate tracks: {e}")
    
    def populate_drivers(self) -> None:
        """Populate driver dropdown"""
        try:
            self.driver_combo.clear()
            
            # Add "No driver" option
            self.driver_combo.addItem("No driver selected", None)
            
            if self.metadata and self.metadata.get('drivers'):
                drivers = self.metadata.get('drivers', [])
                
                # Sort drivers by name for better UX
                drivers_sorted = sorted(drivers, key=lambda d: d.name)
                
                for driver in drivers_sorted:
                    self.driver_combo.addItem(driver.name, driver)
                    
                logger.info(f"Populated {len(drivers)} drivers")
            else:
                logger.warning("No drivers available in metadata")
            
        except Exception as e:
            logger.error(f"Error populating drivers: {e}")
            raise UIError(f"Failed to populate drivers: {e}")
    
    def on_selection_changed(self) -> None:
        """Handle track/series/session selection changes"""
        try:
            # Check if all required selections are made
            track_selected = self.track_combo.currentText() != ""
            series_selected = self.series_buttons.checkedButton() is not None
            session_type_selected = self.session_type_buttons.checkedButton() is not None
            
            if track_selected and series_selected and session_type_selected:
                self.save_button.setEnabled(True)
                logger.debug("All selections made, enabling save button")
            else:
                self.save_button.setEnabled(False)
                logger.debug("Incomplete selections, disabling save button")
                
        except Exception as e:
            logger.error(f"Error handling selection change: {e}")
    
    def on_tags_changed(self, tag_ids: List[str]) -> None:
        """Handle tag selection changes"""
        self.selected_tag_ids = tag_ids
        logger.debug(f"Selected tag IDs: {tag_ids}")
    
    # update_context_display method removed - context display was removed per user request
    
    def save_note(self) -> None:
        """Save the racing note"""
        try:
            body = self.body_edit.toPlainText().strip()
            if not body:
                logger.warning("Attempted to save empty note")
                return
            
            # Ensure all selections are made
            track_data = self.track_combo.currentData()
            series_button = self.series_buttons.checkedButton()
            session_type_button = self.session_type_buttons.checkedButton()
            
            if not all([track_data, series_button, session_type_button]):
                logger.warning("Attempted to save note with incomplete selections")
                return
            
            series_name = series_button.text()
            session_type_raw = session_type_button.text()
            
            # Map UI session type to database enum values
            session_type_map = {
                'PRACTICE': 'Practice',
                'QUALIFYING': 'Qualifying', 
                'RACE': 'Race'
            }
            session_type = session_type_map.get(session_type_raw, session_type_raw)
            
            # Get selected driver (if any)
            selected_driver = self.driver_combo.currentData()
            driver_id = selected_driver.id if selected_driver else None
            
            # Convert selected tag IDs to UUIDs
            from uuid import UUID
            tag_uuids = [UUID(tag_id) for tag_id in self.selected_tag_ids]
            
            # Create note with track/series/driver context
            note_create = NoteCreate(
                body=body,
                shared=True,  # All notes are shared now
                session_id=None,  # We'll create/find session in backend
                driver_id=driver_id,
                category=NoteCategory.GENERAL,
                tag_ids=tag_uuids  # Include selected tags
            )
            
            # Add context info for backend processing
            context_info = {
                'track': track_data,
                'series': series_name,
                'session_type': session_type
            }
            
            if selected_driver:
                logger.info(f"Saving note for {session_type} at {track_data.name} - Driver: {selected_driver.name} - Tags: {len(tag_uuids)}")
            else:
                logger.info(f"Saving note for {session_type} at {track_data.name} - General note - Tags: {len(tag_uuids)}")
            
            # Include media files in the signal
            self.note_created.emit((note_create, context_info, self.uploaded_files))
            
            # Clear form
            self.clear_form()
            
        except Exception as e:
            logger.error(f"Error saving note: {e}")
            raise ValidationError(f"Failed to save note: {e}")
    

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            # Check if any of the URLs are files
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    event.acceptProposedAction()
                    logger.debug("Drag enter accepted")
                    return
        event.ignore()
        logger.debug("Drag enter ignored")
    
    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events"""
        try:
            if event.mimeData().hasUrls():
                files = []
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if os.path.isfile(file_path):
                            files.append(file_path)
                
                if files:
                    self.handle_dropped_files(files)
                    event.acceptProposedAction()
                    logger.info(f"Dropped {len(files)} files")
                    return
            event.ignore()
            
        except Exception as e:
            logger.error(f"Error handling drop event: {e}")
            event.ignore()
    
    def handle_dropped_files(self, file_paths: list) -> None:
        """Handle dropped media files"""
        try:
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                file_ext = os.path.splitext(file_name)[1].lower()
                
                # Determine file type
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    file_type = "📷 Image"
                elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                    file_type = "🎥 Video"
                elif file_ext in ['.pdf']:
                    file_type = "📄 PDF"
                elif file_ext in ['.csv', '.xlsx', '.xls']:
                    file_type = "📊 Data"
                elif file_ext in ['.txt', '.doc', '.docx']:
                    file_type = "📝 Document"
                else:
                    file_type = "📎 File"
                
                size_mb = file_size / (1024 * 1024)
                
                file_info = {
                    'path': file_path,
                    'name': file_name,
                    'size': file_size,
                    'type': file_type,
                    'ext': file_ext,
                    'size_mb': size_mb
                }
                
                self.uploaded_files.append(file_info)
                logger.debug(f"Added file: {file_name} ({file_type})")
            
            self.update_media_display()
            
        except Exception as e:
            logger.error(f"Error handling dropped files: {e}")
            raise UIError(f"Failed to handle dropped files: {e}")
    
    def update_media_display(self) -> None:
        """Update the media files display"""
        try:
            if not self.uploaded_files:
                self.media_frame.setVisible(False)
                return
            
            self.media_frame.setVisible(True)
            
            # Create display text
            file_texts = []
            for file_info in self.uploaded_files:
                size_mb = file_info['size'] / (1024 * 1024)
                if size_mb < 1:
                    size_text = f"{file_info['size'] / 1024:.1f} KB"
                else:
                    size_text = f"{size_mb:.1f} MB"
                
                file_text = f"{file_info['type']} {file_info['name']} ({size_text})"
                file_texts.append(file_text)
            
            self.media_list.setText("\n".join(file_texts))
            logger.debug(f"Updated media display with {len(self.uploaded_files)} files")
            
        except Exception as e:
            logger.error(f"Error updating media display: {e}")
    
    def clear_form(self) -> None:
        """Clear the form after successful save"""
        try:
            self.body_edit.clear()
            self.uploaded_files.clear()
            self.update_media_display()
            
            # Clear tag selection
            self.tag_selector.clear_selection()
            self.selected_tag_ids.clear()
            
            # Keep track/series/session selections for easier repeated note taking
            logger.debug("Form cleared after successful save")
            
        except Exception as e:
            logger.error(f"Error clearing form: {e}") 