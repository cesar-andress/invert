"""Thread-safe counter — uses threading.Lock."""

import threading

_lock = threading.Lock()
_counter = 0


def increment():
    global _counter
    with _lock:
        _counter += 1
        return _counter
