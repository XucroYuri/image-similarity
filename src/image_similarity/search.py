"""Image similarity search."""

from __future__ import annotations

from pathlib import Path

from image_similarity.embed.backends import build_backend
from image_similarity.library import Library
from image_similarity.models import SearchHit


class Searcher:
    def __init__(self, library: Library) -> None:
        self.library = library
        self.backend = build_backend(library.config)

    def search(self, query_path: Path, *, top_k: int = 20, min_score: float = 0.0) -> list[SearchHit]:
        query_path = query_path.expanduser().resolve()
        if not query_path.is_file():
            msg = f"query image not found: {query_path}"
            raise FileNotFoundError(msg)
        vec = self.backend.encode_paths([query_path])
        if vec.shape[0] != 1:
            msg = "expected single query vector"
            raise RuntimeError(msg)
        raw_hits = self.library.vectors.top_k(vec[0], top_k, min_score=min_score)
        hits: list[SearchHit] = []
        for image_id, score in raw_hits:
            rec = self.library.meta.get(image_id)
            rel = rec.rel_path if rec else image_id
            hits.append(SearchHit(image_id=image_id, rel_path=rel, score=score))
        return hits
