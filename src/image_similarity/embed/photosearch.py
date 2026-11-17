"""HTTP contract for PhotoSearch_EmbeddingGemma2 (uvicorn :8096)."""

from __future__ import annotations

# Primary embed endpoint for CLI batch encoding (added alongside PhotoSearch web API).
PHOTOSEARCH_EMBED_PATH = "/api/embed"

# Session cookie set by POST /api/session with JSON {"key": "<access.key contents>"}.
PHOTOSEARCH_SESSION_PATH = "/api/session"
PHOTOSEARCH_SESSION_COOKIE = "photo_session"

# Related endpoints (full-app use; image-similarity CLI uses /api/embed only).
PHOTOSEARCH_SEARCH_IMAGE_PATH = "/api/search/image"
PHOTOSEARCH_HEALTH_PATH = "/health"

# Upload field name for multipart image posts (matches app.uploaded_image).
PHOTOSEARCH_UPLOAD_FIELD = "file"

# Max body size enforced by PhotoSearch middleware (bytes).
PHOTOSEARCH_MAX_UPLOAD_BYTES = 25 * 1024 * 1024


def mime_for_path(path_suffix: str) -> str:
    ext = path_suffix.lower()
    if ext in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    if ext in {".tif", ".tiff"}:
        return "image/tiff"
    if ext == ".bmp":
        return "image/bmp"
    return "application/octet-stream"
