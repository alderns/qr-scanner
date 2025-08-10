"""
History tab component for the QR Scanner application.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Tuple

from ...config.theme import THEME_COLORS, HEADER_FONT, NORMAL_FONT, COMPONENT_SPACING
from ..components import ModernButton


class HistoryTab:
    """Simplified history tab for scan history."""
    
    def __init__(self, parent: tk.Frame, app_manager, callbacks: dict):
        self.parent = parent
        self.app_manager = app_manager
        self.callbacks = callbacks
        
        self.scan_history = []
        self.history_tree = None
        
        self._create_history_interface()
    
    def _create_history_interface(self):
        """Create a simplified history interface."""
        # Main container
        main_frame = tk.Frame(self.parent, bg=THEME_COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Scan History", 
                              font=HEADER_FONT, fg=THEME_COLORS['text'], 
                              bg=THEME_COLORS['background'])
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Controls
        controls_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'])
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        export_button = ModernButton(controls_frame, text="Export", 
                                    style='primary',
                                    command=self._export_history)
        export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = ModernButton(controls_frame, text="Clear", 
                                   style='warning',
                                   command=self._clear_history)
        clear_button.pack(side=tk.LEFT)
        
        # History treeview
        tree_frame = tk.Frame(main_frame, bg=THEME_COLORS['background'], 
                             relief='solid', borderwidth=1,
                             highlightbackground=THEME_COLORS['border'],
                             highlightcolor=THEME_COLORS['border'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview
        columns = ('Time', 'ID', 'Name', 'Status', 'Type')
        self.history_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Define headings
        self.history_tree.heading('Time', text='Time')
        self.history_tree.heading('ID', text='ID')
        self.history_tree.heading('Name', text='Name')
        self.history_tree.heading('Status', text='Status')
        self.history_tree.heading('Type', text='Type')
        
        # Define columns
        self.history_tree.column('Time', width=100)
        self.history_tree.column('ID', width=120)
        self.history_tree.column('Name', width=150)
        self.history_tree.column('Status', width=80)
        self.history_tree.column('Type', width=60)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.history_tree.bind('<Double-1>', self._copy_from_history)
    
    def add_to_history(self, timestamp: str, id_number: str, name: str, status: str, barcode_type: str):
        """Add a new scan to the history."""
        # Add to internal list
        self.scan_history.append((timestamp, id_number, name, status, barcode_type))
        
        # Add to treeview (newest first)
        if self.history_tree:
            self.history_tree.insert('', 0, values=(timestamp, id_number, name, status, barcode_type))
        
        # Update scan count
        if self.callbacks.get('update_scan_count'):
            self.callbacks['update_scan_count']()
    
    def clear_history(self):
        """Clear the scan history."""
        self.scan_history.clear()
        if self.history_tree:
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
        
        if self.callbacks.get('update_scan_count'):
            self.callbacks['update_scan_count']()
    
    def _copy_from_history(self, event):
        """Copy selected item from history to clipboard."""
        if not self.history_tree:
            return
            
        selection = self.history_tree.selection()
        if selection:
            item = self.history_tree.item(selection[0])
            id_number = item['values'][1]  # ID is in column 1
            if self.app_manager.copy_to_clipboard(id_number):
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("ID copied to clipboard")
    
    def _export_history(self):
        """Export scan history to file."""
        if not self.scan_history:
            messagebox.showwarning("No Data", "No history to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export History",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Time,ID,Name,Status,Type\n")
                    for timestamp, id_number, name, status, barcode_type in self.scan_history:
                        f.write(f"{timestamp},{id_number},{name},{status},{barcode_type}\n")
                
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](f"History exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _clear_history(self):
        """Clear the scan history."""
        if not self.scan_history:
            return
        
        if messagebox.askyesno("Clear History", "Clear all scan history?"):
            self.clear_history()
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("History cleared")
    
    def get_history_count(self) -> int:
        """Get the number of items in history."""
        return len(self.scan_history)
    
    def get_history_data(self) -> List[Tuple]:
        """Get the scan history data."""
        return self.scan_history.copy() 