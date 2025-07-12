#!/bin/bash
# WiseDesktopNoteApp Launcher for macOS
# Double-click this file to launch the app

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the app directory
cd "$SCRIPT_DIR"

# Print startup message
echo "🚀 Starting Wise Desktop Note App..."
echo "📍 Working directory: $SCRIPT_DIR"

# Launch the app
python3 run_app.py

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo "❌ App failed to start. Press any key to close..."
    read -n 1
fi 