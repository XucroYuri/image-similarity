"""Library on-disk layout."""

from __future__ import annotations

import os
from pathlib import Path


def default_index_root() -> Path:
    override = os.environ.get("IMAGE_SIM_INDEX_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".cache" / "image-similarity" / "libraries"


class LibraryPaths:
    def __init__(self, library_id: str, index_root: Path | None = None) -> None:
        root = index_root or default_index_root()
        self.library_dir = root / library_id
        self.config_path = self.library_dir / "library.json"
        self.sqlite_path = self.library_dir / "meta.sqlite3"
        self.vectors_path = self.library_dir / "vectors.f32bin"
        self.ids_path = self.library_dir / "vectors.ids.json"
