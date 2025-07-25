#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any
import threading
import time

from .components import ModernButton, StatusIndicator, ResponsiveFrame
from ..config.theme import (
    THEME_COLORS, TITLE_FONT, HEADER_FONT, SUBTITLE_FONT, NORMAL_FONT, SMALL_FONT, 
    COMPONENT_SPACING, BUTTON_STYLES
)
from ..config.settings import DEFAULT_SPREADSHEET_ID, DEFAULT_SHEET_NAME
from .tabs.scanner_tab import ScannerTab
from .tabs.settings_tab import SettingsTab
from .tabs.history_tab import HistoryTab
from .tabs.logs_tab import LogsTab
from ..utils.name_parser import extract_names_from_qr_data, clean_name

WINDOW_TITLE = "QR Scanner"
WINDOW_SIZE = "800x800"

class MainWindow:
    """Minimalist main window for the QR Scanner application."""
    
    def __init__(self, root, app_manager):
        self.root = root
        self.app_manager = app_manager
        self.is_scanning = False
        
        # Minimum window size
        self.min_window_size = (800, 600)
        
        # Initialize GUI
        self.setup_styles()
        self.setup_gui()
        self.setup_accessibility()
        
        # Set up closing handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Setup ttk styles for a clean, minimalist look."""
        style = ttk.Style()
        
        # Configure notebook style
        style.configure('TNotebook', background=THEME_COLORS['background'])
        style.configure('TNotebook.Tab', padding=(10, 5), font=NORMAL_FONT)
        
        # Configure treeview styles
        style.configure('Treeview', 
                       background=THEME_COLORS['surface'],
                       foreground=THEME_COLORS['text'],
                       fieldbackground=THEME_COLORS['surface'],
                       font=NORMAL_FONT)
        
        style.configure('Treeview.Heading', 
                       background=THEME_COLORS['primary'],
                       foreground='black',
                       font=SUBTITLE_FONT)
    
    def setup_gui(self):
        """Setup the minimalist GUI layout."""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=THEME_COLORS['background'])
        
        # Set minimum window size
        self.root.minsize(*self.min_window_size)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container
        self.main_container = tk.Frame(self.root, bg=THEME_COLORS['background'])
        self.main_container.grid(row=0, column=0, sticky='nsew', 
                                padx=COMPONENT_SPACING['content_padding'], 
                                pady=COMPONENT_SPACING['content_padding'])
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Create sections
        self._create_header_section(self.main_container)
        self._create_main_content(self.main_container)
        self._create_status_bar(self.main_container)
        
        # Set initial status
        self._set_initial_status()
    
    def setup_accessibility(self):
        """Setup basic accessibility features."""
        # Add keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self._toggle_camera())
        self.root.bind('<Control-c>', lambda e: self._copy_last_scan())
        self.root.bind('<Control-h>', lambda e: self._clear_history())
    
    def _create_header_section(self, parent):
        """Create a simplified header with just the title and essential status."""
        header_frame = tk.Frame(parent, bg=THEME_COLORS['background'])
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, COMPONENT_SPACING['header_margin']))
        
        # Simple title
        title_label = tk.Label(header_frame, text="QR Scanner", 
                              font=TITLE_FONT, fg=THEME_COLORS['text'], 
                              bg=THEME_COLORS['background'])
        title_label.pack(side=tk.LEFT)
        
        # Essential status only
        self.camera_status = StatusIndicator(header_frame, "Camera Ready", "neutral")
        self.camera_status.pack(side=tk.RIGHT)
    
    def _create_main_content(self, parent):
        """Create the main content area with simplified tabs."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky='nsew')
        
        # Scanner tab (main functionality)
        scanner_frame = tk.Frame(self.notebook, bg=THEME_COLORS['background'])
        self.notebook.add(scanner_frame, text="Scanner")
        self._create_scanner_tab(scanner_frame)
        
        # Settings tab (essential configuration only)
        settings_frame = tk.Frame(self.notebook, bg=THEME_COLORS['background'])
        self.notebook.add(settings_frame, text="Settings")
        self._create_settings_tab(settings_frame)
        
        # History tab (simplified)
        history_frame = tk.Frame(self.notebook, bg=THEME_COLORS['background'])
        self.notebook.add(history_frame, text="History")
        self._create_history_tab(history_frame)
    
    def _create_scanner_tab(self, parent):
        """Create a streamlined scanner tab with essential controls."""
        # Main container
        main_frame = tk.Frame(parent, bg=THEME_COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video frame (larger, more prominent)
        self.video_frame = tk.Label(main_frame, text="Click 'Start' to begin scanning",
                                   font=NORMAL_FONT, fg=THEME_COLORS['text_secondary'],
                                   bg=THEME_COLORS['surface'], relief='solid', borderwidth=1,
                                   highlightbackground=THEME_COLORS['border'],
                                   highlightcolor=THEME_COLORS['border'])
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Essential controls only
        controls_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'])
        controls_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Primary action button
        self.start_button = ModernButton(controls_frame, text="Start Camera", 
                                        style='primary',
                                        command=self._toggle_camera)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Secondary actions
        copy_button = ModernButton(controls_frame, text="Copy Last", 
                                  style='secondary',
                                  command=self._copy_last_scan)
        copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = ModernButton(controls_frame, text="Clear History", 
                                   style='warning',
                                   command=self._clear_history)
        clear_button.pack(side=tk.LEFT)
        
        # Last scan display (simplified)
        self.last_scan_text = tk.Text(main_frame, height=3, wrap=tk.WORD,
                                     font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                     fg=THEME_COLORS['text'], relief='solid', borderwidth=1,
                                     highlightbackground=THEME_COLORS['border'],
                                     highlightcolor=THEME_COLORS['border'])
        self.last_scan_text.pack(fill=tk.X, padx=20, pady=(0, 20))
    
    def _create_settings_tab(self, parent):
        """Create a simplified settings tab with essential configuration."""
        # Use the existing settings tab but with simplified layout
        callbacks = {
            'update_status': self.update_status,
            'update_scan_count': self._update_scan_count
        }
        self.settings_tab = SettingsTab(parent, self.app_manager, callbacks)
    
    def _create_history_tab(self, parent):
        """Create a simplified history tab."""
        callbacks = {
            'update_status': self.update_status,
            'update_scan_count': self._update_scan_count
        }
        self.history_tab = HistoryTab(parent, self.app_manager, callbacks)
    
    def _create_status_bar(self, parent):
        """Create a minimal status bar."""
        self.status_bar = tk.Frame(parent, bg=THEME_COLORS['surface'], 
                                  relief='solid', borderwidth=1, height=25,
                                  highlightbackground=THEME_COLORS['border'],
                                  highlightcolor=THEME_COLORS['border'])
        self.status_bar.grid(row=2, column=0, sticky='ew', pady=(COMPONENT_SPACING['status_margin'], 0))
        self.status_bar.grid_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", 
                                    font=SMALL_FONT, fg=THEME_COLORS['text_secondary'],
                                    bg=THEME_COLORS['surface'])
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def update_status(self, message):
        """Update the status bar message."""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
            self.root.update_idletasks()
    
    def _set_initial_status(self):
        """Set initial status."""
        self.camera_status.set_status('neutral')
        self.camera_status.set_text("Camera Ready")
    
    def handle_app_callback(self, callback_type, data=None):
        """Handle callbacks from the application manager."""
        if callback_type == 'scan':
            self.process_scan(data['content'], data['type'])
        elif callback_type == 'video_frame':
            self.update_video_frame(data)
    
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
            self.start_button.configure(text="Stop Camera", bg=THEME_COLORS['error'], fg='white')
            self.camera_status.set_status('success')
            self.camera_status.set_text("Camera Active")
            self.update_status("Camera started")
        else:
            messagebox.showerror("Error", "Could not open camera")
            self.update_status("Camera error")
    
    def _stop_camera(self):
        """Stop the camera."""
        self.app_manager.stop_camera()
        self.is_scanning = False
        self.start_button.configure(text="Start Camera", bg=THEME_COLORS['primary'], fg='white')
        self.camera_status.set_status('neutral')
        self.camera_status.set_text("Camera Ready")
        self.video_frame.config(text="Camera stopped", image="")
        self.update_status("Camera stopped")
    
    def _clear_history(self):
        """Clear scan history."""
        self.app_manager.clear_history()
        if hasattr(self, 'history_tab'):
            self.history_tab.clear_history()
        self.last_scan_text.delete(1.0, tk.END)
        self.update_status("History cleared")
    
    def _copy_last_scan(self):
        """Copy the last scan to clipboard."""
        last_scan = self.app_manager.get_last_scan()
        if last_scan and self.app_manager.copy_to_clipboard(last_scan):
            self.update_status("Last scan copied to clipboard")
        else:
            self.update_status("No scan to copy")
    
    def update_video_frame(self, photo):
        """Update the video frame with a new image."""
        if photo and self.video_frame:
            self.video_frame.config(image=photo, text="")
            self.video_frame.image = photo
    
    def process_scan(self, data, barcode_type):
        """Process a new scan."""
        # Update last scan text
        self.last_scan_text.delete(1.0, tk.END)
        self.last_scan_text.insert(1.0, data)
        
        # Look up volunteer information
        volunteer_info = self.app_manager.lookup_volunteer(data)
        
        if volunteer_info:
            first_name = volunteer_info['first_name']
            last_name = volunteer_info['last_name']
            self.update_status(f"Found: {first_name} {last_name}")
        else:
            self.update_status(f"ID '{data}' not found in master list")
        
        # Add to history
        if hasattr(self, 'history_tab'):
            try:
                first_name, last_name = extract_names_from_qr_data(data)
                first_name = clean_name(first_name)
                last_name = clean_name(last_name)
                display_name = f"{first_name} {last_name}"
            except:
                display_name = data
            
            self.history_tab.add_to_history(
                time.strftime('%H:%M:%S'),
                data,
                display_name,
                "Success" if volunteer_info else "Not Found",
                barcode_type
            )
    
    def _update_scan_count(self):
        """Update scan count display."""
        if hasattr(self, 'history_tab'):
            count = self.history_tab.get_history_count()
            # Could add a scan count display if needed
    
    def on_closing(self):
        """Handle application closing."""
        if self.is_scanning:
            self.app_manager.stop_camera()
        self.app_manager.shutdown()
        self.root.destroy() 