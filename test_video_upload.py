#!/usr/bin/env python3
"""
Test script to verify video upload functionality
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append('.')

from app.data.supabase_client import SupabaseClient
from app.data.models import NoteCreate, NoteView, NoteCategory
from dotenv import load_dotenv
import tempfile

async def test_video_upload():
    """Test video upload functionality"""
    load_dotenv()
    
    client = SupabaseClient()
    if not client.connect():
        print("❌ Could not connect to database")
        return False
    
    print("✅ Connected to database")
    
    # Create a dummy video file for testing
    test_video_path = None
    try:
        # Create a temporary file with video extension
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(b"dummy video content for testing")
            test_video_path = temp_file.name
        
        print(f"📹 Created test video file: {test_video_path}")
        
        # Test media attachment
        media_files = [{
            'path': test_video_path,
            'name': 'test_video.mp4',
            'size': os.path.getsize(test_video_path),
            'ext': '.mp4',
            'type': '🎥 Video'
        }]
        
        # Create a test note with video
        note_create = NoteCreate(
            body="Test note with video attachment",
            category=NoteCategory.GENERAL
        )
        
        # Create mock context info
        context_info = {
            'track': type('Track', (), {'name': 'Test Track', 'id': None})(),
            'series': 'Test Series',
            'session_type': 'Practice'
        }
        
        print("🚀 Creating note with video attachment...")
        note = await client.create_note_with_context(note_create, context_info, media_files)
        
        if note:
            print(f"✅ Successfully created note with ID: {note.id}")
            
            # Verify the note can be retrieved with media
            notes = await client.get_notes(limit=5)
            notes_with_media = [n for n in notes if hasattr(n, 'media_files') and n.media_files]
            
            if notes_with_media:
                print(f"✅ Found {len(notes_with_media)} notes with media")
                
                # Check if our video is there
                for note in notes_with_media:
                    for media in note.media_files:
                        if media.filename == 'test_video.mp4':
                            print(f"✅ Video file found: {media.filename} ({media.media_type})")
                            return True
            else:
                print("❌ No notes with media found after creation")
                return False
        else:
            print("❌ Failed to create note")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test file
        if test_video_path and os.path.exists(test_video_path):
            os.unlink(test_video_path)
            print(f"🧹 Cleaned up test file: {test_video_path}")

async def test_current_notes():
    """Test current notes retrieval"""
    load_dotenv()
    
    client = SupabaseClient()
    if not client.connect():
        print("❌ Could not connect to database")
        return
    
    print("📋 Testing current notes retrieval...")
    notes = await client.get_notes(limit=10)
    print(f"Found {len(notes)} notes")
    
    notes_with_media = [n for n in notes if hasattr(n, 'media_files') and n.media_files]
    print(f"Notes with media: {len(notes_with_media)}")
    
    if notes_with_media:
        print("\n📹 Notes with media:")
        for i, note in enumerate(notes_with_media, 1):
            print(f"  {i}. {note.body[:50]}...")
            for j, media in enumerate(note.media_files, 1):
                print(f"     {j}. {media.filename} ({media.media_type})")

if __name__ == "__main__":
    print("🎬 Testing Video Upload Functionality")
    print("=" * 50)
    
    # Test current notes first
    asyncio.run(test_current_notes())
    print()
    
    # Test video upload
    success = asyncio.run(test_video_upload())
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Video upload test PASSED")
    else:
        print("❌ Video upload test FAILED")
        print("\n💡 Make sure you've updated the database view first!")
        print("   See DATABASE_UPDATE_INSTRUCTIONS.md for details") 