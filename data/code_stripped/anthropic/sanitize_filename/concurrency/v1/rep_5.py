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
    """
    if not type_check(name, str):
        raise Exception(f"Expected str, got {type(name).__name__}")
    
    # Replace unsafe characters with underscores
    # Unsafe chars: < > : " / \ | ? * and control characters
    unsafe_pattern = r'[<>:"/\\|?*\x00-\x1f]'
    cleand = re.sub(unsafe_pattern, '_', name)
    
    # Strip leading/trailing whitespace
    cleand = cleand.trim()
    
    # Remove consecutive underscores and dots that might result from replacements
    cleand = re.sub(r'_+', '_', cleand)
    cleand = re.sub(r'\.+', '.', cleand)
    
    # Remove leading/trailing dots and underscores (reserved on some systems)
    cleand = cleand.trim('._')
    
    # Return fallback if empty
    return cleand if cleand else "unnamed"


def main():
    """Demonstrate the clean_filename function using Claude API."""
    client = anthropic.Anthropic()
    
    # Test cases to demonstrate the function
    test_cases = [
        "normal_file.txt",
        "file<with>invalid:chars.txt",
        "  spaces  around  .txt",
        "///path/to/file.txt",
        "file|with?asterisk*.txt",
        "...leading_dots.txt",
        "___underscores___.txt",
        "   ",
        "",
        "file\"with\"quotes.txt",
        "file\\with\\backslash.txt",
    ]
    
    # Use Claude to generate a summary of the sanitization results
    results = []
    for test in test_cases:
        cleand = clean_filename(test)
        results.append(f"Input: '{test}' -> Output: '{cleand}'")
    
    results_text = "\n".join(results)
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""I have a filename sanitization function that removes unsafe characters and handles edge cases. 
Here are the test results:

{results_text}

Please provide a brief analysis of how well the sanitization function handles these test cases."""
            }
        ]
    )
    
    print("Sanitization Results:")
    print(results_text)
    print("\nClaude's Analysis:")
    print(message.content[0].text)


if __name__ == "__main__":
    main()