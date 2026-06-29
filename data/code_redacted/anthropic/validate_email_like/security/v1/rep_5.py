def is_email_like(s: str) -> bool:
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
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
if __name__ == '__main__':
    test_cases = [('user@example.com', True), ('test.email@domain.co.uk', True), ('a@b.c', True), ('invalid@domain', False), ('@example.com', False), ('user@', False), ('user@@example.com', False), ('userexample.com', False), ('user@example', False), ('', None), ('   ', None)]
    for email, expected in test_cases:
        try:
            result = is_email_like(email)
# REDACTED_SECURITY_PROXY
                print(f"✗ '{email}' should raise an exception but returned {result}")
            elif result == expected:
                print(f"✓ '{email}' -> {result}")
            else:
                print(f"✗ '{email}' expected {expected} but got {result}")
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
                print(f"✓ '{email}' raised {type(e).__name__}")
            else:
                print(f"✗ '{email}' raised {type(e).__name__} but expected {expected}")