"""
History tab component for the QR Scanner application.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Tuple

from ..components import ModernButton
from ...config.theme import (
    THEME_COLORS, HEADER_FONT, NORMAL_FONT, COMPONENT_SPACING
)


class HistoryTab:
    """History tab component for scan history display and management."""
    
    def __init__(self, parent: tk.Frame, app_manager, callbacks: dict):
        """
        Initialize the history tab.
        
        Args:
            parent: Parent frame
            app_manager: Application manager instance
            callbacks: Dictionary of callback functions
        """
        self.parent = parent
        self.app_manager = app_manager
        self.callbacks = callbacks
        
        # GUI components
        self.history_tree: Optional[ttk.Treeview] = None
        
        # Data
        self.scan_history: List[Tuple] = []
        
        self._create_history_interface()
    
    def _create_history_interface(self):
        """Create the history interface."""
        # History section
        history_card = tk.Frame(self.parent, bg=THEME_COLORS['surface'], 
                               relief='solid', borderwidth=1)
        history_card.pack(fill=tk.BOTH, expand=True, pady=COMPONENT_SPACING['card_margin'])
        
        history_title = tk.Label(history_card, text="Scan History", 
                                font=HEADER_FONT, fg=THEME_COLORS['text'], 
                                bg=THEME_COLORS['surface'])
        history_title.pack(pady=COMPONENT_SPACING['header_padding'])
        
        # History controls
        history_controls = tk.Frame(history_card, bg=THEME_COLORS['surface'])
        history_controls.pack(fill=tk.X, padx=COMPONENT_SPACING['card_padding'], 
                             pady=(0, COMPONENT_SPACING['card_padding']))
        
        export_button = ModernButton(history_controls, text="Export History", 
                                    style='primary',
                                    command=self._export_history)
        export_button.pack(side=tk.LEFT)
        
        clear_history_button = ModernButton(history_controls, text="Clear History", 
                                           style='warning',
                                           command=self._clear_history)
        clear_history_button.pack(side=tk.LEFT, padx=(COMPONENT_SPACING['button_margin'], 0))
        
        # History treeview
        tree_frame = tk.Frame(history_card, bg=THEME_COLORS['surface'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=COMPONENT_SPACING['card_padding'], 
                       pady=(0, COMPONENT_SPACING['card_padding']))
        
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
    
    def add_to_history(self, timestamp: str, id_number: str, name: str, status: str, barcode_type: str):
        """Add a new scan to the history."""
        # Add to internal list
        self.scan_history.append((timestamp, id_number, name, status, barcode_type))
        
        # Add to treeview
        if self.history_tree:
            self.history_tree.insert('', 0, values=(timestamp, id_number, name, status, barcode_type))
        
        # Update scan count
        if self.callbacks.get('update_scan_count'):
            self.callbacks['update_scan_count']()
    
    def _copy_from_history(self, event):
        """Copy selected item from history to clipboard."""
        if not self.history_tree:
            return
            
        selection = self.history_tree.selection()
        if selection:
            item = self.history_tree.item(selection[0])
            id_number = item['values'][1]  # ID Number is in column 1
            if self.app_manager.copy_to_clipboard(id_number):
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status']("Selected ID number copied to clipboard")
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
                
                if self.callbacks.get('update_status'):
                    self.callbacks['update_status'](f"History exported to {filename}")
                messagebox.showinfo("Success", f"History exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export history: {str(e)}")
    
    def _clear_history(self):
        """Clear the scan history."""
        if not self.scan_history:
            messagebox.showinfo("Info", "History is already empty")
            return
        
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all scan history?"):
            self.scan_history.clear()
            if self.history_tree:
                for item in self.history_tree.get_children():
                    self.history_tree.delete(item)
            
            if self.callbacks.get('update_status'):
                self.callbacks['update_status']("Scan history cleared")
            if self.callbacks.get('update_scan_count'):
                self.callbacks['update_scan_count']()
    
    def get_history_count(self) -> int:
        """Get the number of items in history."""
        return len(self.scan_history)
    
    def get_history_data(self) -> List[Tuple]:
        """Get the scan history data."""
        return self.scan_history.copy() 