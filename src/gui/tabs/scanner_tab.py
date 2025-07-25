"""
Scanner tab component for the QR Scanner application.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable

from ..components import ModernButton
from ...config.theme import (
    THEME_COLORS, HEADER_FONT, NORMAL_FONT, COMPONENT_SPACING
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
                              relief='solid', borderwidth=1,
                              highlightbackground=THEME_COLORS['border'],
                              highlightcolor=THEME_COLORS['border'])
        camera_card.pack(fill=tk.BOTH, expand=True, pady=(0, COMPONENT_SPACING['card_margin']))
        
        camera_title = tk.Label(camera_card, text="Camera Feed", font=HEADER_FONT,
                               fg=THEME_COLORS['text'], bg=THEME_COLORS['surface'])
        camera_title.pack(pady=COMPONENT_SPACING['header_padding'])
        
        # Video frame
        self.video_frame = tk.Label(camera_card, text="Camera not started", 
                                   font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                   fg=THEME_COLORS['text_secondary'], 
                                   relief='solid', borderwidth=1,
                                   highlightbackground=THEME_COLORS['border'],
                                   highlightcolor=THEME_COLORS['border'])
        self.video_frame.pack(padx=COMPONENT_SPACING['card_padding'], 
                             pady=(0, COMPONENT_SPACING['card_padding']), 
                             fill=tk.BOTH, expand=True)
        
        # Camera controls
        control_frame = tk.Frame(camera_card, bg=THEME_COLORS['surface'])
        control_frame.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                          pady=(0, COMPONENT_SPACING['card_padding']))
        
        self.start_button = ModernButton(control_frame, text="Start Camera", 
                                        style='success',
                                        command=self._toggle_camera)
        self.start_button.pack(side=tk.LEFT)
        
        copy_button = ModernButton(control_frame, text="Copy Last Scan", 
                                  style='secondary',
                                  command=self._copy_last_scan)
        copy_button.pack(side=tk.LEFT, padx=(COMPONENT_SPACING['button_margin'], 0))
        
        # Right panel - Results
        right_panel = tk.Frame(self.parent, bg=THEME_COLORS['background'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Last scan section
        last_scan_card = tk.Frame(right_panel, bg=THEME_COLORS['surface'], 
                                 relief='solid', borderwidth=1,
                                 highlightbackground=THEME_COLORS['border'],
                                 highlightcolor=THEME_COLORS['border'])
        last_scan_card.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['card_margin']))
        
        last_scan_title = tk.Label(last_scan_card, text="Last Scan", font=HEADER_FONT,
                                  fg=THEME_COLORS['text'], bg=THEME_COLORS['surface'])
        last_scan_title.pack(pady=COMPONENT_SPACING['header_padding'])
        
        self.last_scan_text = tk.Text(last_scan_card, height=4, wrap=tk.WORD,
                                     font=NORMAL_FONT, bg=THEME_COLORS['surface'],
                                     fg=THEME_COLORS['text'], relief='solid', borderwidth=1,
                                     highlightbackground=THEME_COLORS['border'],
                                     highlightcolor=THEME_COLORS['border'])
        self.last_scan_text.pack(padx=COMPONENT_SPACING['card_padding'], 
                                pady=(0, COMPONENT_SPACING['card_padding']), fill=tk.X)
    
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
            self.start_button.configure(text="Stop Camera", bg=THEME_COLORS['error'], fg='white')
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Camera started")
        else:
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Failed to start camera")
    
    def _stop_camera(self):
        """Stop the camera."""
        self.app_manager.stop_camera()
        self.is_scanning = False
        self.start_button.configure(text="Start Camera", bg=THEME_COLORS['success'], fg='white')
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
        """Process a new scan using the centralized scan service."""
        if not self.last_scan_text:
            return
        
        # Use the scan service to process the scan
        scan_result = self.app_manager.process_scan(data, barcode_type)
        
        # Update last scan text
        self.last_scan_text.delete(1.0, tk.END)
        self.last_scan_text.insert(1.0, data)
        
        if scan_result.success:
            # Update status based on scan result
            if scan_result.user_found and scan_result.volunteer_info:
                # User found in master list - show welcome message
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](scan_result.welcome_message or f"Welcome, {scan_result.first_name} {scan_result.last_name}! ✅")
                
                # Add to Google Sheets only if user is found
                if self.app_manager.add_scan_data_via_service(data, barcode_type):
                    final_message = f"✅ {scan_result.first_name} {scan_result.last_name} - Checked in successfully"
                else:
                    final_message = f"❌ Failed to add {scan_result.first_name} {scan_result.last_name} to sheets"
            else:
                # User not found in master list
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](scan_result.not_found_message or f"User not found ❌ (ID: {data})")
                
                # Do not add to Google Sheets for users not found
                final_message = f"⚠️ User not in master list - not added to sheets"
            
            # Call the history callback if available
            if self.callbacks.get('add_to_history'):
                self.callbacks['add_to_history'](
                    scan_result.timestamp, 
                    scan_result.data, 
                    scan_result.formatted_name, 
                    scan_result.status, 
                    scan_result.barcode_type
                )
            
            # Update scan count
            if self.callbacks.get('update_scan_count'):
                self.callbacks['update_scan_count']()
            
            # Update status with final message
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](final_message)
        else:
            # Handle scan error
            if self.callbacks.get('update_status'):
                self.callbacks['update_status'](f"❌ Scan error: {scan_result.error_message}") 