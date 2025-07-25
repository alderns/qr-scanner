"""
Configuration manager for the QR Scanner application.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

from .settings import *
from .paths import SETTINGS_FILE, ensure_directories
from ..utils.logger import LoggerMixin, get_logger

logger = get_logger(__name__)


@dataclass
class AppConfig:
    """Application configuration data class."""
    
    # Window settings
    window_title: str = WINDOW_TITLE
    window_size: str = WINDOW_SIZE
    min_window_size: str = MIN_WINDOW_SIZE
    
    # Camera settings
    camera_index: int = CAMERA_INDEX
    scan_delay: float = SCAN_DELAY
    camera_resolution: tuple = CAMERA_RESOLUTION
    camera_fps: int = CAMERA_FPS
    
    # Google Sheets settings
    default_spreadsheet_id: str = DEFAULT_SPREADSHEET_ID
    default_sheet_name: str = DEFAULT_SHEET_NAME
    master_list_sheet: str = MASTER_LIST_SHEET
    
    # Auto-save settings
    auto_save_interval: int = AUTO_SAVE_INTERVAL
    max_history_items: int = MAX_HISTORY_ITEMS
    
    # Logging settings
    log_level: str = LOG_LEVEL
    log_format: str = LOG_FORMAT
    
    # Performance settings
    thread_pool_size: int = THREAD_POOL_SIZE
    max_concurrent_scans: int = MAX_CONCURRENT_SCANS
    cache_size: int = CACHE_SIZE


class ConfigManager(LoggerMixin):
    """Manages application configuration and settings."""
    
    def __init__(self):
        """Initialize the configuration manager."""
        super().__init__()
        self.config = AppConfig()
        self.user_settings: Dict[str, Any] = {}
        self._load_user_settings()
    
    def _load_user_settings(self):
        """Load user-specific settings from file."""
        try:
            ensure_directories()
            
            if SETTINGS_FILE.exists():
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    self.user_settings = json.load(f)
                self.log_info("User settings loaded successfully")
            else:
                self.user_settings = {}
                self.log_info("No user settings file found, using defaults")
                
        except Exception as e:
            self.log_error(f"Error loading user settings: {str(e)}")
            self.user_settings = {}
    
    def _save_user_settings(self):
        """Save user-specific settings to file."""
        try:
            ensure_directories()
            
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.user_settings, f, indent=2, ensure_ascii=False)
            
            self.log_info("User settings saved successfully")
            
        except Exception as e:
            self.log_error(f"Error saving user settings: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        # Check user settings first
        if key in self.user_settings:
            return self.user_settings[key]
        
        # Check default config
        if hasattr(self.config, key):
            return getattr(self.config, key)
        
        return default
    
    def set(self, key: str, value: Any):
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        try:
            self.user_settings[key] = value
            self._save_user_settings()
            self.log_info(f"Configuration updated: {key} = {value}")
            
        except Exception as e:
            self.log_error(f"Error setting configuration: {str(e)}")
    
    def get_google_sheets_config(self) -> Dict[str, str]:
        """Get Google Sheets configuration."""
        return {
            'spreadsheet_id': self.get('default_spreadsheet_id', DEFAULT_SPREADSHEET_ID),
            'sheet_name': self.get('default_sheet_name', DEFAULT_SHEET_NAME),
            'master_list_sheet': self.get('master_list_sheet', MASTER_LIST_SHEET)
        }
    
    def set_google_sheets_config(self, spreadsheet_id: str, sheet_name: str, master_list_sheet: str = None):
        """Set Google Sheets configuration."""
        self.set('default_spreadsheet_id', spreadsheet_id)
        self.set('default_sheet_name', sheet_name)
        if master_list_sheet:
            self.set('master_list_sheet', master_list_sheet)
    
    def get_camera_config(self) -> Dict[str, Any]:
        """Get camera configuration."""
        return {
            'camera_index': self.get('camera_index', CAMERA_INDEX),
            'scan_delay': self.get('scan_delay', SCAN_DELAY),
            'camera_resolution': self.get('camera_resolution', CAMERA_RESOLUTION),
            'camera_fps': self.get('camera_fps', CAMERA_FPS)
        }
    
    def set_camera_config(self, camera_index: int = None, scan_delay: float = None, 
                         camera_resolution: tuple = None, camera_fps: int = None):
        """Set camera configuration."""
        if camera_index is not None:
            self.set('camera_index', camera_index)
        if scan_delay is not None:
            self.set('scan_delay', scan_delay)
        if camera_resolution is not None:
            self.set('camera_resolution', camera_resolution)
        if camera_fps is not None:
            self.set('camera_fps', camera_fps)
    
    def get_window_config(self) -> Dict[str, str]:
        """Get window configuration."""
        return {
            'window_title': self.get('window_title', WINDOW_TITLE),
            'window_size': self.get('window_size', WINDOW_SIZE),
            'min_window_size': self.get('min_window_size', MIN_WINDOW_SIZE)
        }
    
    def set_window_config(self, window_title: str = None, window_size: str = None, 
                         min_window_size: str = None):
        """Set window configuration."""
        if window_title is not None:
            self.set('window_title', window_title)
        if window_size is not None:
            self.set('window_size', window_size)
        if min_window_size is not None:
            self.set('min_window_size', min_window_size)
    
    def get_performance_config(self) -> Dict[str, int]:
        """Get performance configuration."""
        return {
            'thread_pool_size': self.get('thread_pool_size', THREAD_POOL_SIZE),
            'max_concurrent_scans': self.get('max_concurrent_scans', MAX_CONCURRENT_SCANS),
            'cache_size': self.get('cache_size', CACHE_SIZE),
            'max_history_items': self.get('max_history_items', MAX_HISTORY_ITEMS)
        }
    
    def set_performance_config(self, thread_pool_size: int = None, max_concurrent_scans: int = None,
                              cache_size: int = None, max_history_items: int = None):
        """Set performance configuration."""
        if thread_pool_size is not None:
            self.set('thread_pool_size', thread_pool_size)
        if max_concurrent_scans is not None:
            self.set('max_concurrent_scans', max_concurrent_scans)
        if cache_size is not None:
            self.set('cache_size', cache_size)
        if max_history_items is not None:
            self.set('max_history_items', max_history_items)
    
    def reset_to_defaults(self):
        """Reset all user settings to defaults."""
        try:
            self.user_settings.clear()
            self._save_user_settings()
            self.log_info("Configuration reset to defaults")
            
        except Exception as e:
            self.log_error(f"Error resetting configuration: {str(e)}")
    
    def export_config(self, filepath: Path) -> bool:
        """
        Export configuration to file.
        
        Args:
            filepath: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            export_data = {
                'user_settings': self.user_settings,
                'default_config': asdict(self.config)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.log_info(f"Configuration exported to {filepath}")
            return True
            
        except Exception as e:
            self.log_error(f"Error exporting configuration: {str(e)}")
            return False
    
    def import_config(self, filepath: Path) -> bool:
        """
        Import configuration from file.
        
        Args:
            filepath: Path to import file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'user_settings' in import_data:
                self.user_settings = import_data['user_settings']
                self._save_user_settings()
                self.log_info(f"Configuration imported from {filepath}")
                return True
            else:
                self.log_error("Invalid configuration file format")
                return False
                
        except Exception as e:
            self.log_error(f"Error importing configuration: {str(e)}")
            return False 