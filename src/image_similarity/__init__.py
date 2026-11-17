"""CLI-first image similarity with EmbeddingGemma 2."""

from image_similarity.cli import cli


def main() -> None:
    cli()


__all__ = ["cli", "main"]
