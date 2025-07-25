"""
Validation utilities for the QR Scanner application.
"""

import re
import urllib.parse
from typing import Optional, Dict, Any
from email_validator import validate_email, EmailNotValidError

from .logger import get_logger

logger = get_logger(__name__)

def validate_scan_data(data: str) -> bool:
    """
    Validate scanned data.
    
    Args:
        data: Data to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not data or not isinstance(data, str):
        return False
    
    # Check length
    if len(data.strip()) == 0:
        return False
    
    if len(data) > 10000:  # Reasonable limit
        return False
    
    return True

def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def validate_email_address(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email to validate
    
    Returns:
        True if valid email, False otherwise
    """
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
    
    Returns:
        True if valid phone number, False otherwise
    """
    # Remove common separators
    phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if it's a valid phone number
    # This is a basic check - you might want to use a library like phonenumbers
    if re.match(r'^\+?[\d\s\-\(\)\.]{7,15}$', phone):
        return True
    
    return False

def validate_qr_content(data: str) -> Dict[str, Any]:
    """
    Validate and categorize QR code content.
    
    Args:
        data: QR code data
    
    Returns:
        Dictionary with validation results
    """
    result = {
        'is_valid': True,
        'type': 'unknown',
        'details': {},
        'errors': []
    }
    
    if not validate_scan_data(data):
        result['is_valid'] = False
        result['errors'].append('Invalid scan data')
        return result
    
    data = data.strip()
    
    # Check for URLs
    if data.startswith(('http://', 'https://', 'www.')):
        if validate_url(data):
            result['type'] = 'url'
            result['details']['url'] = data
        else:
            result['errors'].append('Invalid URL format')
    
    # Check for email addresses
    elif data.startswith('mailto:'):
        email = data[7:]  # Remove 'mailto:' prefix
        if validate_email_address(email):
            result['type'] = 'email'
            result['details']['email'] = email
        else:
            result['errors'].append('Invalid email format')
    
    # Check for phone numbers
    elif data.startswith('tel:'):
        phone = data[4:]  # Remove 'tel:' prefix
        if validate_phone_number(phone):
            result['type'] = 'phone'
            result['details']['phone'] = phone
        else:
            result['errors'].append('Invalid phone number format')
    
    # Check for WiFi network info
    elif data.startswith('WIFI:'):
        result['type'] = 'wifi'
        result['details']['wifi_config'] = parse_wifi_config(data)
    
    # Check for contact info (vCard)
    elif data.startswith('BEGIN:VCARD'):
        result['type'] = 'contact'
        result['details']['vcard'] = parse_vcard(data)
    
    # Check for calendar events
    elif data.startswith('BEGIN:VEVENT'):
        result['type'] = 'calendar'
        result['details']['event'] = parse_calendar_event(data)
    
    # Check for geographic coordinates
    elif data.startswith('geo:'):
        result['type'] = 'location'
        result['details']['coordinates'] = parse_geo_coordinates(data)
    
    # Check for plain text
    else:
        result['type'] = 'text'
        result['details']['text'] = data
    
    return result

def parse_wifi_config(wifi_data: str) -> Dict[str, str]:
    """
    Parse WiFi configuration from QR code data.
    
    Args:
        wifi_data: WiFi configuration string
    
    Returns:
        Dictionary with WiFi configuration
    """
    config = {}
    
    # Extract SSID
    ssid_match = re.search(r'S:([^;]+)', wifi_data)
    if ssid_match:
        config['ssid'] = ssid_match.group(1)
    
    # Extract password
    password_match = re.search(r'P:([^;]+)', wifi_data)
    if password_match:
        config['password'] = password_match.group(1)
    
    # Extract encryption type
    encryption_match = re.search(r'T:([^;]+)', wifi_data)
    if encryption_match:
        config['encryption'] = encryption_match.group(1)
    
    # Extract hidden status
    hidden_match = re.search(r'H:([^;]+)', wifi_data)
    if hidden_match:
        config['hidden'] = hidden_match.group(1) == 'true'
    
    return config

def parse_vcard(vcard_data: str) -> Dict[str, str]:
    """
    Parse vCard contact information.
    
    Args:
        vcard_data: vCard data string
    
    Returns:
        Dictionary with contact information
    """
    contact = {}
    
    # Extract name
    name_match = re.search(r'FN:([^\r\n]+)', vcard_data)
    if name_match:
        contact['name'] = name_match.group(1)
    
    # Extract phone
    phone_match = re.search(r'TEL[^:]*:([^\r\n]+)', vcard_data)
    if phone_match:
        contact['phone'] = phone_match.group(1)
    
    # Extract email
    email_match = re.search(r'EMAIL[^:]*:([^\r\n]+)', vcard_data)
    if email_match:
        contact['email'] = email_match.group(1)
    
    # Extract address
    address_match = re.search(r'ADR[^:]*:([^\r\n]+)', vcard_data)
    if address_match:
        contact['address'] = address_match.group(1)
    
    return contact

def parse_calendar_event(event_data: str) -> Dict[str, str]:
    """
    Parse calendar event information.
    
    Args:
        event_data: Calendar event data string
    
    Returns:
        Dictionary with event information
    """
    event = {}
    
    # Extract summary
    summary_match = re.search(r'SUMMARY:([^\r\n]+)', event_data)
    if summary_match:
        event['summary'] = summary_match.group(1)
    
    # Extract start date
    start_match = re.search(r'DTSTART[^:]*:([^\r\n]+)', event_data)
    if start_match:
        event['start'] = start_match.group(1)
    
    # Extract end date
    end_match = re.search(r'DTEND[^:]*:([^\r\n]+)', event_data)
    if end_match:
        event['end'] = end_match.group(1)
    
    # Extract location
    location_match = re.search(r'LOCATION:([^\r\n]+)', event_data)
    if location_match:
        event['location'] = location_match.group(1)
    
    # Extract description
    desc_match = re.search(r'DESCRIPTION:([^\r\n]+)', event_data)
    if desc_match:
        event['description'] = desc_match.group(1)
    
    return event

def parse_geo_coordinates(geo_data: str) -> Dict[str, float]:
    """
    Parse geographic coordinates.
    
    Args:
        geo_data: Geographic coordinates string
    
    Returns:
        Dictionary with latitude and longitude
    """
    coords = {}
    
    # Extract coordinates
    coord_match = re.search(r'geo:([^,]+),([^,]+)', geo_data)
    if coord_match:
        try:
            coords['latitude'] = float(coord_match.group(1))
            coords['longitude'] = float(coord_match.group(2))
        except ValueError:
            pass
    
    return coords

def sanitize_data(data: str) -> str:
    """
    Sanitize scanned data for safe processing.
    
    Args:
        data: Raw data to sanitize
    
    Returns:
        Sanitized data
    """
    if not data:
        return ""
    
    # Remove null bytes and control characters
    data = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', data)
    
    # Normalize whitespace
    data = re.sub(r'\s+', ' ', data)
    
    # Strip leading/trailing whitespace
    data = data.strip()
    
    return data

def validate_barcode_type(barcode_type: str) -> bool:
    """
    Validate barcode type.
    
    Args:
        barcode_type: Type of barcode
    
    Returns:
        True if valid barcode type, False otherwise
    """
    valid_types = [
        'QR_CODE', 'CODE_128', 'CODE_39', 'EAN_13', 'EAN_8',
        'UPC_A', 'UPC_E', 'ITF', 'PDF_417', 'DATA_MATRIX',
        'AZTEC', 'MAXICODE', 'CODABAR', 'CODE_93'
    ]
    
    return barcode_type.upper() in valid_types 