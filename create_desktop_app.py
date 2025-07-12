#!/usr/bin/env python3
"""
Create a proper macOS .app bundle for Racing Notes Desktop Launcher
This creates a more professional desktop app that can be put in Applications folder
"""

import os
import sys
from pathlib import Path
import subprocess

def create_app_bundle():
    """Create a proper macOS .app bundle"""
    
    # Get current directory
    current_dir = Path.cwd()
    desktop_dir = Path.home() / "Desktop"
    
    # App bundle name
    app_name = "Racing Notes Launcher"
    app_bundle = desktop_dir / f"{app_name}.app"
    
    # Create the app bundle structure
    contents_dir = app_bundle / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    # Create directories
    macos_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Info.plist
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.racingnotes.launcher</string>
    <key>CFBundleName</key>
    <string>{app_name}</string>
    <key>CFBundleVersion</key>
    <string>2.6.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>"""
    
    (contents_dir / "Info.plist").write_text(info_plist)
    
    # Create the main executable script - Fixed the path issue
    launcher_script = f"""#!/bin/bash

# Racing Notes Desktop App Launcher
# Professional launcher for Racing Notes v2.6.0

# Get the path to the Racing Notes app (properly escaped)
RACING_NOTES_DIR="{str(current_dir)}"

# Open Terminal and run the app with proper path handling
osascript -e 'tell application "Terminal" to do script "cd \\"'"$RACING_NOTES_DIR"'\\" && clear && echo \\"🏁 Racing Notes Desktop App\\" && echo \\"==================================\\" && echo \\"🚀 Launching Racing Notes v2.6.0...\\" && echo \\"📍 Location: '"$RACING_NOTES_DIR"'\\" && echo \\"⏰ Started at: $(date)\\" && echo \\"==================================\\" && echo && python3 run_app.py"'
"""
    
    launcher_path = macos_dir / "launcher"
    launcher_path.write_text(launcher_script)
    
    # Make the launcher executable
    os.chmod(launcher_path, 0o755)
    
    print(f"✅ Created {app_name}.app on your Desktop!")
    print(f"📱 You can now double-click the app to launch Racing Notes")
    print(f"📁 App location: {app_bundle}")
    print(f"🎯 The app will open Terminal and launch Racing Notes from: {current_dir}")
    
    return app_bundle

def main():
    """Main function"""
    print("🚀 Creating macOS App Bundle for Racing Notes...")
    print("=" * 50)
    
    try:
        app_path = create_app_bundle()
        print("\n✅ Success! Desktop app created successfully!")
        print(f"📍 Location: {app_path}")
        print("\n💡 Instructions:")
        print("1. Go to your Desktop")
        print("2. Double-click 'Racing Notes Launcher.app'")
        print("3. The app will open Terminal and launch Racing Notes")
        print("4. You can drag the app to your Applications folder if you want")
        
    except Exception as e:
        print(f"❌ Error creating app bundle: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 