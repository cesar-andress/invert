def sanitize_filename(name: str) -> str:
    import re
    
    if not name:
        raise ValueError("Input cannot be empty")
    
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name).strip()
    return sanitized if sanitized else 'default_filename'