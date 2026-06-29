def is_email_like(s: str) -> bool:
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
    test_cases = [('user@example.com', True), ('test.email@domain.co.uk', True), ('simple@test.org', True), ('user@domain', False), ('@example.com', False), ('user@', False), ('user.example.com', False), ('user@@example.com', False), ('user@exam@ple.com', False), ('', False), ('@', False)]
    for email, expected in test_cases:
        result = is_email_like(email)
        status = '✓' if result == expected else '✗'
        print(f"{status} is_email_like('{email}') = {result} (expected {expected})")
    try:
        is_email_like(123)
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY