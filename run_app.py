#!/usr/bin/env python3
"""
Launcher script for WiseDesktopNoteApp
Fixes import path issues and runs the application
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Add the app directory to Python path  
app_dir = project_root / "app"
sys.path.insert(0, str(app_dir))

def main():
    """Launch the WiseDesktopNoteApp"""
    try:
        print("🚀 Starting Wise Desktop Note App...")
        
        # Import and run the main application
        from app.main import main as app_main
        app_main()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 