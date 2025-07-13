"""
Offline cache system for WiseDesktopNoteApp using TinyDB
"""

import os
import json
import re
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
from uuid import UUID
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from app.data.models import NoteView, NoteCreate, Track, Series, Driver, Session, Tag
from app.settings import CACHE_DIR, CACHE_SIZE_LIMIT

logger = logging.getLogger(__name__)

class OfflineCache:
    """TinyDB-based offline cache for racing notes"""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize databases
        self.notes_db = TinyDB(
            self.cache_dir / "notes.json",
            storage=CachingMiddleware(JSONStorage)
        )
        self.metadata_db = TinyDB(
            self.cache_dir / "metadata.json",
            storage=CachingMiddleware(JSONStorage)
        )
        self.outbox_db = TinyDB(
            self.cache_dir / "outbox.json",
            storage=CachingMiddleware(JSONStorage)
        )
        
        # Create tables
        self.notes_table = self.notes_db.table('notes')
        self.tracks_table = self.metadata_db.table('tracks')
        self.series_table = self.metadata_db.table('series')
        self.drivers_table = self.metadata_db.table('drivers')
        self.sessions_table = self.metadata_db.table('sessions')
        self.tags_table = self.metadata_db.table('tags')
        self.outbox_table = self.outbox_db.table('pending_notes')
        
        self.query = Query()
    
    def _serialize_model(self, model) -> Dict[str, Any]:
        """Convert pydantic model to dict for storage"""
        if hasattr(model, 'model_dump'):
            data = model.model_dump()
        else:
            data = dict(model)
            
        # Convert UUID and datetime objects to strings
        for key, value in data.items():
            if isinstance(value, UUID):
                data[key] = str(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, list) and value and isinstance(value[0], (UUID, datetime)):
                data[key] = [str(v) if isinstance(v, UUID) else v.isoformat() if isinstance(v, datetime) else v for v in value]
        
        return data
    
    def _deserialize_note(self, data: Dict[str, Any]) -> NoteView:
        """Convert stored dict back to NoteView model"""
        # Convert string UUIDs and datetimes back to proper types
        if 'id' in data and isinstance(data['id'], str):
            data['id'] = UUID(data['id'])
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if 'session_date' in data and isinstance(data['session_date'], str):
            from datetime import date
            data['session_date'] = date.fromisoformat(data['session_date'])
            
        return NoteView(**data)
    
    # Note cache operations
    def cache_notes(self, notes: List[NoteView]) -> None:
        """Cache a list of notes"""
        try:
            # Clear existing notes if we're refreshing
            self.notes_table.truncate()
            
            # Add new notes
            for note in notes:
                data = self._serialize_model(note)
                self.notes_table.insert(data)
            
            # Trim cache if it exceeds size limit
            self._trim_cache()
            
            # Update last sync timestamp
            self._update_last_sync()
            
        except Exception as e:
            logger.error(f"Error caching notes: {e}")
    
    def get_cached_notes(self, limit: int = 100, offset: int = 0) -> List[NoteView]:
        """Get cached notes"""
        try:
            # Get notes sorted by created_at descending
            all_notes = self.notes_table.all()
            
            # Sort by created_at (stored as ISO string)
            sorted_notes = sorted(
                all_notes, 
                key=lambda x: x.get('created_at', ''), 
                reverse=True
            )
            
            # Apply pagination
            paginated_notes = sorted_notes[offset:offset + limit]
            
            # Convert back to NoteView objects
            return [self._deserialize_note(data) for data in paginated_notes]
            
        except Exception as e:
            logger.error(f"Error retrieving cached notes: {e}")
            return []
    
    def search_cached_notes(self, search_text: str, limit: int = 100) -> List[NoteView]:
        """Search cached notes by text"""
        try:
            results = self.notes_table.search(
                self.query.body.search(search_text, flags=re.IGNORECASE)
            )
            
            # Sort by created_at descending
            sorted_results = sorted(
                results[:limit], 
                key=lambda x: x.get('created_at', ''), 
                reverse=True
            )
            
            return [self._deserialize_note(data) for data in sorted_results]
            
        except Exception as e:
            logger.error(f"Error searching cached notes: {e}")
            return []
    
    def _trim_cache(self) -> None:
        """Trim cache to size limit"""
        try:
            all_notes = self.notes_table.all()
            if len(all_notes) > CACHE_SIZE_LIMIT:
                # Sort by created_at and keep only the most recent
                sorted_notes = sorted(
                    all_notes, 
                    key=lambda x: x.get('created_at', ''), 
                    reverse=True
                )
                
                # Clear and re-insert only the most recent notes
                self.notes_table.truncate()
                for note in sorted_notes[:CACHE_SIZE_LIMIT]:
                    self.notes_table.insert(note)
                    
        except Exception as e:
            logger.error(f"Error trimming cache: {e}")
    
    # Metadata cache operations
    def cache_tracks(self, tracks: List[Track]) -> None:
        """Cache track data"""
        try:
            self.tracks_table.truncate()
            for track in tracks:
                self.tracks_table.insert(self._serialize_model(track))
        except Exception as e:
            logger.error(f"Error caching tracks: {e}")
    
    def get_cached_tracks(self) -> List[Track]:
        """Get cached tracks"""
        try:
            data = self.tracks_table.all()
            return [Track(**item) for item in data]
        except Exception as e:
            logger.error(f"Error retrieving cached tracks: {e}")
            return []
    
    def cache_series(self, series: List[Series]) -> None:
        """Cache series data"""
        try:
            self.series_table.truncate()
            for s in series:
                self.series_table.insert(self._serialize_model(s))
        except Exception as e:
            logger.error(f"Error caching series: {e}")
    
    def get_cached_series(self) -> List[Series]:
        """Get cached series"""
        try:
            data = self.series_table.all()
            return [Series(**item) for item in data]
        except Exception as e:
            logger.error(f"Error retrieving cached series: {e}")
            return []
    
    def cache_drivers(self, drivers: List[Driver]) -> None:
        """Cache driver data"""
        try:
            self.drivers_table.truncate()
            for driver in drivers:
                self.drivers_table.insert(self._serialize_model(driver))
        except Exception as e:
            logger.error(f"Error caching drivers: {e}")
    
    def get_cached_drivers(self) -> List[Driver]:
        """Get cached drivers"""
        try:
            data = self.drivers_table.all()
            return [Driver(**item) for item in data]
        except Exception as e:
            logger.error(f"Error retrieving cached drivers: {e}")
            return []
    
    def cache_tags(self, tags: List[Tag]) -> None:
        """Cache tag data"""
        try:
            self.tags_table.truncate()
            for tag in tags:
                self.tags_table.insert(self._serialize_model(tag))
        except Exception as e:
            logger.error(f"Error caching tags: {e}")
    
    def get_cached_tags(self) -> List[Tag]:
        """Get cached tags"""
        try:
            data = self.tags_table.all()
            return [Tag(**item) for item in data]
        except Exception as e:
            logger.error(f"Error retrieving cached tags: {e}")
            return []
    
    def cache_sessions(self, sessions: List[Session]) -> None:
        """Cache session data"""
        try:
            self.sessions_table.truncate()
            for session in sessions:
                self.sessions_table.insert(self._serialize_model(session))
        except Exception as e:
            logger.error(f"Error caching sessions: {e}")
    
    def get_cached_sessions(self) -> List[Session]:
        """Get cached sessions"""
        try:
            data = self.sessions_table.all()
            return [Session(**item) for item in data]
        except Exception as e:
            logger.error(f"Error retrieving cached sessions: {e}")
            return []
    
    # Offline operations (outbox pattern)
    def queue_note_for_sync(self, note_create: NoteCreate) -> None:
        """Queue a note for sync when online"""
        try:
            data = self._serialize_model(note_create)
            data['queued_at'] = datetime.now().isoformat()
            data['sync_status'] = 'pending'
            self.outbox_table.insert(data)
        except Exception as e:
            logger.error(f"Error queuing note for sync: {e}")
    
    def get_pending_notes(self) -> List[Dict[str, Any]]:
        """Get notes queued for sync"""
        try:
            return self.outbox_table.search(self.query.sync_status == 'pending')
        except Exception as e:
            logger.error(f"Error retrieving pending notes: {e}")
            return []
    
    def mark_note_synced(self, doc_id: int) -> None:
        """Mark a queued note as synced"""
        try:
            self.outbox_table.update(
                {'sync_status': 'synced', 'synced_at': datetime.now().isoformat()},
                doc_ids=[doc_id]
            )
        except Exception as e:
            logger.error(f"Error marking note as synced: {e}")
    
    def clear_synced_notes(self) -> None:
        """Remove synced notes from outbox"""
        try:
            self.outbox_table.remove(self.query.sync_status == 'synced')
        except Exception as e:
            logger.error(f"Error clearing synced notes: {e}")
    
    # Utility methods
    def _update_last_sync(self) -> None:
        """Update last sync timestamp"""
        try:
            sync_table = self.metadata_db.table('sync_info')
            sync_table.upsert(
                {'last_sync': datetime.now().isoformat()},
                self.query.type == 'last_sync'
            )
        except Exception as e:
            logger.error(f"Error updating last sync: {e}")
    
    def get_last_sync(self) -> Optional[datetime]:
        """Get last sync timestamp"""
        try:
            sync_table = self.metadata_db.table('sync_info')
            result = sync_table.search(self.query.type == 'last_sync')
            if result:
                return datetime.fromisoformat(result[0]['last_sync'])
        except Exception as e:
            logger.error(f"Error retrieving last sync: {e}")
        return None
    
    def is_cache_stale(self, max_age_hours: int = 24) -> bool:
        """Check if cache is stale"""
        last_sync = self.get_last_sync()
        if not last_sync:
            return True
        
        age = datetime.now() - last_sync
        return age.total_seconds() > (max_age_hours * 3600)
    
    def clear_all_cache(self) -> None:
        """Clear all cached data"""
        try:
            self.notes_db.drop_tables()
            self.metadata_db.drop_tables()
            self.outbox_db.drop_tables()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


# Global cache instance
offline_cache = OfflineCache() 