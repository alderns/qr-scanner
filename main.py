#!/usr/bin/env python3

import sys
import signal
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

# Global variables for cleanup
app_manager = None
root = None

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    print(f"\nReceived signal {signum}, shutting down immediately...")
    try:
        if app_manager:
            app_manager.shutdown()
        if root:
            root.quit()
    except Exception as e:
        print(f"Error in signal handler: {e}")
    finally:
        import os
        os._exit(0)

def main():
    global app_manager, root
    
    logger = setup_logger("QRScanner")
    logger.info("Starting QR Scanner application")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
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
        
        try:
            root.mainloop()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            if app_manager:
                app_manager.shutdown()
            if root:
                root.quit()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            if app_manager:
                app_manager.shutdown()
            if root:
                root.quit()
        
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
        if app_manager:
            app_manager.shutdown()
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main() 