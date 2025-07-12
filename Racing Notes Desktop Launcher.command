#!/bin/bash

# Racing Notes Desktop Launcher
# Double-click this file to launch Racing Notes from your desktop

# Set the script to exit if any command fails
set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Clear the terminal for a clean start
clear

# Display header
echo "🏁 Racing Notes Desktop Launcher"
echo "=================================================="
echo "🚀 Launching Racing Notes v2.5.0..."
echo "📍 Location: $SCRIPT_DIR"
echo "⏰ Started at: $(date)"
echo "=================================================="
echo

# Navigate to the Racing Notes directory
cd "$SCRIPT_DIR"

# Check if the app exists
if [ ! -f "run_app.py" ]; then
    echo "❌ Error: Racing Notes app not found!"
    echo "💡 Make sure this launcher is in the same folder as your Racing Notes app"
    echo "📁 Looking for: run_app.py"
    echo
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

# Launch the app
echo "🎬 Starting Racing Notes..."
echo "💡 Close this window to stop the app"
echo
python3 run_app.py

# Keep terminal open after app closes
echo
echo "=================================================="
echo "🏁 Racing Notes has been closed"
echo "⏰ Ended at: $(date)"
echo "=================================================="
echo
echo "Press any key to close this window..."
read -n 1 