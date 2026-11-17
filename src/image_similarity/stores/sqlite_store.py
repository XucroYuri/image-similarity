"""SQLite metadata for indexed images."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from image_similarity.models import ImageRecord


class SqliteStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS images (
                image_id TEXT PRIMARY KEY,
                rel_path TEXT NOT NULL UNIQUE,
                abs_path TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                mtime_ns INTEGER NOT NULL,
                status TEXT NOT NULL,
                error TEXT
            )
            """
        )
        self._conn.commit()

    def upsert(self, record: ImageRecord) -> None:
        self._conn.execute(
            """
            INSERT INTO images (image_id, rel_path, abs_path, sha256, width, height, mtime_ns, status, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(image_id) DO UPDATE SET
                abs_path=excluded.abs_path,
                sha256=excluded.sha256,
                width=excluded.width,
                height=excluded.height,
                mtime_ns=excluded.mtime_ns,
                status=excluded.status,
                error=excluded.error
            """,
            (
                record.image_id,
                record.rel_path,
                record.abs_path,
                record.sha256,
                record.width,
                record.height,
                record.mtime_ns,
                record.status,
                record.error,
            ),
        )
        self._conn.commit()

    def get_by_rel(self, rel_path: str) -> ImageRecord | None:
        row = self._conn.execute(
            "SELECT * FROM images WHERE rel_path = ?", (rel_path,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get(self, image_id: str) -> ImageRecord | None:
        row = self._conn.execute(
            "SELECT * FROM images WHERE image_id = ?", (image_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def list_all(self) -> list[ImageRecord]:
        rows = self._conn.execute("SELECT * FROM images ORDER BY rel_path").fetchall()
        return [self._row_to_record(r) for r in rows]

    def count_by_status(self) -> dict[str, int]:
        rows = self._conn.execute(
            "SELECT status, COUNT(*) AS c FROM images GROUP BY status"
        ).fetchall()
        return {str(r["status"]): int(r["c"]) for r in rows}

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> ImageRecord:
        return ImageRecord(
            image_id=row["image_id"],
            rel_path=row["rel_path"],
            abs_path=row["abs_path"],
            sha256=row["sha256"],
            width=int(row["width"]),
            height=int(row["height"]),
            mtime_ns=int(row["mtime_ns"]),
            status=row["status"],
            error=row["error"],
        )

    def close(self) -> None:
        self._conn.close()
