import cv2
import numpy as np
from pyzbar import pyzbar
import threading
import time
from PIL import Image, ImageTk

from ..utils.logger import get_logger

logger = get_logger(__name__)


class CameraManager:
    def __init__(self, scan_callback=None):
        self.cap = None
        self.scanning = False
        self.last_scan = ""
        self.scan_callback = scan_callback
        self.scan_thread = None
        
    def start_camera(self):
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
        self.scanning = False
        if self.scan_thread:
            self.scan_thread.join(timeout=1.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        logger.info("Camera stopped")
    
    def _scan_loop(self):
        while self.scanning:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                display_width = 640
                display_height = 480
                pil_image = pil_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(pil_image)
                
                if self.scan_callback:
                    self.scan_callback(None, None, photo)
                
                barcodes = pyzbar.decode(frame)
                
                for barcode in barcodes:
                    data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    
                    if data != self.last_scan:
                        self.last_scan = data
                        logger.info(f"Scanned {barcode_type}: {data}")
                        
                        if self.scan_callback:
                            self.scan_callback(data, barcode_type, None)
                
                time.sleep(0.03)
                
            except Exception as e:
                logger.error(f"Error in scan loop: {str(e)}")
                time.sleep(0.1)
    
    def get_last_scan(self):
        return self.last_scan
    
    def clear_last_scan(self):
        self.last_scan = "" 