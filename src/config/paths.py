"""
Path configuration for the QR Scanner application.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
SRC_DIR = BASE_DIR / "src"
ASSETS_DIR = BASE_DIR / "assets"
DOCS_DIR = BASE_DIR / "docs"
TESTS_DIR = BASE_DIR / "src" / "tests"

# Application paths
APP_DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"
TEMP_DIR = BASE_DIR / "temp"

# Asset paths
ICONS_DIR = ASSETS_DIR / "icons"
STYLES_DIR = ASSETS_DIR / "styles"
IMAGES_DIR = ASSETS_DIR / "images"

# Configuration paths
CONFIG_DIR = SRC_DIR / "config"
SETTINGS_FILE = CONFIG_DIR / "user_settings.json"

# Data paths
HISTORY_FILE = APP_DATA_DIR / "scan_history.json"
SETTINGS_BACKUP = APP_DATA_DIR / "settings_backup.json"
EXPORT_DIR = APP_DATA_DIR / "exports"

# Google Sheets paths
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = BASE_DIR / "token.pickle"

def get_credentials_path():
    """Get the path to the credentials file."""
    return CREDENTIALS_PATH

def get_token_path():
    """Get the path to the token file."""
    return TOKEN_PATH

# Create directories if they don't exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        APP_DATA_DIR,
        LOGS_DIR,
        CACHE_DIR,
        TEMP_DIR,
        ICONS_DIR,
        STYLES_DIR,
        IMAGES_DIR,
        EXPORT_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# File patterns
SCAN_HISTORY_PATTERN = "scan_history_*.json"
EXPORT_PATTERN = "qr_export_*.csv"
LOG_PATTERN = "qr_scanner_*.log"

# URL patterns for validation
URL_PATTERNS = [
    r'^https?://',  # HTTP/HTTPS URLs
    r'^mailto:',    # Email links
    r'^tel:',       # Phone links
    r'^geo:',       # Geographic coordinates
    r'^wifi:',      # WiFi network info
    r'^BEGIN:VCARD', # Contact info
    r'^BEGIN:VEVENT', # Calendar events
] 