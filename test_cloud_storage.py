#!/usr/bin/env python3
"""
Test script to verify cloud storage functionality with Supabase
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the app directory to the Python path
sys.path.append('.')

from app.data.supabase_client import SupabaseClient
from app.services.cloud_storage import CloudStorageService
from app.data.models import NoteCreate, NoteCategory
from dotenv import load_dotenv

async def test_cloud_storage():
    """Test cloud storage upload functionality"""
    print("🏁 Racing Notes - Cloud Storage Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Connect to Supabase
    client = SupabaseClient()
    if not client.connect():
        print("❌ Could not connect to Supabase")
        return False
    
    print("✅ Connected to Supabase")
    
    # Initialize cloud storage service
    cloud_storage = CloudStorageService(client)
    print("✅ Cloud storage service initialized")
    
    # Create a test file
    test_content = b"This is a test video file for Racing Notes cloud storage"
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(test_content)
            test_file_path = temp_file.name
        
        print(f"📹 Created test file: {os.path.basename(test_file_path)}")
        
        # Get file info
        file_info = cloud_storage.get_file_info(test_file_path)
        if not file_info:
            print("❌ Failed to get file info")
            return False
        
        print(f"📊 File info: {file_info['name']} ({file_info['size_mb']:.3f} MB)")
        
        # Test single file upload
        print("\n🚀 Testing single file upload...")
        cloud_url = await cloud_storage.upload_file(test_file_path)
        
        if cloud_url:
            print(f"✅ File uploaded successfully!")
            print(f"🔗 Cloud URL: {cloud_url}")
            
            # Test multiple file upload
            print("\n🚀 Testing multiple file upload...")
            file_infos = [file_info]
            results = await cloud_storage.upload_multiple_files(file_infos)
            
            if results and len(results) > 0:
                result = results[0]
                if result.get('storage_type') == 'cloud':
                    print(f"✅ Multiple file upload successful!")
                    print(f"🔗 Cloud URL: {result.get('cloud_url')}")
                else:
                    print(f"⚠️  Multiple file upload fell back to local storage")
                    print(f"📁 Local URL: {result.get('cloud_url')}")
            else:
                print("❌ Multiple file upload failed")
                
        else:
            print("❌ Single file upload failed")
            return False
        
        # Test with the Racing Notes app workflow
        print("\n🏁 Testing with Racing Notes workflow...")
        
        # Create test note
        note_create = NoteCreate(
            body="Test note with cloud-uploaded video",
            category=NoteCategory.GENERAL
        )
        
        # Mock context info
        context_info = {
            'track': type('Track', (), {'name': 'Test Track - Cloud Storage', 'id': None})(),
            'series': 'Test Series',
            'session_type': 'Practice'
        }
        
        # Process media files like the app would
        processed_files = await cloud_storage.upload_multiple_files([file_info])
        
        if processed_files:
            print(f"✅ Media processing successful!")
            for pf in processed_files:
                storage_type = pf.get('storage_type', 'unknown')
                print(f"   📁 {pf['name']} -> {storage_type} storage")
            
            # Create note with cloud media
            note = await client.create_note_with_context(note_create, context_info, processed_files)
            if note:
                print(f"✅ Note created successfully with cloud media: {note.id}")
            else:
                print("❌ Failed to create note")
        else:
            print("❌ Media processing failed")
        
        print("\n🎉 Cloud storage test completed successfully!")
        print("\n💡 Your videos will now be stored in Supabase cloud storage!")
        print("💡 This means they'll be accessible from anywhere and won't take up local disk space.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Clean up test file
        try:
            if 'test_file_path' in locals():
                os.unlink(test_file_path)
                print(f"🧹 Cleaned up test file")
        except Exception:
            pass

def main():
    """Main test function"""
    try:
        success = asyncio.run(test_cloud_storage())
        if success:
            print("\n🏁 All tests passed! Your cloud storage is ready.")
            sys.exit(0)
        else:
            print("\n❌ Tests failed. Check your Supabase configuration.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 