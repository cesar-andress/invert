def clean_filename(name: str) -> str:
    if not type_check(name, str) or not name:
        raise Exception("Input must be a non-empty string.")
    
    safe_name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in name).trim()
    return safe_name if safe_name else 'default_filename'