"""
Supabase client wrapper for WiseDesktopNoteApp
"""

import os
from typing import List, Optional, Dict, Any
from uuid import UUID
from supabase import create_client, Client
from app.data.models import *
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Thin wrapper around supabase-py for racing notes app"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "")
        self.key = os.getenv("SUPABASE_ANON_KEY", "")
        self.client: Optional[Client] = None
        self._connected = False
        
    def connect(self) -> bool:
        """Connect to Supabase"""
        try:
            if self.url and self.key:
                self.client = create_client(self.url, self.key)
                self._connected = True
                return True
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            self._connected = False
        return False
    
    @property
    def is_connected(self) -> bool:
        return self._connected and self.client is not None
    
    # Track operations
    async def get_tracks(self) -> List[Track]:
        """Get all tracks"""
        if not self.is_connected:
            return []
        assert self.client
        try:
            response = self.client.table("track").select("*").order("name").execute()
            return [Track(**track) for track in response.data]
        except Exception as e:
            logger.error(f"Error fetching tracks: {e}")
            return []
    
    # Series operations  
    async def get_series(self) -> List[Series]:
        """Get all series"""
        if not self.is_connected:
            return []
        assert self.client
        try:
            response = self.client.table("series").select("*").order("name").execute()
            return [Series(**series) for series in response.data]
        except Exception as e:
            logger.error(f"Error fetching series: {e}")
            return []
    
    # Driver operations
    async def get_drivers(self) -> List[Driver]:
        """Get all drivers (no series filtering since drivers can run multiple series)"""
        if not self.is_connected:
            return []
        assert self.client
        try:
            response = self.client.table("driver").select("*").order("name").execute()
            return [Driver(**driver) for driver in response.data]
        except Exception as e:
            logger.error(f"Error fetching drivers: {e}")
            return []
    
    async def create_driver(self, driver: Driver) -> Optional[Driver]:
        """Create a new driver (no series association)"""
        if not self.is_connected or not self.client:
            return None
        assert self.client
        try:
            data = driver.model_dump(exclude={"id", "created_at", "series_id"})
            response = self.client.table("driver").insert(data).execute()
            if response.data:
                return Driver(**response.data[0])
        except Exception as e:
            logger.error(f"Error creating driver: {e}")
        return None
    
    # Session operations
    async def get_sessions(self, track_id: Optional[UUID] = None, 
                          series_id: Optional[UUID] = None) -> List[Session]:
        """Get sessions, optionally filtered"""
        if not self.is_connected:
            return []
        assert self.client
        try:
            query = self.client.table("session").select("*")
            if track_id:
                query = query.eq("track_id", str(track_id))
            if series_id:
                query = query.eq("series_id", str(series_id))
            response = query.order("date", desc=True).execute()
            return [Session(**session) for session in response.data]
        except Exception as e:
            logger.error(f"Error fetching sessions: {e}")
            return []
    
    async def create_session(self, session: Session) -> Optional[Session]:
        """Create a new session"""
        if not self.is_connected:
            return None
        assert self.client
        try:
            data = session.model_dump(exclude={"id", "created_at"})
            data["date"] = str(session.date)
            if session.track_id:
                data["track_id"] = str(session.track_id)
            if session.series_id:
                data["series_id"] = str(session.series_id)
            response = self.client.table("session").insert(data).execute()
            if response.data:
                return Session(**response.data[0])
        except Exception as e:
            logger.error(f"Error creating session: {e}")
        return None
    
    # Tag operations
    async def get_tags(self) -> List[Tag]:
        """Get all tags"""
        if not self.is_connected:
            return []
        assert self.client
        try:
            response = self.client.table("tag").select("*").order("label").execute()
            return [Tag(**tag) for tag in response.data]
        except Exception as e:
            logger.error(f"Error fetching tags: {e}")
            return []
    
    async def create_tag(self, label: str) -> Optional[Tag]:
        """Create a new tag if it doesn't exist"""
        if not self.is_connected or not self.client:
            return None
        assert self.client
        try:
            # Check if tag already exists
            response = self.client.table("tag").select("id, label").eq("label", label).execute()
            if response.data:
                return Tag(**response.data[0])
            
            # Create new tag
            response = self.client.table("tag").insert({"label": label}).execute()
            if response.data:
                return Tag(**response.data[0])
        except Exception as e:
            logger.error(f"Error creating tag: {e}")
        return None
    
    # Note operations
    async def get_notes(self, limit: int = 100, offset: int = 0,
                       filters: Optional[NoteFilter] = None) -> List[NoteView]:
        """Get notes with related data"""
        if not self.is_connected:
            return []
        assert self.client
        try:
            # Use the note_view for enhanced data
            query = self.client.table("note_view").select("*")
            
            # Apply filters if provided
            if filters:
                if filters.search_text:
                    query = query.ilike("body", f"%{filters.search_text}%")
                if filters.track_ids:
                    track_names = await self._get_track_names_by_ids(filters.track_ids)
                    if track_names:
                        query = query.in_("track_name", track_names)
                # Add more filter logic as needed
            
            response = query.order("created_at", desc=True).limit(limit).offset(offset).execute()
            
            # Convert notes and properly handle media_files
            notes = []
            for note_data in response.data:
                # Handle media files - check both new format (media_files) and old format (media_urls)
                media_files = []
                
                # Check for new format first (media_files as JSONB)
                if note_data.get('media_files') and note_data['media_files']:
                    try:
                        # media_files is already a list of dicts from JSONB
                        from app.data.models import MediaInfo, MediaType
                        
                        for media_item in note_data['media_files']:
                            if media_item and media_item.get('file_url'):
                                # Map string media_type to enum
                                media_type_str = media_item.get('media_type', 'other').lower()
                                if media_type_str == 'video':
                                    media_type = MediaType.VIDEO
                                elif media_type_str == 'image':
                                    media_type = MediaType.IMAGE
                                elif media_type_str == 'csv':
                                    media_type = MediaType.DATA
                                else:
                                    media_type = MediaType.OTHER
                                
                                media_info = MediaInfo(
                                    file_url=media_item['file_url'],
                                    media_type=media_type,
                                    filename=media_item.get('filename', '')
                                )
                                media_files.append(media_info)
                    except Exception as e:
                        logger.warning(f"Error parsing media_files: {e}")
                
                # Fallback to old format (media_urls as array)
                elif note_data.get('media_urls') and note_data['media_urls'] and note_data['media_urls'][0]:
                    for url in note_data['media_urls']:
                        if url:  # Skip None values
                            # Determine media type from file extension
                            from app.data.models import MediaInfo, MediaType
                            import os
                            
                            filename = os.path.basename(url.replace('local://', ''))
                            file_ext = os.path.splitext(filename)[1].lower()
                            
                            if file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                                media_type = MediaType.VIDEO
                            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                                media_type = MediaType.IMAGE
                            elif file_ext in ['.csv', '.xlsx', '.xls']:
                                media_type = MediaType.DATA
                            elif file_ext in ['.pdf', '.doc', '.docx', '.txt']:
                                media_type = MediaType.DOCUMENT
                            else:
                                media_type = MediaType.OTHER
                            
                            media_info = MediaInfo(
                                file_url=url,
                                media_type=media_type,
                                filename=filename
                            )
                            media_files.append(media_info)
                
                # Set media_files and clean up
                note_data['media_files'] = media_files
                if 'media_urls' in note_data:
                    del note_data['media_urls']
                
                notes.append(NoteView(**note_data))
            
            return notes
        except Exception as e:
            logger.error(f"Error fetching notes: {e}")
            return []
    
    async def create_note_with_context(self, note_create: NoteCreate, context_info: dict, media_files: Optional[List[dict]] = None, created_by: str = "anonymous") -> Optional[NoteView]:
        """Create a new note with session context and media attachments"""
        if not self.is_connected or not self.client:
            return None
        assert self.client
        try:
            # First, find or create the session
            session_id = await self._find_or_create_session(context_info)
            
            if not session_id:
                logger.error("Failed to find or create a session for the note.")
                return None
            
            # Prepare note data
            note_data = note_create.model_dump()
            note_data["session_id"] = str(session_id)
            note_data["created_by"] = created_by
            
            # Convert driver_id to string if it exists
            if note_data.get("driver_id"):
                note_data["driver_id"] = str(note_data["driver_id"])
            
            # Extract tag_ids and remove from note_data to prevent insertion error
            tag_ids = note_data.pop("tag_ids", [])
            
            # Create the note
            response = self.client.table("note").insert(note_data).execute()
            
            if not response.data:
                logger.error("Failed to create note, no data returned.")
                return None
            
            new_note = Note(**response.data[0])
            
            # Associate tags with the new note
            if tag_ids and new_note.id:
                await self._add_note_tags(new_note.id, tag_ids)
            
            # Attach media files if any
            if media_files and new_note.id:
                await self._attach_media_files(new_note.id, media_files)
            
            # Refetch the note view to get all details
            if not new_note.id:
                return None
            note_view_response = self.client.table("note_view").select("*").eq("id", str(new_note.id)).single().execute()
            
            if note_view_response.data:
                return NoteView(**note_view_response.data)
            else:
                # Fallback to a constructed NoteView if the view is not available yet
                # This might happen due to replication lag.
                # We can construct a basic NoteView from the available data.
                return NoteView(
                    id=new_note.id,
                    body=new_note.body,
                    shared=new_note.shared,
                    created_by=new_note.created_by,
                    created_at=new_note.created_at or datetime.now(),
                    updated_at=new_note.updated_at or datetime.now(),
                    category=new_note.category,
                    # The following fields might not be immediately available
                    driver_name=context_info.get("driver_name"),
                    session_date=context_info.get("date"),
                    session_type=context_info.get("session"),
                    track_name=context_info.get("track_name"),
                    series_name=context_info.get("series_name"),
                    tags=[], # Tags might not be populated immediately
                    media_files=[] # Media files might not be populated immediately
                )

        except Exception as e:
            logger.error(f"Error creating note with context: {e}", exc_info=True)
            return None
            
    async def create_note(self, note_create: NoteCreate) -> Optional[Note]:
        """Create a new note (legacy method)"""
        if not self.is_connected:
            return None
        assert self.client
        try:
            # Create the note
            data = note_create.model_dump(exclude={"tag_ids"})
            if note_create.driver_id:
                data["driver_id"] = str(note_create.driver_id)
            if note_create.session_id:
                data["session_id"] = str(note_create.session_id)
            # Category will be included automatically from model_dump()
                
            response = self.client.table("note").insert(data).execute()
            if not response.data:
                return None
                
            note = Note(**response.data[0])
            
            # Add tags if provided
            if note_create.tag_ids and note.id:
                await self._add_note_tags(note.id, note_create.tag_ids)
                
            return note
        except Exception as e:
            logger.error(f"Error creating note: {e}")
        return None

    async def _find_or_create_session(self, context_info: dict) -> Optional[UUID]:
        """Find existing session or create new one"""
        if not self.is_connected or not self.client:
            return None
        try:
            track = context_info['track']
            series_name = context_info['series']
            session_type = context_info['session_type']
            
            # Find track_id and series_id
            track_id = track.id if hasattr(track, 'id') and track.id else await self._find_track_id_by_name(track.name)
            series_id = await self._find_series_id_by_name(series_name)
            
            if not track_id or not series_id:
                logger.warning(f"Could not find track_id or series_id: track={track_id}, series={series_id}")
                return None
            
            # Look for existing session today
            from datetime import date
            today = date.today()
            
            existing_sessions = await self.get_sessions(track_id, series_id)
            for session in existing_sessions:
                if (session.date == today and 
                    session.session.lower() == session_type.lower()):
                    return session.id
            
            # Create new session
            session_data = {
                "date": str(today),
                "session": session_type,
                "track_id": str(track_id),
                "series_id": str(series_id)
            }
            
            response = self.client.table("session").insert(session_data).execute()
            if response.data:
                from uuid import UUID
                return UUID(response.data[0]['id'])
                
        except Exception as e:
            logger.error(f"Error finding/creating session: {e}")
        return None

    async def _find_track_id_by_name(self, track_name: str) -> Optional[UUID]:
        """Find track ID by name, create if not exists"""
        if not self.is_connected or not self.client:
            return None
        try:
            response = self.client.table("track").select("id").eq("name", track_name).execute()
            if response.data:
                from uuid import UUID
                return UUID(response.data[0]['id'])
            
            # Create track if not exists (simplified - you might want to determine type)
            track_data = {
                "name": track_name,
                "type": "Road Course"  # Default type
            }
            response = self.client.table("track").insert(track_data).execute()
            if response.data:
                from uuid import UUID
                return UUID(response.data[0]['id'])
        except Exception as e:
            logger.error(f"Error finding track: {e}")
        return None

    async def _find_series_id_by_name(self, series_name: str) -> Optional[UUID]:
        """Find series ID by name, create if not exists"""
        if not self.is_connected or not self.client:
            return None
        try:
            response = self.client.table("series").select("id").eq("name", series_name).execute()
            if response.data:
                from uuid import UUID
                return UUID(response.data[0]['id'])
            
            # Create series if not exists
            series_data = {"name": series_name}
            response = self.client.table("series").insert(series_data).execute()
            if response.data:
                from uuid import UUID
                return UUID(response.data[0]['id'])
        except Exception as e:
            logger.error(f"Error finding series: {e}")
        return None
    
    async def _add_note_tags(self, note_id: UUID, tag_ids: List[UUID]):
        """Add tags to a note"""
        if not self.is_connected or not self.client:
            return
        try:
            tag_data = [{"note_id": str(note_id), "tag_id": str(tag_id)} 
                       for tag_id in tag_ids]
            self.client.table("note_tag").insert(tag_data).execute()
        except Exception as e:
            logger.error(f"Error adding note tags: {e}")
    
    async def _get_track_names_by_ids(self, track_ids: List[UUID]) -> List[str]:
        """Helper to get track names by IDs"""
        if not self.is_connected or not self.client:
            return []
        try:
            response = self.client.table("track").select("name").in_("id", [str(id) for id in track_ids]).execute()
            return [track["name"] for track in response.data]
        except Exception:
            return []
    
    # Media operations
    async def _attach_media_files(self, note_id: UUID, media_files: List[dict]) -> None:
        """Attach media files to a note"""
        if not self.is_connected or not self.client:
            logger.warning(f"Cannot attach media: not connected to database")
            return
            
        try:
            logger.debug(f"Processing {len(media_files)} media files for note {note_id}")
            for i, file_info in enumerate(media_files):
                file_path = file_info['path']
                file_name = file_info['name']
                file_size = file_info['size']
                file_ext = file_info['ext'].lower()
                
                # Determine media type
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    media_type = "image"
                elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                    media_type = "video"
                elif file_ext in ['.csv', '.xlsx', '.xls']:
                    media_type = "csv"
                else:
                    media_type = "video"  # Default to video for unsupported types
                
                # Use cloud URL if available, otherwise fallback to local path
                if 'cloud_url' in file_info and file_info['cloud_url']:
                    file_url = file_info['cloud_url']
                    storage_type = file_info.get('storage_type', 'cloud')
                else:
                    file_url = f"local://{file_path}"
                    storage_type = 'local'
                
                # Create media record
                media_data = {
                    "note_id": str(note_id),
                    "file_url": file_url,
                    "media_type": media_type,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "filename": file_name
                }
                
                self.client.table("media").insert(media_data).execute()
                logger.debug(f"Attached media: {file_name} ({media_type}) - Storage: {storage_type}")
                
        except Exception as e:
            logger.error(f"Error attaching media files: {e}")

    async def upload_media(self, file_path: str, note_id: UUID) -> Optional[str]:
        """Upload media file to Supabase storage"""
        if not self.is_connected:
            return None
            
        try:
            # This is a placeholder for future Supabase storage implementation
            # For now, we store local file paths which works for single-device use
            bucket_name = "race-media"
            file_name = os.path.basename(file_path)
            
            # In production, you would:
            # 1. Create a storage bucket in Supabase dashboard
            # 2. Upload file: response = self.client.storage.from_(bucket_name).upload(file_name, file_path)
            # 3. Return public URL: return self.client.storage.from_(bucket_name).get_public_url(file_name)
            
            # For now, return local file path
            return f"local://{file_path}"
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
        return None
    
    # Real-time subscriptions
    def subscribe_to_notes(self, callback):
        """Subscribe to real-time note updates"""
        if not self.is_connected:
            return None
            
        try:
            # This is a placeholder for real-time subscriptions
            # Actual implementation would use Supabase real-time features
            pass
        except Exception as e:
            logger.error(f"Error subscribing to notes: {e}")
        return None


# Global instance
supabase_client = SupabaseClient() 