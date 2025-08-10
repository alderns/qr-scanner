"""
Modern GUI components for the QR Scanner application.
Enhanced with accessibility, responsive design, and performance optimizations.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional, Callable, Any
from ..config.theme import THEME_COLORS, NORMAL_FONT, SMALL_FONT, COMPONENT_SPACING, BUTTON_STYLES


class Tooltip:
    """Custom tooltip widget with fade-in/out effects."""
    
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.timer = None
        
        # Bind events
        self.widget.bind('<Enter>', self._on_enter)
        self.widget.bind('<Leave>', self._on_leave)
        self.widget.bind('<Button-1>', self._on_click)
    
    def _on_enter(self, event):
        """Show tooltip after delay."""
        self.timer = self.widget.after(self.delay, self._show_tooltip)
    
    def _on_leave(self, event):
        """Hide tooltip immediately."""
        if self.timer:
            self.widget.after_cancel(self.timer)
            self.timer = None
        self._hide_tooltip()
    
    def _on_click(self, event):
        """Hide tooltip on click."""
        self._hide_tooltip()
    
    def _show_tooltip(self):
        """Create and show the tooltip."""
        if self.tooltip:
            return
        
        # Get widget position
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Configure tooltip appearance
        self.tooltip.configure(bg=THEME_COLORS['surface'], relief='solid', borderwidth=1,
                              highlightbackground=THEME_COLORS['border'],
                              highlightcolor=THEME_COLORS['border'])
        
        # Create tooltip label
        label = tk.Label(self.tooltip, text=self.text, 
                        font=SMALL_FONT, fg=THEME_COLORS['text'],
                        bg=THEME_COLORS['surface'], padx=8, pady=4)
        label.pack()
        
        # Fade in effect
        self.tooltip.attributes('-alpha', 0.0)
        self._fade_in()
    
    def _fade_in(self, alpha=0.0):
        """Animate tooltip fade-in."""
        if alpha < 1.0 and self.tooltip:
            alpha += 0.1
            self.tooltip.attributes('-alpha', alpha)
            self.tooltip.after(20, lambda: self._fade_in(alpha))
    
    def _hide_tooltip(self):
        """Hide and destroy tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class ModernButton(tk.Button):
    """Enhanced modern button with accessibility, tooltips, and performance optimizations."""
    
    def __init__(self, parent, text="", tooltip="", command=None, style=None, **kwargs):
        # Check if a predefined style is requested
        if style and style in BUTTON_STYLES:
            style_config = BUTTON_STYLES[style].copy()
            # Override with any custom kwargs
            style_config.update(kwargs)
            kwargs = style_config
        
        # Store the original background color
        self.original_bg = kwargs.get('bg', THEME_COLORS['surface'])
        self.original_fg = kwargs.get('fg', THEME_COLORS['text'])
        
        # Add accessibility attributes
        kwargs['text'] = text
        kwargs['command'] = command
        
        super().__init__(parent, **kwargs)
        self.configure(
            relief=tk.FLAT,
            borderwidth=0,
            padx=COMPONENT_SPACING['button_padding_x'],
            pady=COMPONENT_SPACING['button_padding_y'],
            font=NORMAL_FONT,
            cursor='hand2',
            bg=self.original_bg,
            fg=self.original_fg,
            activebackground=self.original_bg,
            activeforeground=self.original_fg
        )
        
        # Add tooltip if provided
        if tooltip:
            Tooltip(self, tooltip)
        
        # Bind events for accessibility and performance
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Key-Return>', self._on_return)
        self.bind('<Key-space>', self._on_space)
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
        
        # Performance optimization: reduce update frequency
        self._last_update = 0
        self._update_threshold = 50  # milliseconds
    
    def _on_enter(self, event):
        """Handle mouse enter event with enhanced hover effect."""
        # Throttle updates for performance
        current_time = time.time() * 1000
        if current_time - self._last_update < self._update_threshold:
            return
        self._last_update = current_time
        
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
    
    def _on_return(self, event):
        """Handle Enter key press for accessibility."""
        if self.cget('state') != 'disabled':
            self.invoke()
    
    def _on_space(self, event):
        """Handle Space key press for accessibility."""
        if self.cget('state') != 'disabled':
            self.invoke()
    
    def _on_focus_in(self, event):
        """Handle focus in for accessibility."""
        self.configure(relief=tk.RAISED, borderwidth=0)
    
    def _on_focus_out(self, event):
        """Handle focus out for accessibility."""
        self.configure(relief=tk.FLAT, borderwidth=0)


class StatusIndicator(tk.Frame):
    """Enhanced status indicator with accessibility and animations."""
    
    def __init__(self, parent, text="", status="neutral", tooltip="", **kwargs):
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
        
        # Add tooltip if provided
        if tooltip:
            Tooltip(self, tooltip)
        
        self.set_status(status)
    
    def set_status(self, status):
        """Set the status and update colors with animation."""
        color = self.status_colors.get(status, self.status_colors['neutral'])
        
        # Animate status change
        self._animate_status_change(color, status)
    
    def _animate_status_change(self, color, status):
        """Animate the status change for better visual feedback."""
        # Clear previous dot
        self.dot.delete("all")
        
        # Create new dot with animation
        def animate_dot(step=0):
            if step <= 10:
                # Create growing circle effect
                size = 2 + (step * 0.8)
                self.dot.create_oval(6-size, 6-size, 6+size, 6+size, 
                                   fill=color, outline="")
                self.after(20, lambda: animate_dot(step + 1))
            else:
                # Final state
                self.dot.create_oval(2, 2, 10, 10, fill=color, outline="")
        
        animate_dot()
        
        # Update text color
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


class ResponsiveFrame(tk.Frame):
    """Responsive frame that adapts to window resizing."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Bind resize events
        self.bind('<Configure>', self._on_resize)
        
        # Store minimum sizes
        self.min_width = kwargs.get('min_width', 200)
        self.min_height = kwargs.get('min_height', 100)
        
        # Responsive breakpoints
        self.breakpoints = {
            'small': 600,
            'medium': 900,
            'large': 1200
        }
    
    def _on_resize(self, event):
        """Handle resize events for responsive design."""
        if event.width > 1 and event.height > 1:  # Avoid invalid resize events
            self._update_layout(event.width, event.height)
    
    def _update_layout(self, width, height):
        """Update layout based on current size."""
        # Determine current breakpoint
        if width < self.breakpoints['small']:
            self._apply_small_layout()
        elif width < self.breakpoints['medium']:
            self._apply_medium_layout()
        else:
            self._apply_large_layout()
    
    def _apply_small_layout(self):
        """Apply small screen layout."""
        # Override in subclasses
        pass
    
    def _apply_medium_layout(self):
        """Apply medium screen layout."""
        # Override in subclasses
        pass
    
    def _apply_large_layout(self):
        """Apply large screen layout."""
        # Override in subclasses
        pass


class LoadingIndicator(tk.Frame):
    """Animated loading indicator for long-running operations."""
    
    def __init__(self, parent, text="Loading...", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Loading text
        self.text_label = tk.Label(self, text=text, font=NORMAL_FONT,
                                  fg=THEME_COLORS['text'], bg=THEME_COLORS['background'])
        self.text_label.pack(pady=(0, 10))
        
        # Animated dots
        self.dots_canvas = tk.Canvas(self, width=60, height=20, 
                                   bg=THEME_COLORS['background'], highlightthickness=0)
        self.dots_canvas.pack()
        
        # Animation state
        self.is_animating = False
        self.animation_id = None
    
    def start(self):
        """Start the loading animation."""
        self.is_animating = True
        self._animate_dots()
    
    def stop(self):
        """Stop the loading animation."""
        self.is_animating = False
        if self.animation_id:
            self.after_cancel(self.animation_id)
            self.animation_id = None
    
    def _animate_dots(self):
        """Animate the loading dots."""
        if not self.is_animating:
            return
        
        # Clear canvas
        self.dots_canvas.delete("all")
        
        # Draw animated dots
        import math
        current_time = time.time()
        for i in range(3):
            offset = math.sin(current_time * 3 + i * 2) * 0.5 + 0.5
            y = 10 + offset * 5
            x = 15 + i * 15
            self.dots_canvas.create_oval(x-3, y-3, x+3, y+3, 
                                       fill=THEME_COLORS['primary'], outline="")
        
        # Schedule next frame
        self.animation_id = self.after(100, self._animate_dots)


class VirtualizedTreeview(ttk.Treeview):
    """Virtualized treeview for efficient rendering of large datasets."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Data storage
        self._all_data = []
        self._visible_data = []
        self._page_size = 100
        self._current_page = 0
        
        # Performance optimization
        self._last_update = 0
        self._update_threshold = 50  # milliseconds
        
        # Bind scroll events for virtualization
        self.bind('<<TreeviewSelect>>', self._on_select)
        
        # Scrollbar binding
        self.vsb = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        self.configure(yscrollcommand=self._on_scroll)
    
    def _on_scroll(self, *args):
        """Handle scroll events for virtualization."""
        self.vsb.set(*args)
        self._update_visible_data()
    
    def _update_visible_data(self):
        """Update visible data based on scroll position."""
        current_time = time.time() * 1000
        if current_time - self._last_update < self._update_threshold:
            return
        self._last_update = current_time
        
        # Calculate visible range
        start_idx = int(self.yview()[0] * len(self._all_data))
        end_idx = min(start_idx + self._page_size, len(self._all_data))
        
        # Update visible data
        self._visible_data = self._all_data[start_idx:end_idx]
        self._refresh_display()
    
    def _refresh_display(self):
        """Refresh the display with current visible data."""
        # Clear current items
        for item in self.get_children():
            self.delete(item)
        
        # Add visible items
        for i, data in enumerate(self._visible_data):
            self.insert('', 'end', values=data)
    
    def set_data(self, data):
        """Set the complete dataset."""
        self._all_data = data
        self._update_visible_data()
    
    def _on_select(self, event):
        """Handle selection events."""
        # Override in subclasses if needed
        pass


 