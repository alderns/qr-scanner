"""
Modern GUI components for the QR Scanner application.
"""

import tkinter as tk
from tkinter import ttk
from ..config.theme import THEME_COLORS, NORMAL_FONT, SMALL_FONT, BUTTON_PADDING


class ModernButton(tk.Button):
    """Custom modern button with hover effects."""
    
    def __init__(self, parent, **kwargs):
        # Store the original background color
        self.original_bg = kwargs.get('bg', THEME_COLORS['surface'])
        
        super().__init__(parent, **kwargs)
        self.configure(
            relief=tk.FLAT,
            borderwidth=0,
            padx=BUTTON_PADDING,
            pady=8,
            font=NORMAL_FONT,
            cursor='hand2',
            bg=self.original_bg
        )
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event):
        """Handle mouse enter event with enhanced hover effect."""
        # Create a lighter version of the current background color
        current_bg = self.cget('bg')
        if current_bg == THEME_COLORS['primary']:
            hover_color = THEME_COLORS['primary_hover']
        elif current_bg == THEME_COLORS['warning']:
            hover_color = THEME_COLORS['warning_hover']
        elif current_bg == THEME_COLORS['success']:
            hover_color = THEME_COLORS['success_hover']
        elif current_bg == THEME_COLORS['secondary']:
            hover_color = THEME_COLORS['secondary_hover']
        elif current_bg == THEME_COLORS['error']:
            hover_color = THEME_COLORS['error_hover']
        else:
            hover_color = THEME_COLORS['hover']
        
        # Apply hover effect with subtle border
        self.configure(
            background=hover_color,
            relief=tk.RAISED,
        )
    
    def _on_leave(self, event):
        """Handle mouse leave event - restore original color."""
        self.configure(
            background=self.original_bg,
            relief=tk.FLAT,
            borderwidth=0
        )


class StatusIndicator(tk.Frame):
    """Custom status indicator with colored dot."""
    
    def __init__(self, parent, text="", status="neutral", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.status_colors = {
            'success': THEME_COLORS['success'],
            'warning': THEME_COLORS['warning'],
            'error': THEME_COLORS['error'],
            'neutral': THEME_COLORS['text_secondary']
        }
        
        # Status dot
        self.dot = tk.Canvas(self, width=12, height=12, bg=THEME_COLORS['background'], 
                           highlightthickness=0)
        self.dot.pack(side=tk.LEFT, padx=(0, 8))
        
        # Status text
        self.label = tk.Label(self, text=text, font=SMALL_FONT, 
                             fg=THEME_COLORS['text_secondary'], bg=THEME_COLORS['background'])
        self.label.pack(side=tk.LEFT)
        
        self.set_status(status)
    
    def set_status(self, status):
        """Set the status and update colors."""
        color = self.status_colors.get(status, self.status_colors['neutral'])
        self.dot.delete("all")
        self.dot.create_oval(2, 2, 10, 10, fill=color, outline="")
        
        if status == 'success':
            self.label.configure(fg=THEME_COLORS['success'])
        elif status == 'warning':
            self.label.configure(fg=THEME_COLORS['warning'])
        elif status == 'error':
            self.label.configure(fg=THEME_COLORS['error'])
        else:
            self.label.configure(fg=THEME_COLORS['text_secondary'])
    
    def set_text(self, text):
        """Update the status text."""
        self.label.configure(text=text) 