"""
Settings tab component for the QR Scanner application.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any

from ...config.theme import THEME_COLORS, HEADER_FONT, NORMAL_FONT, COMPONENT_SPACING
from ...config.settings import DEFAULT_SPREADSHEET_ID, DEFAULT_SHEET_NAME
from ..components import ModernButton, StatusIndicator


class SettingsTab:
    """Simplified settings tab for essential configuration."""
    
    def __init__(self, parent: tk.Frame, app_manager, callbacks: dict):
        self.parent = parent
        self.app_manager = app_manager
        self.callbacks = callbacks
        
        self._create_settings_interface()
        # Delay initial status check to ensure GUI is fully initialized
        self.parent.after(100, self._check_initial_status)
    
    def _create_settings_interface(self):
        """Create a simplified settings interface."""
        # Main container
        main_frame = tk.Frame(self.parent, bg=THEME_COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Google Sheets section (simplified)
        sheets_frame = tk.Frame(main_frame, bg=THEME_COLORS['surface'], 
                               relief='solid', borderwidth=1,
                               highlightbackground=THEME_COLORS['border'],
                               highlightcolor=THEME_COLORS['border'])
        sheets_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(sheets_frame, text="Google Sheets Setup", 
                              font=HEADER_FONT, fg=THEME_COLORS['text'], 
                              bg=THEME_COLORS['surface'])
        title_label.pack(pady=15)
        
        # Credentials status
        self.credentials_status = StatusIndicator(sheets_frame, "Checking credentials...", "neutral")
        self.credentials_status.pack(pady=(0, 15))
        
        # Setup credentials button
        self.credentials_button = ModernButton(sheets_frame, text="Setup Credentials", 
                                              style='warning',
                                              command=self._setup_credentials)
        self.credentials_button.pack(pady=(0, 15))
        
        # Connection fields
        conn_frame = tk.Frame(sheets_frame, bg=THEME_COLORS['surface'])
        conn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Spreadsheet ID
        tk.Label(conn_frame, text="Spreadsheet ID:", font=NORMAL_FONT,
                fg=THEME_COLORS['text'], bg=THEME_COLORS['surface']).pack(anchor=tk.W)
        
        # Spreadsheet ID frame with edit button
        spreadsheet_frame = tk.Frame(conn_frame, bg=THEME_COLORS['surface'])
        spreadsheet_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.spreadsheet_entry = tk.Entry(spreadsheet_frame, font=NORMAL_FONT, 
                                         bg=THEME_COLORS['surface'], fg=THEME_COLORS['text'],
                                         relief='solid', borderwidth=1,
                                         highlightbackground=THEME_COLORS['border'],
                                         highlightcolor=THEME_COLORS['border'])
        self.spreadsheet_entry.insert(0, DEFAULT_SPREADSHEET_ID)
        self.spreadsheet_entry.configure(state='readonly')
        # Prevent text selection in readonly mode
        self.spreadsheet_entry.bind('<Button-1>', lambda e: 'break' if self.spreadsheet_entry.cget('state') == 'readonly' else None)
        self.spreadsheet_entry.bind('<B1-Motion>', lambda e: 'break' if self.spreadsheet_entry.cget('state') == 'readonly' else None)
        self.spreadsheet_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.edit_spreadsheet_btn = ModernButton(spreadsheet_frame, text="Edit", 
                                                style='secondary',
                                                command=self._toggle_spreadsheet_edit)
        self.edit_spreadsheet_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Sheet name
        tk.Label(conn_frame, text="Sheet Name:", font=NORMAL_FONT,
                fg=THEME_COLORS['text'], bg=THEME_COLORS['surface']).pack(anchor=tk.W)
        
        # Sheet name frame with edit button
        sheet_name_frame = tk.Frame(conn_frame, bg=THEME_COLORS['surface'])
        sheet_name_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.sheet_name_entry = tk.Entry(sheet_name_frame, font=NORMAL_FONT,
                                        bg=THEME_COLORS['surface'], fg=THEME_COLORS['text'],
                                        relief='solid', borderwidth=1,
                                        highlightbackground=THEME_COLORS['border'],
                                        highlightcolor=THEME_COLORS['border'])
        self.sheet_name_entry.insert(0, DEFAULT_SHEET_NAME)
        self.sheet_name_entry.configure(state='readonly')
        self.sheet_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.edit_sheet_name_btn = ModernButton(sheet_name_frame, text="Edit", 
                                               style='secondary',
                                               command=self._toggle_sheet_name_edit)
        self.edit_sheet_name_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Connect button
        self.connect_button = ModernButton(conn_frame, text="Connect", 
                                          style='success',
                                          command=self._connect_to_sheets)
        self.connect_button.pack(anchor=tk.W, pady=(5, 0))
        
        # Connection status
        self.sheets_status = StatusIndicator(sheets_frame, "Not connected", "error")
        self.sheets_status.pack(pady=(0, 15))
        
        # Master List section (simplified)
        master_frame = tk.Frame(main_frame, bg=THEME_COLORS['surface'], 
                               relief='solid', borderwidth=1,
                               highlightbackground=THEME_COLORS['border'],
                               highlightcolor=THEME_COLORS['border'])
        master_frame.pack(fill=tk.X)
        
        # Title
        master_title = tk.Label(master_frame, text="Master List", 
                               font=HEADER_FONT, fg=THEME_COLORS['text'], 
                               bg=THEME_COLORS['surface'])
        master_title.pack(pady=15)
        
        # Controls
        controls_frame = tk.Frame(master_frame, bg=THEME_COLORS['surface'])
        controls_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Auto-load checkbox
        self.auto_load_var = tk.BooleanVar(value=True)
        auto_load_check = tk.Checkbutton(controls_frame, text="Auto-load on startup", 
                                        variable=self.auto_load_var, 
                                        command=self._update_auto_load_setting,
                                        font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                        fg=THEME_COLORS['text'])
        auto_load_check.pack(side=tk.LEFT)
        
        # Load button
        load_button = ModernButton(controls_frame, text="Load Now", 
                                  style='secondary',
                                  command=self._load_master_list)
        load_button.pack(side=tk.RIGHT)
        
        # Status
        self.master_list_status = StatusIndicator(master_frame, "Not loaded", "neutral")
        self.master_list_status.pack(pady=(0, 15))
    
    def _check_initial_status(self):
        """Check initial status of credentials and connection."""
        # First, try to auto-setup credentials if they exist
        self._auto_setup_credentials()
        
        # Check credentials status after auto-setup
        try:
            if self.app_manager.check_credentials():
                self.credentials_status.set_status('success')
                self.credentials_status.set_text("Credentials OK")
                self.credentials_button.pack_forget()
                
                # Auto-connect to sheets if credentials are available
                self._auto_connect_to_sheets()
            else:
                self.credentials_status.set_status('error')
                self.credentials_status.set_text("Credentials needed")
        except Exception:
            self.credentials_status.set_status('error')
            self.credentials_status.set_text("Credentials needed")
        
        # Check sheets connection
        try:
            if self.app_manager.is_sheets_connected():
                self.sheets_status.set_status('success')
                self.sheets_status.set_text("Connected")
                
                # Auto-load master list if connected
                self._auto_load_master_list_data()
            else:
                self.sheets_status.set_status('error')
                self.sheets_status.set_text("Not connected")
        except Exception:
            self.sheets_status.set_status('error')
            self.sheets_status.set_text("Not connected")
    
    def _auto_connect_to_sheets(self):
        """Automatically connect to sheets using default settings."""
        try:
            spreadsheet_id = self.spreadsheet_entry.get().strip()
            sheet_name = self.sheet_name_entry.get().strip()
            
            if spreadsheet_id and sheet_name:
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("Auto-connecting to Google Sheets...")
                
                spreadsheet_title = self.app_manager.connect_to_sheets(spreadsheet_id, sheet_name)
                self.sheets_status.set_status('success')
                self.sheets_status.set_text(f"Connected to {spreadsheet_title}")
                
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](f"Auto-connected to: {spreadsheet_title}")
                
                # Auto-load master list after successful connection
                self._auto_load_master_list_data()
            else:
                # Use default values if fields are empty
                default_spreadsheet_id = DEFAULT_SPREADSHEET_ID
                default_sheet_name = DEFAULT_SHEET_NAME
                
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("Auto-connecting with default settings...")
                
                spreadsheet_title = self.app_manager.connect_to_sheets(default_spreadsheet_id, default_sheet_name)
                self.sheets_status.set_status('success')
                self.sheets_status.set_text(f"Connected to {spreadsheet_title}")
                
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](f"Auto-connected to: {spreadsheet_title}")
                
                # Auto-load master list after successful connection
                self._auto_load_master_list_data()
        except Exception as e:
            self.sheets_status.set_status('error')
            self.sheets_status.set_text("Auto-connect failed")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Auto-connect failed: {str(e)}")
    
    def _auto_setup_credentials(self):
        """Automatically setup credentials if they exist."""
        try:
            from ...config.paths import get_credentials_path
            import os
            
            credentials_path = get_credentials_path()
            if os.path.exists(credentials_path):
                # Check if credentials are already set up
                if self.app_manager.check_credentials():
                    self.credentials_status.set_status('success')
                    self.credentials_status.set_text("Credentials OK")
                    self.credentials_button.pack_forget()
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Credentials already configured")
                    return
                
                # Auto-setup credentials
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("Auto-setting up credentials...")
                
                if self.app_manager.setup_credentials(str(credentials_path)):
                    self.credentials_status.set_status('success')
                    self.credentials_status.set_text("Credentials OK")
                    self.credentials_button.pack_forget()
                    
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Credentials auto-configured")
                else:
                    self.credentials_status.set_status('error')
                    self.credentials_status.set_text("Auto-setup failed")
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Failed to auto-configure credentials")
            else:
                self.credentials_status.set_status('error')
                self.credentials_status.set_text("No credentials.json found")
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("Please add credentials.json file")
        except Exception as e:
            self.credentials_status.set_status('error')
            self.credentials_status.set_text("Auto-setup failed")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Auto-setup failed: {str(e)}")
    
    def _setup_credentials(self):
        """Setup Google Sheets API credentials."""
        filename = filedialog.askopenfilename(
            title="Select credentials.json file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if self.app_manager.setup_credentials(filename):
                    self.credentials_status.set_status('success')
                    self.credentials_status.set_text("Credentials OK")
                    self.credentials_button.pack_forget()
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Credentials configured")
                else:
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Failed to setup credentials")
            except Exception as e:
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](f"Error: {str(e)}")
    
    def _connect_to_sheets(self):
        """Connect to Google Sheets."""
        spreadsheet_id = self.spreadsheet_entry.get().strip()
        sheet_name = self.sheet_name_entry.get().strip()
        
        if not spreadsheet_id or not sheet_name:
            messagebox.showwarning("Invalid Input", "Please enter both Spreadsheet ID and Sheet Name")
            return
        
        if self.callbacks.get('update_status'):
            self.callbacks['update_status']("Connecting to Google Sheets...")
        
        try:
            spreadsheet_title = self.app_manager.connect_to_sheets(spreadsheet_id, sheet_name)
            self.sheets_status.set_status('success')
            self.sheets_status.set_text(f"Connected to {spreadsheet_title}")
            
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Connected to: {spreadsheet_title}")
            
            # Auto-load master list if enabled
            if self.auto_load_var.get():
                self._auto_load_master_list_data()
                
        except Exception as e:
            self.sheets_status.set_status('error')
            self.sheets_status.set_text(f"Connection failed: {str(e)}")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Connection error: {str(e)}")
    
    def _load_master_list(self):
        """Load master list data."""
        if not self.app_manager.is_sheets_connected():
            messagebox.showwarning("Not Connected", "Please connect to Google Sheets first!")
            return
        
        if self.callbacks.get('update_status'):
            self.callbacks['update_status']("Loading master list...")
        
        try:
            count = self.app_manager.load_master_list()
            if count > 0:
                self.master_list_status.set_status('success')
                self.master_list_status.set_text(f"Loaded {count} records")
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](f"Master list loaded: {count} records")
            else:
                self.master_list_status.set_status('error')
                self.master_list_status.set_text("No data found")
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("No data found in master list")
        except Exception as e:
            self.master_list_status.set_status('error')
            self.master_list_status.set_text("Load failed")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Error loading master list: {str(e)}")
    
    def _update_auto_load_setting(self):
        """Update the auto-load setting."""
        enabled = "enabled" if self.auto_load_var.get() else "disabled"
        if self.callbacks.get('update_status'):
            self.callbacks['update_status'](f"Auto-load {enabled}")
    
    def _auto_load_master_list_data(self):
        """Automatically load master list data."""
        if not self.app_manager.is_sheets_connected():
            return
        
        # Check if auto-load is enabled
        if not self.auto_load_var.get():
            return
        
        try:
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Auto-loading master list...")
            
            count = self.app_manager.load_master_list()
            if count > 0:
                self.master_list_status.set_status('success')
                self.master_list_status.set_text(f"Auto-loaded {count} records")
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](f"Auto-loaded {count} records")
            else:
                self.master_list_status.set_status('error')
                self.master_list_status.set_text("No master list data")
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("No data found in master list")
        except Exception as e:
            self.master_list_status.set_status('error')
            self.master_list_status.set_text("Auto-load failed")
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Auto-load failed: {str(e)}")
    
    def update_credentials_status(self, status: str, message: str):
        """Update the credentials status indicator."""
        self.credentials_status.set_status(status)
        self.credentials_status.set_text(message)
        
        if status == 'error':
            self.credentials_button.pack(pady=(0, 15))
        else:
            self.credentials_button.pack_forget()
    
    def _toggle_spreadsheet_edit(self):
        """Toggle spreadsheet ID field between readonly and editable."""
        if self.spreadsheet_entry.cget('state') == 'readonly':
            # Store current value before enabling edit
            current_value = self.spreadsheet_entry.get()
            self.spreadsheet_entry.configure(state='normal')
            self.spreadsheet_entry.delete(0, tk.END)
            self.spreadsheet_entry.insert(0, current_value)
            self.edit_spreadsheet_btn.configure(text="Save")
        else:
            # Store current value before making readonly
            current_value = self.spreadsheet_entry.get()
            self.spreadsheet_entry.configure(state='readonly')
            self.spreadsheet_entry.delete(0, tk.END)
            self.spreadsheet_entry.insert(0, current_value)
            # Clear any text selection to remove highlighting
            self.spreadsheet_entry.selection_clear()
            self.edit_spreadsheet_btn.configure(text="Edit")
    
    def _toggle_sheet_name_edit(self):
        """Toggle sheet name field between readonly and editable."""
        if self.sheet_name_entry.cget('state') == 'readonly':
            # Store current value before enabling edit
            current_value = self.sheet_name_entry.get()
            self.sheet_name_entry.configure(state='normal')
            self.sheet_name_entry.delete(0, tk.END)
            self.sheet_name_entry.insert(0, current_value)
            self.edit_sheet_name_btn.configure(text="Save")
        else:
            # Store current value before making readonly
            current_value = self.sheet_name_entry.get()
            self.sheet_name_entry.configure(state='readonly')
            self.sheet_name_entry.delete(0, tk.END)
            self.sheet_name_entry.insert(0, current_value)
            self.edit_sheet_name_btn.configure(text="Edit") 