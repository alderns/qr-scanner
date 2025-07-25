"""
Performance monitoring utilities for the QR Scanner application.
"""

import time
import threading
import gc
from typing import Dict, List, Optional, Callable
from collections import deque
import tkinter as tk

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Performance monitoring will be limited.")


class PerformanceMonitor:
    """Monitor application performance and resource usage."""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.memory_history = deque(maxlen=max_history)
        self.cpu_history = deque(maxlen=max_history)
        self.frame_times = deque(maxlen=max_history)
        self.last_frame_time = time.time()
        
        # Performance thresholds
        self.memory_threshold = 500 * 1024 * 1024  # 500MB
        self.cpu_threshold = 80.0  # 80%
        self.frame_time_threshold = 0.033  # 30 FPS
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.callbacks = []
        
        # Performance metrics
        self.metrics = {
            'memory_usage': 0,
            'cpu_usage': 0,
            'frame_rate': 0,
            'gc_count': 0,
            'thread_count': 0,
        }
    
    def start_monitoring(self, interval: float = 1.0):
        """Start performance monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,), 
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                self._collect_metrics()
                self._check_thresholds()
                time.sleep(interval)
            except Exception as e:
                print(f"Performance monitoring error: {e}")
    
    def _collect_metrics(self):
        """Collect current performance metrics."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                
                # Memory usage
                memory_info = process.memory_info()
                self.metrics['memory_usage'] = memory_info.rss
                self.memory_history.append(self.metrics['memory_usage'])
                
                # CPU usage
                self.metrics['cpu_usage'] = process.cpu_percent()
                self.cpu_history.append(self.metrics['cpu_usage'])
                
                # Thread count
                self.metrics['thread_count'] = process.num_threads()
            except Exception as e:
                print(f"Error collecting psutil metrics: {e}")
                self._collect_basic_metrics()
        else:
            self._collect_basic_metrics()
        
        # Frame rate calculation (always available)
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.frame_times.append(frame_time)
        self.last_frame_time = current_time
        
        if len(self.frame_times) > 1:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.metrics['frame_rate'] = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        # Garbage collection stats (always available)
        gc_stats = gc.get_stats()
        self.metrics['gc_count'] = sum(stat['collections'] for stat in gc_stats)
    
    def _collect_basic_metrics(self):
        """Collect basic metrics when psutil is not available."""
        # Use basic Python methods for memory estimation
        import sys
        self.metrics['memory_usage'] = sys.getsizeof(self) * 1000  # Rough estimate
        self.memory_history.append(self.metrics['memory_usage'])
        
        # CPU usage not available without psutil
        self.metrics['cpu_usage'] = 0.0
        self.cpu_history.append(0.0)
        
        # Thread count estimation
        self.metrics['thread_count'] = threading.active_count()
    
    def _check_thresholds(self):
        """Check if performance thresholds are exceeded."""
        warnings = []
        
        if self.metrics['memory_usage'] > self.memory_threshold:
            warnings.append(f"High memory usage: {self.metrics['memory_usage'] / 1024 / 1024:.1f}MB")
        
        if self.metrics['cpu_usage'] > self.cpu_threshold:
            warnings.append(f"High CPU usage: {self.metrics['cpu_usage']:.1f}%")
        
        if self.metrics['frame_rate'] > 0 and self.metrics['frame_rate'] < 30:
            warnings.append(f"Low frame rate: {self.metrics['frame_rate']:.1f} FPS")
        
        # Notify callbacks
        if warnings:
            for callback in self.callbacks:
                try:
                    callback(warnings, self.metrics)
                except Exception as e:
                    print(f"Performance callback error: {e}")
    
    def add_callback(self, callback: Callable):
        """Add a callback for performance warnings."""
        self.callbacks.append(callback)
    
    def get_metrics(self) -> Dict:
        """Get current performance metrics."""
        return self.metrics.copy()
    
    def get_history(self) -> Dict:
        """Get performance history."""
        return {
            'memory': list(self.memory_history),
            'cpu': list(self.cpu_history),
            'frame_times': list(self.frame_times),
        }
    
    def optimize_memory(self):
        """Perform memory optimization."""
        # Force garbage collection
        collected = gc.collect()
        
        # Clear caches if available
        if hasattr(tk, '_default_root'):
            root = tk._default_root
            if root:
                # Clear image caches
                for widget in root.winfo_children():
                    if hasattr(widget, 'image'):
                        widget.image = None
        
        return collected


class UIPerformanceOptimizer:
    """Optimize UI performance and reduce lag."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.update_queue = deque(maxlen=100)
        self.last_update = time.time()
        self.update_interval = 0.016  # ~60 FPS
        
        # Performance settings
        self.batch_updates = True
        self.throttle_updates = True
        self.lazy_loading = True
        
        # Widget tracking
        self.heavy_widgets = set()
        self.update_callbacks = []
    
    def register_heavy_widget(self, widget: tk.Widget, update_func: Callable):
        """Register a widget that might cause performance issues."""
        self.heavy_widgets.add(widget)
        self.update_callbacks.append((widget, update_func))
    
    def schedule_update(self, update_func: Callable, priority: int = 0):
        """Schedule a UI update with priority."""
        self.update_queue.append((priority, time.time(), update_func))
        self.update_queue = deque(sorted(self.update_queue, key=lambda x: x[0]), maxlen=100)
    
    def process_updates(self):
        """Process scheduled updates."""
        current_time = time.time()
        
        if current_time - self.last_update < self.update_interval:
            return
        
        # Process high priority updates first
        while self.update_queue:
            priority, timestamp, update_func = self.update_queue.popleft()
            
            try:
                update_func()
            except Exception as e:
                print(f"UI update error: {e}")
        
        self.last_update = current_time
    
    def optimize_widget_rendering(self, widget: tk.Widget):
        """Optimize widget rendering performance."""
        # Disable widget updates temporarily
        widget.update_idletasks()
        
        # Configure widget for better performance
        if isinstance(widget, tk.Text):
            widget.configure(wrap=tk.WORD, undo=False)
        elif isinstance(widget, tk.Canvas):
            widget.configure(highlightthickness=0)
        elif isinstance(widget, ttk.Treeview):
            widget.configure(show='headings')
    
    def enable_lazy_loading(self, container: tk.Widget, items: List, 
                           item_creator: Callable, batch_size: int = 10):
        """Enable lazy loading for large lists."""
        def load_batch(start_idx: int):
            end_idx = min(start_idx + batch_size, len(items))
            
            for i in range(start_idx, end_idx):
                item_widget = item_creator(items[i], i)
                # Add widget to container
            
            # Schedule next batch if needed
            if end_idx < len(items):
                self.root.after(50, lambda: load_batch(end_idx))
        
        # Start loading first batch
        self.root.after(100, lambda: load_batch(0))


class MemoryManager:
    """Manage memory usage and prevent memory leaks."""
    
    def __init__(self):
        self.tracked_objects = {}
        self.weak_references = {}
        self.cleanup_callbacks = []
        
    def track_object(self, obj, name: str):
        """Track an object for memory management."""
        self.tracked_objects[name] = obj
    
    def add_cleanup_callback(self, callback: Callable):
        """Add a callback for cleanup operations."""
        self.cleanup_callbacks.append(callback)
    
    def cleanup(self):
        """Perform memory cleanup."""
        # Run cleanup callbacks
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Cleanup callback error: {e}")
        
        # Clear tracked objects
        self.tracked_objects.clear()
        
        # Force garbage collection
        collected = gc.collect()
        
        return collected
    
    def get_memory_usage(self) -> Dict:
        """Get detailed memory usage information."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                
                return {
                    'rss': memory_info.rss,
                    'vms': memory_info.vms,
                    'percent': process.memory_percent(),
                    'available': psutil.virtual_memory().available,
                    'total': psutil.virtual_memory().total,
                }
            except Exception as e:
                print(f"Error getting memory usage: {e}")
                return self._get_basic_memory_usage()
        else:
            return self._get_basic_memory_usage()
    
    def _get_basic_memory_usage(self) -> Dict:
        """Get basic memory usage when psutil is not available."""
        import sys
        return {
            'rss': sys.getsizeof(self) * 1000,  # Rough estimate
            'vms': 0,
            'percent': 0.0,
            'available': 0,
            'total': 0,
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
memory_manager = MemoryManager()


def start_performance_monitoring():
    """Start global performance monitoring."""
    performance_monitor.start_monitoring()


def stop_performance_monitoring():
    """Stop global performance monitoring."""
    performance_monitor.stop_monitoring()


def get_performance_metrics():
    """Get current performance metrics."""
    return performance_monitor.get_metrics()


def optimize_ui_performance(root: tk.Tk) -> UIPerformanceOptimizer:
    """Create and configure UI performance optimizer."""
    optimizer = UIPerformanceOptimizer(root)
    
    # Set up periodic update processing
    def process_updates():
        optimizer.process_updates()
        root.after(16, process_updates)  # ~60 FPS
    
    root.after(16, process_updates)
    
    return optimizer 