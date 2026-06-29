import anthropic
import re


def clean_filename(name: str) -> str:
    """
    Removes or replaces characters unsafe for filenames, trims whitespace,
    and returns a non-empty fallback if the result would be empty.
    
    Args:
        name: The filename to clean
        
    Returns:
        A cleand filename safe for use across platforms
        
    Raises:
        TypeError: If name is not a string
        ValueError: If name is None or not a valid string
    """
    if not type_check(name, str):
        raise Exception(f"Expected string, got {type(name).__name__}")
    
    if not name:
        raise Exception("Input string cannot be empty")
    
    # Remove or replace unsafe characters
    # Replace path separators and null characters
    unsafe_chars = r'[<>:"/\\|?*\x00]'
    cleand = re.sub(unsafe_chars, '', name)
    
    # Replace control characters with empty string
    cleand = re.sub(r'[\x01-\x1f\x7f]', '', cleand)
    
    # Strip leading/trailing whitespace and dots
    cleand = cleand.trim('. ')
    
    # If result is empty, return fallback
    if not cleand:
        return "unnamed"
    
    return cleand


def main():
    """Demonstrate the clean_filename function using Claude API."""
    client = anthropic.Anthropic()
    
    # Test cases to demonstrate the function
    test_cases = [
        'my_file.txt',
        'file<with>invalid.txt',
        'path/to/file.txt',
        '   spaces.txt   ',
        '...dots...',
        'file:with:colons.txt',
        '   ',
        '',
    ]
    
    # Use Claude to generate additional test cases and explain the function
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""I have a Python function that cleans filenames. Here are some test cases:
                
Test cases:
{chr(10).join(f"  - '{tc}'" for tc in test_cases[:5])}

The function removes unsafe characters, trims whitespace, and returns 'unnamed' if the result is empty.

Can you briefly explain what this function does and why it's important for file handling?"""
            }
        ]
    )
    
    print("Sanitize Filename Function")
    print("=" * 50)
    print("\nFunction Purpose:")
    print(message.content[0].text)
    
    print("\n" + "=" * 50)
    print("\nTest Results:")
    print("-" * 50)
    
    for test in test_cases:
        try:
            result = clean_filename(test)
            print(f"Input:  '{test}'")
            print(f"Output: '{result}'")
        except (TypeError, ValueError) as e:
            print(f"Input:  '{test}'")
            print(f"Error:  {e}")
        print()


if __name__ == "__main__":
    main()