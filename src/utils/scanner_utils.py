"""
QR Scanner simulation utilities.
"""

import random
import time
import tkinter as tk
from tkinter import ttk
import warnings

from ..config.settings import (
    MIN_TYPING_DELAY, MAX_TYPING_DELAY, PAUSE_PROBABILITY,
    PAUSE_DELAY_MIN, PAUSE_DELAY_MAX, ENTER_DELAY,
    NOTIFICATION_DURATION, NOTIFICATION_SIZE
)

# Suppress zbar warnings
warnings.filterwarnings("ignore", category=UserWarning)


def type_like_human(text):
    """Simulate realistic human typing with variable speed and occasional pauses."""
    try:
        import pyautogui
        
        for char in text:
            # Type the character
            pyautogui.write(char)
            
            # Fast random delay between characters
            delay = random.uniform(MIN_TYPING_DELAY, MAX_TYPING_DELAY)
            
            # Occasionally add longer pauses (like human thinking)
            if random.random() < PAUSE_PROBABILITY:
                delay += random.uniform(PAUSE_DELAY_MIN, PAUSE_DELAY_MAX)
            
            time.sleep(delay)
            
    except ImportError:
        print("pyautogui not available - typing simulation disabled")
        print("Install with: pip install pyautogui")


def simulate_qr_scanner_behavior(data, root):
    """Simulate real QR scanner behavior: type data + press Enter."""
    try:
        import pyautogui
        
        def simulate_typing():
            try:
                # Type the QR code data with realistic typing simulation
                type_like_human(data)
                
                # Small delay before Enter
                time.sleep(ENTER_DELAY)
                
                # Press Enter (like a real scanner would)
                pyautogui.press('enter')
                
                print(f"QR Scanner Simulation: typed '{data}' + Enter")
                
            except Exception as e:
                print(f"Error during typing simulation: {e}")
        
        # Execute the simulation after a short delay
        root.after(100, simulate_typing)
        
    except ImportError:
        print("pyautogui not available - QR scanner simulation disabled")
        print("Install with: pip install pyautogui")
    except Exception as e:
        print(f"Error simulating QR scanner behavior: {e}")


def show_auto_notification(root, message):
    """Show a notification that automatically closes after a set duration."""
    # Create a toplevel window
    notification = tk.Toplevel(root)
    notification.title("QR Code Detected")
    notification.geometry(NOTIFICATION_SIZE)
    notification.configure(bg='#2c3e50')
    
    # Center the notification
    notification.transient(root)
    notification.grab_set()
    
    # Make it appear on top
    notification.lift()
    notification.attributes('-topmost', True)
    
    # Add content
    content_frame = ttk.Frame(notification)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Icon or title
    title_label = ttk.Label(content_frame, text="✓ QR Code Detected", 
                           font=('Arial', 12, 'bold'))
    title_label.pack(pady=(0, 10))
    
    # Message
    message_label = ttk.Label(content_frame, text=message, 
                             font=('Arial', 10), wraplength=300)
    message_label.pack(pady=(0, 15))
    
    # Progress bar
    progress = ttk.Progressbar(content_frame, mode='determinate', 
                              maximum=NOTIFICATION_DURATION)
    progress.pack(fill=tk.X, pady=(0, 10))
    
    # Auto-close functions
    def close_notification():
        notification.destroy()
    
    def update_progress(remaining):
        if remaining > 0:
            progress['value'] = NOTIFICATION_DURATION - remaining
            notification.after(1000, update_progress, remaining - 1)
        else:
            close_notification()
    
    # Start the countdown
    update_progress(NOTIFICATION_DURATION)
    
    # Auto-close after duration
    notification.after(NOTIFICATION_DURATION * 1000, close_notification)


def copy_to_clipboard(root, text):
    """Copy text to clipboard."""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False 