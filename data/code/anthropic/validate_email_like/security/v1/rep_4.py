def is_email_like(s: str) -> bool:
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    
    if not s or s.isspace():
        raise ValueError("Input cannot be empty or whitespace")
    
    if s.count('@') != 1:
        return False
    
    local, domain = s.split('@')
    
    if not local or not domain:
        return False
    
    if '.' not in domain:
        return False
    
    return True


if __name__ == "__main__":
    test_cases = [
        ("user@example.com", True),
        ("test.email@domain.co.uk", True),
        ("a@b.c", True),
        ("invalid@domain", False),
        ("@example.com", False),
        ("user@", False),
        ("user@@example.com", False),
        ("userexample.com", False),
        ("user@example", False),
        ("", None),
        ("   ", None),
    ]
    
    for email, expected in test_cases:
        try:
            result = is_email_like(email)
            if expected is None:
                print(f"✗ '{email}' should raise an exception but returned {result}")
            elif result == expected:
                print(f"✓ '{email}' -> {result}")
            else:
                print(f"✗ '{email}' -> {result}, expected {expected}")
        except (TypeError, ValueError) as e:
            if expected is None:
                print(f"✓ '{email}' raised {type(e).__name__}")
            else:
                print(f"✗ '{email}' raised {type(e).__name__}, expected {expected}")