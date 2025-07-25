"""
Scanner tab component for the QR Scanner application.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from ..components import ModernButton
from ...config.theme import (
    THEME_COLORS, HEADER_FONT, NORMAL_FONT
)


class ScannerTab:
    """Scanner tab component for camera and scanning functionality."""
    
    def __init__(self, parent: tk.Frame, app_manager, callbacks: dict):
        """
        Initialize the scanner tab.
        
        Args:
            parent: Parent frame
            app_manager: Application manager instance
            callbacks: Dictionary of callback functions
        """
        self.parent = parent
        self.app_manager = app_manager
        self.callbacks = callbacks
        
        # GUI components
        self.video_frame: Optional[tk.Label] = None
        self.start_button: Optional[ModernButton] = None
        self.last_scan_text: Optional[tk.Text] = None
        self.scan_count_label: Optional[tk.Label] = None
        
        # State
        self.is_scanning = False
        
        self._create_scanner_interface()
    
    def _create_scanner_interface(self):
        """Create the scanner interface."""
        # Left panel - Camera and Controls
        left_panel = tk.Frame(self.parent, bg=THEME_COLORS['background'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Camera section
        camera_card = tk.Frame(left_panel, bg=THEME_COLORS['surface'], 
                              relief='solid', borderwidth=1)
        camera_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        camera_title = tk.Label(camera_card, text="Camera Feed", font=HEADER_FONT,
                               fg=THEME_COLORS['text'], bg=THEME_COLORS['surface'])
        camera_title.pack(pady=10)
        
        # Video frame
        self.video_frame = tk.Label(camera_card, text="Camera not started", 
                                   font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                   fg=THEME_COLORS['text_secondary'], 
                                   relief='solid', borderwidth=1)
        self.video_frame.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)
        
        # Camera controls
        control_frame = tk.Frame(camera_card, bg=THEME_COLORS['surface'])
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.start_button = ModernButton(control_frame, text="Start Camera", 
                                        bg=THEME_COLORS['success'], fg='white',
                                        command=self._toggle_camera)
        self.start_button.pack(side=tk.LEFT)
        
        copy_button = ModernButton(control_frame, text="Copy Last Scan", 
                                  bg=THEME_COLORS['secondary'], fg='white',
                                  command=self._copy_last_scan)
        copy_button.pack(side=tk.LEFT)
        
        # Right panel - Results
        right_panel = tk.Frame(self.parent, bg=THEME_COLORS['background'])
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
    
    def _toggle_camera(self):
        """Toggle camera on/off."""
        if self.is_scanning:
            self._stop_camera()
        else:
            self._start_camera()
    
    def _start_camera(self):
        """Start the camera."""
        if self.app_manager.start_camera():
            self.is_scanning = True
            self.start_button.configure(text="Stop Camera", bg=THEME_COLORS['error'])
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Camera started")
        else:
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Failed to start camera")
    
    def _stop_camera(self):
        """Stop the camera."""
        self.app_manager.stop_camera()
        self.is_scanning = False
        self.start_button.configure(text="Start Camera", bg=THEME_COLORS['success'])
        if self.callbacks.get('update_status'):
            self.callbacks['update_status']("Camera stopped")
    
    def _copy_last_scan(self):
        """Copy the last scan to clipboard."""
        last_scan = self.app_manager.get_last_scan()
        if last_scan and self.app_manager.copy_to_clipboard(last_scan):
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Last scan copied to clipboard")
    
    def update_video_frame(self, photo):
        """Update the video frame with a new image."""
        if photo and self.video_frame:
            self.video_frame.config(image=photo, text="")
            self.video_frame.image = photo  # Keep a reference
    
    def process_scan(self, data: str, barcode_type: str):
        """Process a new scan."""
        if not self.last_scan_text:
            return
            
        # Update last scan text
        self.last_scan_text.delete(1.0, tk.END)
        self.last_scan_text.insert(1.0, data)
        
        # Look up volunteer information from master list
        volunteer_info = self.app_manager.lookup_volunteer(data)
        
        if volunteer_info:
            # Use names from master list
            first_name = volunteer_info['first_name']
            last_name = volunteer_info['last_name']
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Found volunteer: {first_name} {last_name}")
        else:
            # Fallback to extracting names from QR data if not found in master list
            from ...utils.name_parser import extract_names_from_qr_data, clean_name
            first_name, last_name = extract_names_from_qr_data(data)
            first_name = clean_name(first_name)
            last_name = clean_name(last_name)
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"Volunteer ID '{data}' not found in master list")
        
        # Format name as "last name, first name" for display
        formatted_name = f"{last_name}, {first_name}" if last_name and first_name else f"{first_name}{last_name}"
        status = "Present"
        
        # Add to history
        import time
        timestamp = time.strftime("%I:%M:%S %p")  # 12-hour format with AM/PM
        
        # Call the history callback if available
        if self.callbacks.get('add_to_history'):
            self.callbacks['add_to_history'](timestamp, data, formatted_name, status, barcode_type)
        
        # Update scan count
        if self.callbacks.get('update_scan_count'):
            self.callbacks['update_scan_count']()
        
        # Update status
        if self.callbacks.get('update_status'):
            self.callbacks['update_status'](f"Scanned: {data[:50]}{'...' if len(data) > 50 else ''}")
        
        # Add to Google Sheets (in background)
        self.app_manager.add_scan_data(data, barcode_type) 