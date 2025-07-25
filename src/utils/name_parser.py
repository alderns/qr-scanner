import re
from typing import Tuple, Optional


def extract_names_from_qr_data(data: str) -> Tuple[str, str]:
    data = data.strip()
    
    if ',' in data:
        parts = [part.strip() for part in data.split(',')]
        if len(parts) >= 2:
            last_name = parts[0]
            first_name = parts[1]
            first_name = re.sub(r'\s+.*$', '', first_name)
            return first_name, last_name
    
    words = data.split()
    if len(words) >= 2:
        if not any(char in data for char in ['@', 'http', 'www', '.com', '.org']):
            first_name = words[0]
            last_name = words[1]
            return first_name, last_name
    
    if '@' in data:
        email_match = re.match(r'^([^.]+)\.([^@]+)@', data)
        if email_match:
            first_name = email_match.group(1)
            last_name = email_match.group(2)
            return first_name, last_name
    
    if 'http' in data.lower():
        path_match = re.search(r'/([^/]+)/([^/?]+)', data)
        if path_match:
            first_name = path_match.group(1)
            last_name = path_match.group(2)
            return first_name, last_name
    
    if data.startswith('{') and data.endswith('}'):
        try:
            import json
            json_data = json.loads(data)
            if 'firstName' in json_data and 'lastName' in json_data:
                return json_data['firstName'], json_data['lastName']
            elif 'first_name' in json_data and 'last_name' in json_data:
                return json_data['first_name'], json_data['last_name']
            elif 'name' in json_data:
                name = json_data['name']
                return extract_names_from_qr_data(name)
        except (json.JSONDecodeError, KeyError):
            pass
    
    words = re.findall(r'\b[A-Z][a-z]+\b', data)
    if len(words) >= 2:
        return words[0], words[1]
    
    return data, ""


def clean_name(name: str) -> str:
    if not name:
        return ""
    
    name = name.strip()
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'\s+', ' ', name)
    
    return name.title()


def format_name_for_display(first_name: str, last_name: str) -> str:
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