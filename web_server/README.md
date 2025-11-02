# Article Generator Web Server

A modern web interface for the article generation functionality, converted from the command-line `auto_article.py` script. This web server provides an intuitive interface for creating properly formatted markdown articles using AI assistance.

## Features

✨ **Intuitive Web Interface**: Clean, modern web UI instead of command-line prompts
🚀 **Batch Processing**: Create multiple articles at once
🤖 **AI-Powered**: Uses Google Gemini AI for intelligent article processing
📝 **Smart Formatting**: Automatically fixes punctuation, formatting, and structure
🎯 **Metadata Extraction**: Intelligently extracts authors, dates, categories from natural language
🏷️ **Auto-Tagging**: Generates relevant tags automatically
📂 **File Management**: Creates properly named markdown files in the content directory
🌍 **Multi-language Support**: Handle alternate language links
🎨 **Poetry Detection**: Special handling for poems, haikus, and verse

## Quick Start

1. **Navigate to the web server directory:**
   ```bash
   cd web_server
   ```

2. **Run the startup script:**
   ```bash
   ./start_server.sh
   ```

3. **Open your browser and go to:**
   ```
   http://localhost:8000
   ```

That's it! The web interface will guide you through creating articles.

## Manual Setup (Alternative)

If you prefer to set up manually:

1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   python app.py
   ```

## How to Use

### Creating Articles

1. **Fill in metadata (optional):**
   - Title (will be auto-generated if not provided)
   - Author name
   - Date (accepts various formats)
   - Category (science, technology, opinion, news, art, misc)
   - Description
   - Alternate language links

2. **Paste your article content:**
   - Raw text, drafts, or existing articles
   - Include natural language metadata in the text if desired
   - Examples: "The author is John Smith", "Written on Oct 26 2025"

3. **Add more articles (optional):**
   - Click "Add Another Article" to process multiple articles at once

4. **Generate:**
   - Click "Generate Articles" to process with AI
   - Files will be automatically created in the `../content/` directory

### Natural Language Metadata

You can include metadata directly in your article text:

```
The author is Jane Doe and this was written on October 15th, 2025.
Category is technology. This is a review of the new AI system.

[Your article content here...]
```

The AI will extract this information and format it properly.

### Poetry and Creative Writing

The system automatically detects poetry, haikus, and creative writing:

```
This is a haiku about autumn leaves falling gently.

Leaves drift down slowly
Autumn wind carries them far  
Season of changes
```

## API Endpoints

### `POST /api/process-articles`

Process articles and create markdown files.

**Request body:**
```json
{
  "articles": [
    {
      "title": "Optional title",
      "date": "2025-01-15",
      "author": "Author Name", 
      "category": "technology",
      "description": "Optional description",
      "body": "Article content here...",
      "alternates": [
        {"hreflang": "en", "href": "https://example.com/en"}
      ]
    }
  ],
  "model_name": "gemini-2.5-pro"
}
```

**Response:**
```json
{
  "success": true,
  "files_created": [
    "../content/technology-new-ai-breakthrough.md"
  ],
  "raw_response": "AI response text..."
}
```

### `GET /api/models`

Get available AI models.

### `GET /health`

Health check endpoint.

## Configuration

### AI Model Selection

Available models:
- **gemini-2.5-pro** (Recommended) - Best quality, slower
- **gemini-1.5-flash** - Faster processing, good quality  
- **gemini-1.5-pro** - Balanced option

### API Key

The Google Gemini API key is currently hardcoded in the script. For production use, set it as an environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Then modify `app.py` to use:
```python
API_KEY = os.getenv("GEMINI_API_KEY")
```

## File Output

Generated files follow this naming convention:
- Format: `{category}-{slugified-title}.md`
- Example: `technology-new-ai-breakthrough-in-quantum-computing.md`
- Location: `../content/` directory

## Supported Categories

- **science** - Scientific articles and research
- **research** - Research articles, academic insights, and investigative pieces
- **technology** - Tech news, reviews, tutorials
- **opinion** - Editorial content, personal views
- **news** - Current events, announcements
- **art** - Creative writing, poetry, artistic content
- **misc** - General content that doesn't fit other categories

## Troubleshooting

### Server Won't Start
- Check that Python 3 is installed: `python3 --version`
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available: `lsof -i :8000`

### AI Processing Errors
- Verify your internet connection
- Check the Gemini API key is valid
- Try a different model (gemini-1.5-flash for faster processing)

### File Creation Issues
- Ensure the `../content/` directory exists and is writable
- Check file permissions in the content directory

### Browser Issues
- Try clearing browser cache
- Check browser console for JavaScript errors
- Ensure JavaScript is enabled

## Differences from Original Script

### Improvements:
- ✅ Web-based interface instead of command-line prompts
- ✅ Visual feedback with loading indicators
- ✅ Better error handling and user feedback
- ✅ Batch processing with progress indication
- ✅ Form validation and helpful hints
- ✅ Responsive design for mobile devices
- ✅ Real-time form management (add/remove articles)

### Maintained Features:
- ✅ All original AI prompting and processing logic
- ✅ Same file naming and formatting conventions
- ✅ Identical metadata extraction capabilities
- ✅ Full poetry/verse detection system
- ✅ Same category and tagging policies

## Development

To modify or extend the web server:

1. **Backend (FastAPI)**: Edit `app.py`
2. **Frontend (HTML/CSS/JS)**: Edit `templates/index.html`
3. **Dependencies**: Update `requirements.txt`

The server supports hot reloading during development:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## License

This project maintains the same license as the original script.