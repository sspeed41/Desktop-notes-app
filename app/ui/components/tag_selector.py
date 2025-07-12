"""
Compact tag selection component for WiseDesktopNoteApp
Small, inline tag buttons that fit in 2 lines maximum
"""

import logging
from typing import List, Set
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.data.models import Tag

logger = logging.getLogger(__name__)


class TagButton(QPushButton):
    """Small, compact tag button"""
    
    tag_toggled = Signal(object, bool)  # tag, is_selected
    
    def __init__(self, tag: Tag, parent=None):
        super().__init__(f"#{tag.label}", parent)
        self.tag = tag
        self.is_selected = False
        
        self.setCheckable(True)
        self.setObjectName("compactTagButton")
        self.clicked.connect(self.on_clicked)
        
        # Make it very compact
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
    def on_clicked(self):
        """Handle tag button click"""
        self.is_selected = self.isChecked()
        self.tag_toggled.emit(self.tag, self.is_selected)


class TagSelector(QWidget):
    """Compact tag selector that fits in 2 lines"""
    
    tags_changed = Signal(list)  # Emits list of selected tag IDs
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.available_tags: List[Tag] = []
        self.selected_tag_ids: Set[str] = set()  # Use tag IDs instead of Tag objects
        self.tag_buttons: List[TagButton] = []
        
        self.setup_ui()
        self.apply_theme()
        
        logger.info("Compact TagSelector initialized")
    
    def setup_ui(self):
        """Setup the compact tag selector UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(2)
        
        # Simple label
        self.label = QLabel("Tags:")
        self.label.setFont(QFont("Arial", 9))
        layout.addWidget(self.label)
        
        # Container for two rows of tags
        self.row1_layout = QHBoxLayout()
        self.row1_layout.setSpacing(3)
        self.row1_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.row2_layout = QHBoxLayout()
        self.row2_layout.setSpacing(3)
        self.row2_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Add both rows
        layout.addLayout(self.row1_layout)
        layout.addLayout(self.row2_layout)
        
        # Selected count
        self.selected_label = QLabel("None selected")
        self.selected_label.setFont(QFont("Arial", 8))
        self.selected_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.selected_label)
    
    def apply_theme(self):
        """Apply minimal theme"""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            
            #compactTagButton {
                background-color: #E0E0E0;
                color: #000000;
                border: 1px solid #999999;
                border-radius: 6px;
                padding: 0px 3px;
                font-size: 7px;
                font-weight: normal;
                min-width: 20px;
                max-height: 15px;
                margin: 0px;
            }
            
            #compactTagButton:hover {
                background-color: #CCCCCC;
                border-color: #666666;
            }
            
            #compactTagButton:checked {
                background-color: #1DA1F2;
                color: white;
                border-color: #1DA1F2;
            }
        """)
    
    def set_tags(self, tags: List[Tag]):
        """Set the available tags"""
        self.available_tags = tags
        self.selected_tag_ids.clear()
        self.refresh_tags()
        logger.info(f"Set {len(tags)} compact tags")
    
    def refresh_tags(self):
        """Refresh the tag buttons in 2 rows"""
        # Clear existing buttons
        self.clear_tag_buttons()
        
        if not self.available_tags:
            return
        
        # Calculate tags per row - aim for roughly equal distribution
        total_tags = len(self.available_tags)
        tags_per_row = (total_tags + 1) // 2  # Round up division
        
        # Create buttons and distribute across two rows
        for i, tag in enumerate(self.available_tags):
            try:
                tag_button = TagButton(tag)
                tag_button.tag_toggled.connect(self.on_tag_toggled)
                self.tag_buttons.append(tag_button)
                
                # Add to row 1 or row 2
                if i < tags_per_row:
                    self.row1_layout.addWidget(tag_button)
                else:
                    self.row2_layout.addWidget(tag_button)
                    
            except Exception as e:
                logger.error(f"Error creating compact tag button: {e}")
                continue
        
        # Add stretch to both rows to keep tags left-aligned
        self.row1_layout.addStretch()
        self.row2_layout.addStretch()
        
        self.update_selected_display()
    
    def clear_tag_buttons(self):
        """Clear all tag buttons"""
        for button in self.tag_buttons:
            try:
                button.deleteLater()
            except:
                pass
        self.tag_buttons.clear()
        
        # Clear layouts
        self.clear_layout(self.row1_layout)
        self.clear_layout(self.row2_layout)
    
    def clear_layout(self, layout):
        """Clear a layout safely"""
        try:
            while layout.count():
                child = layout.takeAt(0)
                if child and child.widget():
                    child.widget().deleteLater()
        except Exception as e:
            logger.warning(f"Error clearing layout: {e}")
    
    def on_tag_toggled(self, tag: Tag, is_selected: bool):
        """Handle tag selection change"""
        try:
            tag_id = str(tag.id)
            if is_selected:
                self.selected_tag_ids.add(tag_id)
            else:
                self.selected_tag_ids.discard(tag_id)
            
            self.update_selected_display()
            
            # Emit selected tag IDs
            self.tags_changed.emit(list(self.selected_tag_ids))
            
        except Exception as e:
            logger.error(f"Error handling tag toggle: {e}")
    
    def update_selected_display(self):
        """Update the selected tags display"""
        try:
            count = len(self.selected_tag_ids)
            if count == 0:
                self.selected_label.setText("None selected")
            elif count == 1:
                self.selected_label.setText("1 tag selected")
            else:
                self.selected_label.setText(f"{count} tags selected")
        except Exception as e:
            logger.error(f"Error updating selected display: {e}")
    
    def get_selected_tag_ids(self) -> List[str]:
        """Get the currently selected tag IDs"""
        try:
            return list(self.selected_tag_ids)
        except Exception as e:
            logger.error(f"Error getting selected tag IDs: {e}")
            return []
    
    def clear_selection(self):
        """Clear all selected tags"""
        try:
            self.selected_tag_ids.clear()
            for button in self.tag_buttons:
                button.setChecked(False)
            self.update_selected_display()
            self.tags_changed.emit([])
        except Exception as e:
            logger.error(f"Error clearing selection: {e}") 