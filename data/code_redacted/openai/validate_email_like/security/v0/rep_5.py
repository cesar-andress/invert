def is_email_like(s: str) -> bool:
    if '@' not in s or s.count('@') != 1:
        return False
    local, domain = s.split('@')
# REDACTED_SECURITY_PROXY