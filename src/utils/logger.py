"""
Logging configuration and utilities for the QR Scanner application.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE
from ..config.paths import LOGS_DIR, ensure_directories

# Global logger instance
_logger: Optional[logging.Logger] = None

def setup_logger(name: str = "QRScanner", level: str = None) -> logging.Logger:
    """
    Setup and configure the application logger.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Ensure log directory exists
    ensure_directories()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level or LOG_LEVEL))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = LOGS_DIR / f"qr_scanner_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Error file handler
    error_log_file = LOGS_DIR / f"qr_scanner_errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    _logger = logger
    return logger

def get_logger(name: str = "QRScanner") -> logging.Logger:
    """
    Get the application logger.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    if _logger is None:
        return setup_logger(name)
    return _logger

def log_function_call(func):
    """
    Decorator to log function calls with parameters and return values.
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = func.__name__
        
        # Log function call
        logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func_name} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in {func_name}: {str(e)}", exc_info=True)
            raise
    
    return wrapper

def log_performance(func):
    """
    Decorator to log function performance.
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function
    """
    import time
    
    def wrapper(*args, **kwargs):
        logger = get_logger()
        func_name = func.__name__
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func_name} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func_name} failed after {execution_time:.4f} seconds: {str(e)}")
            raise
    
    return wrapper

class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self):
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def log_debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def log_error(self, message: str, exc_info: bool = False):
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)
    
    def log_critical(self, message: str, exc_info: bool = False):
        """Log critical message."""
        self.logger.critical(message, exc_info=exc_info) 