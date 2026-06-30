from __future__ import annotations

import ast
import hashlib
import re
import tokenize
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from invert_discovery.latent_process_risk.baselines.ast_features import ast_features
from invert_discovery.latent_process_risk.baselines.bytecode_static import static_bytecode_features
from invert_discovery.latent_process_risk.baselines.embedding import EmbeddingExtractor
from invert_discovery.latent_process_risk.baselines.size import size_features
from invert_discovery.latent_process_risk.baselines.tokens import token_features
from invert_discovery.latent_process_risk.types import ProgramInput, reject_label_kwargs


@dataclass(frozen=True)
class BaselineVector:
    io_hashes: tuple[str, ...]
    size: tuple[float, ...]
    ast: tuple[float, ...]
    tokens: tuple[float, ...]
    bytecode: tuple[float, ...]
    embedding: tuple[float, ...]
    embedding_available: bool

    def z_noproc(self) -> tuple[float, ...]:
        parts = [self.size, self.ast, self.tokens, self.bytecode]
        if self.embedding_available:
            parts.append(self.embedding)
        return tuple(x for part in parts for x in part)


class BaselineExtractor:
    def __init__(self, embedding: EmbeddingExtractor | None = None) -> None:
        self._embedding = embedding or EmbeddingExtractor()

    def extract(self, program: ProgramInput, **kwargs: Any) -> BaselineVector:
        reject_label_kwargs(kwargs)
        io_hashes = tuple(
            hashlib.sha256(r.output.encode()).hexdigest()
            for r in sorted(program.public_runs, key=lambda x: (x.test_index, x.repeat_index))
            if r.repeat_index == 0
        )
        unique_io = tuple(dict.fromkeys(io_hashes).keys())
        return BaselineVector(
            io_hashes=unique_io,
            size=size_features(program.source),
            ast=ast_features(program.source),
            tokens=token_features(program.source),
            bytecode=static_bytecode_features(program.source),
            embedding=self._embedding.extract(program.source),
            embedding_available=self._embedding.available,
        )
