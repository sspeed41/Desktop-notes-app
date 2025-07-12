"""
Data service layer for WiseDesktopNoteApp
Handles all data operations with consistent patterns
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from PySide6.QtCore import QObject, Signal
from uuid import UUID

from app.data.models import *
from app.data.supabase_client import SupabaseClient
from app.data.cache import OfflineCache
from app.services.cloud_storage import CloudStorageService

logger = logging.getLogger(__name__)

class DataService(QObject):
    """Main data service with simple reliable operations"""
    
    # Public signals
    notes_loaded = Signal(list)
    note_created = Signal(object)
    metadata_loaded = Signal(dict)
    connection_status = Signal(bool)
    error_occurred = Signal(str)
    upload_progress = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.supabase_client = SupabaseClient()
        self.cache = OfflineCache()
        self.cloud_storage: Optional[CloudStorageService] = None
        self.logger = logging.getLogger(__name__)
        self.is_connected = False
        
    def connect_to_database(self):
        """Connect to Supabase database"""
        try:
            is_connected = self.supabase_client.connect()
            self.is_connected = is_connected
            
            if is_connected:
                # Initialize cloud storage service after successful connection
                self.cloud_storage = CloudStorageService(self.supabase_client)
                self.logger.info("Cloud storage service initialized")
                
            self.connection_status.emit(is_connected)
            return is_connected
        except Exception as e:
            self.logger.warning(f"Database connection failed: {e}")
            self.connection_status.emit(False)
            return False
    
    def load_notes(self, limit: int = 100, offset: int = 0, filters: Optional[NoteFilter] = None):
        """Load notes synchronously"""
        try:
            if self.supabase_client.is_connected:
                # Create and run async operation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    notes = loop.run_until_complete(self.supabase_client.get_notes(limit, offset, filters))
                    # Cache the notes
                    self.cache.cache_notes(notes)
                    self.logger.info(f"Loaded {len(notes)} notes from database")
                finally:
                    loop.close()
            else:
                # Use cached notes
                notes = self.cache.get_cached_notes(limit, offset)
                self.logger.info(f"Loaded {len(notes)} notes from cache")
            
            self.notes_loaded.emit(notes)
        except Exception as e:
            self.logger.error(f"Failed to load notes: {e}")
            self.error_occurred.emit(f"Failed to load notes: {e}")
    
    def create_note(self, note_create: NoteCreate, context_info: dict, media_files: Optional[list] = None, created_by: str = "anonymous"):
        """Create note synchronously"""
        try:
            self.logger.info(f"Creating note: {note_create.body[:50]}...")
            
            if self.supabase_client.is_connected:
                # Create and run async operation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # Create note with minimal media processing
                    processed_media_files = []
                    
                    if media_files:
                        self.logger.info(f"Note has {len(media_files)} media files")
                        processed_media_files = media_files
                    
                    # Create note with processed media files
                    note = loop.run_until_complete(
                        self.supabase_client.create_note_with_context(
                            note_create=note_create,
                            context_info=context_info,
                            media_files=processed_media_files,
                            created_by=created_by
                        )
                    )
                    
                    if note:
                        self.logger.info(f"Note created successfully with ID: {note.id}")
                    else:
                        self.logger.warning("Note creation returned None")
                        
                finally:
                    loop.close()
                    
            else:
                # Queue for offline sync
                self.cache.queue_note_for_sync(note_create)
                note = None  # Will be created when back online
                self.logger.info("Note queued for offline sync")
            
            self.note_created.emit(note)
            
        except Exception as e:
            self.logger.error(f"Failed to create note: {e}", exc_info=True)
            self.error_occurred.emit(f"Failed to create note: {e}")
    
    def load_metadata(self):
        """Load all metadata synchronously"""
        try:
            metadata = {}
            
            if self.supabase_client.is_connected:
                # Create and run async operation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    tracks = loop.run_until_complete(self.supabase_client.get_tracks())
                    series = loop.run_until_complete(self.supabase_client.get_series())
                    drivers = loop.run_until_complete(self.supabase_client.get_drivers())
                    tags = loop.run_until_complete(self.supabase_client.get_tags())
                    
                    metadata = {
                        'tracks': tracks,
                        'series': series,
                        'drivers': drivers,
                        'tags': tags
                    }
                    
                    # Cache metadata
                    self.cache.cache_tracks(tracks)
                    self.cache.cache_series(series)
                    self.cache.cache_drivers(drivers)
                    self.cache.cache_tags(tags)
                finally:
                    loop.close()
            else:
                # Use cached metadata
                metadata = {
                    'tracks': self.cache.get_cached_tracks(),
                    'series': self.cache.get_cached_series(),
                    'drivers': self.cache.get_cached_drivers(),
                    'tags': self.cache.get_cached_tags()
                }
            
            self.metadata_loaded.emit(metadata)
        except Exception as e:
            self.logger.error(f"Failed to load metadata: {e}")
            self.error_occurred.emit(f"Failed to load metadata: {e}")
    
    def shutdown(self):
        """Clean shutdown of service"""
        pass 