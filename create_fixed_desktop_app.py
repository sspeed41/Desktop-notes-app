#!/usr/bin/env python3
"""
Create a reliable macOS .app bundle for Racing Notes Desktop Launcher
This version properly handles paths with spaces and special characters
"""

import os
import sys
from pathlib import Path
import shutil

def create_app_bundle():
    """Create a proper macOS .app bundle"""
    
    # Get current directory
    current_dir = Path.cwd()
    desktop_dir = Path.home() / "Desktop"
    
    # App bundle name
    app_name = "Racing Notes Launcher"
    app_bundle = desktop_dir / f"{app_name}.app"
    
    # Remove existing app if it exists
    if app_bundle.exists():
        shutil.rmtree(app_bundle)
    
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
    
    # Create a simple launcher script that properly handles paths
    launcher_script = f"""#!/bin/bash

# Racing Notes Desktop App Launcher
# Professional launcher for Racing Notes v2.6.0

# Navigate to the correct directory
cd "{current_dir}"

# Check if we're in the right place
if [ ! -f "run_app.py" ]; then
    echo "❌ Error: Racing Notes app not found!"
    echo "📁 Expected location: {current_dir}"
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

# Clear and start the app
clear
echo "🏁 Racing Notes Desktop App"
echo "=================================="
echo "🚀 Launching Racing Notes v2.6.0..."
echo "📍 Location: {current_dir}"
echo "⏰ Started at: $(date)"
echo "=================================="
echo

# Launch the app
python3 run_app.py

# Keep terminal open after app closes
echo
echo "=================================="
echo "🏁 Racing Notes has been closed"
echo "⏰ Ended at: $(date)"
echo "=================================="
echo
echo "Press any key to close this window..."
read -n 1
"""
    
    launcher_path = macos_dir / "launcher"
    launcher_path.write_text(launcher_script)
    
    # Make the launcher executable
    os.chmod(launcher_path, 0o755)
    
    print(f"✅ Created {app_name}.app on your Desktop!")
    print(f"📱 You can now double-click the app to launch Racing Notes")
    print(f"📁 App location: {app_bundle}")
    print(f"🎯 The app will launch Racing Notes from: {current_dir}")
    
    return app_bundle

def main():
    """Main function"""
    print("🚀 Creating Fixed macOS App Bundle for Racing Notes...")
    print("=" * 60)
    
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