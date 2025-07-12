"""
Media preview component for displaying videos and images like Twitter/X
"""

import os
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, 
    QSlider, QGridLayout, QApplication, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QThread, QPoint
from PySide6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QIcon, QMovie
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from app.data.models import MediaInfo, MediaType
from app.settings import COLORS, FONTS


class VideoThumbnailGenerator(QThread):
    """Thread for generating video thumbnails"""
    
    thumbnail_ready = Signal(str, QPixmap)  # file_path, thumbnail
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        """Generate thumbnail for video"""
        try:
            # For now, create a simple placeholder thumbnail
            # In a real implementation, you'd use ffmpeg or similar to extract frames
            pixmap = QPixmap(300, 200)
            pixmap.fill(QColor(25, 25, 25))
            
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont(FONTS["primary"], 14))
            
            # Draw video icon and filename
            filename = os.path.basename(self.file_path)
            painter.drawText(10, 30, "🎥 VIDEO")
            painter.drawText(10, 60, filename[:30] + "..." if len(filename) > 30 else filename)
            painter.drawText(10, 90, "Click to play")
            
            # Draw play button
            play_button_rect = pixmap.rect()
            play_button_rect.setWidth(60)
            play_button_rect.setHeight(60)
            play_button_rect.moveCenter(pixmap.rect().center())
            
            painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
            painter.setPen(QColor(255, 255, 255, 0))  # Transparent pen
            painter.drawEllipse(play_button_rect)
            
            # Draw play triangle
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            center = play_button_rect.center()
            points = [
                QPoint(center.x() - 12, center.y() - 15),
                QPoint(center.x() - 12, center.y() + 15),
                QPoint(center.x() + 15, center.y())
            ]
            painter.drawPolygon(points)
            
            painter.end()
            
            self.thumbnail_ready.emit(self.file_path, pixmap)
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")


class VideoPreview(QFrame):
    """Video preview widget with play controls like Twitter/X"""
    
    video_clicked = Signal(str)  # file_path
    
    def __init__(self, file_path: str, filename: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.filename = filename or os.path.basename(file_path)
        self.thumbnail_pixmap = None
        self.is_playing = False
        
        self.setObjectName("videoPreview")
        self.setFixedSize(300, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setup_ui()
        self.generate_thumbnail()
        
    def setup_ui(self):
        """Setup the video preview UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video display area
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setObjectName("videoDisplay")
        self.video_label.setStyleSheet(f"""
            #videoDisplay {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        layout.addWidget(self.video_label)
        
        # Video info overlay
        self.info_label = QLabel(f"🎥 {self.filename}")
        self.info_label.setFont(QFont(FONTS["secondary"], 10))
        self.info_label.setObjectName("videoInfo")
        self.info_label.setStyleSheet(f"""
            #videoInfo {{
                color: {COLORS['text_secondary']};
                background-color: rgba(0, 0, 0, 150);
                padding: 4px 8px;
                border-radius: 4px;
                margin: 4px;
            }}
        """)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
    def generate_thumbnail(self):
        """Generate video thumbnail"""
        self.thumbnail_generator = VideoThumbnailGenerator(self.file_path)
        self.thumbnail_generator.thumbnail_ready.connect(self.on_thumbnail_ready)
        self.thumbnail_generator.start()
        
    def on_thumbnail_ready(self, file_path: str, thumbnail: QPixmap):
        """Handle thumbnail generation completion"""
        if file_path == self.file_path:
            self.thumbnail_pixmap = thumbnail
            self.video_label.setPixmap(thumbnail.scaled(
                self.video_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            ))
            
    def mousePressEvent(self, event):
        """Handle video click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.video_clicked.emit(self.file_path)
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        """Handle mouse enter for hover effect"""
        self.setStyleSheet(f"""
            #videoPreview {{
                border: 2px solid {COLORS['primary']};
                border-radius: 12px;
            }}
        """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave to remove hover effect"""
        self.setStyleSheet(f"""
            #videoPreview {{
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        super().leaveEvent(event)


class ImagePreview(QLabel):
    """Image preview widget like Twitter/X"""
    
    image_clicked = Signal(str)  # file_path
    
    def __init__(self, file_path: str, filename: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.filename = filename or os.path.basename(file_path)
        
        self.setObjectName("imagePreview")
        self.setFixedSize(300, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.load_image()
        
    def load_image(self):
        """Load and display image"""
        try:
            if self.file_path.startswith("local://"):
                actual_path = self.file_path[8:]  # Remove "local://" prefix
            else:
                actual_path = self.file_path
                
            if os.path.exists(actual_path):
                pixmap = QPixmap(actual_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.size(), 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.setPixmap(scaled_pixmap)
                else:
                    self.setText(f"�� {self.filename}")
            else:
                self.setText(f"📷 {self.filename}\n(File not found)")
                
        except Exception as e:
            self.setText(f"📷 {self.filename}\n(Error loading)")
            print(f"Error loading image: {e}")
            
        self.setStyleSheet(f"""
            #imagePreview {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                color: {COLORS['text_secondary']};
            }}
        """)
        
    def mousePressEvent(self, event):
        """Handle image click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.image_clicked.emit(self.file_path)
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        """Handle mouse enter for hover effect"""
        self.setStyleSheet(f"""
            #imagePreview {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['primary']};
                border-radius: 12px;
                color: {COLORS['text_secondary']};
            }}
        """)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave to remove hover effect"""
        self.setStyleSheet(f"""
            #imagePreview {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                color: {COLORS['text_secondary']};
            }}
        """)
        super().leaveEvent(event)


class MediaPreview(QWidget):
    """Media preview container that displays videos and images like Twitter/X"""
    
    media_clicked = Signal(str, str)  # file_path, media_type
    
    def __init__(self, media_files: List[MediaInfo], parent=None):
        super().__init__(parent)
        self.media_files = media_files
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the media preview UI"""
        if not self.media_files:
            return
            
        # Create grid layout for media items
        if len(self.media_files) == 1:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 8, 0, 8)
            self.add_media_item(self.media_files[0], layout)
        else:
            # For multiple media items, use a grid
            layout = QGridLayout(self)
            layout.setContentsMargins(0, 8, 0, 8)
            layout.setSpacing(8)
            
            for i, media_info in enumerate(self.media_files[:4]):  # Limit to 4 items
                row = i // 2
                col = i % 2
                media_widget = self.create_media_widget(media_info)
                if media_widget:
                    layout.addWidget(media_widget, row, col)
                    
            if len(self.media_files) > 4:
                # Add "+X more" label
                more_label = QLabel(f"+{len(self.media_files) - 4} more")
                more_label.setFont(QFont(FONTS["secondary"], 10))
                more_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                more_label.setObjectName("moreMediaLabel")
                more_label.setStyleSheet(f"""
                    #moreMediaLabel {{
                        color: {COLORS['text_secondary']};
                        background-color: {COLORS['surface']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 12px;
                        padding: 20px;
                    }}
                """)
                layout.addWidget(more_label, (len(self.media_files) - 1) // 2, 1)
                
    def add_media_item(self, media_info: MediaInfo, layout):
        """Add a single media item to the layout"""
        media_widget = self.create_media_widget(media_info)
        if media_widget:
            layout.addWidget(media_widget)
            
    def create_media_widget(self, media_info: MediaInfo) -> Optional[QWidget]:
        """Create appropriate widget for media type"""
        try:
            if media_info.media_type == MediaType.VIDEO:
                widget = VideoPreview(media_info.file_url, media_info.filename)
                widget.video_clicked.connect(lambda path: self.media_clicked.emit(path, "video"))
                return widget
            elif media_info.media_type == MediaType.IMAGE:
                widget = ImagePreview(media_info.file_url, media_info.filename)
                widget.image_clicked.connect(lambda path: self.media_clicked.emit(path, "image"))
                return widget
            else:
                # For other media types, show a generic file preview
                widget = QLabel(f"📎 {media_info.filename or 'Unknown file'}")
                widget.setFont(QFont(FONTS["secondary"], 10))
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                widget.setObjectName("genericMediaPreview")
                widget.setStyleSheet(f"""
                    #genericMediaPreview {{
                        color: {COLORS['text_secondary']};
                        background-color: {COLORS['surface']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 12px;
                        padding: 20px;
                    }}
                """)
                return widget
                
        except Exception as e:
            print(f"Error creating media widget: {e}")
            return None


class SimpleMediaPreview(QWidget):
    """Simplified media preview for Twitter-like display"""
    
    def __init__(self, media_files: List[MediaInfo], parent=None):
        super().__init__(parent)
        self.media_files = media_files
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup simple media preview UI"""
        if not self.media_files:
            return
            
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)
        
        # Show first media item with details
        first_media = self.media_files[0]
        
        # Create media container
        media_container = QFrame()
        media_container.setObjectName("mediaContainer")
        media_container.setFixedHeight(200)
        media_container.setStyleSheet(f"""
            #mediaContainer {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        container_layout = QVBoxLayout(media_container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(8)
        
        # Media type icon and filename
        if first_media.media_type == MediaType.VIDEO:
            icon = "🎥"
            type_text = "Video"
        elif first_media.media_type == MediaType.IMAGE:
            icon = "📷"
            type_text = "Image"
        else:
            icon = "📎"
            type_text = "File"
            
        # Title
        title_label = QLabel(f"{icon} {type_text}")
        title_label.setFont(QFont(FONTS["primary"], 14, QFont.Weight.Bold))
        title_label.setObjectName("mediaTitle")
        title_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        container_layout.addWidget(title_label)
        
        # Filename
        filename = first_media.filename or "Unknown file"
        filename_label = QLabel(filename)
        filename_label.setFont(QFont(FONTS["secondary"], 11))
        filename_label.setObjectName("mediaFilename")
        filename_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        filename_label.setWordWrap(True)
        container_layout.addWidget(filename_label)
        
        # Click to play/view message
        if first_media.media_type == MediaType.VIDEO:
            action_text = "▶️ Click to play video"
        elif first_media.media_type == MediaType.IMAGE:
            action_text = "🔍 Click to view image"
        else:
            action_text = "📎 Click to open file"
            
        action_label = QLabel(action_text)
        action_label.setFont(QFont(FONTS["secondary"], 10))
        action_label.setObjectName("mediaAction")
        action_label.setStyleSheet(f"""
            color: {COLORS['primary']};
            background-color: {COLORS['background']};
            padding: 8px;
            border-radius: 6px;
            border: 1px solid {COLORS['border']};
        """)
        container_layout.addWidget(action_label)
        
        container_layout.addStretch()
        
        # Multiple files indicator
        if len(self.media_files) > 1:
            count_label = QLabel(f"📎 {len(self.media_files)} files attached")
            count_label.setFont(QFont(FONTS["secondary"], 9))
            count_label.setObjectName("mediaCount")
            count_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            container_layout.addWidget(count_label)
            
        layout.addWidget(media_container)
        
        # Make container clickable
        media_container.mousePressEvent = self.on_media_click
        
    def on_media_click(self, event):
        """Handle media container click"""
        if self.media_files:
            first_media = self.media_files[0]
            
            # Open media viewer dialog
            from app.ui.components.media_viewer import show_media_viewer
            
            media_type = "video" if first_media.media_type == MediaType.VIDEO else \
                        "image" if first_media.media_type == MediaType.IMAGE else "file"
                        
            show_media_viewer(
                first_media.file_url,
                media_type,
                first_media.filename,
                self.parent()
            ) 