"""
Main window for the QR Scanner application.
Refactored and cleaned up - v3.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
from PIL import Image, ImageTk

from .components import ModernButton, StatusIndicator
from ..config.theme import (
    THEME_COLORS, TITLE_FONT, HEADER_FONT, NORMAL_FONT, SMALL_FONT,
    BUTTON_PADDING, SECTION_PADDING
)
from ..config.settings import (
    WINDOW_TITLE, WINDOW_SIZE,
    DEFAULT_SPREADSHEET_ID, DEFAULT_SHEET_NAME,
    SUPPORTED_IMAGE_TYPES
)


class MainWindow:
    """Main window class for the QR Scanner application."""
    
    def __init__(self, root, app_manager):
        self.root = root
        self.app_manager = app_manager
        
        # Initialize variables
        self.scan_history = []
        self.auto_load_master_list = True
        self.is_scanning = False
        
        # GUI components
        self.video_frame = None
        self.start_button = None
        self.last_scan_text = None
        self.master_list_status = None
        self.history_tree = None
        self.auto_load_var = None
        self.credentials_button = None
        self.spreadsheet_entry = None
        self.sheet_name_entry = None
        self.connect_button = None
        self.sheets_status = None
        self.scan_count_label = None
        self.status_bar = None
        
        # Setup GUI
        self.setup_gui()
        self.setup_styles()
        
    def setup_styles(self):
        """Setup custom ttk styles."""
        style = ttk.Style()
        
        # Configure modern theme
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure('Card.TFrame', background=THEME_COLORS['surface'], 
                       relief='solid', borderwidth=1)
        
        # Configure label styles
        style.configure('Title.TLabel', font=TITLE_FONT, 
                       foreground=THEME_COLORS['text'], background=THEME_COLORS['background'])
        style.configure('Header.TLabel', font=HEADER_FONT, 
                       foreground=THEME_COLORS['text'], background=THEME_COLORS['background'])
        style.configure('Status.TLabel', font=SMALL_FONT, 
                       foreground=THEME_COLORS['text_secondary'], background=THEME_COLORS['background'])
        
        # Configure button styles
        style.configure('Primary.TButton', 
                       background=THEME_COLORS['primary'],
                       foreground='white',
                       font=NORMAL_FONT,
                       padding=(15, 8))
        
        style.configure('Success.TButton', 
                       background=THEME_COLORS['success'],
                       foreground='white',
                       font=NORMAL_FONT,
                       padding=(15, 8))
        
        style.configure('Warning.TButton', 
                       background=THEME_COLORS['warning'],
                       foreground='white',
                       font=NORMAL_FONT,
                       padding=(15, 8))
        
        # Configure treeview styles
        style.configure('Treeview', 
                       background=THEME_COLORS['surface'],
                       foreground=THEME_COLORS['text'],
                       fieldbackground=THEME_COLORS['surface'],
                       font=NORMAL_FONT)
        
        style.configure('Treeview.Heading', 
                       background=THEME_COLORS['primary'],
                       foreground='white',
                       font=HEADER_FONT)
        
    def setup_gui(self):
        """Setup the main GUI layout."""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=THEME_COLORS['background'])
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = tk.Frame(self.root, bg=THEME_COLORS['background'])
        main_container.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create all sections
        self._create_header_section(main_container)
        self._create_main_content(main_container)
        self._create_status_bar(main_container)
        
        # Set initial status
        self._set_initial_status()
        
    def _create_header_section(self, parent):
        """Create the header section with title and stats."""
        header_frame = tk.Frame(parent, bg=THEME_COLORS['background'])
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        
        # Title
        title_label = tk.Label(header_frame, text="QR Code Scanner", 
                              font=TITLE_FONT, fg=THEME_COLORS['text'], bg=THEME_COLORS['background'])
        title_label.pack(side=tk.LEFT)
        
        # Stats frame
        stats_frame = tk.Frame(header_frame, bg=THEME_COLORS['background'])
        stats_frame.pack(side=tk.RIGHT)
        
        # Scan count
        self.scan_count_label = tk.Label(stats_frame, text="Scans: 0", 
                                        font=SMALL_FONT, fg=THEME_COLORS['text_secondary'], 
                                        bg=THEME_COLORS['background'])
        self.scan_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Camera status
        self.camera_status = StatusIndicator(stats_frame, "Camera: Ready", "neutral")
        self.camera_status.pack(side=tk.LEFT, padx=(0, 20))
        
        # Sheets status
        self.sheets_status_indicator = StatusIndicator(stats_frame, "Sheets: Disconnected", "error")
        self.sheets_status_indicator.pack(side=tk.LEFT)
    
    def _create_main_content(self, parent):
        """Create the main content area with video and controls."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        
        # Scanner tab
        scanner_frame = tk.Frame(self.notebook, bg=THEME_COLORS['background'])
        self.notebook.add(scanner_frame, text="Scanner")
        self._create_scanner_tab(scanner_frame)
        
        # Settings tab
        settings_frame = tk.Frame(self.notebook, bg=THEME_COLORS['background'])
        self.notebook.add(settings_frame, text="Settings")
        self._create_settings_tab(settings_frame)
        
        # History tab
        history_frame = tk.Frame(self.notebook, bg=THEME_COLORS['background'])
        self.notebook.add(history_frame, text="History")
        self._create_history_tab(history_frame)
    
    def _create_scanner_tab(self, parent):
        """Create the scanner tab with video and controls."""
        # Left panel - Video
        left_panel = tk.Frame(parent, bg=THEME_COLORS['background'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Video section
        video_card = tk.Frame(left_panel, bg=THEME_COLORS['surface'], 
                             relief='solid', borderwidth=1)
        video_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Video title
        video_title = tk.Label(video_card, text="Camera Feed", font=HEADER_FONT,
                              fg=THEME_COLORS['text'], bg=THEME_COLORS['surface'])
        video_title.pack(pady=10)
        
        # Video frame
        self.video_frame = tk.Label(video_card, text="Click 'Start Camera' to begin scanning",
                                   font=NORMAL_FONT, fg=THEME_COLORS['text_secondary'],
                                   bg=THEME_COLORS['surface'], relief='solid', borderwidth=1)
        self.video_frame.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = tk.Frame(left_panel, bg=THEME_COLORS['background'])
        control_frame.pack(fill=tk.X)
        
        self.start_button = ModernButton(control_frame, text="Start Camera", 
                                        bg=THEME_COLORS['primary'], fg='white',
                                        command=self._toggle_camera)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = ModernButton(control_frame, text="Clear History", 
                                   bg=THEME_COLORS['warning'], fg='white',
                                   command=self._clear_history)
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        copy_button = ModernButton(control_frame, text="Copy Last Scan", 
                                  bg=THEME_COLORS['secondary'], fg='white',
                                  command=self._copy_last_scan)
        copy_button.pack(side=tk.LEFT)
        
        # Right panel - Results
        right_panel = tk.Frame(parent, bg=THEME_COLORS['background'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Last scan section
        last_scan_card = tk.Frame(right_panel, bg=THEME_COLORS['surface'], 
                                 relief='solid', borderwidth=1)
        last_scan_card.pack(fill=tk.X, pady=(0, 10))
        
        last_scan_title = tk.Label(last_scan_card, text="Last Scan", font=HEADER_FONT,
                                  fg=THEME_COLORS['text'], bg=THEME_COLORS['surface'])
        last_scan_title.pack(pady=10)
        
        self.last_scan_text = tk.Text(last_scan_card, height=4, wrap=tk.WORD,
                                     font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                     fg=THEME_COLORS['text'], relief='solid', borderwidth=1)
        self.last_scan_text.pack(padx=20, pady=(0, 20), fill=tk.X)
    
    def _create_settings_tab(self, parent):
        """Create the settings tab for Google Sheets configuration."""
        # Google Sheets section
        sheets_card = tk.Frame(parent, bg=THEME_COLORS['surface'], 
                              relief='solid', borderwidth=1)
        sheets_card.pack(fill=tk.X, pady=10)
        
        sheets_title = tk.Label(sheets_card, text="Google Sheets Integration", 
                               font=HEADER_FONT, fg=THEME_COLORS['text'], 
                               bg=THEME_COLORS['surface'])
        sheets_title.pack(pady=10)
        
        # Credentials section
        cred_frame = tk.Frame(sheets_card, bg=THEME_COLORS['surface'])
        cred_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        cred_label = tk.Label(cred_frame, text="API Credentials:", font=NORMAL_FONT,
                             fg=THEME_COLORS['text'], bg=THEME_COLORS['surface'])
        cred_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.credentials_status = StatusIndicator(cred_frame, "Checking credentials...", "neutral")
        self.credentials_status.pack(anchor=tk.W)
        
        # Manual setup button (only shown if auto-setup fails)
        self.credentials_button = ModernButton(cred_frame, text="Setup Credentials Manually", 
                                              bg=THEME_COLORS['warning'], fg='white',
                                              command=self._setup_credentials)
        self.credentials_button.pack(anchor=tk.W, pady=(5, 0))
        self.credentials_button.pack_forget()  # Hide by default
        
        # Connection section
        conn_frame = tk.Frame(sheets_card, bg=THEME_COLORS['surface'])
        conn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        conn_label = tk.Label(conn_frame, text="Spreadsheet Connection:", font=NORMAL_FONT,
                             fg=THEME_COLORS['text'], bg=THEME_COLORS['surface'])
        conn_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Spreadsheet ID
        id_frame = tk.Frame(conn_frame, bg=THEME_COLORS['surface'])
        id_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(id_frame, text="Spreadsheet ID:", font=NORMAL_FONT,
                fg=THEME_COLORS['text'], bg=THEME_COLORS['surface']).pack(anchor=tk.W)
        self.spreadsheet_entry = tk.Entry(id_frame, font=NORMAL_FONT, 
                                         bg=THEME_COLORS['surface'], fg=THEME_COLORS['text'],
                                         relief='solid', borderwidth=1)
        self.spreadsheet_entry.insert(0, DEFAULT_SPREADSHEET_ID)
        self.spreadsheet_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Sheet name
        sheet_frame = tk.Frame(conn_frame, bg=THEME_COLORS['surface'])
        sheet_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(sheet_frame, text="Sheet Name:", font=NORMAL_FONT,
                fg=THEME_COLORS['text'], bg=THEME_COLORS['surface']).pack(anchor=tk.W)
        self.sheet_name_entry = tk.Entry(sheet_frame, font=NORMAL_FONT,
                                        bg=THEME_COLORS['surface'], fg=THEME_COLORS['text'],
                                        relief='solid', borderwidth=1)
        self.sheet_name_entry.insert(0, DEFAULT_SHEET_NAME)
        self.sheet_name_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Connect button
        self.connect_button = ModernButton(conn_frame, text="Connect to Sheets", 
                                          bg=THEME_COLORS['success'], fg='white',
                                          command=self._connect_to_sheets)
        self.connect_button.pack(anchor=tk.W, pady=(10, 0))
        
        # Connection status
        self.sheets_status = StatusIndicator(sheets_card, "Not connected to Google Sheets", "error")
        self.sheets_status.pack(pady=(0, 20))
        
        # Master List section
        master_list_card = tk.Frame(parent, bg=THEME_COLORS['surface'], 
                                   relief='solid', borderwidth=1)
        master_list_card.pack(fill=tk.X, pady=10)
        
        master_list_title = tk.Label(master_list_card, text="Master List Management", 
                                    font=HEADER_FONT, fg=THEME_COLORS['text'], 
                                    bg=THEME_COLORS['surface'])
        master_list_title.pack(pady=10)
        
        # Master list controls
        ml_controls = tk.Frame(master_list_card, bg=THEME_COLORS['surface'])
        ml_controls.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.auto_load_var = tk.BooleanVar(value=True)
        auto_load_check = tk.Checkbutton(ml_controls, text="Auto-load Master List", 
                                        variable=self.auto_load_var, 
                                        command=self._update_auto_load_setting,
                                        font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                        fg=THEME_COLORS['text'])
        auto_load_check.pack(side=tk.LEFT)
        
        load_button = ModernButton(ml_controls, text="Load Master List", 
                                  bg=THEME_COLORS['secondary'], fg='white',
                                  command=self._load_master_list)
        load_button.pack(side=tk.RIGHT)
        
        debug_button = ModernButton(ml_controls, text="Debug Structure", 
                                   bg=THEME_COLORS['warning'], fg='white',
                                   command=self._debug_master_list)
        debug_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Master list status
        self.master_list_status = StatusIndicator(master_list_card, "Not loaded", "neutral")
        self.master_list_status.pack(pady=(0, 20))
    
    def _create_history_tab(self, parent):
        """Create the history tab with scan history."""
        # History section
        history_card = tk.Frame(parent, bg=THEME_COLORS['surface'], 
                               relief='solid', borderwidth=1)
        history_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        history_title = tk.Label(history_card, text="Scan History", 
                                font=HEADER_FONT, fg=THEME_COLORS['text'], 
                                bg=THEME_COLORS['surface'])
        history_title.pack(pady=10)
        
        # History controls
        history_controls = tk.Frame(history_card, bg=THEME_COLORS['surface'])
        history_controls.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        export_button = ModernButton(history_controls, text="Export History", 
                                    bg=THEME_COLORS['primary'], fg='white',
                                    command=self._export_history)
        export_button.pack(side=tk.LEFT)
        
        clear_history_button = ModernButton(history_controls, text="Clear History", 
                                           bg=THEME_COLORS['warning'], fg='white',
                                           command=self._clear_history)
        clear_history_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # History treeview
        tree_frame = tk.Frame(history_card, bg=THEME_COLORS['surface'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create treeview for history
        columns = ('Time', 'ID Number', 'Name', 'Status', 'Type')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.history_tree.heading('Time', text='Time')
        self.history_tree.heading('ID Number', text='ID Number')
        self.history_tree.heading('Name', text='Name')
        self.history_tree.heading('Status', text='Status')
        self.history_tree.heading('Type', text='Type')
        
        # Define columns
        self.history_tree.column('Time', width=120)
        self.history_tree.column('ID Number', width=150)
        self.history_tree.column('Name', width=200)
        self.history_tree.column('Status', width=100)
        self.history_tree.column('Type', width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event to copy from history
        self.history_tree.bind('<Double-1>', self._copy_from_history)
    
    def _create_status_bar(self, parent):
        """Create the status bar at the bottom."""
        self.status_bar = tk.Frame(parent, bg=THEME_COLORS['surface'], 
                                  relief='solid', borderwidth=1, height=30)
        self.status_bar.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        self.status_bar.grid_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", 
                                    font=SMALL_FONT, fg=THEME_COLORS['text_secondary'],
                                    bg=THEME_COLORS['surface'])
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def update_status(self, message):
        """Update the status bar message."""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
    
    def _set_initial_status(self):
        """Set initial status for all indicators."""
        # Set initial sheets status
        if hasattr(self, 'sheets_status'):
            self.sheets_status.set_status('error')
            self.sheets_status.set_text("Not connected to Google Sheets")
        
        # Set initial credentials status
        if hasattr(self, 'credentials_status'):
            self.credentials_status.set_status('neutral')
            self.credentials_status.set_text("Checking credentials...")
    
    def handle_app_callback(self, callback_type, data=None):
        """Handle callbacks from the application manager."""
        if callback_type == 'scan':
            self.process_scan(data['content'], data['type'])
        elif callback_type == 'video_frame':
            self.update_video_frame(data)
        elif callback_type == 'sheets_status':
            # Update both status indicators
            self.sheets_status_indicator.set_status(data['status'])
            self.sheets_status_indicator.set_text(data['text'])
            if hasattr(self, 'sheets_status'):
                self.sheets_status.set_status(data['status'])
                self.sheets_status.set_text(data['text'])
        elif callback_type == 'credentials_status':
            self.update_credentials_status(data['status'], data['message'])
    
    def update_credentials_status(self, status, message):
        """Update the credentials status indicator."""
        if hasattr(self, 'credentials_status'):
            self.credentials_status.set_status(status)
            self.credentials_status.set_text(message)
            
            # Show/hide manual setup button based on status
            if status == 'error':
                self.credentials_button.pack(anchor=tk.W, pady=(5, 0))
            else:
                self.credentials_button.pack_forget()
    
    def _toggle_camera(self):
        """Toggle camera on/off."""
        if not self.is_scanning:
            self._start_camera()
        else:
            self._stop_camera()
    
    def _start_camera(self):
        """Start the camera."""
        if self.app_manager.start_camera():
            self.is_scanning = True
            self.start_button.configure(text="Stop Camera", bg=THEME_COLORS['error'])
            self.camera_status.set_status('success')
            self.camera_status.set_text("Camera: Active")
            self.update_status("Camera started")
        else:
            messagebox.showerror("Error", "Could not open camera")
            self.update_status("Camera error")
    
    def _stop_camera(self):
        """Stop the camera."""
        self.app_manager.stop_camera()
        self.is_scanning = False
        self.start_button.configure(text="Start Camera", bg=THEME_COLORS['primary'])
        self.camera_status.set_status('neutral')
        self.camera_status.set_text("Camera: Ready")
        self.video_frame.config(text="Camera stopped", image="")
        self.update_status("Camera stopped")
    
    def _clear_history(self):
        """Clear scan history."""
        self.scan_history.clear()
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        self.app_manager.clear_history()
        self.last_scan_text.delete(1.0, tk.END)
        self.scan_count_label.configure(text="Scans: 0")
        self.update_status("History cleared")
    
    def _copy_last_scan(self):
        """Copy last scan to clipboard."""
        last_scan = self.app_manager.get_last_scan()
        if last_scan:
            if self.app_manager.copy_to_clipboard(last_scan):
                self.update_status("Last scan copied to clipboard")
                messagebox.showinfo("Copied", "Last scan copied to clipboard!")
        else:
            messagebox.showwarning("No Data", "No scan data to copy")
    
    def _copy_from_history(self, event):
        """Copy selected item from history to clipboard."""
        selection = self.history_tree.selection()
        if selection:
            item = self.history_tree.item(selection[0])
            id_number = item['values'][1]  # ID Number is in column 1
            if self.app_manager.copy_to_clipboard(id_number):
                self.update_status("Selected ID number copied to clipboard")
                messagebox.showinfo("Copied", "Selected ID number copied to clipboard!")
    
    def _export_history(self):
        """Export scan history to file."""
        if not self.scan_history:
            messagebox.showwarning("No Data", "No history to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Scan History",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Time,ID Number,Name,Status,Type\n")
                    for timestamp, id_number, name, status, barcode_type in self.scan_history:
                        f.write(f"{timestamp},{id_number},{name},{status},{barcode_type}\n")
                
                self.update_status(f"History exported to {filename}")
                messagebox.showinfo("Success", f"History exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export history: {str(e)}")
    
    def _update_auto_load_setting(self):
        """Update the auto-load setting based on checkbox."""
        self.auto_load_master_list = self.auto_load_var.get()
        status = "enabled" if self.auto_load_master_list else "disabled"
        self.update_status(f"Auto-load master list {status}")
    
    def _load_master_list(self):
        """Load master list data from Google Sheets."""
        if not self.app_manager.is_sheets_connected():
            messagebox.showwarning("Not Connected", "Please connect to Google Sheets first!")
            return
        
        try:
            # Update status
            self.master_list_status.set_status('warning')
            self.master_list_status.set_text("Loading...")
            self.update_status("Loading master list...")
            self.root.update()
            
            # Get master list data
            count = self.app_manager.load_master_list()
            
            if count > 0:
                self.master_list_status.set_status('success')
                self.master_list_status.set_text(f"Loaded {count} records")
                self.update_status(f"Master list loaded: {count} records")
                messagebox.showinfo("Master List Loaded", f"Successfully loaded {count} records from master list")
            else:
                self.master_list_status.set_status('error')
                self.master_list_status.set_text("No data found")
                self.update_status("No data found in master list")
                messagebox.showwarning("No Data", "No data found in master list sheet")
                
        except Exception as e:
            self.master_list_status.set_status('error')
            self.master_list_status.set_text("Error loading")
            self.update_status(f"Error loading master list: {str(e)}")
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
    
    def _setup_credentials(self):
        """Setup Google Sheets API credentials."""
        try:
            # If credentials.json doesn't exist, ask user to select it
            filename = filedialog.askopenfilename(
                title="Select credentials.json file",
                filetypes=SUPPORTED_IMAGE_TYPES
            )
            
            if filename:
                self.update_status("Setting up credentials...")
                if self.app_manager.setup_credentials(filename):
                    self.update_status("Credentials configured successfully")
                    messagebox.showinfo("Success", "Google Sheets credentials configured successfully!")
                else:
                    self.update_status("Failed to setup credentials")
                    messagebox.showerror("Error", "Failed to setup credentials")
            else:
                messagebox.showwarning("Setup Cancelled", 
                                     "Please download credentials.json from Google Cloud Console")
                
        except Exception as e:
            error_msg = str(e)
            if "verification" in error_msg.lower() or "access blocked" in error_msg.lower():
                messagebox.showerror("Verification Required", 
                                   "Google verification required. Please:\n\n"
                                   "1. Go to Google Cloud Console\n"
                                   "2. Add your email as a test user\n"
                                   "3. Or click 'Advanced' and 'Go to [Project] (unsafe)' when prompted\n\n"
                                   "See README.md for detailed instructions.")
            else:
                messagebox.showerror("Error", f"Failed to setup credentials: {error_msg}")
    
    def _connect_to_sheets(self):
        """Connect to a specific Google Spreadsheet."""
        spreadsheet_id = self.spreadsheet_entry.get().strip()
        sheet_name = self.sheet_name_entry.get().strip()
        
        try:
            self.update_status("Connecting to Google Sheets...")
            spreadsheet_title = self.app_manager.connect_to_sheets(spreadsheet_id, sheet_name)
            
            self.sheets_status_indicator.set_status('success')
            self.sheets_status_indicator.set_text(f"Sheets: {spreadsheet_title}")
            self.sheets_status.set_status('success')
            self.sheets_status.set_text(f"Connected to {spreadsheet_title}")
            self.update_status(f"Connected to: {spreadsheet_title}")
            
            # Auto-load master list if enabled
            if self.auto_load_master_list:
                self.root.after(1000, self._auto_load_master_list_data)
            
            messagebox.showinfo("Success", f"Connected to spreadsheet: {spreadsheet_title}")
            
        except Exception as e:
            self.sheets_status_indicator.set_status('error')
            self.sheets_status_indicator.set_text("Sheets: Error")
            self.sheets_status.set_status('error')
            self.sheets_status.set_text(f"Connection error: {str(e)}")
            self.update_status(f"Connection error: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def _auto_load_master_list_data(self):
        """Automatically load master list data without showing dialogs."""
        if not self.app_manager.is_sheets_connected():
            return
        
        try:
            # Update status
            self.master_list_status.set_status('warning')
            self.master_list_status.set_text("Auto-loading...")
            self.update_status("Auto-loading master list...")
            self.root.update()
            
            # Get master list data
            count = self.app_manager.load_master_list()
            
            if count > 0:
                self.master_list_status.set_status('success')
                self.master_list_status.set_text(f"Auto-loaded {count} records")
                self.update_status(f"Auto-loaded {count} records from master list")
            else:
                self.master_list_status.set_status('error')
                self.master_list_status.set_text("No master list data")
                self.update_status("No data found in master list sheet")
                
        except Exception as e:
            self.master_list_status.set_status('error')
            self.master_list_status.set_text("Auto-load failed")
            self.update_status(f"Auto-load failed: {str(e)}")
    
    def update_video_frame(self, photo):
        """Update the video frame with a new image."""
        if photo:
            self.video_frame.config(image=photo, text="")
            self.video_frame.image = photo  # Keep a reference
    
    def process_scan(self, data, barcode_type):
        """Process a new scan."""
        # Update last scan text
        self.last_scan_text.delete(1.0, tk.END)
        self.last_scan_text.insert(1.0, data)
        
        # Look up volunteer information from master list
        volunteer_info = self.app_manager.lookup_volunteer(data)
        
        if volunteer_info:
            # Use names from master list
            first_name = volunteer_info['first_name']
            last_name = volunteer_info['last_name']
            self.update_status(f"Found volunteer: {first_name} {last_name}")
        else:
            # Fallback to extracting names from QR data if not found in master list
            from ..utils.name_parser import extract_names_from_qr_data, clean_name
            first_name, last_name = extract_names_from_qr_data(data)
            first_name = clean_name(first_name)
            last_name = clean_name(last_name)
            self.update_status(f"Volunteer ID '{data}' not found in master list")
        
        # Format name as "last name, first name" for display
        formatted_name = f"{last_name}, {first_name}" if last_name and first_name else f"{first_name}{last_name}"
        status = "Present"
        
        # Add to history
        timestamp = time.strftime("%I:%M:%S %p")  # 12-hour format with AM/PM
        self.scan_history.append((timestamp, data, formatted_name, status, barcode_type))
        self.history_tree.insert('', 0, values=(timestamp, data, formatted_name, status, barcode_type))
        
        # Update scan count
        scan_count = len(self.scan_history)
        self.scan_count_label.configure(text=f"Scans: {scan_count}")
        
        # Update status
        self.update_status(f"Scanned: {data[:50]}{'...' if len(data) > 50 else ''}")
        
        # Simulate QR scanner behavior immediately
        self.app_manager.simulate_qr_scanner_behavior(data)
        
        # Add to Google Sheets (in background)
        self.app_manager.add_scan_data(data, barcode_type)
    
    def on_closing(self):
        """Handle application closing."""
        self.app_manager.stop_camera()
        self.root.destroy() 