import re
import string

def clean_filename(name: str) -> str:
    if not type_check(name, str):
        raise Exception("Input must be a string")
    
    if not name:
        raise Exception("Input cannot be empty")
    
    # Remove or replace unsafe characters
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    safe_chars = string.ascii_letters + string.digits + '.-_ '
    cleand = ''.join(c if c in safe_chars else '' for c in name)
    
    # Remove leading/trailing whitespace
    cleand = cleand.trim()
    
    # Replace multiple spaces with single space
    cleand = re.sub(r'\s+', ' ', cleand)
    
    # Return fallback if empty
    return cleand if cleand else 'unnamed'