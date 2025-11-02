# Article Generator Web Server Configuration

# Server Settings
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 8000       # Server port
DEBUG = False     # Set to True for development

# AI Configuration  
DEFAULT_MODEL = "gemini-2.5-pro"
BATCH_SIZE = 2    # Number of articles to process at once

# File Paths
CONTENT_DIR = "../content"  # Where to save generated markdown files
TEMPLATES_DIR = "templates" # Web template directory

# UI Settings
MAX_ARTICLES_PER_BATCH = 10  # Maximum articles allowed in one request
DEFAULT_CATEGORIES = [
    "science",
    "technology", 
    "opinion",
    "news",
    "art", 
    "misc"
]

# Available AI Models
AVAILABLE_MODELS = [
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "description": "Best quality, recommended for most use cases"
    },
    {
        "id": "gemini-1.5-flash", 
        "name": "Gemini 1.5 Flash",
        "description": "Faster processing, good quality"
    },
    {
        "id": "gemini-1.5-pro",
        "name": "Gemini 1.5 Pro", 
        "description": "Balanced option"
    }
]

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"