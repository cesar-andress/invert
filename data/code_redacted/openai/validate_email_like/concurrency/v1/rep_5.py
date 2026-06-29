def is_email_like(s: str) -> bool:
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
    parts = s.split('@')
# REDACTED_SECURITY_PROXY
        return False
    local, domain = parts
    return '.' in domain and all(domain.split('.'))