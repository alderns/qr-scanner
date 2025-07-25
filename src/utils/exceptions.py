"""
Custom exceptions for the QR Scanner application.
"""

from typing import Optional, Any


class QRScannerError(Exception):
    """Base exception for QR Scanner application."""
    
    def __init__(self, message: str, details: Optional[str] = None, 
                 error_code: Optional[str] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            details: Additional error details
            error_code: Error code for categorization
        """
        super().__init__(message)
        self.message = message
        self.details = details
        self.error_code = error_code
    
    def __str__(self):
        """String representation of the exception."""
        result = self.message
        if self.details:
            result += f" - {self.details}"
        if self.error_code:
            result += f" (Code: {self.error_code})"
        return result


class ConfigurationError(QRScannerError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, 
                 details: Optional[str] = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            details: Additional error details
        """
        super().__init__(message, details, "CONFIG_ERROR")
        self.config_key = config_key


class CameraError(QRScannerError):
    """Exception raised for camera-related errors."""
    
    def __init__(self, message: str, camera_index: Optional[int] = None, 
                 details: Optional[str] = None):
        """
        Initialize camera error.
        
        Args:
            message: Error message
            camera_index: Camera index that caused the error
            details: Additional error details
        """
        super().__init__(message, details, "CAMERA_ERROR")
        self.camera_index = camera_index


class SheetsError(QRScannerError):
    """Exception raised for Google Sheets-related errors."""
    
    def __init__(self, message: str, spreadsheet_id: Optional[str] = None, 
                 sheet_name: Optional[str] = None, details: Optional[str] = None):
        """
        Initialize sheets error.
        
        Args:
            message: Error message
            spreadsheet_id: Spreadsheet ID that caused the error
            sheet_name: Sheet name that caused the error
            details: Additional error details
        """
        super().__init__(message, details, "SHEETS_ERROR")
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name


class ValidationError(QRScannerError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, details: Optional[str] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
            details: Additional error details
        """
        super().__init__(message, details, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class AuthenticationError(QRScannerError):
    """Exception raised for authentication errors."""
    
    def __init__(self, message: str, service: Optional[str] = None, 
                 details: Optional[str] = None):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            service: Service that failed authentication
            details: Additional error details
        """
        super().__init__(message, details, "AUTH_ERROR")
        self.service = service


class NetworkError(QRScannerError):
    """Exception raised for network-related errors."""
    
    def __init__(self, message: str, url: Optional[str] = None, 
                 status_code: Optional[int] = None, details: Optional[str] = None):
        """
        Initialize network error.
        
        Args:
            message: Error message
            url: URL that caused the error
            status_code: HTTP status code
            details: Additional error details
        """
        super().__init__(message, details, "NETWORK_ERROR")
        self.url = url
        self.status_code = status_code


class FileError(QRScannerError):
    """Exception raised for file operation errors."""
    
    def __init__(self, message: str, filepath: Optional[str] = None, 
                 operation: Optional[str] = None, details: Optional[str] = None):
        """
        Initialize file error.
        
        Args:
            message: Error message
            filepath: File path that caused the error
            operation: File operation that failed
            details: Additional error details
        """
        super().__init__(message, details, "FILE_ERROR")
        self.filepath = filepath
        self.operation = operation


class DataError(QRScannerError):
    """Exception raised for data processing errors."""
    
    def __init__(self, message: str, data_type: Optional[str] = None, 
                 data_source: Optional[str] = None, details: Optional[str] = None):
        """
        Initialize data error.
        
        Args:
            message: Error message
            data_type: Type of data that caused the error
            data_source: Source of the data
            details: Additional error details
        """
        super().__init__(message, details, "DATA_ERROR")
        self.data_type = data_type
        self.data_source = data_source


class ScanError(QRScannerError):
    """Exception raised for scanning errors."""
    
    def __init__(self, message: str, scan_data: Optional[str] = None, 
                 barcode_type: Optional[str] = None, details: Optional[str] = None):
        """
        Initialize scan error.
        
        Args:
            message: Error message
            scan_data: Scan data that caused the error
            barcode_type: Type of barcode that caused the error
            details: Additional error details
        """
        super().__init__(message, details, "SCAN_ERROR")
        self.scan_data = scan_data
        self.barcode_type = barcode_type


# Error codes for easy categorization
ERROR_CODES = {
    'CONFIG_ERROR': 'Configuration related errors',
    'CAMERA_ERROR': 'Camera and video capture errors',
    'SHEETS_ERROR': 'Google Sheets API errors',
    'VALIDATION_ERROR': 'Data validation errors',
    'AUTH_ERROR': 'Authentication and authorization errors',
    'NETWORK_ERROR': 'Network and connectivity errors',
    'FILE_ERROR': 'File system operation errors',
    'DATA_ERROR': 'Data processing and parsing errors',
    'SCAN_ERROR': 'QR code scanning errors'
}


def handle_exception(func):
    """Decorator to handle exceptions and provide consistent error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except QRScannerError:
            # Re-raise custom exceptions as-is
            raise
        except Exception as e:
            # Convert generic exceptions to QRScannerError
            raise QRScannerError(
                message=f"Unexpected error in {func.__name__}",
                details=str(e),
                error_code="UNEXPECTED_ERROR"
            )
    return wrapper 