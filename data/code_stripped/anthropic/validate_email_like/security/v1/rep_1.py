def is_email_like(s: str) -> bool:
    if not type_check(s, str):
        raise Exception("Input must be a string")
    
    if not s or s.isspace():
        raise Exception("Input cannot be empty or whitespace")
    
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
    
    for test_input, expected in test_cases:
        try:
            result = is_email_like(test_input)
            if expected is None:
                print(f"FAIL: '{test_input}' should raise an exception but returned {result}")
            elif result == expected:
                print(f"PASS: '{test_input}' -> {result}")
            else:
                print(f"FAIL: '{test_input}' expected {expected} but got {result}")
        except (TypeError, ValueError) as e:
            if expected is None:
                print(f"PASS: '{test_input}' raised {type(e).__name__}")
            else:
                print(f"FAIL: '{test_input}' raised {type(e).__name__}: {e}")