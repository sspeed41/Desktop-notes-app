"""
Main window for WiseDesktopNoteApp with split layout design
"""

import logging
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QFrame, QInputDialog, QDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from app.ui.feed_view import FeedView
from app.ui.components.note_creation_panel import NoteCreationPanel
from app.services.data_service import DataService
from app.config import get_ui_config, get_config
from app.data.models import NoteCreate
from app.utils.exceptions import UIError, DatabaseError
from app import __version__

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with split layout design"""
    
    def __init__(self):
        super().__init__()
        
        # Get configuration
        self.config = get_config()
        self.ui_config = get_ui_config()
        
        # Initialize data service
        self.data_service: Optional[DataService] = None
        self.is_online = False
        
        logger.info(f"Initializing {self.config.name} v{self.config.version}")
        
        self.setup_ui()
        self.setup_data_service()
        self.apply_theme()
        
        # Start data loading
        self.load_data()
        self.current_user = self._select_user()
    
    def setup_ui(self) -> None:
        """Setup the main UI layout"""
        self.setWindowTitle(f"Racing Notes v{__version__}")
        self.setMinimumSize(1400, 800)
        self.resize(1600, 1000)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar
        self.setup_top_bar(main_layout)
        
        # Create splitter for 50/50 layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left side - Feed view
        feed_container = QWidget()
        feed_layout = QVBoxLayout(feed_container)
        feed_layout.setContentsMargins(0, 0, 0, 0)
        
        # Feed title
        feed_title = QLabel("📰 Recent Racing Notes")
        feed_title.setFont(QFont(self.ui_config.fonts["primary"], 16, QFont.Weight.Bold))
        feed_title.setContentsMargins(20, 16, 20, 8)
        feed_layout.addWidget(feed_title)
        
        # Feed view
        self.feed_view = FeedView()
        feed_layout.addWidget(self.feed_view)
        
        splitter.addWidget(feed_container)
        
        # Right side - Note creation panel
        self.note_panel = NoteCreationPanel()
        self.note_panel.note_created.connect(self.on_note_created)
        splitter.addWidget(self.note_panel)
        
        # Set splitter proportions (50/50)
        splitter.setSizes([800, 800])
        
        logger.debug("UI setup complete")
    
    def setup_top_bar(self, parent_layout: QVBoxLayout) -> None:
        """Setup the top bar with title and status"""
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setObjectName("topBar")
        
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)
        
        # App title/logo area with version
        title_container = QHBoxLayout()
        title_label = QLabel(f"🏁 {self.config.name}")
        title_label.setFont(QFont(self.ui_config.fonts["primary"], 18, QFont.Weight.Bold))
        title_label.setObjectName("titleLabel")
        title_container.addWidget(title_label)
        
        # Version badge
        version_label = QLabel(f"v{self.config.version}")
        version_label.setFont(QFont(self.ui_config.fonts["secondary"], 11, QFont.Weight.Bold))
        version_label.setObjectName("versionLabel")
        version_label.setStyleSheet(f"""
            QLabel#versionLabel {{
                background-color: {self.ui_config.colors['primary']};
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                margin-left: 8px;
            }}
        """)
        title_container.addWidget(version_label)
        title_container.addStretch()
        
        # Add title container to main layout
        title_widget = QWidget()
        title_widget.setLayout(title_container)
        top_layout.addWidget(title_widget)
        
        top_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("🔄 Connecting...")
        self.status_label.setFont(QFont(self.ui_config.fonts["secondary"], 12))
        self.status_label.setObjectName("statusLabel")
        top_layout.addWidget(self.status_label)
        
        parent_layout.addWidget(top_bar)
    
    def setup_data_service(self) -> None:
        """Setup data service for async operations"""
        try:
            self.data_service = DataService()
            
            # Connect signals
            self.data_service.connection_status.connect(self.on_connection_status_changed)
            self.data_service.metadata_loaded.connect(self.on_metadata_loaded)
            self.data_service.notes_loaded.connect(self.on_notes_loaded)
            self.data_service.note_created.connect(self.on_note_saved)
            self.data_service.error_occurred.connect(self.on_error_occurred)
            self.data_service.upload_progress.connect(self.on_upload_progress)
            
            logger.info("DataService initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup data service: {e}")
            self.show_error_message("Failed to initialize data service")
    
    def load_data(self) -> None:
        """Trigger initial data loading"""
        if self.data_service:
            try:
                # Connect to database and load initial data
                self.data_service.connect_to_database()
                self.data_service.load_metadata()
                self.data_service.load_notes()
                
                logger.info("Data loading initiated")
                
            except Exception as e:
                logger.error(f"Error initiating data load: {e}")
                self.show_error_message("Failed to load data")
    
    def apply_theme(self) -> None:
        """Apply clean theme using configuration colors"""
        colors = self.ui_config.colors
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {colors['background']};
                color: {colors['text_primary']};
            }}
            
            #topBar {{
                background-color: {colors['background']};
                border-bottom: 1px solid {colors['border']};
            }}
            
            #titleLabel {{
                color: {colors['text_primary']};
                font-weight: bold;
            }}
            
            #statusLabel {{
                color: {colors['text_secondary']};
            }}
            
            QSplitter::handle {{
                background-color: {colors['border']};
                width: 2px;
            }}
            
            QScrollBar:vertical {{
                background-color: {colors['surface']};
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors['secondary']};
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['text_secondary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        logger.debug("Theme applied")
    
    def on_connection_status_changed(self, is_connected: bool) -> None:
        """Handle connection status changes"""
        self.is_online = is_connected
        colors = self.ui_config.colors
        
        if is_connected:
            self.status_label.setText("🟢 Online")
            self.status_label.setStyleSheet(f"color: {colors['success']};")
            logger.info("Connection established")
        else:
            self.status_label.setText("🔴 Offline")
            self.status_label.setStyleSheet(f"color: {colors['error']};")
            logger.warning("Connection lost - operating in offline mode")
    
    def on_metadata_loaded(self, metadata: Dict[str, Any]) -> None:
        """Handle metadata loading completion"""
        try:
            # Pass metadata to note creation panel
            self.note_panel.set_metadata(metadata)
            logger.info(f"Metadata loaded: {len(metadata.get('tracks', []))} tracks, {len(metadata.get('series', []))} series")
            
        except Exception as e:
            logger.error(f"Error processing metadata: {e}")
    
    def on_notes_loaded(self, notes: list) -> None:
        """Handle notes loading completion"""
        try:
            self.feed_view.set_notes(notes)
            logger.info(f"Loaded {len(notes)} notes")
            
        except Exception as e:
            logger.error(f"Error displaying notes: {e}")
    
    def on_note_created(self, note_data: tuple) -> None:
        """Handle new note creation"""
        try:
            # note_data is a tuple of (note_create, context_info, media_files)
            if len(note_data) == 3:
                note_create, context_info, media_files = note_data
            else:
                # Backward compatibility
                note_create, context_info = note_data
                media_files = []
            
            # Log note creation details
            base_info = f"Creating note for {context_info['session_type']} at {context_info['track'].name} in {context_info['series']}"
            if note_create.driver_id:
                # Find driver name for logging (we don't have it in context_info)
                logger.info(f"{base_info} - Driver-specific note")
            else:
                logger.info(f"{base_info} - General note")
                
            if media_files:
                logger.info(f"Note includes {len(media_files)} media attachments")
            
            # Use the data service to save the note
            if self.data_service:
                self.data_service.create_note(note_create, context_info, media_files, self.current_user)
            else:
                logger.error("Data service not available")
                self.show_error_message("Cannot save note: data service unavailable")
                
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            self.show_error_message("Failed to save note")
    
    def on_note_saved(self, note) -> None:
        """Handle successful note save"""
        try:
            if note:
                logger.info(f"Note saved successfully: {note.id if hasattr(note, 'id') else 'queued for sync'}")
            else:
                logger.warning("Note saved but no confirmation received")
            
            # Always refresh the feed to show the new note
            if self.data_service:
                logger.info("Refreshing note feed after save")
                self.data_service.load_notes()
                
        except Exception as e:
            logger.error(f"Error handling note save confirmation: {e}")
            # Even if there's an error, try to refresh the feed
            if self.data_service:
                self.data_service.load_notes()
    
    def on_error_occurred(self, error_message: str) -> None:
        """Handle errors from data service"""
        logger.error(f"Data service error: {error_message}")
        self.show_error_message(f"Operation failed: {error_message}")
    
    def on_upload_progress(self, progress_message: str) -> None:
        """Handle upload progress updates"""
        colors = self.ui_config.colors
        self.status_label.setText(progress_message)
        self.status_label.setStyleSheet(f"color: {colors['primary']};")
        logger.info(f"Upload progress: {progress_message}")
        
        # Clear progress message after 3 seconds if it's a completion message
        if "✅" in progress_message or "⚠️" in progress_message:
            QTimer.singleShot(3000, lambda: self.status_label.setText("🟢 Online" if self.is_online else "🔴 Offline"))
    
    def show_error_message(self, message: str) -> None:
        """Show error message to user"""
        # For now, just update status label
        colors = self.ui_config.colors
        self.status_label.setText(f"❌ {message}")
        self.status_label.setStyleSheet(f"color: {colors['error']};")
        
        # Clear error message after 5 seconds
        QTimer.singleShot(5000, lambda: self.status_label.setText("🔴 Offline" if not self.is_online else "🟢 Online"))
    
    def closeEvent(self, event) -> None:
        """Handle application close"""
        try:
            logger.info("Application closing...")
            
            if self.data_service:
                self.data_service.shutdown()
                
            logger.info("Application closed successfully")
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during application close: {e}")
            event.accept()  # Always accept to avoid hanging 

    def _select_user(self):
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Select Note Taker")
        dialog.setLabelText("Choose or enter your name:")
        dialog.setComboBoxItems(["Scott Speed", "Dan Stratton", "Josh Wise"])
        dialog.setComboBoxEditable(True)
        if dialog.exec_() == QDialog.DialogCode.Accepted:
            return dialog.textValue() or "Anonymous"
        return "Anonymous" 