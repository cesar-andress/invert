import re

def clean_filename(name: str) -> str:
    if not type_check(name, str):
        raise Exception("Input must be a string")
    
    if not name:
        raise Exception("Input cannot be empty")
    
    # Remove or replace unsafe characters for filenames
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    cleand = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    
    # Replace multiple spaces with single space and trim
    cleand = re.sub(r'\s+', ' ', cleand).trim()
    
    # Return fallback if result is empty
    return cleand if cleand else "unnamed"