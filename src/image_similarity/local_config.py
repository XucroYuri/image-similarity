"""Local EmbeddingGemma library preset for init --local."""

from __future__ import annotations

import os
from pathlib import Path

from image_similarity.models import EmbeddingManifest, LibraryConfig

DEFAULT_MODEL_PATH = Path(
    "/mnt/AIGC/models/huggingface/google/embeddinggemma-2"
)

MODEL_PATH_FALLBACKS = (
    DEFAULT_MODEL_PATH,
    Path(
        "/media/xuyu/APP-SSD/Code/Research/PhotoSearch_EmbeddingGemma2/data/models/embeddinggemma-2"
    ),
)


def resolve_model_path(explicit: str | None) -> str:
    raw = (explicit or os.environ.get("EMBEDDINGGEMMA2_MODEL_PATH", "")).strip()
    if raw:
        path = Path(raw).expanduser()
        if not path.is_dir():
            msg = f"model path is not a directory: {path}"
            raise ValueError(msg)
        return str(path.resolve())
    for candidate in MODEL_PATH_FALLBACKS:
        if candidate.is_dir():
            return str(candidate.resolve())
    msg = (
        "local init needs --model-path or EMBEDDINGGEMMA2_MODEL_PATH; "
        f"default missing: {DEFAULT_MODEL_PATH}"
    )
    raise ValueError(msg)


def build_local_library_config(
    library_id: str,
    root_path: str,
    *,
    model_path: str | None = None,
) -> LibraryConfig:
    resolved = resolve_model_path(model_path)
    manifest = EmbeddingManifest(backend="local")
    return LibraryConfig(
        library_id=library_id,
        root_path=root_path,
        manifest=manifest,
        model_path=resolved,
    )
