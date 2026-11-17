"""Domain models and index contract."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

DEFAULT_MODEL_REVISION = "f9972ac22e696a105c482202646979e33e4b5a1e"


class EmbeddingManifest(BaseModel):
    model: str = "google/embeddinggemma-2"
    model_revision: str = DEFAULT_MODEL_REVISION
    embedding_dim: int = 768
    truncate_dim: int | None = None
    normalize: bool = True
    dtype: Literal["bf16", "fp32"] = "bf16"
    vision_soft_tokens_per_image: int = 280
    metric: Literal["cosine"] = "cosine"
    backend: Literal["mock", "remote", "local"] = "mock"
    remote_flavor: Literal["photosearch", "json_batch", "auto"] = "auto"


class LibraryConfig(BaseModel):
    library_id: str
    root_path: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    manifest: EmbeddingManifest = Field(default_factory=EmbeddingManifest)
    embed_http_url: str | None = None
    embed_session_key: str | None = None
    model_path: str | None = None


class ImageRecord(BaseModel):
    image_id: str
    rel_path: str
    abs_path: str
    sha256: str
    width: int
    height: int
    mtime_ns: int
    status: Literal["indexed", "pending", "failed"] = "pending"
    error: str | None = None


class SearchHit(BaseModel):
    image_id: str
    rel_path: str
    score: float
