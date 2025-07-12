#!/bin/bash

# Development runner script for Wise Desktop Note App

echo "🚀 Starting Wise Desktop Note App..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please update it with your Supabase credentials."
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Install dependencies if needed
if [ ! -d ".venv" ] && [ ! -f "poetry.lock" ]; then
    echo "📦 Installing dependencies..."
    poetry install
fi

# Run the application
echo "🎯 Launching application..."
poetry run python app/main.py 