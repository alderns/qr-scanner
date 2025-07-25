import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
SRC_DIR = BASE_DIR / "src"
ASSETS_DIR = BASE_DIR / "assets"
DOCS_DIR = BASE_DIR / "docs"
TESTS_DIR = BASE_DIR / "src" / "tests"

APP_DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CACHE_DIR = BASE_DIR / "cache"
TEMP_DIR = BASE_DIR / "temp"

ICONS_DIR = ASSETS_DIR / "icons"
STYLES_DIR = ASSETS_DIR / "styles"
IMAGES_DIR = ASSETS_DIR / "images"

CONFIG_DIR = SRC_DIR / "config"
SETTINGS_FILE = CONFIG_DIR / "user_settings.json"

HISTORY_FILE = APP_DATA_DIR / "scan_history.json"
SETTINGS_BACKUP = APP_DATA_DIR / "settings_backup.json"
EXPORT_DIR = APP_DATA_DIR / "exports"

CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = BASE_DIR / "token.pickle"

def get_credentials_path():
    return CREDENTIALS_PATH

def get_token_path():
    return TOKEN_PATH

def ensure_directories():
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

SCAN_HISTORY_PATTERN = "scan_history_*.json"
EXPORT_PATTERN = "qr_export_*.csv"
LOG_PATTERN = "qr_scanner_*.log"

URL_PATTERNS = [
    r'^https?://',
    r'^mailto:',
    r'^tel:',
    r'^geo:',
    r'^wifi:',
    r'^BEGIN:VCARD',
    r'^BEGIN:VEVENT',
] 