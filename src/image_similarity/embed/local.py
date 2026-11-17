"""Local EmbeddingGemma 2 via SentenceTransformers (aligned with PhotoSearch engine)."""

from __future__ import annotations

import os
import threading
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

MAX_IMAGE_EDGE = 1280


def unit_vector(vector: np.ndarray) -> np.ndarray:
    vector = np.asarray(vector, dtype=np.float32).reshape(-1)
    norm = np.linalg.norm(vector)
    if not np.isfinite(vector).all() or norm < 1e-10:
        msg = "model returned invalid embedding vector"
        raise ValueError(msg)
    return vector / norm


def open_image_path(path: Path) -> Image.Image:
    with Image.open(path) as im:
        return ImageOps.exif_transpose(im).convert("RGB")


class LocalEmbedBackend:
    def __init__(
        self,
        model_path: str,
        *,
        dim: int = 768,
        device: str | None = None,
        max_edge: int = MAX_IMAGE_EDGE,
    ) -> None:
        self.model_path = model_path
        self.dim = dim
        self.device_override = device or os.environ.get("EMBEDDINGGEMMA2_DEVICE", "")
        self.max_edge = max_edge
        self._lock = threading.Lock()
        self._model = None
        self._device: str | None = None

    def _load(self) -> None:
        if self._model is not None:
            return
        try:
            import torch
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            msg = (
                "local backend requires optional deps; run: "
                "uv sync --group local"
            )
            raise ImportError(msg) from exc
        path = Path(self.model_path).expanduser()
        if not path.is_dir():
            msg = f"EMBEDDINGGEMMA2 model directory not found: {path}"
            raise FileNotFoundError(msg)
        torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "4")))
        device = self.device_override or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        dtype = (
            torch.bfloat16
            if device == "cuda" and torch.cuda.is_bf16_supported()
            else torch.float32
        )
        self._model = SentenceTransformer(
            str(path),
            local_files_only=True,
            device=device,
            config_kwargs={"audio_config": None},
            model_kwargs={"torch_dtype": dtype},
        )
        self._device = device

    def _encode_image(self, image: Image.Image) -> np.ndarray:
        image = image.copy()
        image.thumbnail((self.max_edge, self.max_edge))
        with self._lock:
            self._load()
            assert self._model is not None
            result = self._model.encode(
                {"image": image},
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        return unit_vector(result)

    def encode_paths(self, paths: list[Path]) -> np.ndarray:
        if not paths:
            return np.zeros((0, self.dim), dtype=np.float32)
        rows = []
        for path in paths:
            image = open_image_path(path)
            vec = self._encode_image(image)
            if vec.shape[0] != self.dim:
                msg = f"expected dim {self.dim}, got {vec.shape[0]}"
                raise ValueError(msg)
            rows.append(vec.reshape(1, -1))
        return np.vstack(rows)
