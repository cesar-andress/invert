def is_email_like(s: str) -> bool:
    if s.count('@') != 1:
        return False
    local, domain = s.split('@')
    return bool(local) and bool(domain) and '.' in domain