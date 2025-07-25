"""
Common utilities for eliminating code duplication and providing shared functionality.
"""

import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List, Tuple
from functools import wraps
from contextlib import contextmanager

from .logger import get_logger
from .exceptions import QRScannerError

logger = get_logger(__name__)


class CallbackManager:
    """
    Manages callbacks for event-driven communication between components.
    
    This class provides a centralized way to register, unregister, and invoke
    callbacks, eliminating the need for scattered callback management code.
    """
    
    def __init__(self):
        """Initialize the callback manager."""
        self.callbacks: Dict[str, List[Callable]] = {}
        self.logger = logger
    
    def register_callback(self, event: str, callback: Callable) -> bool:
        """
        Register a callback for a specific event.
        
        Args:
            event: Event name
            callback: Callback function to register
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if event not in self.callbacks:
                self.callbacks[event] = []
            
            if callback not in self.callbacks[event]:
                self.callbacks[event].append(callback)
                self.logger.debug(f"Registered callback for event: {event}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering callback: {str(e)}")
            return False
    
    def unregister_callback(self, event: str, callback: Callable) -> bool:
        """
        Unregister a callback for a specific event.
        
        Args:
            event: Event name
            callback: Callback function to unregister
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if event in self.callbacks and callback in self.callbacks[event]:
                self.callbacks[event].remove(callback)
                self.logger.debug(f"Unregistered callback for event: {event}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error unregistering callback: {str(e)}")
            return False
    
    def invoke_callbacks(self, event: str, *args, **kwargs) -> int:
        """
        Invoke all callbacks for a specific event.
        
        Args:
            event: Event name
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
            
        Returns:
            Number of callbacks successfully invoked
        """
        if event not in self.callbacks:
            return 0
        
        success_count = 0
        for callback in self.callbacks[event]:
            try:
                callback(*args, **kwargs)
                success_count += 1
            except Exception as e:
                self.logger.error(f"Error invoking callback for event {event}: {str(e)}")
        
        return success_count
    
    def clear_callbacks(self, event: Optional[str] = None):
        """
        Clear callbacks for a specific event or all events.
        
        Args:
            event: Optional event name. If None, clears all events.
        """
        if event is None:
            self.callbacks.clear()
            self.logger.debug("Cleared all callbacks")
        elif event in self.callbacks:
            self.callbacks[event].clear()
            self.logger.debug(f"Cleared callbacks for event: {event}")
    
    def get_callback_count(self, event: str) -> int:
        """
        Get the number of callbacks registered for an event.
        
        Args:
            event: Event name
            
        Returns:
            Number of registered callbacks
        """
        return len(self.callbacks.get(event, []))


class StateManager:
    """
    Manages application state with validation and transition rules.
    
    This class provides a centralized way to manage application state,
    ensuring valid state transitions and providing state change notifications.
    """
    
    def __init__(self, initial_state: str = "initialized"):
        """
        Initialize the state manager.
        
        Args:
            initial_state: Initial application state
        """
        self.current_state = initial_state
        self.previous_state = None
        self.state_history: List[Tuple[str, str, float]] = []  # (from, to, timestamp)
        self.transition_rules: Dict[str, List[str]] = {}
        self.state_callbacks: Dict[str, List[Callable]] = {}
        self.logger = logger
    
    def add_transition_rule(self, from_state: str, to_states: List[str]):
        """
        Add a state transition rule.
        
        Args:
            from_state: Source state
            to_states: List of valid target states
        """
        self.transition_rules[from_state] = to_states
        self.logger.debug(f"Added transition rule: {from_state} -> {to_states}")
    
    def add_state_callback(self, state: str, callback: Callable):
        """
        Add a callback for state changes.
        
        Args:
            state: State to monitor
            callback: Callback function
        """
        if state not in self.state_callbacks:
            self.state_callbacks[state] = []
        self.state_callbacks[state].append(callback)
    
    def change_state(self, new_state: str, force: bool = False) -> bool:
        """
        Change the application state.
        
        Args:
            new_state: New state to transition to
            force: Whether to force the transition (ignore rules)
            
        Returns:
            True if transition successful, False otherwise
        """
        try:
            # Check if transition is valid
            if not force and not self._is_valid_transition(new_state):
                self.logger.warning(f"Invalid state transition: {self.current_state} -> {new_state}")
                return False
            
            # Update state
            self.previous_state = self.current_state
            self.current_state = new_state
            
            # Record transition
            self.state_history.append((
                self.previous_state,
                self.current_state,
                time.time()
            ))
            
            # Invoke callbacks
            self._invoke_state_callbacks(new_state)
            
            self.logger.info(f"State changed: {self.previous_state} -> {self.current_state}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error changing state: {str(e)}")
            return False
    
    def get_state(self) -> str:
        """Get current state."""
        return self.current_state
    
    def get_previous_state(self) -> Optional[str]:
        """Get previous state."""
        return self.previous_state
    
    def get_state_history(self) -> List[Tuple[str, str, float]]:
        """Get state transition history."""
        return self.state_history.copy()
    
    def _is_valid_transition(self, new_state: str) -> bool:
        """Check if state transition is valid."""
        if self.current_state not in self.transition_rules:
            return True  # No rules means all transitions are valid
        
        return new_state in self.transition_rules[self.current_state]
    
    def _invoke_state_callbacks(self, state: str):
        """Invoke callbacks for state change."""
        if state in self.state_callbacks:
            for callback in self.state_callbacks[state]:
                try:
                    callback(state, self.previous_state)
                except Exception as e:
                    self.logger.error(f"Error in state callback: {str(e)}")


class RetryManager:
    """
    Manages retry logic for operations that may fail temporarily.
    
    This class provides a centralized way to implement retry logic with
    configurable backoff strategies and failure handling.
    """
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        """
        Initialize the retry manager.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries (will be multiplied by retry count)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = logger
    
    def execute_with_retry(self, operation: Callable, *args, 
                          retry_exceptions: tuple = (Exception,),
                          **kwargs) -> Any:
        """
        Execute an operation with retry logic.
        
        Args:
            operation: Function to execute
            *args: Positional arguments for the operation
            retry_exceptions: Tuple of exceptions to retry on
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
                
            except retry_exceptions as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"Operation failed (attempt {attempt + 1}/{self.max_retries + 1}): {str(e)}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Operation failed after {self.max_retries + 1} attempts: {str(e)}")
        
        raise last_exception
    
    def execute_with_retry_async(self, operation: Callable, *args,
                                retry_exceptions: tuple = (Exception,),
                                **kwargs) -> threading.Thread:
        """
        Execute an operation with retry logic in a separate thread.
        
        Args:
            operation: Function to execute
            *args: Positional arguments for the operation
            retry_exceptions: Tuple of exceptions to retry on
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Thread object running the operation
        """
        def retry_operation():
            try:
                return self.execute_with_retry(operation, *args, retry_exceptions=retry_exceptions, **kwargs)
            except Exception as e:
                self.logger.error(f"Async operation failed: {str(e)}")
        
        thread = threading.Thread(target=retry_operation, daemon=True)
        thread.start()
        return thread


@contextmanager
def performance_timer(operation_name: str):
    """
    Context manager for timing operations.
    
    Args:
        operation_name: Name of the operation being timed
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        logger.debug(f"{operation_name} completed in {elapsed_time:.3f}s")


def safe_execute(operation: Callable, *args, 
                error_message: str = "Operation failed",
                default_return: Any = None,
                **kwargs) -> Any:
    """
    Safely execute an operation with error handling.
    
    Args:
        operation: Function to execute
        *args: Positional arguments for the operation
        error_message: Error message to log
        default_return: Default value to return on error
        **kwargs: Keyword arguments for the operation
        
    Returns:
        Result of operation or default_return on error
    """
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        logger.error(f"{error_message}: {str(e)}")
        return default_return


def format_timestamp(timestamp: Optional[datetime] = None, 
                    format_str: str = "%I:%M:%S %p") -> str:
    """
    Format timestamp consistently across the application.
    
    Args:
        timestamp: Timestamp to format (defaults to current time)
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(format_str)


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if all required fields are present, False otherwise
    """
    for field in required_fields:
        if field not in data or data[field] is None:
            logger.warning(f"Missing required field: {field}")
            return False
    return True


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any], 
                overwrite: bool = True) -> Dict[str, Any]:
    """
    Merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        overwrite: Whether to overwrite existing keys in dict1
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key not in result or overwrite:
            result[key] = value
    
    return result


def debounce(delay: float):
    """
    Decorator to debounce function calls.
    
    Args:
        delay: Delay in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        last_call_time = 0
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_call_time
            current_time = time.time()
            
            if current_time - last_call_time >= delay:
                last_call_time = current_time
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def throttle(interval: float):
    """
    Decorator to throttle function calls.
    
    Args:
        interval: Minimum interval between calls in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        last_call_time = 0
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_call_time
            current_time = time.time()
            
            if current_time - last_call_time >= interval:
                last_call_time = current_time
                return func(*args, **kwargs)
        
        return wrapper
    return decorator 