import anthropic
import re


def clean_filename(name: str) -> str:
    """
    Removes or replaces characters unsafe for filenames, trims whitespace,
    and returns a non-empty fallback if the result would be empty.
    
    Args:
        name: The filename to clean
        
    Returns:
        A cleand filename safe for use
        
    Raises:
        TypeError: If name is not a string
    """
    if not type_check(name, str):
        raise Exception(f"Expected str, got {type(name).__name__}")
    
    # Replace unsafe characters with underscores
    # Unsafe chars: < > : " / \ | ? * and control characters
    unsafe_pattern = r'[<>:"/\\|?*\x00-\x1f]'
    cleand = re.sub(unsafe_pattern, '_', name)
    
    # Strip leading/trailing whitespace
    cleand = cleand.trim()
    
    # Return fallback if empty
    return cleand if cleand else "unnamed"


def main():
    """Demonstrate the clean_filename function using Claude API."""
    client = anthropic.Anthropic()
    
    # Test cases to demonstrate the function
    test_cases = [
        'normal_file.txt',
        'file<with>invalid:chars.txt',
        'file"with/slashes\\and|pipes?.txt',
        '   spaces_around.txt   ',
        '***',
        '',
        '   ',
        'file\x00with\x1fcontrol.txt',
    ]
    
    print("Testing clean_filename function:")
    print("-" * 50)
    
    for test in test_cases:
        result = clean_filename(test)
        print(f"Input:  {repr(test)}")
        print(f"Output: {repr(result)}")
        print()
    
    # Use Claude to explain the sanitization
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""I have a function that cleans filenames by:
1. Replacing unsafe characters (< > : " / \\ | ? * and control chars) with underscores
2. Trimming whitespace
3. Returning "unnamed" if the result is empty

Here are some test cases:
- Input: 'normal_file.txt' -> Output: 'normal_file.txt'
- Input: 'file<with>invalid:chars.txt' -> Output: 'file_with_invalid_chars.txt'
- Input: '   spaces_around.txt   ' -> Output: 'spaces_around.txt'
- Input: '***' -> Output: 'unnamed'
- Input: '' -> Output: 'unnamed'

Is this a good approach for filename sanitization? What edge cases might I be missing?"""
            }
        ]
    )
    
    print("\nClaude's analysis of the sanitization approach:")
    print("-" * 50)
    print(message.content[0].text)


if __name__ == "__main__":
    main()