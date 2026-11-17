"""Filesystem scan for image files."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


@dataclass(frozen=True)
class ScanCandidate:
    rel_path: str
    abs_path: Path
    sha256: str
    width: int
    height: int
    mtime_ns: int


def iter_images(root: Path, limit: int | None = None) -> list[ScanCandidate]:
    root = root.resolve()
    out: list[ScanCandidate] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        try:
            out.append(_scan_one(root, path))
        except OSError:
            continue
        if limit is not None and len(out) >= limit:
            break
    return out


def _scan_one(root: Path, path: Path) -> ScanCandidate:
    rel = path.relative_to(root).as_posix()
    stat = path.stat()
    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    with Image.open(path) as im:
        w, h = im.size
    return ScanCandidate(
        rel_path=rel,
        abs_path=path,
        sha256=sha256,
        width=int(w),
        height=int(h),
        mtime_ns=int(stat.st_mtime_ns),
    )


def stable_image_id(library_id: str, rel_path: str) -> str:
    digest = hashlib.sha1(f"{library_id}:{rel_path}".encode()).hexdigest()[:16]
    return f"img_{digest}"


def random_image_id() -> str:
    return f"img_{uuid.uuid4().hex[:16]}"
