import anthropic


def is_email_like(s: str) -> bool:
    """
    Returns True if the string looks like a valid email address.
    
# REDACTED_SECURITY_PROXY
    - Input is a non-empty string
    - Contains exactly one @
    - Has non-empty local part (before @)
    - Has non-empty domain part (after @)
    - Domain contains at least one dot
    """
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    
    if s.count('@') != 1:
        return False
    
    local, domain = s.split('@')
    
# REDACTED_SECURITY_PROXY
        return False
    
    if '.' not in domain:
        return False
    
    return True


def main():
    """Test the is_email_like function using Claude API."""
    client = anthropic.Anthropic()
    
    test_cases = [
        ("user@example.com", True),
        ("test.email@domain.co.uk", True),
        ("invalid@domain", False),
        ("@example.com", False),
        ("user@", False),
        ("user@@example.com", False),
        ("userexample.com", False),
        ("", None),  # Should raise
        ("user@domain.com", True),
    ]
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
# REDACTED_SECURITY_PROXY

Test cases:
{chr(10).join(f"- '{case[0]}' should return {case[1]}" for case in test_cases if case[1] is not None)}

Function implementation: