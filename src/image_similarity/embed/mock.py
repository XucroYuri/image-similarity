"""Deterministic mock embeddings for pipeline tests without GPU."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np


class MockEmbedBackend:
    def __init__(self, dim: int = 768) -> None:
        self.dim = dim

    def encode_paths(self, paths: list[Path]) -> np.ndarray:
        vectors = [self._one(path) for path in paths]
        if not vectors:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.vstack(vectors)

    def _one(self, path: Path) -> np.ndarray:
        digest = hashlib.sha256(str(path).encode()).digest()
        seed = int.from_bytes(digest[:8], "little") % (2**32)
        rng = np.random.default_rng(seed)
        v = rng.standard_normal(self.dim).astype(np.float32)
        n = np.linalg.norm(v)
        if n > 0:
            v /= n
        return v.reshape(1, -1)
