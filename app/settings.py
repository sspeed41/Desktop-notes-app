"""
Settings and configuration for WiseDesktopNoteApp
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
def load_settings():
    """Load settings from environment variables"""
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

# Supabase settings
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE", "")
ORG_ID = os.getenv("ORG_ID", "default-org")

# Application settings
APP_NAME = "Wise Desktop Note App"
APP_VERSION = "2.5.0"

# UI Constants - X/Twitter-inspired minimal design
COLORS = {
    "primary": "#1DA1F2",      # Twitter blue
    "secondary": "#657786",    # Gray
    "background": "#FFFFFF",   # White
    "surface": "#F7F9FA",      # Light gray
    "text_primary": "#14171A", # Dark gray
    "text_secondary": "#657786", # Medium gray
    "border": "#E1E8ED",       # Light border
    "hover": "#F7F9FA",        # Hover state
    "success": "#17BF63",      # Green
    "warning": "#FFAD1F",      # Orange
    "error": "#E0245E",        # Red
}

FONTS = {
    "primary": "SF Pro Display",
    "secondary": "SF Pro Text",
    "mono": "SF Mono",
}

# Cache settings
CACHE_DIR = Path.home() / ".wise_desktop_note_app" / "cache"
CACHE_SIZE_LIMIT = 1000  # Maximum number of cached notes

# Supabase storage
STORAGE_BUCKET = "race-media"

# Default tags
DEFAULT_TAGS = [
    "Qualifying", "Restart", "Entry", "Exit", "Min Speed", 
    "Proximity", "Angle", "Shape", "Pass", "Aero", "Pit Road",
    "Green Pit Entry", "Green Pit Exit"
] 