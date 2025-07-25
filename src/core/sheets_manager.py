"""
Google Sheets integration for QR Scanner.
"""

import os
import pickle
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..utils.logger import get_logger
from ..config.paths import get_credentials_path, get_token_path
from ..utils.name_parser import extract_names_from_qr_data, clean_name

logger = get_logger(__name__)


class GoogleSheetsManager:
    """Manages Google Sheets integration for storing scan data."""
    
    def __init__(self):
        self.sheets_service = None
        self.spreadsheet_id = None
        self.sheet_name = "QR_Scans"
        self.master_list_sheet = "MasterList"
        self.master_list_data = []
        self.credentials_file = None
        self.token_file = None
        self.status_callback = None
        
    def set_status_callback(self, callback):
        """Set callback for status updates."""
        self.status_callback = callback
        # Send initial status
        if self.status_callback:
            self.status_callback('sheets_status', {
                'status': 'error',
                'text': 'Not connected to Google Sheets'
            })
        
    def setup_credentials(self, credentials_path):
        """Setup Google Sheets API credentials."""
        try:
            self.credentials_file = credentials_path
            self.token_file = get_token_path()
            
            # Test the credentials
            if self._get_credentials():
                logger.info("Credentials setup successful")
                # Send status update
                if self.status_callback:
                    self.status_callback('credentials_status', {
                        'status': 'success',
                        'message': 'Credentials configured successfully'
                    })
                return True
            else:
                logger.error("Failed to setup credentials")
                # Send status update
                if self.status_callback:
                    self.status_callback('credentials_status', {
                        'status': 'error',
                        'message': 'Failed to setup credentials'
                    })
                return False
                
        except Exception as e:
            logger.error(f"Error setting up credentials: {str(e)}")
            return False
    
    def _get_credentials(self):
        """Get or refresh Google API credentials."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                logger.debug("Loaded existing token")
            except Exception as e:
                logger.warning(f"Could not load existing token: {str(e)}")
        
        # If no valid credentials available, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Refreshed expired token")
                except Exception as e:
                    logger.error(f"Failed to refresh token: {str(e)}")
                    creds = None
            
            if not creds:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, 
                        ['https://www.googleapis.com/auth/spreadsheets']
                    )
                    creds = flow.run_local_server(port=0)
                    logger.info("Generated new credentials")
                except Exception as e:
                    logger.error(f"Failed to generate credentials: {str(e)}")
                    # Send status update
                    if self.status_callback:
                        self.status_callback('credentials_status', {
                            'status': 'error',
                            'message': f'Failed to generate credentials: {str(e)}'
                        })
                    return None
            
            # Save the credentials for next run
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                logger.debug("Saved credentials to token file")
            except Exception as e:
                logger.warning(f"Could not save token: {str(e)}")
        
        return creds
    
    def connect_to_spreadsheet(self, spreadsheet_id, sheet_name):
        """Connect to a specific Google Spreadsheet."""
        try:
            creds = self._get_credentials()
            if not creds:
                raise Exception("No valid credentials available")
            
            # Build the service
            self.sheets_service = build('sheets', 'v4', credentials=creds)
            self.spreadsheet_id = spreadsheet_id
            self.sheet_name = sheet_name
            
            # Test the connection by getting spreadsheet info
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            spreadsheet_title = spreadsheet.get('properties', {}).get('title', 'Unknown')
            logger.info(f"Connected to spreadsheet: {spreadsheet_title}")
            
            # Create sheets if they don't exist
            self._create_sheet_if_needed()
            
            # Ensure headers are set up
            self._ensure_scan_sheet_headers()
            
            # Send status update
            if self.status_callback:
                self.status_callback('sheets_status', {
                    'status': 'success',
                    'text': f'Connected to {spreadsheet_title}'
                })
            
            return spreadsheet_title
            
        except Exception as e:
            logger.error(f"Error connecting to spreadsheet: {str(e)}")
            raise
    
    def _create_sheet_if_needed(self):
        """Create the required sheets if they don't exist."""
        try:
            # Get existing sheets
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            existing_sheets = [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            
            # Create QR_Scans sheet if it doesn't exist
            if self.sheet_name not in existing_sheets:
                self._create_sheet(self.sheet_name)
                self._setup_scan_sheet_headers()
                logger.info(f"Created sheet: {self.sheet_name}")
            
            # Create MasterList sheet if it doesn't exist
            if self.master_list_sheet not in existing_sheets:
                self._create_sheet(self.master_list_sheet)
                logger.info(f"Created sheet: {self.master_list_sheet}")
                
        except Exception as e:
            logger.error(f"Error creating sheets: {str(e)}")
    
    def _create_sheet(self, sheet_name):
        """Create a new sheet in the spreadsheet."""
        try:
            request = {
                'addSheet': {
                    'properties': {
                        'title': sheet_name
                    }
                }
            }
            
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': [request]}
            ).execute()
            
        except Exception as e:
            logger.error(f"Error creating sheet {sheet_name}: {str(e)}")
            raise
    
    def _setup_scan_sheet_headers(self):
        """Setup headers for the scan sheet."""
        try:
            # Set up headers: ID Number, Date, Time In, Name, Status
            headers = [['ID Number', 'Date', 'Time In', 'Name', 'Status']]
            
            body = {
                'values': headers
            }
            
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A1:E1",
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"Setup headers for sheet: {self.sheet_name}")
            
        except Exception as e:
            logger.error(f"Error setting up sheet headers: {str(e)}")
    
    def _ensure_scan_sheet_headers(self):
        """Ensure the scan sheet has proper headers."""
        try:
            # Check if headers exist
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A1:E1"
            ).execute()
            
            values = result.get('values', [])
            
            # If no headers or wrong headers, set them up
            if not values or len(values[0]) < 5 or values[0][0] != 'ID Number':
                self._setup_scan_sheet_headers()
                logger.info("Updated headers for existing scan sheet")
            
        except Exception as e:
            logger.error(f"Error ensuring sheet headers: {str(e)}")
    
    def is_connected(self):
        """Check if connected to Google Sheets."""
        return self.sheets_service is not None and self.spreadsheet_id is not None
    
    def add_scan_data(self, data, barcode_type):
        """Add scan data to the Google Sheet."""
        if not self.is_connected():
            logger.warning("Not connected to Google Sheets")
            return False
        
        try:
            # Get current date and time
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%I:%M:%S %p")  # 12-hour format with AM/PM
            
            # Look up volunteer information from master list
            volunteer_info = self.lookup_volunteer_by_id(data)
            
            if volunteer_info:
                # Use names from master list
                first_name = volunteer_info['first_name']
                last_name = volunteer_info['last_name']
                logger.info(f"Found volunteer in master list: {first_name} {last_name}")
                # Format name as "last name, first name"
                formatted_name = f"{last_name}, {first_name}" if last_name and first_name else f"{first_name}{last_name}"
            else:
                # Check if QR data is already in "last name, first name" format
                if ',' in data and not any(char in data for char in ['@', 'http', 'www', '.com', '.org']):
                    # QR data appears to be a name in "last, first" format, use it directly
                    formatted_name = data.strip()
                    logger.info(f"Using QR data directly as name: {formatted_name}")
                else:
                    # Fallback to extracting names from QR data if not found in master list
                    logger.debug(f"QR data for name extraction: '{data}'")
                    first_name, last_name = extract_names_from_qr_data(data)
                    first_name = clean_name(first_name)
                    last_name = clean_name(last_name)
                    logger.warning(f"Volunteer ID '{data}' not found in master list, using extracted names: {first_name} {last_name}")
                    logger.debug(f"Extracted first_name: '{first_name}', last_name: '{last_name}'")
                    # Format name as "last name, first name"
                    formatted_name = f"{last_name}, {first_name}" if last_name and first_name else f"{first_name}{last_name}"
            
            logger.debug(f"Final formatted name: '{formatted_name}'")
            
            # Set status (you can customize this based on your needs)
            status = "Present"
            
            # Prepare the data: [ID Number, Date, Time In, Name, Status]
            values = [[data, date_str, time_str, formatted_name, status]]
            
            # Append to the sheet
            body = {
                'values': values
            }
            
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A:E",
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"Added scan data to sheets: {data} (Name: {first_name} {last_name})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding scan data: {str(e)}")
            return False
    
    def load_master_list(self):
        """Load master list data from Google Sheets."""
        if not self.is_connected():
            logger.warning("Not connected to Google Sheets")
            return 0
        
        try:
            # Get all data from MasterList sheet
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.master_list_sheet}!A:Z"
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning("No data found in MasterList sheet")
                return 0
            
            # Store headers and data
            self.master_list_headers = values[0] if values else []
            self.master_list_data = values[1:] if len(values) > 1 else []
            
            count = len(self.master_list_data)
            logger.info(f"Loaded {count} records from master list")
            
            # Debug: Log the headers and first few rows to understand the structure
            if count > 0:
                logger.debug(f"Master list headers: {self.master_list_headers}")
                for i, row in enumerate(self.master_list_data[:3]):  # Log first 3 rows
                    logger.debug(f"Master list row {i+1}: {row}")
            
            return count
            
        except Exception as e:
            logger.error(f"Error loading master list: {str(e)}")
            return 0
    
    def search_master_list(self, search_term):
        """Search the master list for a specific term."""
        if not self.master_list_data:
            logger.warning("Master list not loaded")
            return None
        
        search_term = search_term.lower()
        
        for row in self.master_list_data:
            for cell in row:
                if search_term in str(cell).lower():
                    return row
        
        return None
    
    def lookup_volunteer_by_id(self, volunteer_id):
        """
        Look up volunteer information by volunteer ID.
        
        Args:
            volunteer_id: The volunteer ID to search for
            
        Returns:
            Dictionary with volunteer information or None if not found
        """
        if not self.master_list_data:
            logger.warning("Master list not loaded")
            return None
        
        volunteer_id = str(volunteer_id).strip()
        
        # Find the ID column index from headers
        id_column_index = 0  # Default to first column
        first_name_column_index = 1  # Default to second column
        last_name_column_index = 2   # Default to third column
        name_column_index = None     # For combined name column
        
        if hasattr(self, 'master_list_headers') and self.master_list_headers:
            headers = [str(h).lower().strip() for h in self.master_list_headers]
            logger.debug(f"Looking for columns in headers: {self.master_list_headers}")
            
            # Find ID column
            for i, header in enumerate(headers):
                if any(id_keyword in header for id_keyword in ['id', 'volunteer', 'number', 'code']):
                    id_column_index = i
                    logger.debug(f"Found ID column at index {i}: '{self.master_list_headers[i]}'")
                    break
            
            # Find name columns
            for i, header in enumerate(headers):
                header_lower = header.lower()
                if 'first' in header_lower and 'name' in header_lower:
                    first_name_column_index = i
                    logger.debug(f"Found First Name column at index {i}: '{self.master_list_headers[i]}'")
                elif 'last' in header_lower and 'name' in header_lower:
                    last_name_column_index = i
                    logger.debug(f"Found Last Name column at index {i}: '{self.master_list_headers[i]}'")
                elif 'name' in header_lower and ('first' not in header_lower and 'last' not in header_lower):
                    name_column_index = i
                    logger.debug(f"Found Name column at index {i}: '{self.master_list_headers[i]}'")
        
        for row in self.master_list_data:
            # Check if the volunteer ID matches (case-insensitive)
            if row and len(row) > id_column_index and str(row[id_column_index]).strip().lower() == volunteer_id.lower():
                logger.debug(f"Found matching row: {row}")
                
                # Extract names based on column structure
                if name_column_index is not None and len(row) > name_column_index:
                    # Single name column - check if it's "Last, First" format
                    name_value = str(row[name_column_index]).strip()
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
                    first_name = str(row[first_name_column_index]).strip() if len(row) > first_name_column_index else ''
                    last_name = str(row[last_name_column_index]).strip() if len(row) > last_name_column_index else ''
                
                volunteer_info = {
                    'volunteer_id': row[id_column_index] if len(row) > id_column_index else '',
                    'first_name': first_name,
                    'last_name': last_name,
                    'full_row': row
                }
                logger.info(f"Found volunteer: {volunteer_info['first_name']} {volunteer_info['last_name']} (ID: {volunteer_info['volunteer_id']})")
                return volunteer_info
        
        logger.warning(f"Volunteer ID '{volunteer_id}' not found in master list")
        return None
    
    def get_master_list_data(self):
        """Get the loaded master list data."""
        return self.master_list_data
    
    def close(self):
        """Close the Google Sheets connection."""
        try:
            if self.sheets_service:
                # Google Sheets API doesn't require explicit closing
                # Just clear the service reference
                self.sheets_service = None
                self.spreadsheet_id = None
                logger.info("Google Sheets connection closed")
        except Exception as e:
            logger.error(f"Error closing Google Sheets connection: {str(e)}") 