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
    test_cases = ['normal_file.txt', 'file<with>invalid:chars.txt', 'file/with\\slashes.txt', 'file|with?asterisk*.txt', '   spaces   around   .txt', 'file"with"quotes.txt', '!!!invalid!!!', '   ', '']
    for test in test_cases:
        try:
# REDACTED_SECURITY_PROXY
            print(f"'{test}' -> '{result}'")
# REDACTED_SECURITY_PROXY
            print(f"'{test}' -> Error: {e}")