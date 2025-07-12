#!/usr/bin/env python3
"""
Test launcher for Racing Notes App
Tests video functionality and launches the app
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import PySide6
        print("  ✅ PySide6 (GUI framework)")
    except ImportError:
        print("  ❌ PySide6 missing - run: pip install PySide6")
        return False
    
    try:
        import supabase
        print("  ✅ Supabase client")
    except ImportError:
        print("  ❌ Supabase missing - run: pip install supabase")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✅ Python-dotenv")
    except ImportError:
        print("  ❌ Python-dotenv missing - run: pip install python-dotenv")
        return False
    
    return True

def check_database_connection():
    """Check database connection and video support"""
    print("\n🔍 Testing database connection and video support...")
    
    try:
        sys.path.append('.')
        from app.data.supabase_client import SupabaseClient
        from dotenv import load_dotenv
        import asyncio
        
        load_dotenv()
        
        async def test_connection():
            client = SupabaseClient()
            if client.connect() and client.client:
                print("  ✅ Database connection successful")
                
                # Test note view structure
                try:
                    response = client.client.table('note_view').select('*').limit(1).execute()
                    if response.data and 'media_files' in response.data[0]:
                        print("  ✅ Video support enabled (media_files field present)")
                        return True
                    else:
                        print("  ❌ Video support not enabled - media_files field missing")
                        return False
                except Exception as e:
                    print(f"  ❌ Error testing video support: {e}")
                    return False
            else:
                print("  ❌ Database connection failed")
                print("  💡 Check your .env file for SUPABASE_URL and SUPABASE_ANON_KEY")
                return False
        
        return asyncio.run(test_connection())
        
    except Exception as e:
        print(f"  ❌ Error testing database: {e}")
        return False

def launch_app():
    """Launch the Racing Notes application"""
    print("\n🚀 Launching Racing Notes App...")
    print("📹 Video functionality is now enabled!")
    print("💡 Try creating a note and dragging a video file to test it")
    print("\n" + "="*60)
    
    try:
        # Import and run the main application
        from app.main import main as app_main
        app_main()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're in the correct directory")
        return False
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False
    
    return True

def main():
    """Main test and launch function"""
    print("🏁 Racing Notes App - Video Test & Launch")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies missing. Install them first:")
        print("   pip install -r requirements.txt")
        input("\nPress Enter to continue anyway...")
    
    # Check database and video support
    db_ok = check_database_connection()
    if not db_ok:
        print("\n⚠️  Database or video support issues detected")
        choice = input("Continue anyway? (y/n): ").lower().strip()
        if choice != 'y':
            print("Exiting...")
            return
    
    # Launch the app
    print("\n🎬 Everything looks good! Launching app...")
    print("🔥 Video files will now show in your notes feed!")
    
    launch_app()

if __name__ == "__main__":
    main() 