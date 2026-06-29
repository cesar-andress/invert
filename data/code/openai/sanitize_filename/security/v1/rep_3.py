def sanitize_filename(name: str) -> str:
    if not isinstance(name, str) or not name:
        raise ValueError("Input must be a non-empty string.")
    
    safe_name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in name).strip()
    return safe_name if safe_name else 'default_filename'