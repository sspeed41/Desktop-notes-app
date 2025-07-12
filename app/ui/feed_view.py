"""
Feed view component for displaying notes in a Twitter-like timeline
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.ui.components.note_card import NoteCard
from app.data.models import NoteView
from app.settings import COLORS, FONTS


class FeedView(QWidget):
    """Feed view displaying notes in a scrollable timeline"""
    
    note_selected = Signal(NoteView)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes = []
        self.note_cards = []
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup the feed UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for notes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setObjectName("feedScroll")
        
        # Content widget for notes
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(12)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        # Empty state label
        self.empty_label = QLabel("No notes yet.\nClick the ✏️ button to create your first note!")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setFont(QFont(FONTS["secondary"], 14))
        self.empty_label.setObjectName("emptyLabel")
        self.empty_label.setVisible(True)
        self.content_layout.addWidget(self.empty_label)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
    
    def apply_theme(self):
        """Apply X/Twitter-inspired theme"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
            
            #feedScroll {{
                border: none;
                background-color: {COLORS['background']};
            }}
            
            #emptyLabel {{
                color: {COLORS['text_secondary']};
                padding: 60px 20px;
                line-height: 1.6;
            }}
            
            QScrollBar:vertical {{
                background-color: {COLORS['surface']};
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border']};
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['secondary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
    
    def set_notes(self, notes: list[NoteView]):
        """Set the notes to display"""
        self.notes = notes
        self.refresh_feed()
    
    def add_note(self, note: NoteView):
        """Add a new note to the top of the feed"""
        self.notes.insert(0, note)
        self.refresh_feed()
    
    def refresh_feed(self):
        """Refresh the feed display"""
        # Clear existing note cards
        self.clear_notes()
        
        # Hide/show empty state
        if not self.notes:
            self.empty_label.setVisible(True)
            return
        
        self.empty_label.setVisible(False)
        
        # Create note cards
        for note in self.notes:
            card = NoteCard(note)
            card.note_clicked.connect(self.note_selected.emit)
            self.note_cards.append(card)
            self.content_layout.addWidget(card)
        
        # Add stretch at the end
        self.content_layout.addStretch()
    
    def clear_notes(self):
        """Clear all note cards from the feed"""
        # Remove all note cards
        for card in self.note_cards:
            self.content_layout.removeWidget(card)
            card.deleteLater()
        
        self.note_cards.clear()
        
        # Remove stretch if it exists
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item.spacerItem():
                self.content_layout.removeItem(item)
    
    def filter_notes(self, search_text: str = "", filters: dict = None):
        """Filter displayed notes based on search and filters"""
        # TODO: Implement filtering logic
        # For now, just refresh with current notes
        self.refresh_feed()
    
    def scroll_to_top(self):
        """Scroll to the top of the feed"""
        self.scroll_area.verticalScrollBar().setValue(0) 