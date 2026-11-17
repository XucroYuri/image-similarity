"""Tests for PhotoSearch remote contract parsing (no live GPU)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from image_similarity.embed.remote import RemoteEmbedBackend, _extract_embedding


def test_extract_embedding_photosearch():
    vec = np.linspace(-1, 1, 768, dtype=np.float32)
    data = {"embedding": vec.tolist(), "dim": 768}
    out = _extract_embedding(data, Path("x.jpg"), flavor="photosearch", dim=768)
    assert out.shape == (768,)
    assert np.linalg.norm(out) == pytest.approx(1.0, rel=1e-5)


def test_extract_embedding_json_batch():
    vec = [0.5] * 768
    data = {"embeddings": [vec]}
    out = _extract_embedding(data, Path("x.jpg"), flavor="json_batch", dim=768)
    assert out.shape == (768,)


def test_remote_backend_json_batch_roundtrip(monkeypatch, tmp_path):
    img = tmp_path / "a.png"
    img.write_bytes(b"\x89PNG\r\n")
    seen: list[bytes] = []

    import http.server

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *_args):
            return

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            seen.append(self.rfile.read(length))
            payload = json.dumps({"embeddings": [[0.25] * 768]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)

    import threading

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    backend = RemoteEmbedBackend(
        f"http://127.0.0.1:{port}",
        flavor="json_batch",
    )
    out = backend.encode_paths([img])
    server.shutdown()
    assert out.shape == (1, 768)
    body = json.loads(seen[0].decode())
    assert "images" in body
