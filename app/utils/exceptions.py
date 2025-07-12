"""
Custom exception hierarchy for WiseDesktopNoteApp
Provides specific exception types for better error handling
"""

from typing import Optional, Dict, Any


class WiseDesktopNoteAppError(Exception):
    """Base exception for all application errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


# Database-related exceptions
class DatabaseError(WiseDesktopNoteAppError):
    """Base exception for database-related errors"""
    pass


class ConnectionError(DatabaseError):
    """Database connection failed"""
    pass


class QueryError(DatabaseError):
    """Database query failed"""
    pass


class MigrationError(DatabaseError):
    """Database migration failed"""
    pass


# Data validation exceptions
class ValidationError(WiseDesktopNoteAppError):
    """Data validation failed"""
    pass


class ModelValidationError(ValidationError):
    """Pydantic model validation failed"""
    pass


# Cache-related exceptions
class CacheError(WiseDesktopNoteAppError):
    """Base exception for cache-related errors"""
    pass


class CacheCorruptedError(CacheError):
    """Cache data is corrupted"""
    pass


class CacheFullError(CacheError):
    """Cache storage is full"""
    pass


# UI-related exceptions
class UIError(WiseDesktopNoteAppError):
    """Base exception for UI-related errors"""
    pass


class ComponentError(UIError):
    """UI component error"""
    pass


class ThemeError(UIError):
    """Theme loading error"""
    pass


# Media-related exceptions
class MediaError(WiseDesktopNoteAppError):
    """Base exception for media-related errors"""
    pass


class MediaUploadError(MediaError):
    """Media upload failed"""
    pass


class MediaFormatError(MediaError):
    """Unsupported media format"""
    pass


class MediaSizeError(MediaError):
    """Media file too large"""
    pass


# Configuration exceptions
class ConfigurationError(WiseDesktopNoteAppError):
    """Configuration loading failed"""
    pass


class MissingConfigError(ConfigurationError):
    """Required configuration is missing"""
    pass


class InvalidConfigError(ConfigurationError):
    """Configuration format is invalid"""
    pass


# Sync-related exceptions
class SyncError(WiseDesktopNoteAppError):
    """Base exception for synchronization errors"""
    pass


class OfflineModeError(SyncError):
    """Operation not available in offline mode"""
    pass


class SyncConflictError(SyncError):
    """Data synchronization conflict"""
    pass


# Authentication exceptions (for future use)
class AuthError(WiseDesktopNoteAppError):
    """Base exception for authentication errors"""
    pass


class AuthenticationFailedError(AuthError):
    """User authentication failed"""
    pass


class AuthorizationError(AuthError):
    """User not authorized for operation"""
    pass


# Helper functions for error handling
def handle_database_error(func):
    """Decorator to handle database errors consistently"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "connection" in str(e).lower():
                raise ConnectionError(f"Database connection failed: {e}")
            elif "query" in str(e).lower():
                raise QueryError(f"Database query failed: {e}")
            else:
                raise DatabaseError(f"Database operation failed: {e}")
    return wrapper


def handle_validation_error(func):
    """Decorator to handle validation errors consistently"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if hasattr(e, 'errors'):  # Pydantic validation error
                raise ModelValidationError(f"Model validation failed: {e}")
            else:
                raise ValidationError(f"Validation failed: {e}")
    return wrapper 