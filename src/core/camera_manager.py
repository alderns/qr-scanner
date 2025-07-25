"""
Camera management for QR code scanning.
"""

import cv2
import numpy as np
from pyzbar import pyzbar
import threading
import time
from PIL import Image, ImageTk

from ..utils.logger import get_logger

logger = get_logger(__name__)


class CameraManager:
    """Manages camera operations and QR code scanning."""
    
    def __init__(self, scan_callback=None):
        self.cap = None
        self.scanning = False
        self.last_scan = ""
        self.scan_callback = scan_callback
        self.scan_thread = None
        
    def start_camera(self):
        """Start the camera and scanning process."""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                logger.error("Could not open camera")
                return False
            
            self.scanning = True
            self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
            self.scan_thread.start()
            logger.info("Camera started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera: {str(e)}")
            return False
    
    def stop_camera(self):
        """Stop the camera and scanning process."""
        self.scanning = False
        if self.scan_thread:
            self.scan_thread.join(timeout=1.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        logger.info("Camera stopped")
    
    def _scan_loop(self):
        """Main scanning loop that runs in a separate thread."""
        while self.scanning:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # Convert frame to PIL Image for GUI
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # Resize for display
                display_width = 640
                display_height = 480
                pil_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage for tkinter
                photo = ImageTk.PhotoImage(pil_image)
                
                # Send video frame update
                if self.scan_callback:
                    self.scan_callback(None, None, photo)
                
                # Scan for QR codes
                barcodes = pyzbar.decode(frame)
                
                for barcode in barcodes:
                    data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    
                    # Avoid duplicate scans
                    if data != self.last_scan:
                        self.last_scan = data
                        logger.info(f"Scanned {barcode_type}: {data}")
                        
                        # Send scan data
                        if self.scan_callback:
                            self.scan_callback(data, barcode_type, None)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error in scan loop: {str(e)}")
                time.sleep(0.1)
    
    def get_last_scan(self):
        """Get the last scanned data."""
        return self.last_scan
    
    def clear_last_scan(self):
        """Clear the last scan data."""
        self.last_scan = "" 