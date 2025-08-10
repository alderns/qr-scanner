import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime, date
from pathlib import Path

from ...config.theme import THEME_COLORS, NORMAL_FONT, HEADER_FONT, SMALL_FONT, COMPONENT_SPACING
from ...config.paths import LOGS_DIR
from ...gui.components import ModernButton


class LogsTab:
    def __init__(self, parent: tk.Frame, app_manager, callbacks: dict):
        self.parent = parent
        self.app_manager = app_manager
        self.callbacks = callbacks
        
        self.log_files = []
        self.current_log_file = None
        self.log_entries = []
        self.filtered_entries = []
        
        self._create_logs_interface()
        self._load_todays_logs()
    
    def _create_logs_interface(self):
        """Create a minimalist logs interface."""
        # Main container
        main_frame = tk.Frame(self.parent, bg=THEME_COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=COMPONENT_SPACING['card_padding_xxl'], 
                       pady=COMPONENT_SPACING['card_padding_xxl'])
        
        # Header
        header_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'])
        header_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['card_margin']))
        
        title_label = tk.Label(header_frame, text="Application Logs", 
                              font=HEADER_FONT, fg=THEME_COLORS['text'], 
                              bg=THEME_COLORS['background'])
        title_label.pack(side=tk.LEFT)
        
        # Today's date indicator
        today = date.today().strftime("%B %d, %Y")
        date_label = tk.Label(header_frame, text=f"Today: {today}", 
                             font=SMALL_FONT, fg=THEME_COLORS['text_secondary'], 
                             bg=THEME_COLORS['background'])
        date_label.pack(side=tk.RIGHT)
        
        # Simple controls frame
        controls_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'])
        controls_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['card_margin']))
        
        # Level filter (simplified)
        filter_frame = tk.Frame(controls_frame, bg=THEME_COLORS['background'])
        filter_frame.pack(side=tk.LEFT)
        
        tk.Label(filter_frame, text="Show:", font=NORMAL_FONT, 
                fg=THEME_COLORS['text'], bg=THEME_COLORS['background']).pack(side=tk.LEFT)
        
        self.level_var = tk.StringVar(value="ALL")
        level_combo = ttk.Combobox(filter_frame, textvariable=self.level_var, 
                                  values=["ALL", "INFO", "WARNING", "ERROR"],
                                  font=NORMAL_FONT, state="readonly", width=8)
        level_combo.pack(side=tk.LEFT, padx=(8, 0))
        level_combo.bind('<<ComboboxSelected>>', self._apply_filter)
        
        # Action buttons (minimal)
        button_frame = tk.Frame(controls_frame, bg=THEME_COLORS['background'])
        button_frame.pack(side=tk.RIGHT)
        
        self.refresh_button = ModernButton(button_frame, text="Refresh", 
                                         command=self._refresh_logs,
                                         style='secondary')
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.clear_button = ModernButton(button_frame, text="Clear", 
                                       command=self._clear_filter,
                                       style='secondary')
        self.clear_button.pack(side=tk.LEFT)
        
        # Log entries frame
        entries_frame = tk.Frame(main_frame, bg=THEME_COLORS['surface'], 
                                relief='solid', borderwidth=1,
                                highlightbackground=THEME_COLORS['border'],
                                highlightcolor=THEME_COLORS['border'])
        entries_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for log entries (simplified columns)
        columns = ('time', 'level', 'message')
        self.log_tree = ttk.Treeview(entries_frame, columns=columns, show='headings', height=20)
        
        # Define headings
        self.log_tree.heading('time', text='Time')
        self.log_tree.heading('level', text='Level')
        self.log_tree.heading('message', text='Message')
        
        # Define columns
        self.log_tree.column('time', width=100, anchor='w')
        self.log_tree.column('level', width=80, anchor='center')
        self.log_tree.column('message', width=400, anchor='w')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(entries_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click to copy
        self.log_tree.bind('<Double-1>', self._copy_selected_entry)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'])
        status_frame.pack(fill=tk.X, pady=(8, 0))
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                   font=SMALL_FONT, fg=THEME_COLORS['text_secondary'],
                                   bg=THEME_COLORS['background'])
        self.status_label.pack(side=tk.LEFT)
    
    def _load_todays_logs(self):
        """Load content from today's log file."""
        try:
            today_str = date.today().strftime("%Y%m%d")  # Format: YYYYMMDD
            log_path = LOGS_DIR / f"qr_scanner_{today_str}.log"
            
            if not log_path.exists():
                self._update_status(f"No log file for today: qr_scanner_{today_str}.log")
                return
            
            self.current_log_file = log_path.name
            self.log_entries = []
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = self._parse_log_line(line)
                    if entry:
                        self.log_entries.append(entry)
            
            self._apply_filter()
            self._update_status(f"Loaded {len(self.log_entries)} entries from {self.current_log_file}")
            
        except Exception as e:
            self._update_status(f"Error loading logs: {str(e)}")
    
    def _parse_log_line(self, line: str) -> dict:
        """Parse a log line into structured data."""
        try:
            # Expected format: 2025-07-25 18:05:55,541 - src.utils.file_utils - INFO - Starting QR Scanner application
            parts = line.strip().split(' - ', 3)
            if len(parts) >= 4:
                timestamp = parts[0]
                logger = parts[1]
                level = parts[2]
                message = parts[3]
                
                # Extract time from timestamp
                try:
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S,%f")
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = timestamp
                
                return {
                    'timestamp': time_str,
                    'level': level,
                    'logger': logger,
                    'message': message
                }
            else:
                # Fallback for malformed lines
                return {
                    'timestamp': '',
                    'level': 'INFO',
                    'logger': '',
                    'message': line.strip()
                }
        except Exception:
            return {
                'timestamp': '',
                'level': 'INFO',
                'logger': '',
                'message': line.strip()
            }
    
    def _apply_filter(self, event=None):
        """Apply current filter to log entries."""
        level_filter = self.level_var.get()
        
        self.filtered_entries = []
        for entry in self.log_entries:
            if level_filter == "ALL" or entry['level'] == level_filter:
                self.filtered_entries.append(entry)
        
        self._update_log_display()
        self._update_status(f"Showing {len(self.filtered_entries)} of {len(self.log_entries)} entries")
    
    def _update_log_display(self):
        """Update the log display with filtered entries."""
        # Clear existing items
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        # Sort filtered entries by timestamp (newest first)
        sorted_entries = sorted(self.filtered_entries, 
                               key=lambda x: x['timestamp'], 
                               reverse=True)
        
        # Add filtered entries (newest first)
        for entry in sorted_entries:
            # Color code by level
            tags = (entry['level'].lower(),)
            
            self.log_tree.insert('', 'end', values=(
                entry['timestamp'],
                entry['level'],
                entry['message']
            ), tags=tags)
        
        # Configure tag colors
        self.log_tree.tag_configure('debug', foreground='gray')
        self.log_tree.tag_configure('info', foreground='black')
        self.log_tree.tag_configure('warning', foreground='orange')
        self.log_tree.tag_configure('error', foreground='red')
        self.log_tree.tag_configure('critical', foreground='darkred')
        
        # Scroll to top to show latest entries
        if self.log_tree.get_children():
            self.log_tree.yview_moveto(0)
    
    def _refresh_logs(self):
        """Refresh the logs display."""
        self._load_todays_logs()
    
    def _clear_filter(self):
        """Clear the current filter."""
        self.level_var.set("ALL")
        self._apply_filter()
    
    def _copy_selected_entry(self, event=None):
        """Copy selected log entry to clipboard."""
        selection = self.log_tree.selection()
        if selection:
            item = self.log_tree.item(selection[0])
            values = item['values']
            entry_text = f"{values[0]} - {values[1]} - {values[2]}"
            
            self.parent.clipboard_clear()
            self.parent.clipboard_append(entry_text)
            
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Log entry copied to clipboard")
    
    def _update_status(self, message: str):
        """Update the status label."""
        self.status_label.configure(text=message) 