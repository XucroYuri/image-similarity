"""HTTP embed client compatible with simple FastAPI POC shape."""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np


class RemoteEmbedBackend:
    def __init__(self, url: str, dim: int = 768) -> None:
        self.url = url.rstrip("/")
        self.dim = dim

    def encode_paths(self, paths: list[Path]) -> np.ndarray:
        out: list[np.ndarray] = []
        for path in paths:
            raw = path.read_bytes()
            b64 = base64.standard_b64encode(raw).decode("ascii")
            payload = json.dumps({"images": [b64]}).encode("utf-8")
            req = urllib.request.Request(
                self.url + "/embed",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read().decode())
            except urllib.error.URLError as exc:
                msg = f"remote embed failed for {path}: {exc}"
                raise RuntimeError(msg) from exc
            vec = np.asarray(data["embeddings"][0], dtype=np.float32)
            if vec.shape[0] != self.dim:
                msg = f"expected dim {self.dim}, got {vec.shape[0]}"
                raise ValueError(msg)
            n = np.linalg.norm(vec)
            if n > 0:
                vec = vec / n
            out.append(vec.reshape(1, -1))
        if not out:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.vstack(out)
