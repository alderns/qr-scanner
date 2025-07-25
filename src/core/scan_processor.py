import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from collections import deque

from ..utils.logger import LoggerMixin, get_logger
from ..utils.file_utils import FileManager
from ..utils.validation import validate_scan_data
from ..utils.scanner_utils import copy_to_clipboard
from ..config.settings import MAX_HISTORY_ITEMS, AUTO_SAVE_INTERVAL

logger = get_logger(__name__)

class ScanProcessor(LoggerMixin):
    def __init__(self):
        super().__init__()
        
        self.scan_history: deque = deque(maxlen=MAX_HISTORY_ITEMS)
        self.last_scan: Optional[Dict[str, Any]] = None
        
        self.is_processing = False
        self.processing_lock = threading.Lock()
        
        self.on_scan_callback: Optional[Callable] = None
        self.on_error_callback: Optional[Callable] = None
        
        self.last_save_time = time.time()
        self.auto_save_enabled = True
        
        # Initialize file manager
        self.file_manager = FileManager()
        
        self._load_existing_history()
        
        self.log_info("Scan processor initialized")
    
    def set_callbacks(self, on_scan: Optional[Callable] = None, 
                     on_error: Optional[Callable] = None):
        self.on_scan_callback = on_scan
        self.on_error_callback = on_error
    
    def process_scan(self, data: str, barcode_type: str, 
                    source: str = "camera") -> bool:
        try:
            with self.processing_lock:
                if self.is_processing:
                    self.log_warning("Already processing a scan, skipping")
                    return False
                
                self.is_processing = True
            
            if not validate_scan_data(data):
                self.log_warning(f"Invalid scan data: {data}")
                if self.on_error_callback:
                    self.on_error_callback(f"Invalid scan data: {data}")
                return False
            
            scan_record = {
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'barcode_type': barcode_type,
                'source': source
            }
            
            self._process_scan_data(scan_record)
            
            if self.auto_save_enabled:
                self.auto_save()
            
            return True
            
        except Exception as e:
            self.log_error(f"Error processing scan: {str(e)}")
            if self.on_error_callback:
                self.on_error_callback(f"Processing error: {str(e)}")
            return False
        finally:
            with self.processing_lock:
                self.is_processing = False
    
    def _process_scan_data(self, scan_record: Dict[str, Any]):
        self.scan_history.append(scan_record)
        self.last_scan = scan_record
        
        self.log_info(f"Processed scan: {scan_record['data']}")
        
        if self.on_scan_callback:
            self.on_scan_callback(scan_record)
    
    def get_history(self) -> List[Dict[str, Any]]:
        return list(self.scan_history)
    
    def get_last_scan(self) -> Optional[Dict[str, Any]]:
        return self.last_scan
    
    def get_last_scan_data(self) -> Optional[str]:
        if self.last_scan:
            return self.last_scan.get('data')
        return None
    
    def clear_history(self):
        self.scan_history.clear()
        self.last_scan = None
        self.log_info("Scan history cleared")
    
    def get_history_count(self) -> int:
        return len(self.scan_history)
    
    def search_history(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        results = []
        
        for scan in self.scan_history:
            if (query_lower in scan['data'].lower() or 
                query_lower in scan['barcode_type'].lower() or
                query_lower in scan['source'].lower()):
                results.append(scan)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        if not self.scan_history:
            return {
                'total_scans': 0,
                'barcode_types': {},
                'sources': {},
                'first_scan': None,
                'last_scan': None
            }
        
        barcode_types = {}
        sources = {}
        
        for scan in self.scan_history:
            barcode_type = scan['barcode_type']
            source = scan['source']
            
            barcode_types[barcode_type] = barcode_types.get(barcode_type, 0) + 1
            sources[source] = sources.get(source, 0) + 1
        
        return {
            'total_scans': len(self.scan_history),
            'barcode_types': barcode_types,
            'sources': sources,
            'first_scan': self.scan_history[0]['timestamp'] if self.scan_history else None,
            'last_scan': self.scan_history[-1]['timestamp'] if self.scan_history else None
        }
    
    def auto_save(self):
        current_time = time.time()
        if current_time - self.last_save_time >= AUTO_SAVE_INTERVAL:
            self.save_all_data()
            self.last_save_time = current_time
    
    def save_all_data(self) -> bool:
        try:
            history_data = list(self.scan_history)
            self.file_manager.save_scan_history(history_data)
            self.log_info(f"Saved {len(history_data)} scan records")
            return True
        except Exception as e:
            self.log_error(f"Error saving scan data: {str(e)}")
            return False
    
    def _load_existing_history(self):
        try:
            history_data = self.file_manager.load_scan_history()
            if history_data:
                self.scan_history.extend(history_data)
                self.log_info(f"Loaded {len(history_data)} scan records")
        except Exception as e:
            self.log_error(f"Error loading scan history: {str(e)}")
    
    def export_history(self, format_type: str = 'csv', 
                      filename: str = None) -> bool:
        try:
            history_data = list(self.scan_history)
            
            if format_type.lower() == 'csv':
                return self.file_manager.export_to_csv(history_data, filename)
            elif format_type.lower() == 'excel':
                return self.file_manager.export_to_excel(history_data, filename)
            else:
                self.log_error(f"Unsupported export format: {format_type}")
                return False
                
        except Exception as e:
            self.log_error(f"Error exporting history: {str(e)}")
            return False
    
    def get_recent_scans(self, count: int = 10) -> List[Dict[str, Any]]:
        return list(self.scan_history)[-count:]
    
    def duplicate_last_scan(self) -> bool:
        if not self.last_scan:
            self.log_warning("No previous scan to duplicate")
            return False
        
        return self.process_scan(
            self.last_scan['data'],
            self.last_scan['barcode_type'],
            'manual'
        )
    
 