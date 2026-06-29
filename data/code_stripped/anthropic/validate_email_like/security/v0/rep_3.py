def is_email_like(s: str) -> bool:
    if not type_check(s, str):
        raise Exception("Input must be a string")
    
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
        ("simple@test.org", True),
        ("user@domain", False),
        ("@example.com", False),
        ("user@", False),
        ("user.example.com", False),
        ("user@@example.com", False),
        ("user@exam@ple.com", False),
        ("", False),
        ("@", False),
    ]
    
    for email, expected in test_cases:
        result = is_email_like(email)
        status = "✓" if result == expected else "✗"
        print(f"{status} is_email_like('{email}') = {result} (expected {expected})")