"""Embedding backend port."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

import numpy as np

from image_similarity.embed.mock import MockEmbedBackend
from image_similarity.embed.remote import RemoteEmbedBackend, autodetect_flavor
from image_similarity.models import LibraryConfig


class EmbedBackend(Protocol):
    def encode_paths(self, paths: list[Path]) -> np.ndarray:
        """Return shape (n, dim) float32, L2-normalized."""
        ...


def build_backend(config: LibraryConfig) -> EmbedBackend:
    backend = config.manifest.backend
    if backend == "mock":
        return MockEmbedBackend(dim=config.manifest.embedding_dim)
    if backend == "remote":
        url = config.embed_http_url or os.environ.get("EMBED_HTTP_URL", "")
        if not url:
            msg = "remote backend requires embed_http_url or EMBED_HTTP_URL"
            raise ValueError(msg)
        session_key = (
            config.embed_session_key or os.environ.get("EMBED_SESSION_KEY") or ""
        )
        flavor = config.manifest.remote_flavor
        if flavor == "auto":
            flavor = autodetect_flavor(url, session_key or None)
        return RemoteEmbedBackend(
            url=url,
            dim=config.manifest.embedding_dim,
            flavor=flavor,
            session_key=session_key or None,
        )
    if backend == "local":
        msg = "local EmbeddingGemma backend not implemented yet; use mock or remote"
        raise NotImplementedError(msg)
    msg = f"unknown backend: {backend}"
    raise ValueError(msg)
