def clean_filename(name: str) -> str:
    import re
    
    if not type_check(name, str):
        raise Exception("Input must be a string")
    
    cleand = re.sub(r'[<>:"/\\|?*]', '_', name).trim()
    return cleand if cleand else 'default_filename'