"""
Main application manager for the QR Scanner.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import threading
from typing import Optional, Callable, Any
from pathlib import Path

from ..utils.logger import LoggerMixin, get_logger, setup_logger
from ..config.paths import ensure_directories
from ..config.settings import *
from .camera_manager import CameraManager
from .sheets_manager import GoogleSheetsManager
from .scan_processor import ScanProcessor

logger = get_logger(__name__)

class QRScannerApp(LoggerMixin):
    """
    Main application class that coordinates all components.
    
    This class manages the application lifecycle, component initialization,
    and provides a clean interface for the GUI to interact with core functionality.
    """
    
    def __init__(self):
        """Initialize the QR Scanner application."""
        super().__init__()
        
        # Ensure directories exist
        ensure_directories()
        
        # Setup logging
        setup_logger()
        
        # Core components
        self.root: Optional[tk.Tk] = None
        self.camera_manager: Optional[CameraManager] = None
        self.sheets_manager: Optional[GoogleSheetsManager] = None
        self.scan_processor: Optional[ScanProcessor] = None
        
        # Application state
        self.is_initialized = False
        self.is_running = False
        self.auto_save_enabled = True
        
        # Callbacks
        self.gui_callback: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
        self.log_info("QR Scanner App initialized")
    
    def initialize(self, root: tk.Tk, gui_callback: Optional[Callable] = None,
                   status_callback: Optional[Callable] = None) -> bool:
        """
        Initialize the application with GUI components.
        
        Args:
            root: Tkinter root window
            gui_callback: Callback for GUI updates
            status_callback: Callback for status updates
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.root = root
            self.gui_callback = gui_callback
            self.status_callback = status_callback
            
            # Check dependencies
            if not self._check_dependencies():
                return False
            
            # Initialize core components
            self._initialize_components()
            
            # Setup auto-save
            if self.auto_save_enabled:
                self._setup_auto_save()
            
            # Setup cleanup on exit
            self._setup_cleanup()
            
            self.is_initialized = True
            self.log_info("Application initialized successfully")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to initialize application: {str(e)}", exc_info=True)
            return False
    
    def _check_dependencies(self) -> bool:
        """
        Check if all required packages are available.
        
        Returns:
            True if all dependencies are available, False otherwise
        """
        required_packages = [
            'cv2',
            'pyzbar', 
            'PIL',
            'google.oauth2.credentials',
            'google_auth_oauthlib.flow',
            'google.auth.transport.requests',
            'googleapiclient.discovery'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            error_msg = f"Missing required packages: {', '.join(missing_packages)}\n\n"
            error_msg += "Please install required packages:\n"
            error_msg += "pip install opencv-python pyzbar pillow google-api-python-client "
            error_msg += "google-auth-httplib2 google-auth-oauthlib"
            
            self.log_error(error_msg)
            if self.root:
                messagebox.showerror("Dependency Error", error_msg)
            return False
        
        self.log_info("All dependencies available")
        return True
    
    def _initialize_components(self):
        """Initialize all core components."""
        # Initialize scan processor first
        self.scan_processor = ScanProcessor()
        
        # Initialize Google Sheets manager
        self.sheets_manager = GoogleSheetsManager()
        self.sheets_manager.set_status_callback(self.gui_callback)
        
        # Initialize camera manager with callbacks
        self.camera_manager = CameraManager(
            scan_callback=self._camera_callback
        )
        
        # Auto-setup credentials if available
        self._auto_setup_credentials()
        
        self.log_info("Core components initialized")
    
    def _auto_setup_credentials(self):
        """Automatically setup Google Sheets credentials if available."""
        try:
            from ..config.paths import get_credentials_path
            import os
            
            credentials_path = get_credentials_path()
            
            if os.path.exists(credentials_path):
                self.log_info("Found credentials.json, setting up automatically")
                if self.sheets_manager.setup_credentials(str(credentials_path)):
                    self.log_info("Credentials setup successful")
                    if self.status_callback:
                        self.status_callback("Google Sheets credentials configured")
                    if self.gui_callback:
                        self.root.after(0, self.gui_callback, 'credentials_status', 
                                      {'status': 'success', 'message': 'Credentials configured'})
                else:
                    self.log_warning("Failed to setup credentials automatically")
                    if self.status_callback:
                        self.status_callback("Failed to setup Google Sheets credentials")
                    if self.gui_callback:
                        self.root.after(0, self.gui_callback, 'credentials_status', 
                                      {'status': 'error', 'message': 'Failed to setup credentials'})
            else:
                self.log_info("No credentials.json found, manual setup required")
                if self.status_callback:
                    self.status_callback("Please setup Google Sheets credentials")
                if self.gui_callback:
                    self.root.after(0, self.gui_callback, 'credentials_status', 
                                  {'status': 'error', 'message': 'No credentials.json found'})
                    
        except Exception as e:
            self.log_error(f"Error in auto credentials setup: {str(e)}")
            if self.status_callback:
                self.status_callback("Error setting up credentials")
            if self.gui_callback:
                self.root.after(0, self.gui_callback, 'credentials_status', 
                              {'status': 'error', 'message': f'Error: {str(e)}'})
    
    def _handle_scan_actions(self, data: str):
        """Handle scan actions like clipboard copy and typing simulation."""
        try:
            # Copy to clipboard
            if self.copy_to_clipboard(data):
                self.log_info("Data copied to clipboard")
                
        except Exception as e:
            self.log_error(f"Error handling scan actions: {str(e)}")
    
    def _setup_auto_save(self):
        """Setup automatic saving of scan history."""
        def auto_save():
            if self.is_running and self.scan_processor:
                self.scan_processor.auto_save()
                # Schedule next auto-save
                if self.root and self.is_running:
                    self.root.after(AUTO_SAVE_INTERVAL * 1000, auto_save)
        
        if self.root:
            self.root.after(AUTO_SAVE_INTERVAL * 1000, auto_save)
    
    def _setup_cleanup(self):
        """Setup cleanup procedures for application exit."""
        if self.root:
            self.root.protocol("WM_DELETE_WINDOW", self.shutdown)
    
    def start(self) -> bool:
        """
        Start the application.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            if not self.is_initialized:
                self.log_error("Application not initialized")
                return False
            
            self.is_running = True
            self.log_info("Application started")
            
            # Update status
            if self.status_callback:
                self.status_callback("Application started")
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to start application: {str(e)}", exc_info=True)
            return False
    
    def shutdown(self):
        """Shutdown the application gracefully."""
        try:
            self.log_info("Shutting down application...")
            
            # Stop camera
            if self.camera_manager:
                self.camera_manager.stop_camera()
            
            # Save final data
            if self.scan_processor:
                self.scan_processor.save_all_data()
            
            # Close Google Sheets connection
            if self.sheets_manager:
                self.sheets_manager.close()
            
            self.is_running = False
            
            # Destroy root window
            if self.root:
                self.root.destroy()
            
            self.log_info("Application shutdown complete")
            
        except Exception as e:
            self.log_error(f"Error during shutdown: {str(e)}", exc_info=True)
    
    def _camera_callback(self, data: str, barcode_type: str, photo=None):
        """
        Callback for camera events.
        
        Args:
            data: Scanned data
            barcode_type: Type of barcode
            photo: Optional photo data
        """
        try:
            # Process scan data
            if data and barcode_type:
                if self.scan_processor:
                    self.scan_processor.process_scan(data, barcode_type)
                
                # Handle clipboard copy and typing simulation
                self._handle_scan_actions(data)
                
                # Update GUI (thread-safe)
                if self.root and self.gui_callback:
                    self.root.after(0, self.gui_callback, 'scan', {'content': data, 'type': barcode_type})
            
            # Update video frame
            elif photo:
                if self.root and self.gui_callback:
                    self.root.after(0, self.gui_callback, 'video_frame', photo)
                    
        except Exception as e:
            self.log_error(f"Error in camera callback: {str(e)}", exc_info=True)
    
    def _camera_error_callback(self, error: str):
        """
        Callback for camera errors.
        
        Args:
            error: Error message
        """
        self.log_error(f"Camera error: {error}")
        if self.status_callback:
            self.status_callback(f"Camera error: {error}")
    
    # Public API methods
    def get_scan_history(self) -> list:
        """Get the current scan history."""
        if self.scan_processor:
            return self.scan_processor.get_history()
        return []
    
    def clear_history(self):
        """Clear the scan history."""
        if self.scan_processor:
            self.scan_processor.clear_history()
            self.log_info("Scan history cleared")
    
    def export_history(self, format_type: str = 'csv', filename: str = None) -> bool:
        """
        Export scan history.
        
        Args:
            format_type: Export format ('csv', 'excel', 'json')
            filename: Optional filename
        
        Returns:
            True if successful, False otherwise
        """
        if self.scan_processor:
            return self.scan_processor.export_history(format_type, filename)
        return False
    
    def get_camera_manager(self) -> Optional[CameraManager]:
        """Get the camera manager instance."""
        return self.camera_manager
    
    def get_sheets_manager(self) -> Optional[GoogleSheetsManager]:
        """Get the Google Sheets manager instance."""
        return self.sheets_manager
    
    def get_scan_processor(self) -> Optional[ScanProcessor]:
        """Get the scan processor instance."""
        return self.scan_processor
    
    def update_status(self, message: str):
        """Update application status."""
        self.log_info(message)
        if self.status_callback:
            self.status_callback(message)
    
    def is_scanning(self) -> bool:
        """Check if camera is currently scanning."""
        if self.camera_manager:
            return self.camera_manager.is_scanning()
        return False
    
    def start_camera(self) -> bool:
        """Start the camera."""
        if self.camera_manager:
            return self.camera_manager.start_camera()
        return False
    
    def stop_camera(self):
        """Stop the camera."""
        if self.camera_manager:
            self.camera_manager.stop_camera()
    
    def get_last_scan(self) -> Optional[str]:
        """Get the last scanned data."""
        if self.scan_processor:
            return self.scan_processor.get_last_scan_data()
        return None
    
    def setup_credentials(self, credentials_path: str) -> bool:
        """Setup Google Sheets credentials."""
        try:
            if self.sheets_manager:
                return self.sheets_manager.setup_credentials(credentials_path)
            return False
        except Exception as e:
            self.log_error(f"Error setting up credentials: {str(e)}")
            return False
    
    def check_credentials(self) -> bool:
        """Check if Google Sheets credentials are available."""
        try:
            if not self.sheets_manager:
                return False
                
            # Check if credentials file exists and token file exists
            from ..config.paths import get_credentials_path, get_token_path
            import os
            
            creds_path = get_credentials_path()
            token_path = get_token_path()
            
            return os.path.exists(creds_path) and os.path.exists(token_path)
        except Exception as e:
            self.log_error(f"Error checking credentials: {str(e)}")
            return False
    
    def connect_to_sheets(self, spreadsheet_id: str, sheet_name: str) -> str:
        """Connect to Google Sheets."""
        try:
            if not self.sheets_manager:
                raise Exception("Sheets manager not initialized")
            
            spreadsheet_title = self.sheets_manager.connect_to_spreadsheet(spreadsheet_id, sheet_name)
            self.log_info(f"Connected to spreadsheet: {spreadsheet_title}")
            if self.status_callback:
                self.status_callback(f"Connected to: {spreadsheet_title}")
            return spreadsheet_title
        except Exception as e:
            self.log_error(f"Error connecting to spreadsheet: {str(e)}")
            if self.status_callback:
                self.status_callback(f"Connection error: {str(e)}")
            # Send error status to GUI
            if self.gui_callback:
                self.root.after(0, self.gui_callback, 'sheets_status', 
                              {'status': 'error', 'text': f'Connection error: {str(e)}'})
            raise
    
    def is_sheets_connected(self) -> bool:
        """Check if connected to Google Sheets."""
        try:
            if not self.sheets_manager:
                return False
            return self.sheets_manager.is_connected()
        except Exception as e:
            self.log_error(f"Error checking sheets connection: {str(e)}")
            return False
    
    def load_master_list(self) -> int:
        """Load master list data from Google Sheets."""
        try:
            count = self.sheets_manager.load_master_list()
            self.log_info(f"Loaded {count} records from master list")
            return count
        except Exception as e:
            self.log_error(f"Error loading master list: {str(e)}")
            return 0
    
    def add_scan_data(self, data: str, barcode_type: str) -> bool:
        """Add scan data to Google Sheets."""
        try:
            return self.sheets_manager.add_scan_data(data, barcode_type)
        except Exception as e:
            self.log_error(f"Error adding scan data: {str(e)}")
            return False
    
    def lookup_volunteer(self, volunteer_id: str) -> Optional[dict]:
        """Look up volunteer information by ID."""
        try:
            if self.sheets_manager:
                return self.sheets_manager.lookup_volunteer_by_id(volunteer_id)
            return None
        except Exception as e:
            self.log_error(f"Error looking up volunteer: {str(e)}")
            return None
    
    def get_master_list_data(self) -> list:
        """Get the loaded master list data."""
        try:
            if self.sheets_manager:
                return self.sheets_manager.get_master_list_data()
            return []
        except Exception as e:
            self.log_error(f"Error getting master list data: {str(e)}")
            return []
    
    def debug_master_list_structure(self) -> str:
        """Debug the master list structure and return a formatted string."""
        try:
            if not self.sheets_manager:
                return "Sheets manager not available"
            
            data = self.sheets_manager.get_master_list_data()
            if not data:
                return "No master list data loaded"
            
            result = f"Master list has {len(data)} records\n"
            
            # Get headers if available
            if hasattr(self.sheets_manager, 'master_list_headers') and self.sheets_manager.master_list_headers:
                result += f"Headers: {self.sheets_manager.master_list_headers}\n"
            
            result += f"First 3 rows:\n"
            
            for i, row in enumerate(data[:3]):
                result += f"Row {i+1}: {row}\n"
            
            return result
        except Exception as e:
            return f"Error debugging master list: {str(e)}"
    
    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard."""
        try:
            from ..utils.scanner_utils import copy_to_clipboard
            if self.root:
                return copy_to_clipboard(self.root, text)
            return False
        except Exception as e:
            self.log_error(f"Error copying to clipboard: {str(e)}")
            return False 