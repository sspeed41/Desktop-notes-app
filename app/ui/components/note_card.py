"""
Note card component for displaying individual notes
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor

from app.data.models import NoteView
from app.settings import COLORS, FONTS
import logging

logger = logging.getLogger(__name__)


class TagLabel(QLabel):
    """Custom tag label widget"""
    
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("tagLabel")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup tag appearance"""
        self.setFont(QFont(FONTS["secondary"], 10))
        self.setStyleSheet(f"""
            #tagLabel {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 2px 8px;
                border-radius: 10px;
                font-weight: bold;
            }}
        """)


class NoteCard(QFrame):
    """Twitter-like note card widget"""
    
    note_clicked = Signal(NoteView)
    
    def __init__(self, note: NoteView, parent=None):
        super().__init__(parent)
        self.note = note
        self.setObjectName("noteCard")
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup the note card UI"""
        self.setMaximumWidth(800)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        
        # Header with metadata
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # User/author info
        author_label = QLabel(f"{self.note.created_by}")
        author_label.setFont(QFont(FONTS["primary"], 12, QFont.Weight.Bold))
        author_label.setObjectName("authorLabel")
        header_layout.addWidget(author_label)
        
        # Timestamp
        time_str = self.note.created_at.strftime("%b %d, %Y at %I:%M %p")
        time_label = QLabel(time_str)
        time_label.setFont(QFont(FONTS["secondary"], 10))
        time_label.setObjectName("timeLabel")
        header_layout.addWidget(time_label)
        
        header_layout.addStretch()

        if self.note.track_name:
            track_label = QLabel(self.note.track_name)
            track_label.setFont(QFont(FONTS["secondary"], 10, QFont.Weight.Bold))
            track_label.setObjectName("trackLabel")
            header_layout.addWidget(track_label)

        layout.addLayout(header_layout)
        
        # Details layout for driver, series, session
        details_layout = QHBoxLayout()
        details_layout.setSpacing(12)
        
        if self.note.driver_name:
            driver_label = QLabel(f"{self.note.driver_name}")
            driver_label.setFont(QFont(FONTS["secondary"], 10))
            driver_label.setObjectName("contextLabel")
            details_layout.addWidget(driver_label)

        if self.note.series_name:
            series_label = QLabel(f"{self.note.series_name}")
            series_label.setFont(QFont(FONTS["secondary"], 10))
            series_label.setObjectName("contextLabel")
            details_layout.addWidget(series_label)

        if self.note.session_type:
            session_label = QLabel(f"{self.note.session_type.value}")
            session_label.setFont(QFont(FONTS["secondary"], 10))
            session_label.setObjectName("contextLabel")
            details_layout.addWidget(session_label)
        
        details_layout.addStretch()
        layout.addLayout(details_layout)

        # Note body
        body_label = QLabel(self.note.body)
        body_label.setWordWrap(True)
        body_label.setFont(QFont(FONTS["primary"], 13))
        body_label.setObjectName("bodyLabel")
        body_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(body_label)
        
        # Tags
        if self.note.tags:
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(6)
            
            for tag in self.note.tags[:5]:  # Limit to 5 tags for space
                if tag:  # Skip empty tags
                    tag_label = TagLabel(f"#{tag}")
                    tags_layout.addWidget(tag_label)
            
            if len(self.note.tags) > 5:
                more_label = QLabel(f"...+{len(self.note.tags) - 5} more")
                more_label.setFont(QFont(FONTS["secondary"], 9))
                more_label.setObjectName("moreTagsLabel")
                tags_layout.addWidget(more_label)
            
            tags_layout.addStretch()
            layout.addLayout(tags_layout)
        
        # Media attachments with inline preview (like Twitter/X)
        if hasattr(self.note, 'media_files') and self.note.media_files:
            try:
                # Use the new Twitter-like inline media preview
                from app.ui.components.inline_video_player import TwitterLikeMediaPreview
                media_preview = TwitterLikeMediaPreview(self.note.media_files)
                layout.addWidget(media_preview)
                
            except Exception as e:
                # Fallback: simple text display
                error_label = QLabel(f"📎 Media attached (preview error)")
                error_label.setFont(QFont(FONTS["secondary"], 10))
                error_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
                layout.addWidget(error_label)
                logger.debug(f"Media preview error: {e}")
        
        # Footer with actions (placeholder for future features)
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(16)
        
        # Add some spacing
        footer_layout.addStretch()
        
        layout.addLayout(footer_layout)
    
    def apply_theme(self):
        """Apply Twitter-like theme"""
        self.setStyleSheet(f"""
            #noteCard {{
                background-color: {COLORS['background']};
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                border-radius: 0px;
                margin: 0px;
            }}
            
            #noteCard:hover {{
                background-color: {COLORS['hover']};
            }}
            
            #trackLabel {{
                color: {COLORS['text_primary']};
            }}
            
            #authorLabel {{
                color: {COLORS['text_primary']};
                font-weight: bold;
            }}
            
            #timeLabel {{
                color: {COLORS['text_secondary']};
            }}
            
            #contextLabel {{
                color: {COLORS['text_secondary']};
                background-color: {COLORS['surface']};
                padding: 2px 6px;
                border-radius: 6px;
            }}
            
            #bodyLabel {{
                color: {COLORS['text_primary']};
                line-height: 1.4;
                padding: 4px 0px;
            }}
            
            #mediaLabel {{
                color: {COLORS['primary']};
                font-weight: bold;
            }}
            
            #seriesLabel {{
                color: {COLORS['text_secondary']};
                font-style: italic;
            }}
            
            #moreTagsLabel {{
                color: {COLORS['text_secondary']};
                font-style: italic;
            }}
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press for note selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.note_clicked.emit(self.note)
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effect"""
        self.setProperty("hover", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave to remove hover effect"""
        self.setProperty("hover", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)
    
 