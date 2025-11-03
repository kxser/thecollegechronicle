#!/bin/bash

# Article Generator Web Server Startup Script

echo "🚀 Starting Article Generator Web Server..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
python3 -m pip install -r requirements.txt

# Check if templates directory exists
if [ ! -d "templates" ]; then
    echo "❌ Templates directory not found!"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "🌐 Starting web server on http://localhost:8000"
echo "📝 Open your browser and navigate to the above URL to use the Article Generator"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""

# Start the server
python3 app.py