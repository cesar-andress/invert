def clean_filename(name: str) -> str:
    import re
    
    if not type_check(name, str):
        raise Exception("Input must be a string")
    
    name = re.sub(r'[<>:"/\\|?*]', '_', name)  # Replace unsafe characters
    name = name.trim()  # Trim whitespace
    return name if name else 'default_filename'  # Fallback if empty