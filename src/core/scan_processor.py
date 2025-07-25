"""
Scan processor for handling QR code scan data.
"""

import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from collections import deque

from ..utils.logger import LoggerMixin, get_logger
from ..utils.file_utils import save_history, load_history, export_csv, export_excel
from ..utils.validation import validate_scan_data
from ..utils.scanner_utils import copy_to_clipboard, simulate_qr_scanner_behavior
from ..config.settings import MAX_HISTORY_ITEMS, AUTO_SAVE_INTERVAL

logger = get_logger(__name__)

class ScanProcessor(LoggerMixin):
    """
    Processes and manages QR code scan data.
    
    This class handles:
    - Scan data validation and processing
    - History management
    - Auto-save functionality
    - Export capabilities
    - Clipboard operations
    - Typing simulation
    """
    
    def __init__(self):
        """Initialize the scan processor."""
        super().__init__()
        
        # Scan data storage
        self.scan_history: deque = deque(maxlen=MAX_HISTORY_ITEMS)
        self.last_scan: Optional[Dict[str, Any]] = None
        
        # Processing state
        self.is_processing = False
        self.processing_lock = threading.Lock()
        
        # Callbacks
        self.on_scan_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        
        # Auto-save state
        self.last_save_time = time.time()
        self.auto_save_enabled = True
        
        # Load existing history
        self._load_existing_history()
        
        self.log_info("Scan processor initialized")
    
    def set_callbacks(self, on_scan: Optional[Callable] = None, 
                     on_error: Optional[Callable] = None):
        """
        Set callback functions for scan events.
        
        Args:
            on_scan: Callback for successful scans
            on_error: Callback for errors
        """
        self.on_scan_callback = on_scan
        self.on_error_callback = on_error
    
    def process_scan(self, data: str, barcode_type: str, 
                    source: str = "camera") -> bool:
        """
        Process a new scan.
        
        Args:
            data: Scanned data
            barcode_type: Type of barcode
            source: Source of the scan (camera, file, manual)
        
        Returns:
            True if processing successful, False otherwise
        """
        try:
            with self.processing_lock:
                if self.is_processing:
                    self.log_warning("Already processing a scan, skipping")
                    return False
                
                self.is_processing = True
            
            # Validate scan data
            if not validate_scan_data(data):
                self.log_warning(f"Invalid scan data: {data}")
                if self.on_error_callback:
                    self.on_error_callback(f"Invalid scan data: {data}")
                return False
            
            # Create scan record
            scan_record = {
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'barcode_type': barcode_type,
                'source': source,
                'processed': False
            }
            
            # Add to history
            self.scan_history.append(scan_record)
            self.last_scan = scan_record
            
            # Process the scan
            self._process_scan_data(scan_record)
            
            # Mark as processed
            scan_record['processed'] = True
            
            # Trigger callback
            if self.on_scan_callback:
                self.on_scan_callback(scan_record)
            
            self.log_info(f"Processed scan: {data[:50]}...")
            return True
            
        except Exception as e:
            self.log_error(f"Error processing scan: {str(e)}", exc_info=True)
            if self.on_error_callback:
                self.on_error_callback(f"Processing error: {str(e)}")
            return False
        
        finally:
            with self.processing_lock:
                self.is_processing = False
    
    def _process_scan_data(self, scan_record: Dict[str, Any]):
        """
        Process individual scan data.
        
        Args:
            scan_record: Scan record to process
        """
        data = scan_record['data']
        
        # Auto-copy to clipboard (requires root window, will be handled by app manager)
        # copy_to_clipboard requires root window, so we'll skip it here
        # and let the app manager handle it
        self.log_debug("Scan data processed")
        
        # Simulate typing if it's a URL or text (requires root window, will be handled by app manager)
        # simulate_typing requires root window, so we'll skip it here
        # and let the app manager handle it
        self.log_debug("Scan data ready for processing")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the scan history.
        
        Returns:
            List of scan records
        """
        return list(self.scan_history)
    
    def get_last_scan(self) -> Optional[Dict[str, Any]]:
        """
        Get the last scan record.
        
        Returns:
            Last scan record or None
        """
        return self.last_scan
    
    def get_last_scan_data(self) -> Optional[str]:
        """
        Get the data from the last scan.
        
        Returns:
            Last scan data or None
        """
        if self.last_scan:
            return self.last_scan.get('data')
        return None
    
    def clear_history(self):
        """Clear the scan history."""
        self.scan_history.clear()
        self.last_scan = None
        self.log_info("Scan history cleared")
    
    def get_history_count(self) -> int:
        """
        Get the number of items in history.
        
        Returns:
            Number of history items
        """
        return len(self.scan_history)
    
    def search_history(self, query: str) -> List[Dict[str, Any]]:
        """
        Search the scan history.
        
        Args:
            query: Search query
        
        Returns:
            List of matching scan records
        """
        query = query.lower()
        results = []
        
        for record in self.scan_history:
            if (query in record['data'].lower() or 
                query in record['barcode_type'].lower() or
                query in record['source'].lower()):
                results.append(record)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get scan statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.scan_history:
            return {
                'total_scans': 0,
                'today_scans': 0,
                'barcode_types': {},
                'sources': {}
            }
        
        today = datetime.now().date()
        barcode_types = {}
        sources = {}
        today_count = 0
        
        for record in self.scan_history:
            # Count barcode types
            barcode_type = record['barcode_type']
            barcode_types[barcode_type] = barcode_types.get(barcode_type, 0) + 1
            
            # Count sources
            source = record['source']
            sources[source] = sources.get(source, 0) + 1
            
            # Count today's scans
            try:
                scan_date = datetime.fromisoformat(record['timestamp']).date()
                if scan_date == today:
                    today_count += 1
            except:
                pass
        
        return {
            'total_scans': len(self.scan_history),
            'today_scans': today_count,
            'barcode_types': barcode_types,
            'sources': sources
        }
    
    def auto_save(self):
        """Automatically save scan history."""
        if not self.auto_save_enabled:
            return
        
        current_time = time.time()
        if current_time - self.last_save_time >= AUTO_SAVE_INTERVAL:
            self.save_all_data()
            self.last_save_time = current_time
    
    def save_all_data(self) -> bool:
        """
        Save all scan data to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            history_data = self.get_history()
            if save_history(history_data):
                self.log_info(f"Saved {len(history_data)} scan records")
                return True
            else:
                self.log_error("Failed to save scan history")
                return False
        except Exception as e:
            self.log_error(f"Error saving data: {str(e)}", exc_info=True)
            return False
    
    def _load_existing_history(self):
        """Load existing scan history from file."""
        try:
            history_data = load_history()
            if history_data:
                # Convert to deque format
                for record in history_data:
                    if isinstance(record, dict):
                        self.scan_history.append(record)
                
                self.log_info(f"Loaded {len(history_data)} existing scan records")
        except Exception as e:
            self.log_warning(f"Failed to load existing history: {str(e)}")
    
    def export_history(self, format_type: str = 'csv', 
                      filename: str = None) -> bool:
        """
        Export scan history.
        
        Args:
            format_type: Export format ('csv', 'excel', 'json')
            filename: Optional filename
        
        Returns:
            True if successful, False otherwise
        """
        try:
            history_data = self.get_history()
            if not history_data:
                self.log_warning("No data to export")
                return False
            
            if format_type.lower() == 'csv':
                return export_csv(history_data, filename)
            elif format_type.lower() == 'excel':
                return export_excel(history_data, filename)
            elif format_type.lower() == 'json':
                return save_history(history_data, filename)
            else:
                self.log_error(f"Unsupported export format: {format_type}")
                return False
                
        except Exception as e:
            self.log_error(f"Error exporting history: {str(e)}", exc_info=True)
            return False
    
    def get_recent_scans(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent scans.
        
        Args:
            count: Number of recent scans to return
        
        Returns:
            List of recent scan records
        """
        return list(self.scan_history)[-count:]
    
    def duplicate_last_scan(self) -> bool:
        """
        Duplicate the last scan (useful for testing).
        
        Returns:
            True if successful, False otherwise
        """
        if self.last_scan:
            return self.process_scan(
                self.last_scan['data'],
                self.last_scan['barcode_type'],
                'duplicate'
            )
        return False
    
    def validate_and_process(self, data: str, barcode_type: str) -> bool:
        """
        Validate and process scan data with enhanced validation.
        
        Args:
            data: Scan data
            barcode_type: Barcode type
        
        Returns:
            True if valid and processed, False otherwise
        """
        # Enhanced validation
        if not data or not data.strip():
            self.log_warning("Empty scan data")
            return False
        
        if len(data) > 10000:  # Reasonable limit
            self.log_warning("Scan data too long")
            return False
        
        # Process the scan
        return self.process_scan(data.strip(), barcode_type) 