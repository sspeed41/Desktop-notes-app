"""
Pydantic models for WiseDesktopNoteApp
"""

from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel
from uuid import UUID


class TrackType(str, Enum):
    SUPERSPEEDWAY = "Superspeedway"
    INTERMEDIATE = "Intermediate"  
    SHORT_TRACK = "Short Track"
    ROAD_COURSE = "Road Course"


class SessionType(str, Enum):
    PRACTICE = "Practice"
    QUALIFYING = "Qualifying"
    RACE = "Race"


class MediaType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    DATA = "data"
    DOCUMENT = "document"
    OTHER = "other"


class NoteCategory(str, Enum):
    GENERAL = "General"
    TRACK_SPECIFIC = "Track Specific"
    SERIES_SPECIFIC = "Series Specific"
    DRIVER_SPECIFIC = "Driver Specific"


class Track(BaseModel):
    id: Optional[UUID] = None
    name: str
    type: TrackType
    created_at: Optional[datetime] = None


class Series(BaseModel):
    id: Optional[UUID] = None
    name: str
    created_at: Optional[datetime] = None


class Driver(BaseModel):
    id: Optional[UUID] = None
    name: str
    series_id: Optional[UUID] = None
    created_at: Optional[datetime] = None


class Session(BaseModel):
    id: Optional[UUID] = None
    date: date
    session: SessionType
    track_id: Optional[UUID] = None
    series_id: Optional[UUID] = None
    created_at: Optional[datetime] = None


class Tag(BaseModel):
    id: Optional[UUID] = None
    label: str
    created_at: Optional[datetime] = None


class Media(BaseModel):
    id: Optional[UUID] = None
    note_id: Optional[UUID] = None
    file_url: str
    media_type: MediaType
    size_mb: Optional[float] = None
    filename: Optional[str] = None
    created_at: Optional[datetime] = None


class MediaInfo(BaseModel):
    file_url: str
    media_type: MediaType
    filename: Optional[str] = None


class Note(BaseModel):
    id: Optional[UUID] = None
    body: str
    shared: bool = True
    driver_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    category: NoteCategory = NoteCategory.GENERAL
    created_by: str = "anonymous"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class NoteView(BaseModel):
    """Enhanced note view with related data"""
    id: UUID
    body: str
    shared: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    category: NoteCategory = NoteCategory.GENERAL
    driver_name: Optional[str] = None
    session_date: Optional[date] = None
    session_type: Optional[SessionType] = None
    track_name: Optional[str] = None
    track_type: Optional[TrackType] = None
    series_name: Optional[str] = None
    tags: List[str] = []
    media_files: List[MediaInfo] = []


class NoteCreate(BaseModel):
    """Model for creating new notes"""
    body: str
    shared: bool = True
    driver_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    category: NoteCategory = NoteCategory.GENERAL
    tag_ids: List[UUID] = []


class NoteFilter(BaseModel):
    """Model for filtering notes"""
    track_ids: List[UUID] = []
    series_ids: List[UUID] = []
    driver_ids: List[UUID] = []
    session_ids: List[UUID] = []
    tag_ids: List[UUID] = []
    session_types: List[SessionType] = []
    track_types: List[TrackType] = []
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    search_text: Optional[str] = None 