#!/bin/bash
# Launch script for Racing Notes V2.0

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script's directory to ensure relative paths work
cd "$DIR"

echo "🚀 Launching Racing Notes V2.0..."

# Run the main application using python3
python3 run_app.py

echo "🏁 Racing Notes has been closed."
# Keep the terminal window open for a few seconds to see any messages
sleep 3 