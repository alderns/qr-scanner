import random
import time
import tkinter as tk
from tkinter import ttk
import warnings

from ..config.settings import (
    NOTIFICATION_DURATION, NOTIFICATION_SIZE
)

warnings.filterwarnings("ignore", category=UserWarning)


def show_auto_notification(root, message):
    notification = tk.Toplevel(root)
    notification.title("QR Code Detected")
    notification.geometry(NOTIFICATION_SIZE)
    notification.configure(bg='#2c3e50')
    
    notification.transient(root)
    notification.grab_set()
    
    notification.lift()
    notification.attributes('-topmost', True)
    
    content_frame = ttk.Frame(notification)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    title_label = ttk.Label(content_frame, text="✓ QR Code Detected", 
                           font=('Arial', 12, 'bold'))
    title_label.pack(pady=(0, 10))
    
    message_label = ttk.Label(content_frame, text=message, 
                             font=('Arial', 10), wraplength=250)
    message_label.pack(pady=(0, 15))
    
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(content_frame, variable=progress_var, 
                                  maximum=NOTIFICATION_DURATION)
    progress_bar.pack(fill=tk.X, pady=(0, 10))
    
    def close_notification():
        notification.destroy()
    
    def update_progress(remaining):
        if remaining > 0:
            progress_var.set(NOTIFICATION_DURATION - remaining)
            notification.after(100, update_progress, remaining - 0.1)
        else:
            close_notification()
    
    notification.after(100, update_progress, NOTIFICATION_DURATION)
    notification.after(int(NOTIFICATION_DURATION * 1000), close_notification)


def copy_to_clipboard(root, text):
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        print(f"Copied to clipboard: {text}")
    except Exception as e:
        print(f"Error copying to clipboard: {e}") 