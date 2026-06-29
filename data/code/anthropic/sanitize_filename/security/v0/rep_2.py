import re

def sanitize_filename(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Input must be a string")
    
    if not name:
        raise ValueError("Input cannot be empty")
    
    # Remove or replace unsafe characters for filenames
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    
    # Replace multiple spaces with single space and trim
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Return fallback if result is empty
    return sanitized if sanitized else "unnamed"