"""
Volunteer service for handling volunteer data operations.
"""

from typing import Optional, Dict, List, Tuple
from datetime import datetime

from ..utils.logger import LoggerMixin, get_logger
from ..utils.name_parser import extract_names_from_qr_data, clean_name

logger = get_logger(__name__)


class VolunteerService(LoggerMixin):
    """Service for handling volunteer-related operations."""
    
    def __init__(self, sheets_manager):
        """
        Initialize the volunteer service.
        
        Args:
            sheets_manager: Google Sheets manager instance
        """
        super().__init__()
        self.sheets_manager = sheets_manager
        self.master_list_data: List[List[str]] = []
        self.master_list_headers: List[str] = []
    
    def load_master_list(self) -> int:
        """
        Load master list data from Google Sheets.
        
        Returns:
            Number of records loaded
        """
        try:
            count = self.sheets_manager.load_master_list()
            
            # Get the loaded data
            self.master_list_data = self.sheets_manager.get_master_list_data()
            if hasattr(self.sheets_manager, 'master_list_headers'):
                self.master_list_headers = self.sheets_manager.master_list_headers
            
            self.log_info(f"Loaded {count} volunteer records")
            return count
            
        except Exception as e:
            self.log_error(f"Error loading master list: {str(e)}")
            return 0
    
    def lookup_volunteer(self, volunteer_id: str) -> Optional[Dict[str, str]]:
        """
        Look up volunteer information by ID.
        
        Args:
            volunteer_id: The volunteer ID to search for
            
        Returns:
            Dictionary with volunteer information or None if not found
        """
        try:
            if not self.master_list_data:
                self.log_warning("Master list not loaded")
                return None
            
            volunteer_id = str(volunteer_id).strip()
            
            # Find the ID column index from headers
            id_column_index = self._find_id_column_index()
            first_name_column_index, last_name_column_index, name_column_index = self._find_name_column_indices()
            
            for row in self.master_list_data:
                # Check if the volunteer ID matches (case-insensitive)
                if (row and len(row) > id_column_index and 
                    str(row[id_column_index]).strip().lower() == volunteer_id.lower()):
                    
                    self.log_debug(f"Found matching row: {row}")
                    
                    # Extract names based on column structure
                    first_name, last_name = self._extract_names_from_row(
                        row, first_name_column_index, last_name_column_index, name_column_index
                    )
                    
                    volunteer_info = {
                        'volunteer_id': row[id_column_index] if len(row) > id_column_index else '',
                        'first_name': first_name,
                        'last_name': last_name,
                        'full_row': row
                    }
                    
                    self.log_info(f"Found volunteer: {first_name} {last_name} (ID: {volunteer_info['volunteer_id']})")
                    return volunteer_info
            
            self.log_warning(f"Volunteer ID '{volunteer_id}' not found in master list")
            return None
            
        except Exception as e:
            self.log_error(f"Error looking up volunteer: {str(e)}")
            return None
    
    def process_volunteer_scan(self, scan_data: str) -> Tuple[str, str, str]:
        """
        Process a volunteer scan and return formatted information.
        
        Args:
            scan_data: The scanned data (volunteer ID)
            
        Returns:
            Tuple of (formatted_name, first_name, last_name)
        """
        try:
            # Look up volunteer information from master list
            volunteer_info = self.lookup_volunteer(scan_data)
            
            if volunteer_info:
                # Use names from master list
                first_name = volunteer_info['first_name']
                last_name = volunteer_info['last_name']
                self.log_info(f"Found volunteer in master list: {first_name} {last_name}")
            else:
                # Fallback to extracting names from QR data if not found in master list
                self.log_debug(f"QR data for name extraction: '{scan_data}'")
                first_name, last_name = extract_names_from_qr_data(scan_data)
                first_name = clean_name(first_name)
                last_name = clean_name(last_name)
                self.log_warning(f"Volunteer ID '{scan_data}' not found in master list, using extracted names: {first_name} {last_name}")
            
            # Format name as "last name, first name"
            formatted_name = f"{last_name}, {first_name}" if last_name and first_name else f"{first_name}{last_name}"
            self.log_debug(f"Final formatted name: '{formatted_name}'")
            
            return formatted_name, first_name, last_name
            
        except Exception as e:
            self.log_error(f"Error processing volunteer scan: {str(e)}")
            return scan_data, scan_data, ""
    
    def _find_id_column_index(self) -> int:
        """Find the ID column index from headers."""
        id_column_index = 0  # Default to first column
        
        if self.master_list_headers:
            headers = [str(h).lower().strip() for h in self.master_list_headers]
            self.log_debug(f"Looking for ID column in headers: {self.master_list_headers}")
            
            for i, header in enumerate(headers):
                if any(id_keyword in header for id_keyword in ['id', 'volunteer', 'number', 'code']):
                    id_column_index = i
                    self.log_debug(f"Found ID column at index {i}: '{self.master_list_headers[i]}'")
                    break
        
        return id_column_index
    
    def _find_name_column_indices(self) -> Tuple[int, int, Optional[int]]:
        """Find the name column indices from headers."""
        first_name_column_index = 1  # Default to second column
        last_name_column_index = 2   # Default to third column
        name_column_index = None     # For combined name column
        
        if self.master_list_headers:
            for i, header in enumerate(self.master_list_headers):
                header_lower = header.lower()
                if 'first' in header_lower and 'name' in header_lower:
                    first_name_column_index = i
                    self.log_debug(f"Found First Name column at index {i}: '{self.master_list_headers[i]}'")
                elif 'last' in header_lower and 'name' in header_lower:
                    last_name_column_index = i
                    self.log_debug(f"Found Last Name column at index {i}: '{self.master_list_headers[i]}'")
                elif 'name' in header_lower and ('first' not in header_lower and 'last' not in header_lower):
                    name_column_index = i
                    self.log_debug(f"Found Name column at index {i}: '{self.master_list_headers[i]}'")
        
        return first_name_column_index, last_name_column_index, name_column_index
    
    def _extract_names_from_row(self, row: List[str], first_name_index: int, 
                               last_name_index: int, name_index: Optional[int]) -> Tuple[str, str]:
        """Extract names from a row based on column structure."""
        if name_index is not None and len(row) > name_index:
            # Single name column - check if it's "Last, First" format
            name_value = str(row[name_index]).strip()
            if ',' in name_value:
                name_parts = name_value.split(',')
                if len(name_parts) >= 2:
                    last_name = name_parts[0].strip()
                    first_name = name_parts[1].strip()
                else:
                    first_name = name_value
                    last_name = ''
            else:
                # Single name without comma - treat as first name
                first_name = name_value
                last_name = ''
        else:
            # Separate first and last name columns
            first_name = str(row[first_name_index]).strip() if len(row) > first_name_index else ''
            last_name = str(row[last_name_index]).strip() if len(row) > last_name_index else ''
        
        return first_name, last_name
    
    def get_master_list_data(self) -> List[List[str]]:
        """Get the loaded master list data."""
        return self.master_list_data.copy()
    
    def get_master_list_headers(self) -> List[str]:
        """Get the master list headers."""
        return self.master_list_headers.copy()
    
    def debug_master_list_structure(self) -> str:
        """Debug the master list structure and return a formatted string."""
        try:
            if not self.master_list_data:
                return "No master list data loaded"
            
            result = f"Master list has {len(self.master_list_data)} records\n"
            
            if self.master_list_headers:
                result += f"Headers: {self.master_list_headers}\n"
            
            result += f"First 3 rows:\n"
            
            for i, row in enumerate(self.master_list_data[:3]):
                result += f"Row {i+1}: {row}\n"
            
            return result
            
        except Exception as e:
            return f"Error debugging master list: {str(e)}" 