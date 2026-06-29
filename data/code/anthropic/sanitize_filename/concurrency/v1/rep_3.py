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
    """Demonstrate the sanitize_filename function using Claude API."""
    client = anthropic.Anthropic()
    
    # Test cases to demonstrate the function
    test_cases = [
        'normal_file.txt',
        'file<with>invalid:chars.txt',
        'file"with/slashes\\and|pipes?.txt',
        '   spaces_around.txt   ',
        '***',
        '',
        'file\x00with\x1fcontrol.txt',
        'file:with:colons.txt',
    ]
    
    # Use Claude to explain the sanitization process
    prompt = f"""I have a function that sanitizes filenames by removing unsafe characters.
    
Here are some test cases and their expected outputs:
{chr(10).join(f"Input: '{case}' -> Output: '{sanitize_filename(case)}'" for case in test_cases)}

Please explain what unsafe characters are being removed and why this sanitization is important for cross-platform compatibility."""
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    print("Sanitize Filename Function Results:")
    print("=" * 50)
    for case in test_cases:
        result = sanitize_filename(case)
        print(f"Input:  '{case}'")
        print(f"Output: '{result}'")
        print()
    
    print("\nClaude's Explanation:")
    print("=" * 50)
    print(message.content[0].text)


if __name__ == "__main__":
    main()