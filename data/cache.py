"""
Simple stub cache for Streamlit Cloud deployment
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID

from data.models import NoteView, NoteCreate, Track, Series, Driver, Session, Tag

logger = logging.getLogger(__name__)

class OfflineCache:
    """Stub cache for Streamlit Cloud - no actual caching"""
    
    def __init__(self):
        pass
    
    def cache_notes(self, notes: List[NoteView]) -> None:
        pass
    
    def get_cached_notes(self, limit: int = 100, offset: int = 0) -> List[NoteView]:
        return []
    
    def search_cached_notes(self, search_text: str, limit: int = 100) -> List[NoteView]:
        return []
    
    def cache_tracks(self, tracks: List[Track]) -> None:
        pass
    
    def get_cached_tracks(self) -> List[Track]:
        return []
    
    def cache_series(self, series: List[Series]) -> None:
        pass
    
    def get_cached_series(self) -> List[Series]:
        return []
    
    def cache_drivers(self, drivers: List[Driver]) -> None:
        pass
    
    def get_cached_drivers(self) -> List[Driver]:
        return []
    
    def cache_tags(self, tags: List[Tag]) -> None:
        pass
    
    def get_cached_tags(self) -> List[Tag]:
        return []
    
    def cache_sessions(self, sessions: List[Session]) -> None:
        pass
    
    def get_cached_sessions(self) -> List[Session]:
        return []
    
    def queue_note_for_sync(self, note_create: NoteCreate) -> None:
        pass
    
    def get_pending_notes(self) -> List[Dict[str, Any]]:
        return []
    
    def mark_note_synced(self, doc_id: int) -> None:
        pass
    
    def clear_synced_notes(self) -> None:
        pass
    
    def get_last_sync(self) -> Optional[datetime]:
        return None
    
    def is_cache_stale(self, max_age_hours: int = 24) -> bool:
        return True
    
    def clear_all_cache(self) -> None:
        pass 