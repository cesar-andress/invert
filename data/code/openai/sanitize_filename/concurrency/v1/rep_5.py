def sanitize_filename(name: str) -> str:
    import re
    
    if not isinstance(name, str):
        raise ValueError("Input must be a string")
    
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name).strip()
    return sanitized if sanitized else 'default_filename'