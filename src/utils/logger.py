import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE
from ..config.paths import LOGS_DIR, ensure_directories

_logger: Optional[logging.Logger] = None

def setup_logger(name: str = "QRScanner", level: str = None) -> logging.Logger:
    global _logger
    
    if _logger is not None:
        return _logger
    
    ensure_directories()
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level or LOG_LEVEL))
    
    logger.handlers.clear()
    
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(LOG_FORMAT)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    log_file = LOGS_DIR / f"qr_scanner_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    error_log_file = LOGS_DIR / f"qr_scanner_errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    _logger = logger
    return logger

def get_logger(name: str = "QRScanner") -> logging.Logger:
    if _logger is None:
        return setup_logger(name)
    return _logger

def log_function_call(func):
    def wrapper(*args, **kwargs):
        logger = get_logger()
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} raised exception: {str(e)}")
            raise
    return wrapper

def log_performance(func):
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger = get_logger()
        logger.debug(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

class LoggerMixin:
    @property
    def logger(self):
        return get_logger(self.__class__.__name__)
    
    def log_info(self, message: str):
        self.logger.info(message)
    
    def log_debug(self, message: str):
        self.logger.debug(message)
    
    def log_warning(self, message: str):
        self.logger.warning(message)
    
    def log_error(self, message: str, exc_info: bool = False):
        self.logger.error(message, exc_info=exc_info)
    
    def log_critical(self, message: str, exc_info: bool = False):
        self.logger.critical(message, exc_info=exc_info) 