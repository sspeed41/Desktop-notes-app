#!/bin/bash
# Create desktop shortcuts for WiseDesktopNoteApp

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="Wise Desktop Note App"

echo "📱 Creating desktop shortcuts for $APP_NAME..."

# Create app bundle structure
BUNDLE_DIR="$HOME/Desktop/$APP_NAME.app"
CONTENTS_DIR="$BUNDLE_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Create directories
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch_app</string>
    <key>CFBundleIdentifier</key>
    <string>com.scottspeed.wisedesktopnoteapp</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleVersion</key>
    <string>2.5.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.5.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
</dict>
</plist>
EOF

# Create launcher script
cat > "$MACOS_DIR/launch_app" << EOF
#!/bin/bash
cd "$APP_DIR"
python3 run_app.py
EOF

# Make launcher executable
chmod +x "$MACOS_DIR/launch_app"

# Create simple icon (text-based)
cat > "$RESOURCES_DIR/icon.txt" << EOF
🏁 Racing Notes App
EOF

echo "✅ Created desktop app: $BUNDLE_DIR"
echo "🎯 You can now:"
echo "   • Double-click the app on your Desktop"
echo "   • Drag it to your Dock for quick access"
echo "   • Move it to Applications folder"

# Also create a simple alias in Applications
APPS_ALIAS="$HOME/Applications/$APP_NAME"
ln -sf "$APP_DIR/launch_app.command" "$APPS_ALIAS"
echo "✅ Created Applications shortcut: $APPS_ALIAS" 