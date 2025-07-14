#!/usr/bin/env python3
"""
Check if database view was updated and diagnose media display issues
"""

import os
import sys
import asyncio
from datetime import datetime

# Add the project root to the path
sys.path.append('.')

from data.supabase_client import SupabaseClient
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

def check_database_view():
    """Check if the database view has the correct structure"""
    print("🔍 Checking Database View Structure...")
    
    config = load_config()
    if not config:
        return False
    
    try:
        client = create_client(config['SUPABASE_URL'], config['SUPABASE_ANON_KEY'])
        
        # Get the view definition
        print("   Checking note_view columns...")
        response = client.table("note_view").select("*").limit(1).execute()
        
        if response.data:
            sample_note = response.data[0]
            columns = list(sample_note.keys())
            print(f"   Available columns: {columns}")
            
            # Check for media_files column
            if 'media_files' in columns:
                print("   ✅ media_files column exists")
                media_files = sample_note.get('media_files')
                print(f"   media_files type: {type(media_files)}")
                print(f"   media_files value: {media_files}")
            else:
                print("   ❌ media_files column missing")
                
            # Check for old media_urls column
            if 'media_urls' in columns:
                print("   ⚠️  media_urls column still exists (old format)")
                media_urls = sample_note.get('media_urls')
                print(f"   media_urls value: {media_urls}")
            else:
                print("   ✅ media_urls column removed")
                
            return 'media_files' in columns
        else:
            print("   ❌ No data in note_view")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking view: {e}")
        return False

async def check_recent_notes_with_media():
    """Check if recent notes have media files attached"""
    print("\n🔍 Checking Recent Notes with Media...")
    
    config = load_config()
    if not config:
        return
    
    # Set up environment variables
    os.environ["SUPABASE_URL"] = config.get("SUPABASE_URL", "")
    os.environ["SUPABASE_ANON_KEY"] = config.get("SUPABASE_ANON_KEY", "")
    os.environ["SUPABASE_SERVICE_ROLE"] = config.get("SUPABASE_SERVICE_ROLE", "")
    
    supabase_client = SupabaseClient()
    
    if not supabase_client.connect():
        print("   ❌ Failed to connect to database")
        return
    
    try:
        # Get recent notes
        notes = await supabase_client.get_notes(limit=5)
        
        print(f"   Found {len(notes)} recent notes")
        
        for i, note in enumerate(notes, 1):
            print(f"\n   Note {i}: {note.body[:50]}...")
            print(f"   Created by: {note.created_by}")
            print(f"   Media files: {len(note.media_files)}")
            
            if note.media_files:
                for j, media in enumerate(note.media_files, 1):
                    print(f"     Media {j}: {media.filename} ({media.media_type})")
                    print(f"     URL: {media.file_url}")
            else:
                print("     No media files")
                
    except Exception as e:
        print(f"   ❌ Error checking notes: {e}")

def check_media_table():
    """Check if media table has recent entries"""
    print("\n🔍 Checking Media Table...")
    
    config = load_config()
    if not config:
        return
    
    try:
        client = create_client(config['SUPABASE_URL'], config['SUPABASE_ANON_KEY'])
        
        # Get recent media entries
        response = client.table("media").select("*").order("created_at", desc=True).limit(5).execute()
        
        if response.data:
            print(f"   Found {len(response.data)} recent media entries")
            
            for i, media in enumerate(response.data, 1):
                print(f"\n   Media {i}:")
                print(f"     ID: {media['id']}")
                print(f"     Note ID: {media['note_id']}")
                print(f"     Filename: {media['filename']}")
                print(f"     Type: {media['media_type']}")
                print(f"     URL: {media['file_url']}")
                print(f"     Created: {media['created_at']}")
        else:
            print("   ❌ No media entries found")
            
    except Exception as e:
        print(f"   ❌ Error checking media table: {e}")

def test_view_update_sql():
    """Test if we can update the view"""
    print("\n🔍 Testing View Update...")
    
    config = load_config()
    if not config:
        return
    
    try:
        client = create_client(config['SUPABASE_URL'], config['SUPABASE_SERVICE_ROLE'])
        
        # Try to update the view
        update_sql = """
        CREATE OR REPLACE VIEW public.note_view AS
        SELECT
            n.id,
            n.body,
            n.shared,
            n.created_by,
            n.created_at,
            n.updated_at,
            n.category,
            d.name AS driver_name,
            s.date AS session_date,
            s.session AS session_type,
            t.name AS track_name,
            t.type AS track_type,
            sr.name AS series_name,
            COALESCE(
                (SELECT array_agg(tag.label)
                 FROM note_tag
                 JOIN tag ON note_tag.tag_id = tag.id
                 WHERE note_tag.note_id = n.id),
                '{}'::text[]
            ) AS tags,
            COALESCE(
                (SELECT jsonb_agg(
                    jsonb_build_object(
                        'file_url', m.file_url,
                        'media_type', m.media_type,
                        'filename', m.filename
                    )
                )
                 FROM media m
                 WHERE m.note_id = n.id),
                '[]'::jsonb
            ) AS media_files
        FROM
            note n
        LEFT JOIN driver d ON n.driver_id = d.id
        LEFT JOIN session s ON n.session_id = s.id
        LEFT JOIN track t ON s.track_id = t.id
        LEFT JOIN series sr ON s.series_id = sr.id;
        """
        
        print("   Attempting to update view...")
        response = client.rpc('exec_sql', {'sql': update_sql})
        print(f"   Update result: {response}")
        print("   ✅ View update attempted")
        
    except Exception as e:
        print(f"   ❌ Error updating view: {e}")
        print("   You may need to run the SQL manually in Supabase dashboard")

async def main():
    """Run all diagnostic checks"""
    print("🚀 DATABASE VIEW AND MEDIA DIAGNOSTIC")
    print("=" * 50)
    
    # Check 1: Database view structure
    view_ok = check_database_view()
    
    # Check 2: Media table entries
    check_media_table()
    
    # Check 3: Recent notes with media
    await check_recent_notes_with_media()
    
    # Check 4: Try to update view
    if not view_ok:
        test_view_update_sql()
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNOSIS COMPLETE")
    print("=" * 50)
    
    if view_ok:
        print("✅ Database view has correct structure")
        print("🔧 If media still not showing, the issue may be in the UI rendering")
    else:
        print("❌ Database view needs to be updated")
        print("🔧 Run the SQL update in Supabase dashboard manually")

if __name__ == "__main__":
    asyncio.run(main()) 