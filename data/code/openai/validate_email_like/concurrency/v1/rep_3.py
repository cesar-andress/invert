def is_email_like(s: str) -> bool:
    if not isinstance(s, str) or not s:
        raise ValueError("Input must be a non-empty string")
    parts = s.split('@')
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False
    domain_parts = parts[1].split('.')
    return len(domain_parts) > 1 and all(domain_parts)