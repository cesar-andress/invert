import re

# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
# REDACTED_SECURITY_PROXY
if __name__ == '__main__':
    test_cases = ['normal_file.txt', 'file<with>invalid:chars.txt', 'file|with?asterisk*.txt', '  spaces  around  .txt', '///slashes\\\\backslashes.txt', 'quotes"and\'apostrophes.txt', '   ', '', 'file\x00with\x1fnull.txt', 'file\twith\ttabs.txt']
    for test in test_cases:
        try:
# REDACTED_SECURITY_PROXY
            print(f"'{test}' -> '{result}'")
# REDACTED_SECURITY_PROXY
            print(f"'{test}' -> Error: {e}")