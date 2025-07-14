"""
Cloud storage service for uploading media files to Supabase
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import mimetypes

from data.supabase_client import SupabaseClient

# Define exceptions inline since we removed app.utils.exceptions
class MediaUploadError(Exception):
    pass

class MediaSizeError(Exception):
    pass

logger = logging.getLogger(__name__)

class CloudStorageService:
    """Service for handling cloud storage uploads to Supabase"""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.client = supabase_client
        self.bucket_name = "racing-notes-media"
        self.max_file_size_mb = 100  # 100MB max file size
        
    async def upload_file(self, file_path: str, note_id: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Supabase storage and return the public URL
        
        Args:
            file_path: Local path to the file to upload
            note_id: Optional note ID to organize files
            
        Returns:
            Public URL of the uploaded file or None if failed
        """
        try:
            if not os.path.exists(file_path):
                raise MediaUploadError(f"File not found: {file_path}")
            
            if not self.client.is_connected or not self.client.client:
                raise MediaUploadError("Not connected to Supabase")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size_mb * 1024 * 1024:
                raise MediaSizeError(f"File too large: {file_size / (1024*1024):.1f}MB (max: {self.max_file_size_mb}MB)")
            
            # Generate unique filename with timestamp
            original_name = os.path.basename(file_path)
            name, ext = os.path.splitext(original_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create organized folder structure
            year = datetime.now().strftime("%Y")
            month = datetime.now().strftime("%m")
            
            # Determine file type for folder organization
            file_ext = ext.lower()
            if file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                folder = f"videos/{year}/{month}"
            elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                folder = f"images/{year}/{month}"
            elif file_ext in ['.pdf', '.txt', '.doc', '.docx']:
                folder = f"documents/{year}/{month}"
            else:
                folder = f"files/{year}/{month}"
            
            # Create unique filename
            unique_name = f"{name}_{timestamp}{ext}"
            storage_path = f"{folder}/{unique_name}"
            
            logger.info(f"Uploading {original_name} to {storage_path}")
            
            # Upload to Supabase storage
            logger.info(f"Reading file: {original_name}")
            with open(file_path, 'rb') as file:
                file_data = file.read()
                logger.info(f"File read complete, uploading {len(file_data)} bytes")
                
                response = self.client.client.storage.from_(self.bucket_name).upload(
                    path=storage_path,
                    file=file_data
                )
            
            # Check if upload was successful - Supabase returns different response structures
            if hasattr(response, 'error') and getattr(response, 'error', None):
                error_msg = getattr(response, 'error', 'Unknown error')
                logger.error(f"Upload failed: {error_msg}")
                raise MediaUploadError(f"Upload failed: {error_msg}")
            
            # Get public URL
            # Supabase returns a StorageResponse with the URL stored in .data or a simple dict.
            public_url_resp = self.client.client.storage.from_(self.bucket_name).get_public_url(storage_path)

            # Normalise to raw string so callers don’t have to worry about response format
            if isinstance(public_url_resp, dict):
                public_url = public_url_resp.get("publicURL") or public_url_resp.get("publicUrl")
            elif hasattr(public_url_resp, "data"):
                # Expected format (supabase-py <2.0): StorageResponse with .data dict
                data_field: Any = getattr(public_url_resp, "data")  # type: ignore[attr-defined]
                if isinstance(data_field, dict):
                    public_url = data_field.get("publicURL") or data_field.get("publicUrl")
            else:
                # Fallback to string representation (works on older client versions)
                public_url = str(public_url_resp)

            if not public_url:
                raise MediaUploadError("Failed to obtain public URL for uploaded file")

            logger.info(f"Successfully uploaded {original_name} to cloud storage")
            return public_url
                
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            if isinstance(e, (MediaUploadError, MediaSizeError)):
                raise
            else:
                raise MediaUploadError(f"Upload failed: {str(e)}")
    
    async def upload_multiple_files(self, file_infos: list, note_id: Optional[str] = None) -> list:
        """
        Upload multiple files and return their cloud URLs
        
        Args:
            file_infos: List of file info dicts from drag-and-drop
            note_id: Optional note ID to organize files
            
        Returns:
            List of dicts with file info and cloud URLs
        """
        results = []
        
        for file_info in file_infos:
            try:
                file_path = file_info['path']
                cloud_url = await self.upload_file(file_path, note_id)
                
                if cloud_url:
                    # Update file info with cloud URL
                    updated_info = file_info.copy()
                    updated_info['cloud_url'] = cloud_url
                    updated_info['storage_type'] = 'cloud'
                    results.append(updated_info)
                    logger.info(f"Successfully uploaded {file_info['name']} to cloud")
                else:
                    # Keep local path as fallback
                    fallback_info = file_info.copy()
                    fallback_info['cloud_url'] = f"local://{file_path}"
                    fallback_info['storage_type'] = 'local'
                    results.append(fallback_info)
                    logger.warning(f"Failed to upload {file_info['name']}, keeping local reference")
                    
            except Exception as e:
                logger.error(f"Error uploading {file_info.get('name', 'unknown')}: {e}")
                # Keep local path as fallback
                fallback_info = file_info.copy()
                fallback_info['cloud_url'] = f"local://{file_info['path']}"
                fallback_info['storage_type'] = 'local'
                results.append(fallback_info)
        
        return results
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information for upload"""
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Determine file type
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                file_type = "📷 Image"
                media_type = "image"
            elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']:
                file_type = "🎥 Video"
                media_type = "video"
            elif file_ext in ['.pdf']:
                file_type = "📄 PDF"
                media_type = "document"
            elif file_ext in ['.csv', '.xlsx', '.xls']:
                file_type = "📊 Data"
                media_type = "data"
            elif file_ext in ['.txt', '.doc', '.docx']:
                file_type = "📝 Document"
                media_type = "document"
            else:
                file_type = "📎 File"
                media_type = "other"
            
            return {
                'path': file_path,
                'name': file_name,
                'size': file_size,
                'type': file_type,
                'ext': file_ext,
                'media_type': media_type,
                'size_mb': file_size / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return None
    
    def is_supported_file(self, file_path: str) -> bool:
        """Check if file type is supported"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            supported_extensions = [
                # Video
                '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
                # Image
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
                # Document
                '.pdf', '.txt', '.doc', '.docx',
                # Data
                '.csv', '.xlsx', '.xls'
            ]
            return file_ext in supported_extensions
        except Exception:
            return False 