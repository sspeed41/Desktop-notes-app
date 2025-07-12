"""
Utility functions for the WiseDesktopNoteApp.
"""
import os
from app.data.models import MediaType

def get_media_type_from_path(file_path: str) -> MediaType:
    """Determine media type from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
        return MediaType.VIDEO
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        return MediaType.IMAGE
    elif ext in ['.csv', '.xlsx', '.xls']:
        return MediaType.DATA
    elif ext in ['.pdf', '.txt', '.doc', '.docx']:
        return MediaType.DOCUMENT
    else:
        return MediaType.OTHER 