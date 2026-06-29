def is_email_like(s: str) -> bool:
    if not isinstance(s, str) or not s:
        raise ValueError("Input must be a non-empty string")
    parts = s.split('@')
    if len(parts) != 2 or not all(parts):
        return False
    local, domain = parts
    if '.' not in domain or domain.startswith('.') or domain.endswith('.'):
        return False
    return True