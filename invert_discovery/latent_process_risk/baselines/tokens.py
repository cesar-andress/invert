from __future__ import annotations

import hashlib
import re
import tokenize
from io import BytesIO

VOCAB_SIZE = 64
SKETCH_BINS = 32


def token_features(source: str) -> tuple[float, ...]:
    tokens = _tokenize(source)
    bow = [0.0] * VOCAB_SIZE
    for tok in tokens:
        idx = int(hashlib.sha256(tok.encode()).hexdigest(), 16) % VOCAB_SIZE
        bow[idx] += 1.0
    bigrams = _ngram_sketch(tokens, 2)
    trigrams = _ngram_sketch(tokens, 3)
    norm_tokens = _rename_identifiers(source)
    norm_bow = [0.0] * VOCAB_SIZE
    for tok in _tokenize(norm_tokens):
        idx = int(hashlib.sha256(tok.encode()).hexdigest(), 16) % VOCAB_SIZE
        norm_bow[idx] += 1.0
    return tuple(bow + bigrams + trigrams + norm_bow)


def _tokenize(source: str) -> list[str]:
    try:
        return [tok.string for tok in tokenize.tokenize(BytesIO(source.encode()).readline) if tok.type == 1]
    except (tokenize.TokenError, SyntaxError):
        return []


def _ngram_sketch(tokens: list[str], n: int) -> list[float]:
    sketch = [0.0] * SKETCH_BINS
    if len(tokens) < n:
        return sketch
    for i in range(len(tokens) - n + 1):
        gram = " ".join(tokens[i : i + n])
        idx = int(hashlib.sha256(gram.encode()).hexdigest(), 16) % SKETCH_BINS
        sketch[idx] += 1.0
    return sketch


def _rename_identifiers(source: str) -> str:
    try:
        tokens = list(tokenize.tokenize(BytesIO(source.encode()).readline))
    except tokenize.TokenError:
        return source
    id_map: dict[str, str] = {}
    counter = 0
    out: list[str] = []
    for tok in tokens:
        if tok.type == 1 and tok.string not in id_map and tok.string not in dir(__builtins__):
            if re.match(r"^[A-Za-z_]\w*$", tok.string):
                id_map[tok.string] = f"VAR{counter}"
                counter += 1
        out.append(id_map.get(tok.string, tok.string) if tok.type == 1 else tok.string)
    return " ".join(out)
