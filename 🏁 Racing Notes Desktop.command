#!/bin/bash
# 🏁 Racing Notes Desktop Launcher
# Double-click this file from your Desktop to launch Racing Notes!

# Set the absolute path to the Racing Notes app
RACING_NOTES_DIR="/Users/scottspeed/Desktop/CursorDesktopNotesV2.0 copy "

# Clear the terminal and show a nice startup message
clear
echo "🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁"
echo "🏁                                                🏁"
echo "🏁     RACING NOTES DESKTOP LAUNCHER v2.5.0      🏁"
echo "🏁                                                🏁"
echo "🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁"
echo ""
echo "🚀 Starting Racing Notes v2.5.0..."
echo "📍 Location: $RACING_NOTES_DIR"
echo "⏰ Started at: $(date)"
echo ""

# Navigate to the Racing Notes directory
cd "$RACING_NOTES_DIR"

# Check if the app exists
if [ ! -f "run_app.py" ]; then
    echo "❌ Error: Racing Notes app not found!"
    echo "💡 Looking for Racing Notes app at: $RACING_NOTES_DIR"
    echo "📁 Expected file: run_app.py"
    echo
    echo "Press any key to exit..."
    read -n 1 -s
    exit 1
fi

# Launch the app
python3 run_app.py

# Show completion message
echo ""
echo "🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁"
echo "🏁 Racing Notes has been closed."
echo "🏁 Thanks for using Racing Notes! 🏁"
echo "⏰ Ended at: $(date)"
echo "🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁"
echo ""
echo "Press any key to close this window..."
read -n 1 -s 