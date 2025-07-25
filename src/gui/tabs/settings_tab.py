"""
Settings tab component for the QR Scanner application.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from ..components import ModernButton, StatusIndicator
from ...config.theme import (
    THEME_COLORS, HEADER_FONT, NORMAL_FONT, COMPONENT_SPACING
)
from ...config.settings import (
    DEFAULT_SPREADSHEET_ID, DEFAULT_SHEET_NAME
)


class SettingsTab:
    """Settings tab component for Google Sheets and master list configuration."""
    
    def __init__(self, parent: tk.Frame, app_manager, callbacks: dict):
        """
        Initialize the settings tab.
        
        Args:
            parent: Parent frame
            app_manager: Application manager instance
            callbacks: Dictionary of callback functions
        """
        self.parent = parent
        self.app_manager = app_manager
        self.callbacks = callbacks
        
        # GUI components
        self.credentials_button: Optional[ModernButton] = None
        self.spreadsheet_entry: Optional[tk.Entry] = None
        self.sheet_name_entry: Optional[tk.Entry] = None
        self.connect_button: Optional[ModernButton] = None
        self.sheets_status: Optional[StatusIndicator] = None
        self.master_list_status: Optional[StatusIndicator] = None
        self.auto_load_var: Optional[tk.BooleanVar] = None
        
        # State
        self.auto_load_master_list = True
        
        self._create_settings_interface()
    
    def _create_settings_interface(self):
        """Create the settings interface."""
        # Google Sheets section
        sheets_card = tk.Frame(self.parent, bg=THEME_COLORS['surface'], 
                              relief='solid', borderwidth=1)
        sheets_card.pack(fill=tk.X, pady=COMPONENT_SPACING['card_margin'])
        
        sheets_title = tk.Label(sheets_card, text="Google Sheets Integration", 
                               font=HEADER_FONT, fg=THEME_COLORS['text'], 
                               bg=THEME_COLORS['surface'])
        sheets_title.pack(pady=COMPONENT_SPACING['header_padding'])
        
        # Credentials section
        cred_frame = tk.Frame(sheets_card, bg=THEME_COLORS['surface'])
        cred_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                       pady=(0, COMPONENT_SPACING['card_padding']))
        
        cred_label = tk.Label(cred_frame, text="API Credentials:", font=NORMAL_FONT,
                             fg=THEME_COLORS['text'], bg=THEME_COLORS['surface'])
        cred_label.pack(anchor=tk.W, pady=(0, COMPONENT_SPACING['form_label_margin']))
        
        self.credentials_status = StatusIndicator(cred_frame, "Checking credentials...", "neutral")
        self.credentials_status.pack(anchor=tk.W)
        
        # Manual setup button (only shown if auto-setup fails)
        self.credentials_button = ModernButton(cred_frame, text="Setup Credentials Manually", 
                                              style='warning',
                                              command=self._setup_credentials)
        self.credentials_button.pack(anchor=tk.W, pady=(COMPONENT_SPACING['form_field_margin'], 0))
        self.credentials_button.pack_forget()  # Hide by default
        
        # Connection section
        conn_frame = tk.Frame(sheets_card, bg=THEME_COLORS['surface'])
        conn_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                       pady=(0, COMPONENT_SPACING['card_padding']))
        
        conn_label = tk.Label(conn_frame, text="Spreadsheet Connection:", font=NORMAL_FONT,
                             fg=THEME_COLORS['text'], bg=THEME_COLORS['surface'])
        conn_label.pack(anchor=tk.W, pady=(0, COMPONENT_SPACING['form_section_margin']))
        
        # Spreadsheet ID
        id_frame = tk.Frame(conn_frame, bg=THEME_COLORS['surface'])
        id_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['form_field_margin']))
        
        tk.Label(id_frame, text="Spreadsheet ID:", font=NORMAL_FONT,
                fg=THEME_COLORS['text'], bg=THEME_COLORS['surface']).pack(anchor=tk.W)
        self.spreadsheet_entry = tk.Entry(id_frame, font=NORMAL_FONT, 
                                         bg=THEME_COLORS['surface'], fg=THEME_COLORS['text'],
                                         relief='solid', borderwidth=1)
        self.spreadsheet_entry.insert(0, DEFAULT_SPREADSHEET_ID)
        self.spreadsheet_entry.pack(fill=tk.X, pady=(COMPONENT_SPACING['entry_margin'], 0))
        
        # Sheet name
        sheet_frame = tk.Frame(conn_frame, bg=THEME_COLORS['surface'])
        sheet_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['form_field_margin']))
        
        tk.Label(sheet_frame, text="Sheet Name:", font=NORMAL_FONT,
                fg=THEME_COLORS['text'], bg=THEME_COLORS['surface']).pack(anchor=tk.W)
        self.sheet_name_entry = tk.Entry(sheet_frame, font=NORMAL_FONT,
                                        bg=THEME_COLORS['surface'], fg=THEME_COLORS['text'],
                                        relief='solid', borderwidth=1)
        self.sheet_name_entry.insert(0, DEFAULT_SHEET_NAME)
        self.sheet_name_entry.pack(fill=tk.X, pady=(COMPONENT_SPACING['entry_margin'], 0))
        
        # Connect button
        self.connect_button = ModernButton(conn_frame, text="Connect to Sheets", 
                                          style='success',
                                          command=self._connect_to_sheets)
        self.connect_button.pack(anchor=tk.W, pady=(COMPONENT_SPACING['form_section_margin'], 0))
        
        # Connection status
        self.sheets_status = StatusIndicator(sheets_card, "Not connected to Google Sheets", "error")
        self.sheets_status.pack(pady=(0, COMPONENT_SPACING['card_padding']))
        
        # Master List section
        master_list_card = tk.Frame(self.parent, bg=THEME_COLORS['surface'], 
                                   relief='solid', borderwidth=1)
        master_list_card.pack(fill=tk.X, pady=COMPONENT_SPACING['card_margin'])
        
        master_list_title = tk.Label(master_list_card, text="Master List Management", 
                                    font=HEADER_FONT, fg=THEME_COLORS['text'], 
                                    bg=THEME_COLORS['surface'])
        master_list_title.pack(pady=COMPONENT_SPACING['header_padding'])
        
        # Master list controls
        ml_controls = tk.Frame(master_list_card, bg=THEME_COLORS['surface'])
        ml_controls.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                        pady=(0, COMPONENT_SPACING['card_padding']))
        
        self.auto_load_var = tk.BooleanVar(value=True)
        auto_load_check = tk.Checkbutton(ml_controls, text="Auto-load Master List", 
                                        variable=self.auto_load_var, 
                                        command=self._update_auto_load_setting,
                                        font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                        fg=THEME_COLORS['text'])
        auto_load_check.pack(side=tk.LEFT)
        
        load_button = ModernButton(ml_controls, text="Load Master List", 
                                  style='secondary',
                                  command=self._load_master_list)
        load_button.pack(side=tk.RIGHT)
        
        debug_button = ModernButton(ml_controls, text="Debug Structure", 
                                   style='warning',
                                   command=self._debug_master_list)
        debug_button.pack(side=tk.RIGHT, padx=(COMPONENT_SPACING['button_margin'], 0))
        
        # Master list status
        self.master_list_status = StatusIndicator(master_list_card, "Not loaded", "neutral")
        self.master_list_status.pack(pady=(0, 20))
    
    def _setup_credentials(self):
        """Setup Google Sheets API credentials manually."""
        filename = filedialog.askopenfilename(
            title="Select Google Sheets API Credentials File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if self.app_manager.setup_credentials(filename):
                    self.credentials_status.set_status('success')
                    self.credentials_status.set_text("Credentials configured successfully")
                    self.credentials_button.pack_forget()  # Hide the button
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Google Sheets credentials configured")
                else:
                    self.credentials_status.set_status('error')
                    self.credentials_status.set_text("Failed to configure credentials")
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Failed to configure credentials")
            except Exception as e:
                error_msg = f"Error setting up credentials: {str(e)}"
                self.credentials_status.set_status('error')
                self.credentials_status.set_text("Error configuring credentials")
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](error_msg)
                messagebox.showerror("Error", f"Failed to setup credentials: {error_msg}")
    
    def _connect_to_sheets(self):
        """Connect to a specific Google Spreadsheet."""
        spreadsheet_id = self.spreadsheet_entry.get().strip()
        sheet_name = self.sheet_name_entry.get().strip()
        
        try:
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Connecting to Google Sheets...")
            spreadsheet_title = self.app_manager.connect_to_sheets(spreadsheet_id, sheet_name)
            
            self.sheets_status.set_status('success')
            self.sheets_status.set_text(f"Connected to {spreadsheet_title}")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Connected to: {spreadsheet_title}")
            
            # Auto-load master list if enabled
            if self.auto_load_master_list:
                self.parent.after(1000, self._auto_load_master_list_data)
            
            messagebox.showinfo("Success", f"Connected to spreadsheet: {spreadsheet_title}")
            
        except Exception as e:
            self.sheets_status.set_status('error')
            self.sheets_status.set_text(f"Connection error: {str(e)}")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Connection error: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def _load_master_list(self):
        """Load master list data from Google Sheets."""
        if not self.app_manager.is_sheets_connected():
            messagebox.showwarning("Not Connected", "Please connect to Google Sheets first!")
            return
        
        try:
            # Update status
            self.master_list_status.set_status('warning')
            self.master_list_status.set_text("Loading...")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Loading master list...")
            self.parent.update()
            
            # Get master list data
            count = self.app_manager.load_master_list()
            
            if count > 0:
                self.master_list_status.set_status('success')
                self.master_list_status.set_text(f"Loaded {count} records")
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](f"Master list loaded: {count} records")
                messagebox.showinfo("Master List Loaded", f"Successfully loaded {count} records from master list")
            else:
                self.master_list_status.set_status('error')
                self.master_list_status.set_text("No data found")
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("No data found in master list")
                messagebox.showwarning("No Data", "No data found in master list sheet")
                
        except Exception as e:
            self.master_list_status.set_status('error')
            self.master_list_status.set_text("Error loading")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Error loading master list: {str(e)}")
            messagebox.showerror("Error", f"Failed to load master list: {str(e)}")
    
    def _debug_master_list(self):
        """Debug the master list structure."""
        debug_info = self.app_manager.debug_master_list_structure()
        
        # Also test the specific volunteer ID lookup
        test_id = "CCFM-W-003"
        volunteer_info = self.app_manager.lookup_volunteer(test_id)
        if volunteer_info:
            debug_info += f"\n\nTest lookup for {test_id}:"
            debug_info += f"\nFirst Name: '{volunteer_info['first_name']}'"
            debug_info += f"\nLast Name: '{volunteer_info['last_name']}'"
        else:
            debug_info += f"\n\nTest lookup for {test_id}: NOT FOUND in master list"
        
        messagebox.showinfo("Master List Debug Info", debug_info)
    
    def _update_auto_load_setting(self):
        """Update the auto-load setting based on checkbox."""
        self.auto_load_master_list = self.auto_load_var.get()
        status = "enabled" if self.auto_load_master_list else "disabled"
        if self.callbacks.get('update_status'):
            self.callbacks['update_status'](f"Auto-load master list {status}")
    
    def _auto_load_master_list_data(self):
        """Automatically load master list data without showing dialogs."""
        if not self.app_manager.is_sheets_connected():
            return
        
        try:
            # Update status
            self.master_list_status.set_status('warning')
            self.master_list_status.set_text("Auto-loading...")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Auto-loading master list...")
            self.parent.update()
            
            # Get master list data
            count = self.app_manager.load_master_list()
            
            if count > 0:
                self.master_list_status.set_status('success')
                self.master_list_status.set_text(f"Auto-loaded {count} records")
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](f"Auto-loaded {count} records from master list")
            else:
                self.master_list_status.set_status('error')
                self.master_list_status.set_text("No master list data")
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("No data found in master list sheet")
                
        except Exception as e:
            self.master_list_status.set_status('error')
            self.master_list_status.set_text("Auto-load failed")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Auto-load failed: {str(e)}")
    
    def update_credentials_status(self, status: str, message: str):
        """Update the credentials status display."""
        self.credentials_status.set_status(status)
        self.credentials_status.set_text(message)
        
        if status == 'error':
            self.credentials_button.pack(anchor=tk.W, pady=(5, 0))
        else:
            self.credentials_button.pack_forget() 