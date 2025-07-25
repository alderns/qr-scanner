import os
from pathlib import Path

APP_NAME = "QR Code Scanner"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Modern QR Code Scanner with Google Sheets Integration"

WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"
WINDOW_SIZE = "1000x800"
MIN_WINDOW_SIZE = "800x800"

CAMERA_INDEX = 0
SCAN_DELAY = 0.03
CAMERA_RESOLUTION = (640, 480)
CAMERA_FPS = 30

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DEFAULT_SPREADSHEET_ID = "1PjW2-qgjWs5123qkzVyOBc-OKs2Ygk1143zkl_CymwQ"
DEFAULT_SHEET_NAME = "Scanner"
MASTER_LIST_SHEET = "MasterList"

# Master List Configuration
DEFAULT_MASTER_LIST_SPREADSHEET_ID = ""  # Leave empty to use main spreadsheet, or set to separate spreadsheet ID
DEFAULT_MASTER_LIST_SHEET_NAME = "MasterList"

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"

SUPPORTED_IMAGE_TYPES = [("JSON files", "*.json"), ("All files", "*.*")]
SUPPORTED_EXPORT_TYPES = [
    ("CSV files", "*.csv"),
    ("Text files", "*.txt"),
    ("Excel files", "*.xlsx"),
    ("All files", "*.*")
]

NOTIFICATION_DURATION = 2.0
NOTIFICATION_SIZE = "300x150"

# Auto-save settings
AUTO_SAVE_INTERVAL = 300  # 5 minutes instead of 30 seconds
MAX_HISTORY_ITEMS = 1000

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "qr_scanner.log"

THREAD_POOL_SIZE = 4
MAX_CONCURRENT_SCANS = 2
CACHE_SIZE = 100

ENCRYPT_CREDENTIALS = True
SESSION_TIMEOUT = 3600 