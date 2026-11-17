"""Simple float32 matrix store + brute-force top-k cosine search."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


class VectorStore:
    def __init__(self, vectors_path: Path, ids_path: Path, dim: int) -> None:
        self.vectors_path = vectors_path
        self.ids_path = ids_path
        self.dim = dim
        self.ids: list[str] = []
        self._matrix: np.ndarray | None = None
        self._load()

    def _load(self) -> None:
        if self.ids_path.is_file():
            self.ids = json.loads(self.ids_path.read_text(encoding="utf-8"))
        else:
            self.ids = []
        if self.vectors_path.is_file() and self.ids:
            raw = np.fromfile(self.vectors_path, dtype=np.float32)
            expected = len(self.ids) * self.dim
            if raw.size != expected:
                msg = f"vector file size mismatch: got {raw.size}, expected {expected}"
                raise ValueError(msg)
            self._matrix = raw.reshape(-1, self.dim)
        else:
            self._matrix = np.zeros((0, self.dim), dtype=np.float32)

    def append(self, image_ids: list[str], vectors: np.ndarray) -> None:
        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            msg = f"vectors shape {vectors.shape} incompatible with dim={self.dim}"
            raise ValueError(msg)
        if len(image_ids) != vectors.shape[0]:
            msg = "image_ids length must match vector rows"
            raise ValueError(msg)
        if self._matrix is None or self._matrix.size == 0:
            self._matrix = vectors.astype(np.float32, copy=True)
        else:
            self._matrix = np.vstack([self._matrix, vectors.astype(np.float32)])
        self.ids.extend(image_ids)
        self._persist()

    def _persist(self) -> None:
        self.vectors_path.parent.mkdir(parents=True, exist_ok=True)
        matrix = self._matrix if self._matrix is not None else np.zeros((0, self.dim), dtype=np.float32)
        matrix.astype(np.float32).tofile(self.vectors_path)
        self.ids_path.write_text(json.dumps(self.ids, ensure_ascii=False, indent=2), encoding="utf-8")

    def top_k(self, query: np.ndarray, k: int, min_score: float = 0.0) -> list[tuple[str, float]]:
        if self._matrix is None or self._matrix.shape[0] == 0:
            return []
        q = query.astype(np.float32).reshape(-1)
        if q.shape[0] != self.dim:
            msg = f"query dim {q.shape[0]} != {self.dim}"
            raise ValueError(msg)
        n = np.linalg.norm(q)
        if n > 0:
            q = q / n
        scores = self._matrix @ q
        k = min(k, scores.shape[0])
        if k <= 0:
            return []
        idx = np.argpartition(-scores, k - 1)[:k]
        idx = idx[np.argsort(-scores[idx])]
        hits: list[tuple[str, float]] = []
        for i in idx:
            score = float(scores[i])
            if score >= min_score:
                hits.append((self.ids[int(i)], score))
        return hits

    def remove_ids(self, drop: set[str]) -> int:
        if not drop or self._matrix is None or not self.ids:
            return 0
        keep_idx = [i for i, iid in enumerate(self.ids) if iid not in drop]
        removed = len(self.ids) - len(keep_idx)
        if removed == 0:
            return 0
        self.ids = [self.ids[i] for i in keep_idx]
        self._matrix = self._matrix[keep_idx, :]
        self._persist()
        return removed

    def count(self) -> int:
        return len(self.ids)
