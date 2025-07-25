#!/usr/bin/env python3

import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.core.app_manager import QRScannerApp
from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger
from src.config.paths import ensure_directories

try:
    from src.utils.performance_monitor import start_performance_monitoring, stop_performance_monitoring
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITORING_AVAILABLE = False
    start_performance_monitoring = lambda: None
    stop_performance_monitoring = lambda: None

def main():
    logger = setup_logger("QRScanner")
    logger.info("Starting QR Scanner application")
    
    try:
        ensure_directories()
        root = tk.Tk()
        app_manager = QRScannerApp()
        main_window = MainWindow(root, app_manager)
        
        if not app_manager.initialize(
            root=root,
            gui_callback=main_window.handle_app_callback,
            status_callback=main_window.update_status
        ):
            logger.error("Failed to initialize application")
            messagebox.showerror("Initialization Error", 
                               "Failed to initialize application. Check logs for details.")
            return
        
        if not app_manager.start():
            logger.error("Failed to start application")
            messagebox.showerror("Startup Error", 
                               "Failed to start application. Check logs for details.")
            return
        
        logger.info("Application started successfully")
        
        if PERFORMANCE_MONITORING_AVAILABLE:
            start_performance_monitoring()
            logger.info("Performance monitoring started")
        
        root.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        messagebox.showerror("Unexpected Error", 
                           f"An unexpected error occurred: {str(e)}\n\nCheck logs for details.")
    finally:
        if PERFORMANCE_MONITORING_AVAILABLE:
            stop_performance_monitoring()
            logger.info("Performance monitoring stopped")
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main() 