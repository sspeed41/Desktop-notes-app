#!/usr/bin/env python3
"""
Comprehensive Media Upload Debugging System
This script will test every component of the media upload pipeline
"""

import os
import sys
import asyncio
from datetime import datetime
from uuid import uuid4
import json

# Add the project root to the path
sys.path.append('.')

from data.supabase_client import SupabaseClient
from data.models import NoteCreate, NoteCategory
from supabase import create_client

def load_config():
    """Load configuration from secrets file"""
    try:
        import toml
        with open('.streamlit/secrets.toml', 'r') as f:
            secrets = toml.load(f)
        return secrets
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return None

async def test_database_connection(supabase_client):
    """Test basic database connectivity"""
    print("\n🔍 Testing Database Connection...")
    try:
        if not supabase_client.connect():
            print("❌ Failed to connect to database")
            return False
        
        # Test basic query
        tracks = await supabase_client.get_tracks()
        print(f"✅ Database connected - found {len(tracks)} tracks")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_storage_upload(config):
    """Test direct storage upload"""
    print("\n🔍 Testing Storage Upload...")
    try:
        client = create_client(config['SUPABASE_URL'], config['SUPABASE_ANON_KEY'])
        
        # Create test file
        test_content = f"Test upload at {datetime.now()}"
        test_filename = f"debug_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_path = f"uploads/{test_filename}"
        
        print(f"   Uploading: {test_path}")
        
        response = client.storage.from_("racing-notes-media").upload(
            path=test_path,
            file=test_content.encode('utf-8'),
            file_options={"content-type": "text/plain"}
        )
        
        print(f"   Response: {response}")
        
        # Check for errors
        error = getattr(response, 'error', None)
        if error:
            print(f"❌ Storage upload failed: {error}")
            return None
        
        # Get public URL
        public_url = client.storage.from_("racing-notes-media").get_public_url(test_path)
        print(f"✅ Storage upload successful: {public_url}")
        
        return {
            'filename': test_filename,
            'file_url': public_url,
            'media_type': 'image',  # Use valid enum value
            'size_mb': 0.001
        }
        
    except Exception as e:
        print(f"❌ Storage upload exception: {e}")
        return None

async def test_media_insertion(supabase_client, media_file):
    """Test direct media insertion into database"""
    print("\n🔍 Testing Media Database Insertion...")
    try:
        # Create a test note first
        note_create = NoteCreate(
            body="Test note for media debugging",
            category=NoteCategory.GENERAL
        )
        
        # Create note without media first
        note_data = note_create.model_dump()
        note_data["created_by"] = "debug_test"
        
        # Extract tag_ids and remove from note_data to prevent insertion error (same as real code)
        tag_ids = note_data.pop("tag_ids", [])
        
        response = supabase_client.client.table("note").insert(note_data).execute()
        
        if not response.data:
            print("❌ Failed to create test note")
            return False
        
        note_id = response.data[0]['id']
        print(f"✅ Created test note: {note_id}")
        
        # Now try to insert media record
        media_data = {
            "note_id": str(note_id),
            "file_url": media_file['file_url'],
            "media_type": media_file['media_type'],
            "size_mb": media_file['size_mb'],
            "filename": media_file['filename']
        }
        
        print(f"   Inserting media: {media_data}")
        
        media_response = supabase_client.client.table("media").insert(media_data).execute()
        
        print(f"   Media response: {media_response}")
        
        if media_response.data:
            print(f"✅ Media insertion successful: {media_response.data[0]['id']}")
            return True
        else:
            error = getattr(media_response, 'error', 'No data returned')
            print(f"❌ Media insertion failed: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Media insertion exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_note_creation(supabase_client, media_file):
    """Test the full note creation with media pipeline"""
    print("\n🔍 Testing Full Note Creation Pipeline...")
    try:
        note_create = NoteCreate(
            body="Full pipeline test note",
            category=NoteCategory.GENERAL
        )
        
        context_info = {
            'track': None,
            'series': None,
            'session_type': None,
            'driver_name': None,
            'tags': []
        }
        
        media_files = [media_file]
        
        print(f"   Creating note with media: {media_files}")
        
        new_note = await supabase_client.create_note_with_context(
            note_create, 
            context_info, 
            media_files=media_files, 
            created_by="debug_test"
        )
        
        if new_note:
            print(f"✅ Full pipeline successful: Note {new_note.id}")
            print(f"   Note has {len(new_note.media_files)} media files")
            return True
        else:
            print("❌ Full pipeline failed: No note returned")
            return False
            
    except Exception as e:
        print(f"❌ Full pipeline exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_schema():
    """Test database schema compatibility"""
    print("\n🔍 Testing Database Schema...")
    try:
        config = load_config()
        if not config:
            print("❌ Cannot load config for schema test")
            return False
            
        client = create_client(config['SUPABASE_URL'], config['SUPABASE_ANON_KEY'])
        
        # Test media table structure
        print("   Checking media table structure...")
        
        # Try to get media table info (this might fail, but we'll catch it)
        try:
            response = client.table("media").select("*").limit(1).execute()
            print("✅ Media table accessible")
        except Exception as e:
            print(f"❌ Media table issue: {e}")
        
        # Test valid enum values
        print("   Testing valid media_type values...")
        valid_types = ['image', 'video', 'csv']
        for media_type in valid_types:
            try:
                # Try a dummy insert to test enum validation
                test_data = {
                    "note_id": str(uuid4()),
                    "file_url": "test://url",
                    "media_type": media_type,
                    "size_mb": 1.0,
                    "filename": "test.txt"
                }
                # This will fail due to foreign key, but should pass enum validation
                response = client.table("media").insert(test_data).execute()
                print(f"   ✅ {media_type} - enum valid")
            except Exception as e:
                if "foreign key" in str(e).lower():
                    print(f"   ✅ {media_type} - enum valid (FK error expected)")
                else:
                    print(f"   ❌ {media_type} - enum invalid: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

async def main():
    """Run all debugging tests"""
    print("🚀 COMPREHENSIVE MEDIA UPLOAD DEBUGGING")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Cannot load configuration")
        return
    
    # Set up environment variables for SupabaseClient (same as streamlit_app.py)
    os.environ["SUPABASE_URL"] = config.get("SUPABASE_URL", "")
    os.environ["SUPABASE_ANON_KEY"] = config.get("SUPABASE_ANON_KEY", "")
    os.environ["SUPABASE_SERVICE_ROLE"] = config.get("SUPABASE_SERVICE_ROLE", "")
    
    print(f"🔍 Config loaded:")
    print(f"   SUPABASE_URL: {'✅ Set' if config.get('SUPABASE_URL') else '❌ Missing'}")
    print(f"   SUPABASE_ANON_KEY: {'✅ Set' if config.get('SUPABASE_ANON_KEY') else '❌ Missing'}")
    print(f"   SUPABASE_SERVICE_ROLE: {'✅ Set' if config.get('SUPABASE_SERVICE_ROLE') else '❌ Missing'}")
    
    # Initialize Supabase client
    supabase_client = SupabaseClient()
    
    # Test 1: Database connection
    db_ok = await test_database_connection(supabase_client)
    
    # Test 2: Database schema
    schema_ok = test_database_schema()
    
    # Test 3: Storage upload
    media_file = test_storage_upload(config)
    storage_ok = media_file is not None
    
    # Test 4: Media insertion (only if storage worked)
    media_insert_ok = False
    if storage_ok and db_ok:
        media_insert_ok = await test_media_insertion(supabase_client, media_file)
    
    # Test 5: Full pipeline (only if previous tests passed)
    full_pipeline_ok = False
    if storage_ok and db_ok and media_insert_ok:
        full_pipeline_ok = await test_full_note_creation(supabase_client, media_file)
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 DEBUGGING SUMMARY")
    print("=" * 60)
    print(f"Database Connection:     {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Database Schema:         {'✅ PASS' if schema_ok else '❌ FAIL'}")
    print(f"Storage Upload:          {'✅ PASS' if storage_ok else '❌ FAIL'}")
    print(f"Media Database Insert:   {'✅ PASS' if media_insert_ok else '❌ FAIL'}")
    print(f"Full Pipeline:           {'✅ PASS' if full_pipeline_ok else '❌ FAIL'}")
    
    if not db_ok:
        print("\n🔧 RECOMMENDATION: Fix database connection first")
    elif not schema_ok:
        print("\n🔧 RECOMMENDATION: Fix database schema issues")
    elif not storage_ok:
        print("\n🔧 RECOMMENDATION: Fix Supabase storage configuration")
    elif not media_insert_ok:
        print("\n🔧 RECOMMENDATION: Fix media table insertion logic")
    elif not full_pipeline_ok:
        print("\n🔧 RECOMMENDATION: Fix note creation pipeline")
    else:
        print("\n🎉 ALL TESTS PASSED - Media upload should work!")

if __name__ == "__main__":
    asyncio.run(main()) 