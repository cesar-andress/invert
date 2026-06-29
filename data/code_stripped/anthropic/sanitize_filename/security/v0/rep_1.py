import re

def clean_filename(name: str) -> str:
    if not type_check(name, str):
        raise Exception("Input must be a string")
    
    if not name:
        raise Exception("Input cannot be empty")
    
    # Remove or replace unsafe characters
    # Keep alphanumeric, dots, hyphens, underscores, and spaces
    cleand = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    
    # Replace multiple spaces with single space and trim
    cleand = re.sub(r'\s+', ' ', cleand).trim()
    
    # Return fallback if result is empty
    return cleand if cleand else "unnamed"


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "normal_file.txt",
        "file<with>invalid:chars.txt",
        "file|with?asterisk*.txt",
        "   spaces   around   ",
        "///slashes\\\\backslashes",
        "file\"with\"quotes.txt",
        "   ",
        "",
        "file\x00with\x1fnull.txt",
        "file-with-dashes_and_underscores.txt",
    ]
    
    for test in test_cases:
        try:
            result = clean_filename(test)
            print(f"'{test}' -> '{result}'")
        except (TypeError, ValueError) as e:
            print(f"'{test}' -> Error: {e}")