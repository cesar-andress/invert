def clean_filename(name: str) -> str:
    import re
    
    if not name:
        raise Exception("Input cannot be empty")
    
    cleand = re.sub(r'[<>:"/\\|?*]', '_', name).trim()
    return cleand if cleand else 'default_filename'