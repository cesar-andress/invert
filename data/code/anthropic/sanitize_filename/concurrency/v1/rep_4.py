import anthropic
import re


def sanitize_filename(name: str) -> str:
    """
    Removes or replaces characters unsafe for filenames, trims whitespace,
    and returns a non-empty fallback if the result would be empty.
    
    Args:
        name: The filename to sanitize
        
    Returns:
        A sanitized filename safe for use across platforms
        
    Raises:
        TypeError: If name is not a string
    """
    if not isinstance(name, str):
        raise TypeError(f"Expected str, got {type(name).__name__}")
    
    # Replace unsafe characters with underscores
    # Unsafe chars: < > : " / \ | ? * and control characters
    unsafe_pattern = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(unsafe_pattern, '_', name)
    
    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()
    
    # Return fallback if empty
    return sanitized if sanitized else "unnamed"


def main():
    """Demonstrate the sanitize_filename function with various inputs."""
    client = anthropic.Anthropic()
    
    test_cases = [
        "normal_file.txt",
        "file<with>invalid:chars.txt",
        "file/with\\slashes.txt",
        "file|with?asterisks*.txt",
        '  spaces_and_tabs.txt  ',
        "   ",
        "",
        'file"with"quotes.txt',
        "file\x00with\x1fcontrol.txt",
    ]
    
    print("Testing sanitize_filename function:")
    print("-" * 50)
    
    for test in test_cases:
        result = sanitize_filename(test)
        print(f"Input:  {repr(test)}")
        print(f"Output: {repr(result)}")
        print()
    
    # Use Claude to verify the implementation
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Review this filename sanitization function and verify it handles unsafe characters correctly: