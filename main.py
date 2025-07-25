#!/usr/bin/env python3
"""
Main entry point for the QR Scanner application.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import tkinter as tk
from tkinter import messagebox

from src.core.app_manager import QRScannerApp
from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger, get_logger
from src.config.paths import ensure_directories

def main():
    """Main application entry point."""
    # Setup logging
    logger = setup_logger("QRScanner")
    logger.info("Starting QR Scanner application")
    
    try:
        # Ensure all directories exist
        ensure_directories()
        
        # Create root window
        root = tk.Tk()
        
        # Initialize application manager
        app_manager = QRScannerApp()
        
        # Create main window
        main_window = MainWindow(root, app_manager)
        
        # Initialize application
        if not app_manager.initialize(
            root=root,
            gui_callback=main_window.handle_app_callback,
            status_callback=main_window.update_status
        ):
            logger.error("Failed to initialize application")
            messagebox.showerror("Initialization Error", 
                               "Failed to initialize application. Check logs for details.")
            return
        
        # Start application
        if not app_manager.start():
            logger.error("Failed to start application")
            messagebox.showerror("Startup Error", 
                               "Failed to start application. Check logs for details.")
            return
        
        logger.info("Application started successfully")
        
        # Start GUI main loop
        root.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        messagebox.showerror("Unexpected Error", 
                           f"An unexpected error occurred: {str(e)}\n\nCheck logs for details.")
    finally:
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main() 