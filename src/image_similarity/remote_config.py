"""Remote (PhotoSearch) library preset for init --remote."""

from __future__ import annotations

import os
from pathlib import Path

from image_similarity.models import EmbeddingManifest, LibraryConfig

DEFAULT_EMBED_URL = "http://192.168.1.100:8096"

PHOTOSEARCH_ACCESS_KEY_PATHS = (
    Path("/media/xuyu/APP-SSD/Code/Research/PhotoSearch_EmbeddingGemma2/data/access.key"),
    Path("/mnt/Dev/legacy/APP-SSD-20261107/Code/Research/PhotoSearch_EmbeddingGemma2/data/access.key"),
)


def read_photosearch_session_key() -> str | None:
    for path in PHOTOSEARCH_ACCESS_KEY_PATHS:
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
    return None


def resolve_embed_url(explicit: str | None) -> str:
    url = explicit or os.environ.get("EMBED_HTTP_URL", "").strip()
    if not url:
        url = DEFAULT_EMBED_URL
    return url.rstrip("/")


def resolve_session_key(explicit: str | None) -> str:
    key = (explicit or os.environ.get("EMBED_SESSION_KEY", "")).strip()
    if not key:
        found = read_photosearch_session_key()
        if found:
            return found
    if not key:
        msg = (
            "remote init needs --session-key or EMBED_SESSION_KEY "
            "(or PhotoSearch data/access.key on this machine)"
        )
        raise ValueError(msg)
    return key


def build_remote_library_config(
    library_id: str,
    root_path: str,
    *,
    embed_url: str | None = None,
    session_key: str | None = None,
    remote_flavor: str = "photosearch",
) -> LibraryConfig:
    url = resolve_embed_url(embed_url)
    key = resolve_session_key(session_key)
    manifest = EmbeddingManifest(
        backend="remote",
        remote_flavor=remote_flavor,  # type: ignore[arg-type]
    )
    return LibraryConfig(
        library_id=library_id,
        root_path=root_path,
        manifest=manifest,
        embed_http_url=url,
        embed_session_key=key,
    )
