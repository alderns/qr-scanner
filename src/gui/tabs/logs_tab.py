import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
from pathlib import Path

from ...config.theme import THEME_COLORS, NORMAL_FONT, HEADER_FONT, SMALL_FONT, COMPONENT_SPACING, SPACING
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
        self._load_log_files()
    
    def _create_logs_interface(self):
        """Create the logs interface."""
        # Main container
        main_frame = tk.Frame(self.parent, bg=THEME_COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=COMPONENT_SPACING['content_padding'], 
                       pady=COMPONENT_SPACING['content_padding'])
        
        # Header
        header_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'])
        header_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['header_margin']))
        
        title_label = tk.Label(header_frame, text="Application Logs", 
                              font=HEADER_FONT, fg=THEME_COLORS['text'], 
                              bg=THEME_COLORS['background'])
        title_label.pack(side=tk.LEFT)
        
        # Controls frame
        controls_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'])
        controls_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['form_section_margin']))
        
        # Log file selection
        file_frame = tk.Frame(controls_frame, bg=THEME_COLORS['background'])
        file_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(file_frame, text="Log File:", font=NORMAL_FONT, 
                fg=THEME_COLORS['text'], bg=THEME_COLORS['background']).pack(side=tk.LEFT)
        
        self.log_file_var = tk.StringVar()
        self.log_file_combo = ttk.Combobox(file_frame, textvariable=self.log_file_var, 
                                          font=NORMAL_FONT, state="readonly", width=30)
        self.log_file_combo.pack(side=tk.LEFT, padx=(COMPONENT_SPACING['form_field_margin'], 0))
        self.log_file_combo.bind('<<ComboboxSelected>>', self._on_log_file_selected)
        
        # Filter controls
        filter_frame = tk.Frame(controls_frame, bg=THEME_COLORS['background'])
        filter_frame.pack(side=tk.RIGHT)
        
        tk.Label(filter_frame, text="Filter:", font=NORMAL_FONT, 
                fg=THEME_COLORS['text'], bg=THEME_COLORS['background']).pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(filter_frame, textvariable=self.filter_var, 
                                   font=NORMAL_FONT, width=20)
        self.filter_entry.pack(side=tk.LEFT, padx=(COMPONENT_SPACING['form_field_margin'], SPACING['sm']))
        self.filter_entry.bind('<KeyRelease>', self._apply_filter)
        
        # Level filter
        self.level_var = tk.StringVar(value="ALL")
        level_combo = ttk.Combobox(filter_frame, textvariable=self.level_var, 
                                  values=["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                                  font=SMALL_FONT, state="readonly", width=10)
        level_combo.pack(side=tk.LEFT, padx=(SPACING['sm'], 0))
        level_combo.bind('<<ComboboxSelected>>', self._apply_filter)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'])
        buttons_frame.pack(fill=tk.X, pady=(0, COMPONENT_SPACING['form_section_margin']))
        
                # Action buttons
        self.refresh_button = ModernButton(buttons_frame, text="Refresh", 
                                         command=self._refresh_logs,
                                         style='primary')
        self.refresh_button.pack(side=tk.LEFT, padx=(0, COMPONENT_SPACING['button_margin']))
        
        self.clear_button = ModernButton(buttons_frame, text="Clear Filter", 
                                       command=self._clear_filter,
                                       style='secondary')
        self.clear_button.pack(side=tk.LEFT, padx=(0, COMPONENT_SPACING['button_margin']))
        
        self.export_button = ModernButton(buttons_frame, text="Export Logs", 
                                        command=self._export_logs,
                                        style='success')
        self.export_button.pack(side=tk.LEFT, padx=(0, COMPONENT_SPACING['button_margin']))
        
        self.open_folder_button = ModernButton(buttons_frame, text="Open Logs Folder", 
                                             command=self._open_logs_folder,
                                             style='info')
        self.open_folder_button.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'])
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                   font=SMALL_FONT, fg=THEME_COLORS['text_secondary'],
                                   bg=THEME_COLORS['background'])
        self.status_label.pack(side=tk.LEFT)
        
        # Log entries frame
        entries_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'])
        entries_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for log entries
        columns = ('timestamp', 'level', 'logger', 'message')
        self.log_tree = ttk.Treeview(entries_frame, columns=columns, show='headings', 
                                    height=20)
        
        # Configure columns
        self.log_tree.heading('timestamp', text='Timestamp')
        self.log_tree.heading('level', text='Level')
        self.log_tree.heading('logger', text='Logger')
        self.log_tree.heading('message', text='Message')
        
        self.log_tree.column('timestamp', width=150, minwidth=150)
        self.log_tree.column('level', width=80, minwidth=80)
        self.log_tree.column('logger', width=120, minwidth=120)
        self.log_tree.column('message', width=400, minwidth=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(entries_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        h_scrollbar = ttk.Scrollbar(entries_frame, orient=tk.HORIZONTAL, command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.log_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        entries_frame.grid_rowconfigure(0, weight=1)
        entries_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click for copying
        self.log_tree.bind('<Double-1>', self._copy_log_entry)
        
        # Context menu
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="Copy Entry", command=self._copy_selected_entry)
        self.context_menu.add_command(label="Copy All", command=self._copy_all_entries)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Export Selected", command=self._export_selected)
        
        self.log_tree.bind('<Button-3>', self._show_context_menu)
    
    def _load_log_files(self):
        """Load available log files."""
        try:
            if not LOGS_DIR.exists():
                return
            
            self.log_files = []
            for log_file in LOGS_DIR.glob("*.log"):
                self.log_files.append(log_file.name)
            
            self.log_files.sort(reverse=True)  # Most recent first
            self.log_file_combo['values'] = self.log_files
            
            if self.log_files:
                self.log_file_combo.set(self.log_files[0])
                self._load_log_content(self.log_files[0])
            
        except Exception as e:
            self._update_status(f"Error loading log files: {str(e)}")
    
    def _load_log_content(self, filename: str):
        """Load content from a specific log file."""
        try:
            self.current_log_file = filename
            log_path = LOGS_DIR / filename
            
            if not log_path.exists():
                self._update_status(f"Log file not found: {filename}")
                return
            
            self.log_entries = []
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = self._parse_log_line(line.strip())
                    if entry:
                        self.log_entries.append(entry)
            
            # Sort log entries by timestamp (newest first)
            self.log_entries.sort(key=lambda x: x['timestamp'], reverse=True)
            
            self._apply_filter()
            self._update_status(f"Loaded {len(self.log_entries)} entries from {filename} (newest first)")
            
        except Exception as e:
            self._update_status(f"Error loading log content: {str(e)}")
    
    def _parse_log_line(self, line: str) -> dict:
        """Parse a log line into structured data."""
        if not line:
            return None
        
        try:
            # Expected format: "2024-01-01 12:00:00 - LoggerName - LEVEL - Message"
            parts = line.split(' - ', 3)
            if len(parts) >= 4:
                timestamp = parts[0]
                logger = parts[1]
                level = parts[2]
                message = parts[3]
                
                return {
                    'timestamp': timestamp,
                    'logger': logger,
                    'level': level,
                    'message': message,
                    'raw': line
                }
            else:
                # Fallback for different formats
                return {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'logger': 'Unknown',
                    'level': 'INFO',
                    'message': line,
                    'raw': line
                }
        except Exception:
            return None
    
    def _apply_filter(self, event=None):
        """Apply current filter to log entries."""
        filter_text = self.filter_var.get().lower()
        level_filter = self.level_var.get()
        
        self.filtered_entries = []
        
        for entry in self.log_entries:
            # Level filter
            if level_filter != "ALL" and entry['level'] != level_filter:
                continue
            
            # Text filter
            if filter_text:
                if (filter_text not in entry['message'].lower() and 
                    filter_text not in entry['logger'].lower() and
                    filter_text not in entry['level'].lower()):
                    continue
            
            self.filtered_entries.append(entry)
        
        self._update_log_display()
        self._update_status(f"Showing {len(self.filtered_entries)} of {len(self.log_entries)} entries (newest first)")
    
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
                entry['logger'],
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
    
    def _on_log_file_selected(self, event):
        """Handle log file selection."""
        selected_file = self.log_file_var.get()
        if selected_file:
            self._load_log_content(selected_file)
    
    def _refresh_logs(self):
        """Refresh the logs display."""
        self._load_log_files()
        if self.current_log_file:
            self._load_log_content(self.current_log_file)
    
    def _clear_filter(self):
        """Clear the current filter."""
        self.filter_var.set("")
        self.level_var.set("ALL")
        self._apply_filter()
    
    def _export_logs(self):
        """Export filtered logs to a file."""
        if not self.filtered_entries:
            messagebox.showwarning("No Data", "No log entries to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Logs"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for entry in self.filtered_entries:
                        f.write(f"{entry['raw']}\n")
                
                self._update_status(f"Exported {len(self.filtered_entries)} entries to {filename}")
                messagebox.showinfo("Success", f"Exported {len(self.filtered_entries)} log entries.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {str(e)}")
    
    def _open_logs_folder(self):
        """Open the logs folder in file explorer."""
        try:
            if LOGS_DIR.exists():
                os.startfile(str(LOGS_DIR))
            else:
                messagebox.showinfo("Info", "Logs directory does not exist yet.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open logs folder: {str(e)}")
    
    def _copy_log_entry(self, event):
        """Copy log entry on double-click."""
        self._copy_selected_entry()
    
    def _copy_selected_entry(self):
        """Copy the selected log entry to clipboard."""
        selection = self.log_tree.selection()
        if selection:
            item = self.log_tree.item(selection[0])
            values = item['values']
            entry_text = f"{values[0]} - {values[1]} - {values[2]} - {values[3]}"
            
            self.parent.clipboard_clear()
            self.parent.clipboard_append(entry_text)
            self._update_status("Log entry copied to clipboard")
    
    def _copy_all_entries(self):
        """Copy all filtered entries to clipboard."""
        if not self.filtered_entries:
            return
        
        clipboard_text = "\n".join([entry['raw'] for entry in self.filtered_entries])
        self.parent.clipboard_clear()
        self.parent.clipboard_append(clipboard_text)
        self._update_status(f"Copied {len(self.filtered_entries)} entries to clipboard")
    
    def _export_selected(self):
        """Export selected entries."""
        selection = self.log_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select entries to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Selected Logs"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for item_id in selection:
                        item = self.log_tree.item(item_id)
                        values = item['values']
                        f.write(f"{' - '.join(values)}\n")
                
                self._update_status(f"Exported {len(selection)} selected entries")
                messagebox.showinfo("Success", f"Exported {len(selection)} selected entries.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export selected entries: {str(e)}")
    
    def _show_context_menu(self, event):
        """Show context menu for log entries."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def _update_status(self, message: str):
        """Update the status label."""
        self.status_label.config(text=message)
        if self.callbacks.get('update_status'):
            self.callbacks['update_status'](message) 