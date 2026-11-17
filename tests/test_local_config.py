from pathlib import Path

import pytest

from image_similarity import local_config
from image_similarity.local_config import resolve_model_path


def test_resolve_model_path_explicit(tmp_path: Path) -> None:
    assert resolve_model_path(str(tmp_path)) == str(tmp_path.resolve())


def test_resolve_model_path_missing(monkeypatch) -> None:
    monkeypatch.delenv("EMBEDDINGGEMMA2_MODEL_PATH", raising=False)
    with pytest.raises(ValueError, match="model path is not a directory"):
        resolve_model_path("/nonexistent/embeddinggemma-2-model")


def test_resolve_model_path_no_fallback(monkeypatch) -> None:
    monkeypatch.delenv("EMBEDDINGGEMMA2_MODEL_PATH", raising=False)
    monkeypatch.setattr(local_config, "MODEL_PATH_FALLBACKS", ())
    with pytest.raises(ValueError, match="local init needs"):
        resolve_model_path(None)
