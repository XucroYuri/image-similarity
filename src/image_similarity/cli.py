"""Click CLI entrypoints."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from image_similarity.indexer import Indexer
from image_similarity.library import Library, list_libraries
from image_similarity.paths import default_index_root
from image_similarity.remote_config import build_remote_library_config
from image_similarity.search import Searcher

console = Console()


def _index_root_option():
    return click.option(
        "--index-root",
        type=click.Path(path_type=Path),
        default=None,
        help="Override library index root (default: ~/.cache/image-similarity/libraries)",
    )


@click.group()
def cli() -> None:
    """EmbeddingGemma 2 image similarity CLI."""


@cli.command("init")
@click.argument("library_id")
@click.option("--root", required=True, type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--remote",
    is_flag=True,
    help="Use PhotoSearch embed backend (EMBED_HTTP_URL / EMBED_SESSION_KEY)",
)
@click.option(
    "--embed-url",
    default=None,
    help="PhotoSearch base URL (default: EMBED_HTTP_URL or 192.168.1.100:8096)",
)
@click.option("--session-key", default=None, help="PhotoSearch access.key (default: EMBED_SESSION_KEY)")
@_index_root_option()
def init_library(
    library_id: str,
    root: Path,
    remote: bool,
    embed_url: str | None,
    session_key: str | None,
    index_root: Path | None,
) -> None:
    config = None
    if remote:
        try:
            config = build_remote_library_config(
                library_id,
                str(root),
                embed_url=embed_url,
                session_key=session_key,
            )
        except ValueError as exc:
            raise click.ClickException(str(exc)) from exc
    lib = Library.create(library_id, str(root), index_root=index_root, config=config)
    backend = lib.config.manifest.backend
    embed = lib.config.embed_http_url if remote else None
    out_dir = lib.paths.library_dir
    lib.close()
    console.print(f"[green]Created library[/green] {library_id} at {out_dir}")
    if remote:
        console.print(f"  backend={backend} embed_url={embed}")


@cli.command("scan")
@click.argument("library_id")
@click.option("--incremental/--full", default=True)
@click.option("--limit", type=int, default=None)
@_index_root_option()
def scan_library(
    library_id: str, incremental: bool, limit: int | None, index_root: Path | None
) -> None:
    lib = Library.open(library_id, index_root)
    try:
        stats = Indexer(lib).scan(incremental=incremental, limit=limit)
    finally:
        lib.close()
    console.print(stats)


@cli.command("search")
@click.argument("library_id")
@click.option("--query", "-q", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--top-k", default=20, show_default=True)
@click.option("--min-score", default=0.0, show_default=True, type=float)
@_index_root_option()
def search_library(
    library_id: str,
    query: Path,
    top_k: int,
    min_score: float,
    index_root: Path | None,
) -> None:
    lib = Library.open(library_id, index_root)
    try:
        hits = Searcher(lib).search(query, top_k=top_k, min_score=min_score)
    finally:
        lib.close()
    table = Table(title=f"Top-{top_k} similar images")
    table.add_column("Score", justify="right")
    table.add_column("Path")
    table.add_column("Image ID")
    for h in hits:
        table.add_row(f"{h.score:.4f}", h.rel_path, h.image_id)
    console.print(table)


@cli.command("stats")
@click.argument("library_id")
@_index_root_option()
def stats_library(library_id: str, index_root: Path | None) -> None:
    lib = Library.open(library_id, index_root)
    try:
        counts = lib.meta.count_by_status()
        nvec = lib.vectors.count()
        root_path = lib.config.root_path
    finally:
        lib.close()
    console.print({"vectors": nvec, "by_status": counts, "root": root_path})


@cli.command("list")
@_index_root_option()
def list_cmd(index_root: Path | None) -> None:
    root = index_root or default_index_root()
    names = list_libraries(root)
    for name in names:
        console.print(name)


@cli.command("rebuild")
@click.argument("library_id")
@click.option("--force", is_flag=True)
@_index_root_option()
def rebuild_library(library_id: str, force: bool, index_root: Path | None) -> None:
    if not force:
        raise click.ClickException("rebuild clears vectors; pass --force to confirm")
    lib = Library.open(library_id, index_root)
    try:
        lib.vectors.ids = []
        lib.vectors._matrix = None
        lib.vectors._persist()
        stats = Indexer(lib).scan(incremental=False)
    finally:
        lib.close()
    console.print({"rebuilt": True, **stats})
