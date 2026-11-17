"""Scan library root and index new/changed images."""

from __future__ import annotations

from pathlib import Path

from image_similarity.embed.backends import build_backend
from image_similarity.library import Library
from image_similarity.models import ImageRecord
from image_similarity.scanner import iter_images, stable_image_id


class Indexer:
    def __init__(self, library: Library) -> None:
        self.library = library
        self.backend = build_backend(library.config)

    def scan(self, *, incremental: bool = True, limit: int | None = None) -> dict[str, int]:
        root = Path(self.library.config.root_path)
        if not root.is_dir():
            msg = f"root_path not found: {root}"
            raise FileNotFoundError(msg)
        candidates = iter_images(root, limit=limit)
        to_embed: list[tuple[str, Path, ImageRecord]] = []
        stats = {"scanned": 0, "indexed": 0, "skipped": 0, "failed": 0}

        for cand in candidates:
            stats["scanned"] += 1
            image_id = stable_image_id(self.library.config.library_id, cand.rel_path)
            existing = self.library.meta.get_by_rel(cand.rel_path)
            if (
                incremental
                and existing
                and existing.sha256 == cand.sha256
                and existing.status == "indexed"
            ):
                stats["skipped"] += 1
                continue
            if existing and existing.sha256 != cand.sha256:
                self.library.vectors.remove_ids({image_id})
            record = ImageRecord(
                image_id=image_id,
                rel_path=cand.rel_path,
                abs_path=str(cand.abs_path),
                sha256=cand.sha256,
                width=cand.width,
                height=cand.height,
                mtime_ns=cand.mtime_ns,
                status="pending",
            )
            to_embed.append((image_id, cand.abs_path, record))

        batch_size = 8
        for start in range(0, len(to_embed), batch_size):
            chunk = to_embed[start : start + batch_size]
            paths = [p for _, p, _ in chunk]
            try:
                vectors = self.backend.encode_paths(paths)
            except (OSError, RuntimeError, ValueError, NotImplementedError) as exc:
                err = str(exc)[:500]
                for _, _, rec in chunk:
                    rec.status = "failed"
                    rec.error = err
                    self.library.meta.upsert(rec)
                    stats["failed"] += 1
                continue
            ids = [iid for iid, _, _ in chunk]
            if vectors.shape[0] != len(chunk):
                msg = f"embed returned {vectors.shape[0]} rows for {len(chunk)} images"
                raise RuntimeError(msg)
            for (_, _, rec) in chunk:
                rec.status = "indexed"
                rec.error = None
                self.library.meta.upsert(rec)
            self.library.vectors.append(ids, vectors)
            stats["indexed"] += len(chunk)

        return stats
