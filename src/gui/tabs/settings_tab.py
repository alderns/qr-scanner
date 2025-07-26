"""
Settings tab component for the QR Scanner application.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any

from ...config.theme import THEME_COLORS, HEADER_FONT, NORMAL_FONT, COMPONENT_SPACING, TITLE_FONT, SUBTITLE_FONT
from ...config.settings import DEFAULT_SPREADSHEET_ID, DEFAULT_SHEET_NAME, DEFAULT_MASTER_LIST_SPREADSHEET_ID, DEFAULT_MASTER_LIST_SHEET_NAME
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
        """Create a well-spaced and organized settings interface."""
        # Main container with scrollable content
        main_container = tk.Frame(self.parent, bg=THEME_COLORS['background'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas for scrolling
        canvas = tk.Canvas(main_container, bg=THEME_COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=THEME_COLORS['background'])
        
        # Configure the canvas to expand with the frame
        def _update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", _update_scroll_region)
        
        # Enhanced mouse wheel handling for cross-platform compatibility
        def _on_mousewheel(event):
            try:
                # Handle different platforms
                if event.num == 4:  # Linux scroll up
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:  # Linux scroll down
                    canvas.yview_scroll(1, "units")
                else:  # Windows/Mac
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                # Fallback for any issues
                try:
                    canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
                except:
                    pass
        
        # Bind mouse wheel events to multiple widgets for better coverage
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        main_container.bind("<MouseWheel>", _on_mousewheel)
        
        # Also bind to parent for better event capture
        self.parent.bind("<MouseWheel>", _on_mousewheel)
        
        # Function to bind mouse wheel to all child widgets
        def bind_mousewheel_to_widgets(widget):
            """Recursively bind mouse wheel to all child widgets."""
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_to_widgets(child)
        
        # Bind mouse wheel to all widgets in the scrollable frame
        bind_mousewheel_to_widgets(scrollable_frame)
        
        # Create window in canvas and configure it to expand
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure canvas to expand with the frame
        def _configure_canvas(event):
            # Update the canvas window width to match the canvas width
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', _configure_canvas)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main content frame with same padding as scanner tab
        main_frame = tk.Frame(scrollable_frame, bg=THEME_COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=COMPONENT_SPACING['card_padding_xxl'], 
                       pady=COMPONENT_SPACING['card_padding_xxl'])
        
        # Google Sheets section
        self._create_google_sheets_section(main_frame)
        
        # Master List section
        self._create_master_list_section(main_frame)
        
        # Application Preferences section
        self._create_application_preferences_section(main_frame)
        
        # Bind mouse wheel to all widgets in the main frame
        self._bind_mousewheel_to_widget(main_frame)
    
    def _create_google_sheets_section(self, parent):
        """Create the Google Sheets configuration section."""
        # Section container
        section_frame = tk.Frame(parent, bg=THEME_COLORS['surface'], 
                                relief='solid', borderwidth=1,
                                highlightbackground=THEME_COLORS['border'],
                                highlightcolor=THEME_COLORS['border'])
        section_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['card_margin']))
        
        # Bind mouse wheel to this section
        self._bind_mousewheel_to_widget(section_frame)
        
        # Section header
        header_frame = tk.Frame(section_frame, bg=THEME_COLORS['surface'])
        header_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                         pady=COMPONENT_SPACING['header_padding'])
        
        title_label = tk.Label(header_frame, text="Google Sheets Setup", 
                              font=HEADER_FONT, fg=THEME_COLORS['text'], 
                              bg=THEME_COLORS['surface'])
        title_label.pack(anchor=tk.W)
        
        desc_label = tk.Label(header_frame, text="Configure your Google Sheets connection for storing scan data", 
                             font=NORMAL_FONT, fg=THEME_COLORS['text_secondary'], 
                             bg=THEME_COLORS['surface'])
        desc_label.pack(anchor=tk.W, pady=(4, 0))
        
        # Credentials section
        cred_frame = tk.Frame(section_frame, bg=THEME_COLORS['surface'])
        cred_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                       pady=(0, COMPONENT_SPACING['card_padding']))
        
        # Credentials status
        self.credentials_status = StatusIndicator(cred_frame, "Checking credentials...", "neutral")
        self.credentials_status.pack(anchor=tk.W, pady=(0, 12))
        
        # Setup credentials button
        self.credentials_button = ModernButton(cred_frame, text="Setup Credentials", 
                                              style='warning',
                                              command=self._setup_credentials)
        self.credentials_button.pack(anchor=tk.W, pady=(0, COMPONENT_SPACING['card_padding']))
        
        # Connection configuration section
        conn_frame = tk.Frame(section_frame, bg=THEME_COLORS['surface'])
        conn_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                       pady=(0, COMPONENT_SPACING['card_padding']))
        
        # Section divider
        divider = tk.Frame(conn_frame, height=1, bg=THEME_COLORS['border'])
        divider.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['card_padding']))
        
        # Spreadsheet configuration
        current_config = self.app_manager.config_manager.get_google_sheets_config()
        current_spreadsheet_id = current_config.spreadsheet_id if current_config else DEFAULT_SPREADSHEET_ID
        current_sheet_name = current_config.sheet_name if current_config else DEFAULT_SHEET_NAME
        
        self._create_field_group(conn_frame, "Spreadsheet ID", current_spreadsheet_id, 
                                self._toggle_spreadsheet_edit, "spreadsheet")
        
        self._create_field_group(conn_frame, "Sheet Name", current_sheet_name, 
                                self._toggle_sheet_name_edit, "sheet_name")
        
        # Connect button
        button_frame = tk.Frame(conn_frame, bg=THEME_COLORS['surface'])
        button_frame.pack(fill=tk.X, pady=(16, 0))
        
        self.connect_button = ModernButton(button_frame, text="Connect to Google Sheets", 
                                          style='success',
                                          command=self._connect_to_sheets)
        self.connect_button.pack(anchor=tk.W)
        
        # Connection status
        status_frame = tk.Frame(section_frame, bg=THEME_COLORS['surface'])
        status_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                         pady=(0, COMPONENT_SPACING['card_padding']))
        
        self.sheets_status = StatusIndicator(status_frame, "Not connected", "error")
        self.sheets_status.pack(anchor=tk.W)
    
    def _create_master_list_section(self, parent):
        """Create the Master List configuration section."""
        # Section container
        section_frame = tk.Frame(parent, bg=THEME_COLORS['surface'], 
                                relief='solid', borderwidth=1,
                                highlightbackground=THEME_COLORS['border'],
                                highlightcolor=THEME_COLORS['border'])
        section_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['card_margin']))
        
        # Bind mouse wheel to this section
        self._bind_mousewheel_to_widget(section_frame)
        
        # Section header
        header_frame = tk.Frame(section_frame, bg=THEME_COLORS['surface'])
        header_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                         pady=COMPONENT_SPACING['header_padding'])
        
        title_label = tk.Label(header_frame, text="Master List Configuration", 
                              font=HEADER_FONT, fg=THEME_COLORS['text'], 
                              bg=THEME_COLORS['surface'])
        title_label.pack(anchor=tk.W)
        
        desc_label = tk.Label(header_frame, text="Configure the source for your Master List data", 
                             font=NORMAL_FONT, fg=THEME_COLORS['text_secondary'], 
                             bg=THEME_COLORS['surface'])
        desc_label.pack(anchor=tk.W, pady=(4, 0))
        
        # Configuration fields
        config_frame = tk.Frame(section_frame, bg=THEME_COLORS['surface'])
        config_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                         pady=(0, COMPONENT_SPACING['card_padding']))
        
        # Get current configuration for Master List fields
        current_config = self.app_manager.config_manager.get_google_sheets_config()
        current_master_spreadsheet_id = current_config.master_list_spreadsheet_id if current_config else DEFAULT_MASTER_LIST_SPREADSHEET_ID
        current_master_sheet_name = current_config.master_list_sheet_name if current_config else DEFAULT_MASTER_LIST_SHEET_NAME
        
        # Master List fields
        self._create_field_group(config_frame, "Master List Spreadsheet ID", 
                                current_master_spreadsheet_id, 
                                self._toggle_master_spreadsheet_edit, "master_spreadsheet")
        
        self._create_field_group(config_frame, "Master List Sheet Name", 
                                current_master_sheet_name, 
                                self._toggle_master_sheet_name_edit, "master_sheet_name")
        
        # Controls section
        controls_frame = tk.Frame(section_frame, bg=THEME_COLORS['surface'])
        controls_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                           pady=(0, COMPONENT_SPACING['card_padding']))
        
        # Section divider
        divider = tk.Frame(controls_frame, height=1, bg=THEME_COLORS['border'])
        divider.pack(fill=tk.X, pady=(0, 16))
        
        # Auto-load checkbox
        checkbox_frame = tk.Frame(controls_frame, bg=THEME_COLORS['surface'])
        checkbox_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.auto_load_var = tk.BooleanVar(value=True)
        auto_load_check = tk.Checkbutton(checkbox_frame, text="Auto-load Master List on startup", 
                                        variable=self.auto_load_var, 
                                        command=self._update_auto_load_setting,
                                        font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                        fg=THEME_COLORS['text'])
        auto_load_check.pack(side=tk.LEFT)
        
        # Load button
        button_frame = tk.Frame(controls_frame, bg=THEME_COLORS['surface'])
        button_frame.pack(fill=tk.X)
        
        load_button = ModernButton(button_frame, text="Load Master List Now", 
                                  style='secondary',
                                  command=self._load_master_list)
        load_button.pack(anchor=tk.W)
        
        # Status
        status_frame = tk.Frame(section_frame, bg=THEME_COLORS['surface'])
        status_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                         pady=(0, COMPONENT_SPACING['card_padding']))
        
        self.master_list_status = StatusIndicator(status_frame, "Not loaded", "neutral")
        self.master_list_status.pack(anchor=tk.W)
    
    def _create_field_group(self, parent, label_text, default_value, toggle_command, field_name):
        """Create a field group with label, entry, and toggle button."""
        # Container frame
        field_frame = tk.Frame(parent, bg=THEME_COLORS['surface'])
        field_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['card_padding']))
        
        # Label
        label = tk.Label(field_frame, text=label_text, font=NORMAL_FONT, 
                        fg=THEME_COLORS['text'], bg=THEME_COLORS['surface'])
        label.pack(anchor=tk.W, pady=(0, 4))
        
        # Entry and button frame
        input_frame = tk.Frame(field_frame, bg=THEME_COLORS['surface'])
        input_frame.pack(fill=tk.X)
        
        # Entry field
        entry = tk.Entry(input_frame, font=NORMAL_FONT, state='readonly',
                        bg=THEME_COLORS['background'], fg=THEME_COLORS['text'],
                        relief='solid', borderwidth=1)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        entry.insert(0, default_value)
        
        # Toggle button
        button = ModernButton(input_frame, text="Edit", style='secondary',
                             command=toggle_command)
        button.pack(side=tk.RIGHT)
        
        # Store references for later access
        if field_name == "spreadsheet":
            self.spreadsheet_entry = entry
            self.edit_spreadsheet_btn = button
        elif field_name == "sheet_name":
            self.sheet_name_entry = entry
            self.edit_sheet_name_btn = button
        elif field_name == "master_spreadsheet":
            self.master_spreadsheet_entry = entry
            self.edit_master_spreadsheet_btn = button
        elif field_name == "master_sheet_name":
            self.master_sheet_name_entry = entry
            self.edit_master_sheet_name_btn = button
        
        # Bind mouse wheel to all widgets in this field group
        self._bind_mousewheel_to_widget(field_frame)
    
    def _create_application_preferences_section(self, parent):
        """Create the Application Preferences section."""
        # Section container
        section_frame = tk.Frame(parent, bg=THEME_COLORS['surface'], 
                                relief='solid', borderwidth=1,
                                highlightbackground=THEME_COLORS['border'],
                                highlightcolor=THEME_COLORS['border'])
        section_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['card_margin']))
        
        # Bind mouse wheel to this section
        self._bind_mousewheel_to_widget(section_frame)
        
        # Section header
        header_frame = tk.Frame(section_frame, bg=THEME_COLORS['surface'])
        header_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                         pady=COMPONENT_SPACING['header_padding'])
        
        title_label = tk.Label(header_frame, text="Application Preferences", 
                              font=HEADER_FONT, fg=THEME_COLORS['text'], 
                              bg=THEME_COLORS['surface'])
        title_label.pack(anchor=tk.W)
        
        desc_label = tk.Label(header_frame, text="Configure application behavior and automation", 
                             font=NORMAL_FONT, fg=THEME_COLORS['text_secondary'], 
                             bg=THEME_COLORS['surface'])
        desc_label.pack(anchor=tk.W, pady=(4, 0))
        
        # Preferences frame
        prefs_frame = tk.Frame(section_frame, bg=THEME_COLORS['surface'])
        prefs_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                        pady=(0, COMPONENT_SPACING['card_padding']))
        
        # Get current preferences
        current_prefs = self.app_manager.config_manager.get_user_preferences()
        
        # Auto-connect to Google Sheets checkbox
        auto_connect_frame = tk.Frame(prefs_frame, bg=THEME_COLORS['surface'])
        auto_connect_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.auto_connect_var = tk.BooleanVar(value=current_prefs.get('auto_connect_to_sheets', True))
        auto_connect_check = tk.Checkbutton(auto_connect_frame, 
                                           text="Auto-connect to Google Sheets on startup", 
                                           variable=self.auto_connect_var, 
                                           command=self._update_auto_connect_setting,
                                           font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                           fg=THEME_COLORS['text'])
        auto_connect_check.pack(side=tk.LEFT)
        
        # Auto-load master list checkbox
        auto_load_frame = tk.Frame(prefs_frame, bg=THEME_COLORS['surface'])
        auto_load_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.auto_load_master_var = tk.BooleanVar(value=current_prefs.get('auto_load_master_list', True))
        auto_load_master_check = tk.Checkbutton(auto_load_frame, 
                                               text="Auto-load Master List on startup", 
                                               variable=self.auto_load_master_var, 
                                               command=self._update_auto_load_master_setting,
                                               font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                               fg=THEME_COLORS['text'])
        auto_load_master_check.pack(side=tk.LEFT)
        
        # Clipboard integration checkbox
        clipboard_frame = tk.Frame(prefs_frame, bg=THEME_COLORS['surface'])
        clipboard_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.clipboard_var = tk.BooleanVar(value=current_prefs.get('clipboard_integration', True))
        clipboard_check = tk.Checkbutton(clipboard_frame, 
                                        text="Copy scanned data to clipboard", 
                                        variable=self.clipboard_var, 
                                        command=self._update_clipboard_setting,
                                        font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                        fg=THEME_COLORS['text'])
        clipboard_check.pack(side=tk.LEFT)
        
        # Notifications checkbox
        notifications_frame = tk.Frame(prefs_frame, bg=THEME_COLORS['surface'])
        notifications_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.notifications_var = tk.BooleanVar(value=current_prefs.get('notifications_enabled', True))
        notifications_check = tk.Checkbutton(notifications_frame, 
                                            text="Show notifications for scan events", 
                                            variable=self.notifications_var, 
                                            command=self._update_notifications_setting,
                                            font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                            fg=THEME_COLORS['text'])
        notifications_check.pack(side=tk.LEFT)
    
    def _bind_mousewheel_to_widget(self, widget):
        """Bind mouse wheel to a widget and all its children."""
        def _on_mousewheel(event):
            try:
                # Find the canvas widget to scroll
                canvas = None
                current = widget
                while current and not isinstance(current, tk.Canvas):
                    current = current.master
                
                if current and isinstance(current, tk.Canvas):
                    canvas = current
                    if event.num == 4:  # Linux scroll up
                        canvas.yview_scroll(-1, "units")
                    elif event.num == 5:  # Linux scroll down
                        canvas.yview_scroll(1, "units")
                    else:  # Windows/Mac
                        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except Exception as e:
                pass
        
        widget.bind("<MouseWheel>", _on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel_to_widget(child)
    
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
    
    def refresh_configuration(self):
        """Refresh the configuration fields with current loaded values."""
        try:
            # Get current configuration
            current_config = self.app_manager.config_manager.get_google_sheets_config()
            
            if current_config:
                # Update main spreadsheet fields
                if hasattr(self, 'spreadsheet_entry'):
                    current_value = self.spreadsheet_entry.get()
                    new_value = current_config.spreadsheet_id
                    if current_value != new_value:
                        self.spreadsheet_entry.configure(state='normal')
                        self.spreadsheet_entry.delete(0, tk.END)
                        self.spreadsheet_entry.insert(0, new_value)
                        self.spreadsheet_entry.configure(state='readonly')
                
                if hasattr(self, 'sheet_name_entry'):
                    current_value = self.sheet_name_entry.get()
                    new_value = current_config.sheet_name
                    if current_value != new_value:
                        self.sheet_name_entry.configure(state='normal')
                        self.sheet_name_entry.delete(0, tk.END)
                        self.sheet_name_entry.insert(0, new_value)
                        self.sheet_name_entry.configure(state='readonly')
                
                # Update master list fields
                if hasattr(self, 'master_spreadsheet_entry'):
                    current_value = self.master_spreadsheet_entry.get()
                    new_value = current_config.master_list_spreadsheet_id
                    if current_value != new_value:
                        self.master_spreadsheet_entry.configure(state='normal')
                        self.master_spreadsheet_entry.delete(0, tk.END)
                        self.master_spreadsheet_entry.insert(0, new_value)
                        self.master_spreadsheet_entry.configure(state='readonly')
                
                if hasattr(self, 'master_sheet_name_entry'):
                    current_value = self.master_sheet_name_entry.get()
                    new_value = current_config.master_list_sheet_name
                    if current_value != new_value:
                        self.master_sheet_name_entry.configure(state='normal')
                        self.master_sheet_name_entry.delete(0, tk.END)
                        self.master_sheet_name_entry.insert(0, new_value)
                        self.master_sheet_name_entry.configure(state='readonly')
                
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("Configuration refreshed")
        except Exception as e:
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Error refreshing configuration: {str(e)}")
    
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
        
        # Get Master List configuration from the UI
        master_spreadsheet_id = self.master_spreadsheet_entry.get().strip()
        master_sheet_name = self.master_sheet_name_entry.get().strip()
        
        if not master_spreadsheet_id or not master_sheet_name:
            messagebox.showwarning("Invalid Input", "Please enter both Master List Spreadsheet ID and Sheet Name")
            return
        
        if self.callbacks.get('update_status'):
            self.callbacks['update_status']("Loading master list...")
        
        try:
            # Update the app_manager with the Master List configuration
            self.app_manager.update_master_list_config(master_spreadsheet_id, master_sheet_name)
            
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
    
    def _update_auto_connect_setting(self):
        """Update the auto-connect setting."""
        enabled = self.auto_connect_var.get()
        self.app_manager.config_manager.update_user_preferences(auto_connect_to_sheets=enabled)
        status = "enabled" if enabled else "disabled"
        if self.callbacks.get('update_status'):
            self.callbacks['update_status'](f"Auto-connect to Google Sheets {status}")
    
    def _update_auto_load_master_setting(self):
        """Update the auto-load master list setting."""
        enabled = self.auto_load_master_var.get()
        self.app_manager.config_manager.update_user_preferences(auto_load_master_list=enabled)
        status = "enabled" if enabled else "disabled"
        if self.callbacks.get('update_status'):
            self.callbacks['update_status'](f"Auto-load Master List {status}")
    
    def _update_clipboard_setting(self):
        """Update the clipboard integration setting."""
        enabled = self.clipboard_var.get()
        self.app_manager.config_manager.update_user_preferences(clipboard_integration=enabled)
        status = "enabled" if enabled else "disabled"
        if self.callbacks.get('update_status'):
            self.callbacks['update_status'](f"Clipboard integration {status}")
    
    def _update_notifications_setting(self):
        """Update the notifications setting."""
        enabled = self.notifications_var.get()
        self.app_manager.config_manager.update_user_preferences(notifications_enabled=enabled)
        status = "enabled" if enabled else "disabled"
        if self.callbacks.get('update_status'):
            self.callbacks['update_status'](f"Notifications {status}")
    
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
            
            # Get Master List configuration from the UI
            master_spreadsheet_id = self.master_spreadsheet_entry.get().strip()
            master_sheet_name = self.master_sheet_name_entry.get().strip()
            
            # Update the app_manager with the Master List configuration
            if master_spreadsheet_id and master_sheet_name:
                self.app_manager.update_master_list_config(master_spreadsheet_id, master_sheet_name)
            
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
        entry = self.spreadsheet_entry
        btn = self.edit_spreadsheet_btn
        
        if entry.cget('state') == 'readonly':
            # Store current value before enabling edit
            current_value = entry.get()
            entry.configure(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, current_value)
            btn.configure(text="Save")
        else:
            # Save the new value to configuration
            new_value = entry.get().strip()
            if new_value:
                # Update the configuration
                success = self.app_manager.update_sheets_config(spreadsheet_id=new_value)
                if success:
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status'](f"Spreadsheet ID updated: {new_value}")
                else:
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Failed to update spreadsheet ID")
            
            # Make readonly and update display
            entry.configure(state='readonly')
            entry.delete(0, tk.END)
            entry.insert(0, new_value)
            # Clear any text selection to remove highlighting
            entry.selection_clear()
            btn.configure(text="Edit")
    
    def _toggle_sheet_name_edit(self):
        """Toggle sheet name field between readonly and editable."""
        entry = self.sheet_name_entry
        btn = self.edit_sheet_name_btn
        
        if entry.cget('state') == 'readonly':
            # Store current value before enabling edit
            current_value = entry.get()
            entry.configure(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, current_value)
            btn.configure(text="Save")
        else:
            # Save the new value to configuration
            new_value = entry.get().strip()
            if new_value:
                # Update the configuration
                success = self.app_manager.update_sheets_config(sheet_name=new_value)
                if success:
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status'](f"Sheet name updated: {new_value}")
                else:
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Failed to update sheet name")
            
            # Make readonly and update display
            entry.configure(state='readonly')
            entry.delete(0, tk.END)
            entry.insert(0, new_value)
            # Clear any text selection to remove highlighting
            entry.selection_clear()
            btn.configure(text="Edit")
    
    def _toggle_master_spreadsheet_edit(self):
        """Toggle master list spreadsheet ID field between readonly and editable."""
        entry = self.master_spreadsheet_entry
        btn = self.edit_master_spreadsheet_btn
        
        if entry.cget('state') == 'readonly':
            # Store current value before enabling edit
            current_value = entry.get()
            entry.configure(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, current_value)
            btn.configure(text="Save")
        else:
            # Save the new value to configuration
            new_value = entry.get().strip()
            if new_value:
                # Update the configuration
                success = self.app_manager.update_master_list_config(spreadsheet_id=new_value, sheet_name=self.master_sheet_name_entry.get().strip())
                if success:
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status'](f"Master List Spreadsheet ID updated: {new_value}")
                else:
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Failed to update Master List Spreadsheet ID")
            
            # Make readonly and update display
            entry.configure(state='readonly')
            entry.delete(0, tk.END)
            entry.insert(0, new_value)
            # Clear any text selection to remove highlighting
            entry.selection_clear()
            btn.configure(text="Edit")
    
    def _toggle_master_sheet_name_edit(self):
        """Toggle master list sheet name field between readonly and editable."""
        entry = self.master_sheet_name_entry
        btn = self.edit_master_sheet_name_btn
        
        if entry.cget('state') == 'readonly':
            # Store current value before enabling edit
            current_value = entry.get()
            entry.configure(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, current_value)
            btn.configure(text="Save")
        else:
            # Save the new value to configuration
            new_value = entry.get().strip()
            if new_value:
                # Update the configuration
                success = self.app_manager.update_master_list_config(spreadsheet_id=self.master_spreadsheet_entry.get().strip(), sheet_name=new_value)
                if success:
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status'](f"Master List Sheet Name updated: {new_value}")
                else:
                    if self.callbacks.get('update_status'):
                        self.callbacks['update_status']("Failed to update Master List Sheet Name")
            
            # Make readonly and update display
            entry.configure(state='readonly')
            entry.delete(0, tk.END)
            entry.insert(0, new_value)
            # Clear any text selection to remove highlighting
            entry.selection_clear()
            btn.configure(text="Edit") 