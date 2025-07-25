"""
Main application settings and configuration.
"""

import os
from pathlib import Path

# Application Info
APP_NAME = "QR Code Scanner"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Modern QR Code Scanner with Google Sheets Integration"

# Window Settings
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"
WINDOW_SIZE = "1000x800"
MIN_WINDOW_SIZE = "800x600"

# Camera Settings
CAMERA_INDEX = 0
SCAN_DELAY = 0.03  # seconds
CAMERA_RESOLUTION = (640, 480)
CAMERA_FPS = 30

# Google Sheets Settings
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
DEFAULT_SPREADSHEET_ID = "1PjW2-qgjWs5123qkzVyOBc-OKs2Ygk1143zkl_CymwQ"
DEFAULT_SHEET_NAME = "Scanner"
MASTER_LIST_SHEET = "MasterList"
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.pickle"

# File Settings
SUPPORTED_IMAGE_TYPES = [("JSON files", "*.json"), ("All files", "*.*")]
SUPPORTED_EXPORT_TYPES = [
    ("CSV files", "*.csv"),
    ("Text files", "*.txt"),
    ("Excel files", "*.xlsx"),
    ("All files", "*.*")
]

# Notification Settings
NOTIFICATION_DURATION = 2.0  # seconds
NOTIFICATION_SIZE = "300x150"

# Typing Simulation Settings
MIN_TYPING_DELAY = 0.001
MAX_TYPING_DELAY = 0.005
PAUSE_PROBABILITY = 0.01
PAUSE_DELAY_MIN = 0.05
PAUSE_DELAY_MAX = 0.1
ENTER_DELAY = 0.1

# Auto-save Settings
AUTO_SAVE_INTERVAL = 30  # seconds
MAX_HISTORY_ITEMS = 1000

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = "qr_scanner.log"

# Performance Settings
THREAD_POOL_SIZE = 4
MAX_CONCURRENT_SCANS = 2
CACHE_SIZE = 100

# Security Settings
ENCRYPT_CREDENTIALS = True
SESSION_TIMEOUT = 3600  # 1 hour 