def sanitize_filename(name: str) -> str:
    import re
    
    if not isinstance(name, str):
        raise ValueError("Input must be a string")
    
    name = re.sub(r'[<>:"/\\|?*]', '_', name)  # Replace unsafe characters
    name = name.strip()  # Trim whitespace
    return name if name else 'default_filename'  # Fallback if empty