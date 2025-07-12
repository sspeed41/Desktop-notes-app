"""
Media viewer dialog for displaying videos and images
"""

import os
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QDesktopServices, QIcon
from PySide6.QtCore import QUrl

from app.settings import COLORS, FONTS


class MediaViewerDialog(QDialog):
    """Dialog for viewing media files"""
    
    def __init__(self, file_path: str, media_type: str, filename: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.media_type = media_type
        self.filename = filename if filename is not None else os.path.basename(file_path)
        
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        """Setup the media viewer UI"""
        self.setWindowTitle(f"Media Viewer - {self.filename}")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        if self.media_type == "video":
            icon = "🎥"
            type_text = "Video File"
        elif self.media_type == "image":
            icon = "📷"
            type_text = "Image File"
        else:
            icon = "📎"
            type_text = "Media File"
            
        title_label = QLabel(f"{icon} {type_text}")
        title_label.setFont(QFont(FONTS["primary"], 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Filename
        filename_label = QLabel(self.filename)
        filename_label.setFont(QFont(FONTS["secondary"], 12))
        filename_label.setWordWrap(True)
        layout.addWidget(filename_label)
        
        # Media content area
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_frame.setMinimumHeight(300)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(16)
        
        if self.media_type == "image":
            self.display_image(content_layout)
        else:
            self.display_media_info(content_layout)
            
        layout.addWidget(content_frame)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        # Open with default app button
        open_btn = QPushButton("🚀 Open with Default App")
        open_btn.clicked.connect(self.open_with_default_app)
        actions_layout.addWidget(open_btn)
        
        actions_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        actions_layout.addWidget(close_btn)
        
        layout.addLayout(actions_layout)
        
    def display_image(self, layout):
        """Display image preview"""
        try:
            actual_path = self.file_path.replace("local://", "")
            if os.path.exists(actual_path):
                pixmap = QPixmap(actual_path)
                if not pixmap.isNull():
                    # Scale image to fit dialog
                    scaled_pixmap = pixmap.scaled(
                        QSize(500, 400), 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    image_label = QLabel()
                    image_label.setPixmap(scaled_pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.addWidget(image_label)
                    return
                    
        except Exception as e:
            print(f"Error loading image: {e}")
            
        # Fallback if image can't be loaded
        self.display_media_info(layout)
        
    def display_media_info(self, layout):
        """Display media file information"""
        info_label = QLabel()
        
        if self.media_type == "video":
            info_text = f"""
            🎥 Video File
            
            Filename: {self.filename}
            Location: {self.file_path}
            
            Click "Open with Default App" to play this video
            in your system's default video player.
            """
        else:
            info_text = f"""
            📎 Media File
            
            Filename: {self.filename}
            Location: {self.file_path}
            
            Click "Open with Default App" to open this file
            with your system's default application.
            """
            
        info_label.setText(info_text.strip())
        info_label.setFont(QFont(FONTS["secondary"], 11))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
    def open_with_default_app(self):
        """Open media file with default system application"""
        try:
            actual_path = self.file_path.replace("local://", "")
            if os.path.exists(actual_path):
                url = QUrl.fromLocalFile(actual_path)
                QDesktopServices.openUrl(url)
                print(f"Opening {self.filename} with default app")
            else:
                print(f"File not found: {actual_path}")
        except Exception as e:
            print(f"Error opening file: {e}")
            
    def apply_theme(self):
        """Apply theme to the dialog"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
                color: {COLORS['text_primary']};
            }}
            
            #contentFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
            
            QPushButton:pressed {{
                background-color: {COLORS['primary']};
            }}
        """)


def show_media_viewer(file_path: str, media_type: str, filename: Optional[str] = None, parent=None):
    """Convenience function to show media viewer"""
    viewer = MediaViewerDialog(file_path, media_type, filename, parent)
    viewer.exec() 