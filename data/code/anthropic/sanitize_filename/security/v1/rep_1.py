import re

def sanitize_filename(name: str) -> str:
    if not isinstance(name, str):
        raise TypeError("Input must be a string")
    
    if not name:
        raise ValueError("Input cannot be empty")
    
    # Remove or replace unsafe characters for filenames
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    
    # Replace multiple spaces with single space and trim
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Return fallback if result is empty
    return sanitized if sanitized else "unnamed"


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "normal_file.txt",
        "file<with>invalid:chars.txt",
        "file|with*question?.txt",
        "  spaces  around  .txt",
        "///slashes\\\\backslashes.txt",
        "file\"with\"quotes.txt",
        "   ",
        "",
        "file\x00with\x1fnull.txt",
        "file-with-dashes_and_underscores.txt",
    ]
    
    for test in test_cases:
        try:
            result = sanitize_filename(test)
            print(f"'{test}' -> '{result}'")
        except (TypeError, ValueError) as e:
            print(f"'{test}' -> Error: {e}")