"""
Scan service for centralized scan processing logic.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

from ..utils.logger import LoggerMixin, get_logger
from ..utils.name_parser import extract_names_from_qr_data, clean_name
from ..utils.validation import validate_scan_data
from ..utils.exceptions import ScanError, ValidationError

logger = get_logger(__name__)


@dataclass
class ScanResult:
    """Data class for scan processing results."""
    success: bool
    data: str
    barcode_type: str
    timestamp: str
    formatted_name: str
    first_name: str
    last_name: str
    status: str
    volunteer_info: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None


class ScanService(LoggerMixin):
    """
    Centralized service for processing QR code scans.
    
    This service handles all scan-related operations including:
    - Data validation
    - Name extraction and formatting
    - Volunteer lookup integration
    - Scan result formatting
    """
    
    def __init__(self, volunteer_service=None):
        """
        Initialize the scan service.
        
        Args:
            volunteer_service: Optional volunteer service for lookup operations
        """
        super().__init__()
        self.volunteer_service = volunteer_service
        self.log_info("Scan service initialized")
    
    def process_scan(self, data: str, barcode_type: str, 
                    source: str = "camera") -> ScanResult:
        """
        Process a QR code scan and return structured results.
        
        Args:
            data: Raw scan data
            barcode_type: Type of barcode (QR, Code128, etc.)
            source: Source of the scan (camera, manual, etc.)
            
        Returns:
            ScanResult object with processed scan information
        """
        try:
            # Validate scan data
            if not validate_scan_data(data):
                raise ValidationError(f"Invalid scan data: {data}")
            
            # Get current timestamp
            timestamp = datetime.now().strftime("%I:%M:%S %p")
            
            # Process volunteer information
            volunteer_info, formatted_name, first_name, last_name = self._process_volunteer_data(data)
            
            # Create scan result
            result = ScanResult(
                success=True,
                data=data,
                barcode_type=barcode_type,
                timestamp=timestamp,
                formatted_name=formatted_name,
                first_name=first_name,
                last_name=last_name,
                status="Present",
                volunteer_info=volunteer_info
            )
            
            self.log_info(f"Processed scan: {data} -> {formatted_name}")
            return result
            
        except Exception as e:
            self.log_error(f"Error processing scan: {str(e)}")
            return ScanResult(
                success=False,
                data=data,
                barcode_type=barcode_type,
                timestamp=datetime.now().strftime("%I:%M:%S %p"),
                formatted_name=data,
                first_name="",
                last_name="",
                status="Error",
                error_message=str(e)
            )
    
    def _process_volunteer_data(self, data: str) -> Tuple[Optional[Dict[str, str]], str, str, str]:
        """
        Process volunteer data and extract name information.
        
        Args:
            data: Raw scan data
            
        Returns:
            Tuple of (volunteer_info, formatted_name, first_name, last_name)
        """
        # Try to lookup volunteer in master list first
        volunteer_info = None
        if self.volunteer_service:
            volunteer_info = self.volunteer_service.lookup_volunteer(data)
        
        if volunteer_info:
            # Use names from master list
            first_name = volunteer_info['first_name']
            last_name = volunteer_info['last_name']
            self.log_info(f"Found volunteer in master list: {first_name} {last_name}")
        else:
            # Check if QR data is already in "last name, first name" format
            if self._is_name_format(data):
                # QR data appears to be a name in "last, first" format, use it directly
                formatted_name = data.strip()
                first_name, last_name = self._parse_name_format(data)
                self.log_info(f"Using QR data directly as name: {formatted_name}")
            else:
                # Fallback to extracting names from QR data
                self.log_debug(f"QR data for name extraction: '{data}'")
                first_name, last_name = extract_names_from_qr_data(data)
                first_name = clean_name(first_name)
                last_name = clean_name(last_name)
                self.log_warning(f"Volunteer ID '{data}' not found in master list, using extracted names: {first_name} {last_name}")
        
        # Format name as "last name, first name"
        formatted_name = f"{last_name}, {first_name}" if last_name and first_name else f"{first_name}{last_name}"
        
        return volunteer_info, formatted_name, first_name, last_name
    
    def _is_name_format(self, data: str) -> bool:
        """
        Check if data appears to be in name format.
        
        Args:
            data: Data to check
            
        Returns:
            True if data appears to be a name
        """
        if not data or ',' not in data:
            return False
        
        # Check for common non-name patterns
        non_name_patterns = ['@', 'http', 'www', '.com', '.org', '.net', '.edu']
        return not any(pattern in data.lower() for pattern in non_name_patterns)
    
    def _parse_name_format(self, data: str) -> Tuple[str, str]:
        """
        Parse name from "last, first" format.
        
        Args:
            data: Name data in "last, first" format
            
        Returns:
            Tuple of (first_name, last_name)
        """
        parts = [part.strip() for part in data.split(',', 1)]
        if len(parts) >= 2:
            last_name = parts[0]
            first_name = parts[1].split()[0] if parts[1] else ""
            return first_name, last_name
        return data, ""
    
    def validate_scan_data(self, data: str) -> bool:
        """
        Validate scan data.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return validate_scan_data(data)
    
    def get_scan_summary(self, scan_result: ScanResult) -> Dict[str, Any]:
        """
        Get a summary of scan results for display.
        
        Args:
            scan_result: Scan result to summarize
            
        Returns:
            Dictionary with scan summary
        """
        return {
            'timestamp': scan_result.timestamp,
            'data': scan_result.data,
            'formatted_name': scan_result.formatted_name,
            'status': scan_result.status,
            'barcode_type': scan_result.barcode_type,
            'success': scan_result.success,
            'error_message': scan_result.error_message
        } 