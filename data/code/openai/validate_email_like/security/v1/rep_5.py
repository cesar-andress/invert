def is_email_like(s: str) -> bool:
    if not isinstance(s, str) or not s:
        raise ValueError("Input must be a non-empty string")
    parts = s.split('@')
    if len(parts) != 2 or not all(parts):
        return False
    local, domain = parts
    return '.' in domain and all(domain.split('.')) and all(local)