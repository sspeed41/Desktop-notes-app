"""
Inline video player component like Twitter/X
Auto-play, click to pause/play, with controls overlay
"""

import os
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QSlider, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize, QUrl
from PySide6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QIcon, QPalette
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from app.data.models import MediaInfo, MediaType
from app.settings import COLORS, FONTS


class InlineVideoPlayer(QFrame):
    """Twitter/X-style inline video player with auto-play and click controls"""
    
    def __init__(self, file_path: str, filename: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.filename = filename or os.path.basename(file_path)
        self.is_playing = False
        self.is_muted = True  # Start muted like Twitter
        
        self.setObjectName("inlineVideoPlayer")
        self.setFixedHeight(250)  # Twitter-like aspect ratio
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Initialize media player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setMuted(self.is_muted)
        self.media_player.setAudioOutput(self.audio_output)
        
        # Create video widget
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        self.setup_ui()
        self.setup_video()
        self.apply_styling()
        
        # Connect signals
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.media_player.playbackStateChanged.connect(self.on_playback_state_changed)
        
    def setup_ui(self):
        """Setup the video player UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video container
        self.video_container = QFrame()
        self.video_container.setObjectName("videoContainer")
        
        video_layout = QVBoxLayout(self.video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        # Video widget
        self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        video_layout.addWidget(self.video_widget)
        
        # Controls overlay
        self.create_controls_overlay()
        
        layout.addWidget(self.video_container)
        
        # Video info
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(12, 8, 12, 8)
        
        self.video_info = QLabel(f"🎥 {self.filename}")
        self.video_info.setFont(QFont(FONTS["secondary"], 10))
        self.video_info.setObjectName("videoInfo")
        info_layout.addWidget(self.video_info)
        
        info_layout.addStretch()
        
        # Mute button
        self.mute_btn = QPushButton("🔇" if self.is_muted else "🔊")
        self.mute_btn.setFixedSize(30, 30)
        self.mute_btn.clicked.connect(self.toggle_mute)
        self.mute_btn.setObjectName("muteBtn")
        info_layout.addWidget(self.mute_btn)
        
        layout.addLayout(info_layout)
        
    def create_controls_overlay(self):
        """Create the play/pause overlay like Twitter"""
        self.controls_overlay = QFrame(self.video_container)
        self.controls_overlay.setObjectName("controlsOverlay")
        self.controls_overlay.setGeometry(0, 0, self.width(), self.height())
        
        overlay_layout = QVBoxLayout(self.controls_overlay)
        overlay_layout.addStretch()
        
        # Center play button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.play_button = QPushButton()
        self.play_button.setFixedSize(60, 60)
        self.play_button.setObjectName("playButton")
        self.play_button.clicked.connect(self.toggle_playback)
        self.update_play_button()
        
        button_layout.addWidget(self.play_button)
        button_layout.addStretch()
        
        overlay_layout.addLayout(button_layout)
        overlay_layout.addStretch()
        
        # Initially show overlay
        self.controls_overlay.show()
        
    def setup_video(self):
        """Setup video source"""
        try:
            # Convert local:// path to actual file path
            actual_path = self.file_path.replace("local://", "")
            if os.path.exists(actual_path):
                media_url = QUrl.fromLocalFile(actual_path)
                self.media_player.setSource(media_url)
                print(f"Video loaded: {actual_path}")
            else:
                print(f"Video file not found: {actual_path}")
                self.show_error_placeholder()
        except Exception as e:
            print(f"Error setting up video: {e}")
            self.show_error_placeholder()
            
    def show_error_placeholder(self):
        """Show error placeholder when video can't load"""
        self.video_info.setText(f"🎥 {self.filename} (Cannot load)")
        
    def toggle_playback(self):
        """Toggle play/pause like Twitter"""
        if self.is_playing:
            self.pause_video()
        else:
            self.play_video()
            
    def play_video(self):
        """Play the video"""
        self.media_player.play()
        self.is_playing = True
        self.update_play_button()
        
        # Hide controls after a delay (like Twitter)
        QTimer.singleShot(1000, self.hide_controls)
        
    def pause_video(self):
        """Pause the video"""
        self.media_player.pause()
        self.is_playing = False
        self.update_play_button()
        self.show_controls()
        
    def update_play_button(self):
        """Update play button icon"""
        if self.is_playing:
            self.play_button.setText("⏸️")
            self.play_button.setToolTip("Pause")
        else:
            self.play_button.setText("▶️")
            self.play_button.setToolTip("Play")
            
    def toggle_mute(self):
        """Toggle mute state"""
        self.is_muted = not self.is_muted
        self.audio_output.setMuted(self.is_muted)
        self.mute_btn.setText("🔇" if self.is_muted else "🔊")
        
    def show_controls(self):
        """Show control overlay"""
        self.controls_overlay.show()
        
    def hide_controls(self):
        """Hide control overlay (only if playing)"""
        if self.is_playing:
            self.controls_overlay.hide()
            
    def mousePressEvent(self, event):
        """Handle click to play/pause"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_playback()
        super().mousePressEvent(event)
        
    def enterEvent(self, event):
        """Show controls on hover"""
        self.show_controls()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Hide controls when not hovering (if playing)"""
        if self.is_playing:
            QTimer.singleShot(500, self.hide_controls)
        super().leaveEvent(event)
        
    def resizeEvent(self, event):
        """Resize controls overlay with widget"""
        if hasattr(self, 'controls_overlay'):
            self.controls_overlay.setGeometry(0, 0, self.width(), self.height() - 40)
        super().resizeEvent(event)
        
    def on_media_status_changed(self, status):
        """Handle media status changes"""
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            print(f"Video loaded successfully: {self.filename}")
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            print(f"Invalid video file: {self.filename}")
            self.show_error_placeholder()
            
    def on_playback_state_changed(self, state):
        """Handle playback state changes"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.is_playing = True
        else:
            self.is_playing = False
        self.update_play_button()
        
    def apply_styling(self):
        """Apply Twitter/X-like styling"""
        self.setStyleSheet(f"""
            #inlineVideoPlayer {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin: 8px 0px;
            }}
            
            #inlineVideoPlayer:hover {{
                border-color: {COLORS['primary']};
            }}
            
            #videoContainer {{
                background-color: #000000;
                border-radius: 12px 12px 0px 0px;
            }}
            
            #controlsOverlay {{
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 12px 12px 0px 0px;
            }}
            
            #playButton {{
                background-color: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 30px;
                font-size: 18px;
                font-weight: bold;
                color: #000000;
            }}
            
            #playButton:hover {{
                background-color: rgba(255, 255, 255, 1.0);
                transform: scale(1.1);
            }}
            
            #playButton:pressed {{
                background-color: rgba(200, 200, 200, 0.9);
            }}
            
            #videoInfo {{
                color: {COLORS['text_secondary']};
                padding: 4px 0px;
            }}
            
            #muteBtn {{
                background-color: transparent;
                border: none;
                color: {COLORS['text_secondary']};
                font-size: 14px;
            }}
            
            #muteBtn:hover {{
                background-color: {COLORS['hover']};
                border-radius: 15px;
            }}
        """)


class TwitterLikeMediaPreview(QWidget):
    """Twitter/X-style media preview with inline video"""
    
    def __init__(self, media_files: list, parent=None):
        super().__init__(parent)
        self.media_files = media_files
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the media preview UI"""
        if not self.media_files:
            return
            
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Show first media item (Twitter shows one at a time)
        first_media = self.media_files[0]
        
        if first_media.media_type == MediaType.VIDEO:
            # Create inline video player
            video_player = InlineVideoPlayer(first_media.file_url, first_media.filename)
            layout.addWidget(video_player)
        elif first_media.media_type == MediaType.IMAGE:
            # Create image preview (existing functionality)
            from app.ui.components.media_preview import ImagePreview
            image_preview = ImagePreview(first_media.file_url, first_media.filename)
            layout.addWidget(image_preview)
        else:
            # Generic file preview
            file_label = QLabel(f"📎 {first_media.filename}")
            file_label.setFont(QFont(FONTS["secondary"], 12))
            file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            file_label.setObjectName("filePreview")
            file_label.setStyleSheet(f"""
                #filePreview {{
                    background-color: {COLORS['surface']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 12px;
                    padding: 20px;
                    color: {COLORS['text_secondary']};
                }}
            """)
            layout.addWidget(file_label)
            
        # Show count if multiple files
        if len(self.media_files) > 1:
            count_label = QLabel(f"📎 +{len(self.media_files) - 1} more files")
            count_label.setFont(QFont(FONTS["secondary"], 10))
            count_label.setStyleSheet(f"color: {COLORS['text_secondary']}; padding: 4px 8px;")
            layout.addWidget(count_label) 