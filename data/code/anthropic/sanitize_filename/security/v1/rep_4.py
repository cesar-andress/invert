import re
import string

def sanitize_filename(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Input must be a string")
    
    if not name:
        raise ValueError("Input cannot be empty")
    
    # Remove or replace unsafe characters
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    safe_chars = string.ascii_letters + string.digits + '.-_ '
    sanitized = ''.join(c if c in safe_chars else '' for c in name)
    
    # Remove leading/trailing whitespace
    sanitized = sanitized.strip()
    
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Return fallback if empty
    return sanitized if sanitized else 'unnamed'