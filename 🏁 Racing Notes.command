#!/bin/bash
# 🏁 Racing Notes App - Easy Desktop Launcher
# Just double-click this file to launch your racing notes app!

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Clear the terminal and show a nice startup message
clear
echo "🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁"
echo "🏁                                                🏁"
echo "🏁           RACING NOTES APP                     🏁"
echo "🏁                                                🏁"
echo "🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁🏁"
echo ""
echo "🚀 Starting your Racing Notes app..."
echo "📍 Location: $SCRIPT_DIR"
echo ""

# Launch the app
python3 run_app.py

# Show completion message
echo ""
echo "🏁 Racing Notes app has closed."
echo "Thanks for using Racing Notes! 🏁"
echo ""
echo "Press any key to close this window..."
read -n 1 -s 