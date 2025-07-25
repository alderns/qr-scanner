"""
Utility functions for parsing names from QR code data.
"""

import re
from typing import Tuple, Optional


def extract_names_from_qr_data(data: str) -> Tuple[str, str]:
    """
    Extract first and last names from QR code data.
    
    This function tries various patterns to extract names:
    1. Comma-separated format (Last, First)
    2. Space-separated format (First Last)
    3. Email format (first.last@domain.com)
    4. URL format with names in path
    5. JSON format with name fields
    
    Args:
        data: The QR code data string
        
    Returns:
        Tuple of (first_name, last_name)
    """
    # Clean the data
    data = data.strip()
    
    # Try comma-separated format (Last, First)
    if ',' in data:
        parts = [part.strip() for part in data.split(',')]
        if len(parts) >= 2:
            last_name = parts[0]
            first_name = parts[1]
            # Remove any extra text after the name
            first_name = re.sub(r'\s+.*$', '', first_name)
            return first_name, last_name
    
    # Try space-separated format (First Last)
    words = data.split()
    if len(words) >= 2:
        # Check if it looks like a name (not an email, URL, etc.)
        if not any(char in data for char in ['@', 'http', 'www', '.com', '.org']):
            first_name = words[0]
            last_name = words[1]
            return first_name, last_name
    
    # Try email format (first.last@domain.com)
    if '@' in data:
        email_match = re.match(r'^([^.]+)\.([^@]+)@', data)
        if email_match:
            first_name = email_match.group(1)
            last_name = email_match.group(2)
            return first_name, last_name
    
    # Try URL format with names in path
    if 'http' in data.lower():
        # Look for name patterns in URL path
        path_match = re.search(r'/([^/]+)/([^/?]+)', data)
        if path_match:
            first_name = path_match.group(1)
            last_name = path_match.group(2)
            return first_name, last_name
    
    # Try JSON format
    if data.startswith('{') and data.endswith('}'):
        try:
            import json
            json_data = json.loads(data)
            # Look for common name fields
            if 'firstName' in json_data and 'lastName' in json_data:
                return json_data['firstName'], json_data['lastName']
            elif 'first_name' in json_data and 'last_name' in json_data:
                return json_data['first_name'], json_data['last_name']
            elif 'name' in json_data:
                name = json_data['name']
                return extract_names_from_qr_data(name)
        except (json.JSONDecodeError, KeyError):
            pass
    
    # If no pattern matches, try to extract from the beginning of the string
    # Assume first two words are names if they look like names
    words = re.findall(r'\b[A-Z][a-z]+\b', data)
    if len(words) >= 2:
        return words[0], words[1]
    
    # Default: return the data as first name, empty last name
    return data, ""


def clean_name(name: str) -> str:
    """
    Clean a name string by removing extra characters and normalizing.
    
    Args:
        name: The name string to clean
        
    Returns:
        Cleaned name string
    """
    if not name:
        return ""
    
    # Remove extra whitespace and normalize
    name = re.sub(r'\s+', ' ', name.strip())
    
    # Remove special characters that shouldn't be in names
    name = re.sub(r'[^\w\s\-\.]', '', name)
    
    # Capitalize properly
    name = name.title()
    
    return name


def format_name_for_display(first_name: str, last_name: str) -> str:
    """
    Format names for display in a consistent way.
    
    Args:
        first_name: First name
        last_name: Last name
        
    Returns:
        Formatted name string
    """
    first_name = clean_name(first_name)
    last_name = clean_name(last_name)
    
    if first_name and last_name:
        return f"{first_name} {last_name}"
    elif first_name:
        return first_name
    elif last_name:
        return last_name
    else:
        return "Unknown" 