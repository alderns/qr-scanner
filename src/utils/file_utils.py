"""
File utility functions for the QR Scanner application.
"""

import json
import csv
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import zipfile

from .logger import get_logger, log_function_call
from ..config.paths import (
    APP_DATA_DIR, EXPORT_DIR, HISTORY_FILE, 
    ensure_directories, SCAN_HISTORY_PATTERN
)

logger = get_logger(__name__)

class FileManager:
    """Manages file operations for the QR Scanner application."""
    
    def __init__(self):
        ensure_directories()
        self.logger = logger
    
    @log_function_call
    def save_scan_history(self, history_data: List[Dict[str, Any]], 
                         filename: Optional[str] = None) -> bool:
        """
        Save scan history to JSON file.
        
        Args:
            history_data: List of scan history items
            filename: Optional custom filename
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scan_history_{timestamp}.json"
            
            file_path = APP_DATA_DIR / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Scan history saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save scan history: {str(e)}")
            return False
    
    @log_function_call
    def load_scan_history(self, filename: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load scan history from JSON file.
        
        Args:
            filename: Optional custom filename
        
        Returns:
            List of scan history items
        """
        try:
            if filename is None:
                file_path = HISTORY_FILE
            else:
                file_path = APP_DATA_DIR / filename
            
            if not file_path.exists():
                self.logger.warning(f"History file not found: {file_path}")
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            self.logger.info(f"Loaded {len(history_data)} scan history items")
            return history_data
            
        except Exception as e:
            self.logger.error(f"Failed to load scan history: {str(e)}")
            return []
    
    @log_function_call
    def export_to_csv(self, data: List[Dict[str, Any]], 
                     filename: Optional[str] = None) -> bool:
        """
        Export data to CSV file.
        
        Args:
            data: List of dictionaries to export
            filename: Optional custom filename
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                self.logger.warning("No data to export")
                return False
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"qr_export_{timestamp}.csv"
            
            file_path = EXPORT_DIR / filename
            
            # Get fieldnames from first item
            fieldnames = list(data[0].keys())
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            self.logger.info(f"Data exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export data: {str(e)}")
            return False
    
    @log_function_call
    def export_to_excel(self, data: List[Dict[str, Any]], 
                       filename: Optional[str] = None) -> bool:
        """
        Export data to Excel file.
        
        Args:
            data: List of dictionaries to export
            filename: Optional custom filename
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import pandas as pd
            
            if not data:
                self.logger.warning("No data to export")
                return False
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"qr_export_{timestamp}.xlsx"
            
            file_path = EXPORT_DIR / filename
            
            # Convert to DataFrame and save
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
            self.logger.info(f"Data exported to {file_path}")
            return True
            
        except ImportError:
            self.logger.error("pandas not installed, cannot export to Excel")
            return False
        except Exception as e:
            self.logger.error(f"Failed to export data: {str(e)}")
            return False
    
    @log_function_call
    def backup_file(self, source_path: Union[str, Path], 
                   backup_dir: Optional[Union[str, Path]] = None) -> bool:
        """
        Create a backup of a file.
        
        Args:
            source_path: Path to the file to backup
            backup_dir: Optional backup directory
        
        Returns:
            True if successful, False otherwise
        """
        try:
            source_path = Path(source_path)
            if not source_path.exists():
                self.logger.warning(f"Source file not found: {source_path}")
                return False
            
            if backup_dir is None:
                backup_dir = APP_DATA_DIR / "backups"
                backup_dir.mkdir(exist_ok=True)
            else:
                backup_dir = Path(backup_dir)
                backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = backup_dir / backup_filename
            
            # Copy file
            shutil.copy2(source_path, backup_path)
            
            self.logger.info(f"Backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {str(e)}")
            return False
    
    @log_function_call
    def cleanup_old_files(self, directory: Union[str, Path], 
                         pattern: str, max_age_days: int = 30) -> int:
        """
        Clean up old files in a directory.
        
        Args:
            directory: Directory to clean
            pattern: File pattern to match
            max_age_days: Maximum age of files to keep
        
        Returns:
            Number of files deleted
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
            deleted_count = 0
            
            for file_path in directory.glob(pattern):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    self.logger.debug(f"Deleted old file: {file_path}")
            
            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old files")
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old files: {str(e)}")
            return 0
    
    @log_function_call
    def create_archive(self, source_dir: Union[str, Path], 
                      archive_name: Optional[str] = None) -> bool:
        """
        Create a ZIP archive of a directory.
        
        Args:
            source_dir: Directory to archive
            archive_name: Optional archive name
        
        Returns:
            True if successful, False otherwise
        """
        try:
            source_dir = Path(source_dir)
            if not source_dir.exists():
                self.logger.warning(f"Source directory not found: {source_dir}")
                return False
            
            if archive_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"qr_scanner_backup_{timestamp}.zip"
            
            archive_path = EXPORT_DIR / archive_name
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in source_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(source_dir)
                        zipf.write(file_path, arcname)
            
            self.logger.info(f"Archive created: {archive_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create archive: {str(e)}")
            return False

# Global file manager instance
file_manager = FileManager()

# Convenience functions
 