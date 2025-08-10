"""
Configuration manager for centralized application configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime

from ..utils.logger import LoggerMixin, get_logger
from ..utils.exceptions import ConfigurationError
from .paths import APP_DATA_DIR, ensure_directories
from .settings import *

logger = get_logger(__name__)


@dataclass
class GoogleSheetsConfig:
    """Google Sheets configuration."""
    spreadsheet_id: str = DEFAULT_SPREADSHEET_ID
    sheet_name: str = DEFAULT_SHEET_NAME
    master_list_sheet: str = DEFAULT_MASTER_LIST_SHEET_NAME
    master_list_spreadsheet_id: str = DEFAULT_MASTER_LIST_SPREADSHEET_ID
    master_list_sheet_name: str = DEFAULT_MASTER_LIST_SHEET_NAME
    credentials_file: str = CREDENTIALS_FILE
    token_file: str = TOKEN_FILE
    scopes: list = None
    
    def __post_init__(self):
        if self.scopes is None:
            self.scopes = SCOPES.copy()


@dataclass
class CameraConfig:
    """Camera configuration."""
    camera_index: int = CAMERA_INDEX
    scan_delay: float = SCAN_DELAY
    resolution: tuple = CAMERA_RESOLUTION
    fps: int = CAMERA_FPS
    auto_start: bool = False


@dataclass
class WindowConfig:
    """Window configuration."""
    title: str = WINDOW_TITLE
    size: str = WINDOW_SIZE
    min_size: str = MIN_WINDOW_SIZE
    theme: str = "default"
    auto_save_position: bool = True
    remember_size: bool = True


@dataclass
class PerformanceConfig:
    """Performance configuration."""
    thread_pool_size: int = THREAD_POOL_SIZE
    max_concurrent_scans: int = MAX_CONCURRENT_SCANS
    cache_size: int = CACHE_SIZE
    auto_save_interval: int = AUTO_SAVE_INTERVAL
    max_history_items: int = MAX_HISTORY_ITEMS
    enable_performance_monitoring: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = LOG_LEVEL
    format: str = LOG_FORMAT
    file: str = LOG_FILE
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_console_logging: bool = True
    enable_file_logging: bool = True


@dataclass
class ApplicationConfig:
    """Complete application configuration."""
    app_name: str = APP_NAME
    app_version: str = APP_VERSION
    app_description: str = APP_DESCRIPTION
    
    # Sub-configurations
    google_sheets: GoogleSheetsConfig = None
    camera: CameraConfig = None
    window: WindowConfig = None
    performance: PerformanceConfig = None
    logging: LoggingConfig = None
    
    # User preferences
    auto_save_enabled: bool = True
    clipboard_integration: bool = True
    notifications_enabled: bool = True
    dark_mode: bool = False
    auto_connect_to_sheets: bool = True
    auto_load_master_list: bool = True
    
    def __post_init__(self):
        if self.google_sheets is None:
            self.google_sheets = GoogleSheetsConfig()
        if self.camera is None:
            self.camera = CameraConfig()
        if self.window is None:
            self.window = WindowConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.logging is None:
            self.logging = LoggingConfig()


class ConfigManager(LoggerMixin):
    """
    Centralized configuration manager for the QR Scanner application.
    
    This class provides a unified interface for managing all application
    configuration, including default values, user preferences, and
    configuration persistence.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Optional path to configuration file
        """
        super().__init__()
        
        ensure_directories()
        
        self.config_file = config_file or (APP_DATA_DIR / "user_config.json")
        self.config = ApplicationConfig()
        self._load_config()
        
        self.log_info("Configuration manager initialized")
    
    def get_config(self) -> ApplicationConfig:
        """
        Get the current configuration.
        
        Returns:
            Current application configuration
        """
        return self.config
    
    def get_google_sheets_config(self) -> GoogleSheetsConfig:
        """Get Google Sheets configuration."""
        # Ensure we return a proper GoogleSheetsConfig object
        if isinstance(self.config.google_sheets, dict):
            # Convert dict to GoogleSheetsConfig object
            google_sheets_dict = self.config.google_sheets.copy()
            
            # Ensure new Master List fields exist with defaults
            if 'master_list_spreadsheet_id' not in google_sheets_dict:
                google_sheets_dict['master_list_spreadsheet_id'] = DEFAULT_MASTER_LIST_SPREADSHEET_ID
            if 'master_list_sheet_name' not in google_sheets_dict:
                google_sheets_dict['master_list_sheet_name'] = DEFAULT_MASTER_LIST_SHEET_NAME
            
            # Create and return a new GoogleSheetsConfig object
            return GoogleSheetsConfig(**google_sheets_dict)
        
        return self.config.google_sheets
    
    def get_camera_config(self) -> CameraConfig:
        """Get camera configuration."""
        return self.config.camera
    
    def get_window_config(self) -> WindowConfig:
        """Get window configuration."""
        return self.config.window
    
    def get_performance_config(self) -> PerformanceConfig:
        """Get performance configuration."""
        return self.config.performance
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return self.config.logging
    
    def get_user_preferences(self) -> dict:
        """
        Get user preferences.
        
        Returns:
            Dictionary containing user preferences
        """
        return {
            'auto_save_enabled': self.config.auto_save_enabled,
            'clipboard_integration': self.config.clipboard_integration,
            'notifications_enabled': self.config.notifications_enabled,
            'dark_mode': self.config.dark_mode,
            'auto_connect_to_sheets': self.config.auto_connect_to_sheets,
            'auto_load_master_list': self.config.auto_load_master_list
        }
    
    def update_google_sheets_config(self, **kwargs) -> bool:
        """
        Update Google Sheets configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure we have a proper GoogleSheetsConfig object
            if isinstance(self.config.google_sheets, dict):
                # Convert dict to GoogleSheetsConfig object
                google_sheets_dict = self.config.google_sheets.copy()
                
                # Ensure new Master List fields exist with defaults
                if 'master_list_spreadsheet_id' not in google_sheets_dict:
                    google_sheets_dict['master_list_spreadsheet_id'] = DEFAULT_MASTER_LIST_SPREADSHEET_ID
                if 'master_list_sheet_name' not in google_sheets_dict:
                    google_sheets_dict['master_list_sheet_name'] = DEFAULT_MASTER_LIST_SHEET_NAME
                
                # Create a new GoogleSheetsConfig object
                self.config.google_sheets = GoogleSheetsConfig(**google_sheets_dict)
            
            # Now update the configuration
            for key, value in kwargs.items():
                if hasattr(self.config.google_sheets, key):
                    setattr(self.config.google_sheets, key, value)
                else:
                    self.log_warning(f"Unknown Google Sheets config key: {key}")
            
            self._save_config()
            self.log_info("Google Sheets configuration updated")
            return True
            
        except Exception as e:
            self.log_error(f"Error updating Google Sheets config: {str(e)}")
            return False
    
    def update_camera_config(self, **kwargs) -> bool:
        """
        Update camera configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.camera, key):
                    setattr(self.config.camera, key, value)
                else:
                    self.log_warning(f"Unknown camera config key: {key}")
            
            self._save_config()
            self.log_info("Camera configuration updated")
            return True
            
        except Exception as e:
            self.log_error(f"Error updating camera config: {str(e)}")
            return False
    
    def update_window_config(self, **kwargs) -> bool:
        """
        Update window configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.window, key):
                    setattr(self.config.window, key, value)
                else:
                    self.log_warning(f"Unknown window config key: {key}")
            
            self._save_config()
            self.log_info("Window configuration updated")
            return True
            
        except Exception as e:
            self.log_error(f"Error updating window config: {str(e)}")
            return False
    
    def update_performance_config(self, **kwargs) -> bool:
        """
        Update performance configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.performance, key):
                    setattr(self.config.performance, key, value)
                else:
                    self.log_warning(f"Unknown performance config key: {key}")
            
            self._save_config()
            self.log_info("Performance configuration updated")
            return True
            
        except Exception as e:
            self.log_error(f"Error updating performance config: {str(e)}")
            return False
    
    def update_logging_config(self, **kwargs) -> bool:
        """
        Update logging configuration.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config.logging, key):
                    setattr(self.config.logging, key, value)
                else:
                    self.log_warning(f"Unknown logging config key: {key}")
            
            self._save_config()
            self.log_info("Logging configuration updated")
            return True
            
        except Exception as e:
            self.log_error(f"Error updating logging config: {str(e)}")
            return False
    
    def update_user_preferences(self, **kwargs) -> bool:
        """
        Update user preferences.
        
        Args:
            **kwargs: Preference parameters to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            valid_preferences = [
                'auto_save_enabled', 'clipboard_integration', 
                'notifications_enabled', 'dark_mode', 'auto_connect_to_sheets',
                'auto_load_master_list'
            ]
            
            for key, value in kwargs.items():
                if key in valid_preferences:
                    setattr(self.config, key, value)
                else:
                    self.log_warning(f"Unknown user preference: {key}")
            
            self._save_config()
            self.log_info("User preferences updated")
            return True
            
        except Exception as e:
            self.log_error(f"Error updating user preferences: {str(e)}")
            return False
    
    def reset_to_defaults(self, section: Optional[str] = None) -> bool:
        """
        Reset configuration to default values.
        
        Args:
            section: Optional section to reset (google_sheets, camera, window, performance, logging)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if section is None:
                # Reset entire configuration
                self.config = ApplicationConfig()
                self.log_info("Configuration reset to defaults")
            else:
                # Reset specific section
                if section == 'google_sheets':
                    self.config.google_sheets = GoogleSheetsConfig()
                elif section == 'camera':
                    self.config.camera = CameraConfig()
                elif section == 'window':
                    self.config.window = WindowConfig()
                elif section == 'performance':
                    self.config.performance = PerformanceConfig()
                elif section == 'logging':
                    self.config.logging = LoggingConfig()
                else:
                    self.log_warning(f"Unknown configuration section: {section}")
                    return False
                
                self.log_info(f"{section} configuration reset to defaults")
            
            self._save_config()
            return True
            
        except Exception as e:
            self.log_error(f"Error resetting configuration: {str(e)}")
            return False
    
    def export_config(self, file_path: str) -> bool:
        """
        Export configuration to file.
        
        Args:
            file_path: Path to export configuration to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config_dict = self._config_to_dict()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            self.log_info(f"Configuration exported to {file_path}")
            return True
            
        except Exception as e:
            self.log_error(f"Error exporting configuration: {str(e)}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """
        Import configuration from file.
        
        Args:
            file_path: Path to import configuration from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            self._dict_to_config(config_dict)
            self._save_config()
            
            self.log_info(f"Configuration imported from {file_path}")
            return True
            
        except Exception as e:
            self.log_error(f"Error importing configuration: {str(e)}")
            return False
    
    def validate_config(self) -> bool:
        """
        Validate current configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate Google Sheets config
            if not self.config.google_sheets.spreadsheet_id:
                raise ConfigurationError("Google Sheets spreadsheet ID is required")
            
            # Validate camera config
            if self.config.camera.camera_index < 0:
                raise ConfigurationError("Camera index must be non-negative")
            
            # Validate performance config
            if self.config.performance.thread_pool_size < 1:
                raise ConfigurationError("Thread pool size must be at least 1")
            
            # Validate logging config
            valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.config.logging.level not in valid_log_levels:
                raise ConfigurationError(f"Invalid log level: {self.config.logging.level}")
            
            self.log_info("Configuration validation successful")
            return True
            
        except Exception as e:
            self.log_error(f"Configuration validation failed: {str(e)}")
            return False
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                
                self.log_debug(f"Loaded config dict: {config_dict}")
                self._dict_to_config(config_dict)
                self.log_info(f"Configuration loaded from {self.config_file}")
            else:
                self.log_info("No configuration file found, using defaults")
                
        except Exception as e:
            self.log_error(f"Error loading configuration: {str(e)}")
            self.log_info("Using default configuration")
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            config_dict = self._config_to_dict()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            self.log_debug(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            self.log_error(f"Error saving configuration: {str(e)}")
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = asdict(self.config)
        
        # Add metadata
        config_dict['_metadata'] = {
            'version': self.config.app_version,
            'last_modified': datetime.now().isoformat(),
            'exported_by': 'QR Scanner Config Manager'
        }
        
        return config_dict
    
    def _dict_to_config(self, config_dict: Dict[str, Any]):
        """Convert dictionary to configuration."""
        self.log_debug(f"Converting dict to config: {config_dict}")
        
        # Remove metadata
        config_dict.pop('_metadata', None)
        
        # Reconstruct configuration objects
        if 'google_sheets' in config_dict:
            google_sheets_dict = config_dict['google_sheets']
            self.log_debug(f"Processing google_sheets: {google_sheets_dict}")
            
            # Ensure new Master List fields exist with defaults
            if 'master_list_spreadsheet_id' not in google_sheets_dict:
                google_sheets_dict['master_list_spreadsheet_id'] = DEFAULT_MASTER_LIST_SPREADSHEET_ID
            if 'master_list_sheet_name' not in google_sheets_dict:
                google_sheets_dict['master_list_sheet_name'] = DEFAULT_MASTER_LIST_SHEET_NAME
            
            # Create a new GoogleSheetsConfig object
            self.config.google_sheets = GoogleSheetsConfig(**google_sheets_dict)
            self.log_debug(f"Created GoogleSheetsConfig: {self.config.google_sheets}")
        else:
            # If no google_sheets config, create default
            self.config.google_sheets = GoogleSheetsConfig()
            self.log_debug("Created default GoogleSheetsConfig")
            
        if 'camera' in config_dict:
            self.config.camera = CameraConfig(**config_dict['camera'])
        else:
            self.config.camera = CameraConfig()
            
        if 'window' in config_dict:
            self.config.window = WindowConfig(**config_dict['window'])
        else:
            self.config.window = WindowConfig()
            
        if 'performance' in config_dict:
            self.config.performance = PerformanceConfig(**config_dict['performance'])
        else:
            self.config.performance = PerformanceConfig()
            
        if 'logging' in config_dict:
            self.config.logging = LoggingConfig(**config_dict['logging'])
        else:
            self.config.logging = LoggingConfig()
        
        # Update other attributes
        for key, value in config_dict.items():
            if hasattr(self.config, key) and not key.endswith('_config'):
                setattr(self.config, key, value) 