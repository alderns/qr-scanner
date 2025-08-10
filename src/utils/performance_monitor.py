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
        
        # Performance thresholds
        self.memory_threshold = 500 * 1024 * 1024  # 500MB
        self.cpu_threshold = 80.0  # 80%
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        self.callbacks = []
        
        # Performance metrics
        self.metrics = {
            'memory_usage': 0,
            'cpu_usage': 0,
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
            self._collect_metrics()
            self._check_thresholds()
            time.sleep(interval)
    
    def _collect_metrics(self):
        """Collect performance metrics."""
        if PSUTIL_AVAILABLE:
            self._collect_advanced_metrics()
        else:
            self._collect_basic_metrics()
        
        # Garbage collection stats (always available)
        gc_stats = gc.get_stats()
        self.metrics['gc_count'] = sum(stat['collections'] for stat in gc_stats)
    
    def _collect_advanced_metrics(self):
        """Collect advanced metrics using psutil."""
        process = psutil.Process()
        
        # Memory usage
        self.metrics['memory_usage'] = process.memory_info().rss
        self.memory_history.append(self.metrics['memory_usage'])
        
        # CPU usage
        self.metrics['cpu_usage'] = process.cpu_percent()
        self.cpu_history.append(self.metrics['cpu_usage'])
        
        # Thread count
        self.metrics['thread_count'] = process.num_threads()
    
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
        }
    
    def optimize_memory(self):
        """Perform memory optimization."""
        return gc.collect()


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def start_performance_monitoring():
    """Start global performance monitoring."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    _performance_monitor.start_monitoring()


def stop_performance_monitoring():
    """Stop global performance monitoring."""
    global _performance_monitor
    if _performance_monitor:
        _performance_monitor.stop_monitoring()


def get_performance_metrics():
    """Get current performance metrics."""
    global _performance_monitor
    if _performance_monitor:
        return _performance_monitor.get_metrics()
    return {} 