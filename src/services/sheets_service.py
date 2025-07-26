"""
Google Sheets service for business logic operations.
"""

import os
import pickle
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..utils.logger import LoggerMixin, get_logger
from ..utils.exceptions import SheetsError, AuthenticationError, NetworkError
from ..config.paths import get_credentials_path, get_token_path
from ..config.settings import DEFAULT_MASTER_LIST_SHEET_NAME

logger = get_logger(__name__)


@dataclass
class SheetConfig:
    """Configuration for Google Sheets operations."""
    spreadsheet_id: str
    sheet_name: str
    master_list_sheet: str = DEFAULT_MASTER_LIST_SHEET_NAME
    master_list_spreadsheet_id: Optional[str] = None
    master_list_sheet_name: Optional[str] = None
    credentials_file: Optional[str] = None
    token_file: Optional[str] = None


@dataclass
class ScanData:
    """Data structure for scan information."""
    data: str
    barcode_type: str
    formatted_name: str
    first_name: str
    last_name: str
    status: str = "Present"


class GoogleSheetsService(LoggerMixin):
    """
    Service class for Google Sheets business logic operations.
    
    This service handles all Google Sheets related operations including:
    - Authentication and connection management
    - Data operations (read, write, update)
    - Master list management
    - Error handling and retry logic
    """
    
    def __init__(self, config: SheetConfig):
        """
        Initialize the Google Sheets service.
        
        Args:
            config: Sheet configuration
        """
        super().__init__()
        self.config = config
        self.sheets_service = None
        self.master_list_data = []
        self.master_list_headers = []
        self.status_callback = None
        
        # Set default file paths if not provided
        if not self.config.credentials_file:
            self.config.credentials_file = get_credentials_path()
        if not self.config.token_file:
            self.config.token_file = get_token_path()
        
        self.log_info("Google Sheets service initialized")
    
    def set_status_callback(self, callback):
        """Set callback for status updates."""
        self.status_callback = callback
        self._update_status('error', 'Not connected to Google Sheets')
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            creds = self._get_credentials()
            if not creds:
                raise AuthenticationError("No valid credentials available")
            
            # Build the service
            self.sheets_service = build('sheets', 'v4', credentials=creds)
            self.log_info("Google Sheets authentication successful")
            return True
            
        except Exception as e:
            self.log_error(f"Authentication failed: {str(e)}")
            self._update_status('error', f'Authentication failed: {str(e)}')
            return False
    
    def connect(self) -> bool:
        """
        Connect to the specified spreadsheet.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.sheets_service:
                if not self.authenticate():
                    return False
            
            # Test the connection by getting spreadsheet info
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=self.config.spreadsheet_id
            ).execute()
            
            spreadsheet_title = spreadsheet.get('properties', {}).get('title', 'Unknown')
            self.log_info(f"Connected to spreadsheet: {spreadsheet_title}")
            
            # Create sheets if they don't exist
            self._create_sheet_if_needed()
            
            # Ensure headers are set up
            self._ensure_scan_sheet_headers()
            
            self._update_status('success', f'Connected to {spreadsheet_title}')
            return True
            
        except Exception as e:
            self.log_error(f"Connection failed: {str(e)}")
            self._update_status('error', f'Connection failed: {str(e)}')
            return False
    
    def add_scan_data(self, scan_data: ScanData) -> bool:
        """
        Add or update scan data in Google Sheets.
        If a row with the same ID exists, it will be updated.
        If no matching row exists, a new row will be appended.
        
        Args:
            scan_data: ScanData object containing the scan information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.sheets_service:
                raise SheetsError("Not connected to Google Sheets")
            
            # Only add to sheets if user is found (status is "Present")
            if scan_data.status != "Present":
                self.log_warning(f"User not found in master list - not adding to sheets: {scan_data.data}")
                return False
            
            # Get current date and time
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%I:%M:%S %p")
            
            # Prepare the data: [ID Number, Date, Time In, Name, Status]
            values = [[
                scan_data.data,
                date_str,
                time_str,
                scan_data.status
            ]]
            
            # First, try to find an existing row with the same ID
            existing_row = self._find_row_by_id(scan_data.data)
            
            if existing_row is not None:
                # TEMPORARILY DISABLED: Skip updating existing rows to test
                self.log_info(f"Found existing row for ID: {scan_data.data} - skipping update to preserve formulas")
                return True
            else:
                # Append new row if no existing row found
                body = {'values': values}
                
                result = self.sheets_service.spreadsheets().values().append(
                    spreadsheetId=self.config.spreadsheet_id,
                    range=f"{self.config.sheet_name}!A:D",
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                
                self.log_info(f"Added new row for ID: {scan_data.data}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error adding/updating scan data: {str(e)}")
            return False
    
    def load_master_list(self) -> int:
        """
        Load master list data from Google Sheets.
        
        Returns:
            Number of records loaded
        """
        try:
            if not self.sheets_service:
                raise SheetsError("Not connected to Google Sheets")
            
            # Use Master List specific configuration if available, otherwise use main config
            master_spreadsheet_id = self.config.master_list_spreadsheet_id or self.config.spreadsheet_id
            master_sheet_name = self.config.master_list_sheet_name or self.config.master_list_sheet
            
            # Get all data from MasterList sheet
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=master_spreadsheet_id,
                range=f"{master_sheet_name}!A:Z"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                self.log_warning("No data found in MasterList sheet")
                return 0
            
            # Store headers and data
            self.master_list_headers = values[0] if values else []
            self.master_list_data = values[1:] if len(values) > 1 else []
            
            count = len(self.master_list_data)
            self.log_info(f"Loaded {count} records from master list (spreadsheet: {master_spreadsheet_id}, sheet: {master_sheet_name})")
            
            return count
            
        except Exception as e:
            self.log_error(f"Error loading master list: {str(e)}")
            return 0
    
    def lookup_volunteer(self, volunteer_id: str) -> Optional[Dict[str, str]]:
        """
        Look up volunteer information by volunteer ID.
        
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
            
            # Find column indices
            id_column_index = self._find_id_column_index()
            first_name_column_index, last_name_column_index, _ = self._find_name_column_indices()
            
            # Search for volunteer ID
            for row in self.master_list_data:
                if len(row) > id_column_index and str(row[id_column_index]).strip() == volunteer_id:
                    volunteer_info = {
                        'volunteer_id': volunteer_id,
                        'first_name': row[first_name_column_index] if len(row) > first_name_column_index else "",
                        'last_name': row[last_name_column_index] if len(row) > last_name_column_index else ""
                    }
                    self.log_info(f"Found volunteer: {volunteer_info['first_name']} {volunteer_info['last_name']}")
                    return volunteer_info
            
            self.log_warning(f"Volunteer ID '{volunteer_id}' not found in master list")
            return None
            
        except Exception as e:
            self.log_error(f"Error looking up volunteer: {str(e)}")
            return None
    
    def search_master_list(self, search_term: str) -> Optional[List[str]]:
        """
        Search the master list for a specific term.
        
        Args:
            search_term: Term to search for
            
        Returns:
            Matching row or None if not found
        """
        try:
            if not self.master_list_data:
                self.log_warning("Master list not loaded")
                return None
            
            search_term = search_term.lower()
            
            for row in self.master_list_data:
                for cell in row:
                    if search_term in str(cell).lower():
                        return row
            
            return None
            
        except Exception as e:
            self.log_error(f"Error searching master list: {str(e)}")
            return None
    
    def get_master_list_data(self) -> Tuple[List[str], List[List[str]]]:
        """
        Get master list data.
        
        Returns:
            Tuple of (headers, data)
        """
        return self.master_list_headers, self.master_list_data
    
    def is_connected(self) -> bool:
        """Check if connected to Google Sheets."""
        return self.sheets_service is not None
    
    def _get_credentials(self) -> Optional[Credentials]:
        """Get or refresh Google API credentials."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.config.token_file):
            try:
                with open(self.config.token_file, 'rb') as token:
                    creds = pickle.load(token)
                self.log_debug("Loaded existing token")
            except Exception as e:
                self.log_warning(f"Could not load existing token: {str(e)}")
        
        # If no valid credentials available, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.log_info("Refreshed expired token")
                except Exception as e:
                    self.log_error(f"Failed to refresh token: {str(e)}")
                    creds = None
            
            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config.credentials_file, 
                        ['https://www.googleapis.com/auth/spreadsheets']
                    )
                    creds = flow.run_local_server(port=0)
                    self.log_info("Generated new credentials")
                except Exception as e:
                    self.log_error(f"Failed to generate credentials: {str(e)}")
                    self._update_status('error', f'Failed to generate credentials: {str(e)}')
                    return None
            
            # Save the credentials for next run
            try:
                with open(self.config.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                self.log_debug("Saved credentials to token file")
            except Exception as e:
                self.log_warning(f"Could not save token: {str(e)}")
        
        return creds
    
    def _create_sheet_if_needed(self):
        """Create sheets if they don't exist."""
        try:
            # Get existing sheets
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=self.config.spreadsheet_id
            ).execute()
            
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            
            # Create scan sheet if needed
            if self.config.sheet_name not in existing_sheets:
                self._create_sheet(self.config.sheet_name)
            
            # Create master list sheet if needed
            if self.config.master_list_sheet not in existing_sheets:
                self._create_sheet(self.config.master_list_sheet)
                
        except Exception as e:
            self.log_error(f"Error creating sheets: {str(e)}")
    
    def _create_sheet(self, sheet_name: str):
        """Create a new sheet."""
        try:
            request = {
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=self.config.spreadsheet_id,
                body={'requests': [request]}
            ).execute()
            
            self.log_info(f"Created sheet: {sheet_name}")
            
        except Exception as e:
            self.log_error(f"Error creating sheet {sheet_name}: {str(e)}")
    
    def _setup_scan_sheet_headers(self):
        """Setup headers for the scan sheet."""
        try:
            headers = [['ID Number', 'Date', 'Time In', 'Status']]
            
            body = {'values': headers}
            
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.config.spreadsheet_id,
                range=f"{self.config.sheet_name}!A1:D1",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            self.log_info(f"Setup headers for sheet: {self.config.sheet_name}")
            
        except Exception as e:
            self.log_error(f"Error setting up sheet headers: {str(e)}")
    
    def _ensure_scan_sheet_headers(self):
        """Ensure the scan sheet has proper headers."""
        try:
            # Check if headers exist
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.config.spreadsheet_id,
                range=f"{self.config.sheet_name}!A1:D1"
            ).execute()
            
            values = result.get('values', [])
            
            # If no headers or wrong headers, set them up
            if not values or len(values[0]) < 4 or values[0][0] != 'ID Number':
                self._setup_scan_sheet_headers()
                self.log_info("Updated headers for existing scan sheet")
            
        except Exception as e:
            self.log_error(f"Error ensuring sheet headers: {str(e)}")
    
    def _find_id_column_index(self) -> int:
        """Find the ID column index from headers."""
        id_column_index = 0  # Default to first column
        
        if self.master_list_headers:
            headers = [str(h).lower().strip() for h in self.master_list_headers]
            
            for i, header in enumerate(headers):
                if any(id_keyword in header for id_keyword in ['id', 'volunteer', 'number', 'code']):
                    id_column_index = i
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
                elif 'last' in header_lower and 'name' in header_lower:
                    last_name_column_index = i
                elif 'name' in header_lower and ('first' not in header_lower and 'last' not in header_lower):
                    name_column_index = i
        
        return first_name_column_index, last_name_column_index, name_column_index
    
    def _find_row_by_id(self, volunteer_id: str) -> Optional[int]:
        """
        Find the row number (0-based index) of an existing record with the given ID.
        
        Args:
            volunteer_id: The volunteer ID to search for
            
        Returns:
            Row number (0-based) if found, None if not found
        """
        try:
            if not self.sheets_service:
                return None
            
            # Get all data from the scan sheet
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.config.spreadsheet_id,
                range=f"{self.config.sheet_name}!A:D"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return None
            
            # Skip header row, search in data rows
            for i, row in enumerate(values[1:], start=1):  # start=1 to skip header
                if len(row) > 0 and str(row[0]).strip() == str(volunteer_id).strip():
                    return i  # Return 0-based row index
            
            return None
            
        except Exception as e:
            self.log_error(f"Error finding row by ID: {str(e)}")
            return None
    
    def _update_status(self, status: str, message: str):
        """Update status via callback."""
        if self.status_callback:
            try:
                self.status_callback('sheets_status', {
                    'status': status,
                    'text': message
                })
            except Exception as e:
                self.log_error(f"Error updating status: {str(e)}")
    
    def close(self):
        """Close the service and clean up resources."""
        self.sheets_service = None
        self.master_list_data = []
        self.master_list_headers = []
        self.log_info("Google Sheets service closed") 