"""Thread-unsafe counter — no lock."""

_counter = 0


def increment():
    global _counter
    _counter += 1
    return _counter
