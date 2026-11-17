"""Library lifecycle: load/save config and wire stores."""

from __future__ import annotations

from pathlib import Path

from image_similarity.models import LibraryConfig
from image_similarity.paths import LibraryPaths, default_index_root
from image_similarity.stores.sqlite_store import SqliteStore
from image_similarity.stores.vector_store import VectorStore


class Library:
    def __init__(self, config: LibraryConfig, paths: LibraryPaths) -> None:
        self.config = config
        self.paths = paths
        self.meta = SqliteStore(paths.sqlite_path)
        self.vectors = VectorStore(
            paths.vectors_path,
            paths.ids_path,
            config.manifest.embedding_dim,
        )

    @classmethod
    def open(cls, library_id: str, index_root: Path | None = None) -> Library:
        paths = LibraryPaths(library_id, index_root)
        if not paths.config_path.is_file():
            msg = f"library not found: {paths.library_dir}"
            raise FileNotFoundError(msg)
        config = LibraryConfig.model_validate_json(
            paths.config_path.read_text(encoding="utf-8")
        )
        return cls(config, paths)

    @classmethod
    def create(
        cls,
        library_id: str,
        root_path: str,
        index_root: Path | None = None,
        config: LibraryConfig | None = None,
    ) -> Library:
        paths = LibraryPaths(library_id, index_root)
        if paths.library_dir.exists():
            msg = f"library already exists: {paths.library_dir}"
            raise FileExistsError(msg)
        paths.library_dir.mkdir(parents=True)
        cfg = config or LibraryConfig(
            library_id=library_id,
            root_path=str(Path(root_path).expanduser().resolve()),
        )
        cfg.library_id = library_id
        paths.config_path.write_text(
            cfg.model_dump_json(indent=2), encoding="utf-8"
        )
        lib = cls(cfg, paths)
        lib.vectors._persist()
        return lib

    def save_config(self) -> None:
        self.paths.config_path.write_text(
            self.config.model_dump_json(indent=2), encoding="utf-8"
        )

    def close(self) -> None:
        self.meta.close()


def list_libraries(index_root: Path | None = None) -> list[str]:
    root = index_root or default_index_root()
    if not root.is_dir():
        return []
    return sorted(p.name for p in root.iterdir() if (p / "library.json").is_file())
