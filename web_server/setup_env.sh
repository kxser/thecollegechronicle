#!/bin/bash

# Environment Setup for Article Generator Web Server

echo "🔧 Setting up environment for Article Generator Web Server..."

# Create .env file template if it doesn't exist

# Create content directory if it doesn't exist
CONTENT_DIR="../content"
if [ ! -d "$CONTENT_DIR" ]; then
    echo "📁 Creating content directory..."
    mkdir -p "$CONTENT_DIR"
    echo "✅ Created $CONTENT_DIR directory"
else
    echo "✅ Content directory already exists"
fi

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file if needed (especially the GEMINI_API_KEY)"
echo "2. Run ./start_server.sh to start the web server"
echo "3. Open http://localhost:8000 in your browser"