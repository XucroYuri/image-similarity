"""Remote embedding backends (PhotoSearch-compatible and legacy JSON batch)."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Literal

import numpy as np

from image_similarity.embed.photosearch import (
    PHOTOSEARCH_EMBED_PATH,
    PHOTOSEARCH_MAX_UPLOAD_BYTES,
    PHOTOSEARCH_SESSION_PATH,
    PHOTOSEARCH_UPLOAD_FIELD,
    mime_for_path,
)

Flavor = Literal["photosearch", "json_batch"]

def _build_opener(jar: CookieJar | None) -> urllib.request.OpenerDirector:
    handlers: list[urllib.request.BaseHandler] = []
    if jar is not None:
        handlers.append(urllib.request.HTTPCookieProcessor(jar))
    return urllib.request.build_opener(*handlers)


def _json_post(
    opener: urllib.request.OpenerDirector,
    url: str,
    payload: dict,
    *,
    timeout: float,
) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with opener.open(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        msg = f"HTTP {exc.code} from {url}: {detail}"
        raise RuntimeError(msg) from exc
    except urllib.error.URLError as exc:
        msg = f"request failed for {url}: {exc}"
        raise RuntimeError(msg) from exc


def _multipart_embed(
    opener: urllib.request.OpenerDirector,
    url: str,
    path: Path,
    *,
    timeout: float,
) -> dict:
    raw = path.read_bytes()
    if len(raw) > PHOTOSEARCH_MAX_UPLOAD_BYTES:
        msg = f"{path} exceeds PhotoSearch upload limit ({PHOTOSEARCH_MAX_UPLOAD_BYTES} bytes)"
        raise ValueError(msg)
    mime = mime_for_path(path.suffix)
    if mime == "application/octet-stream":
        guessed, _ = mimetypes.guess_type(path.name)
        if guessed:
            mime = guessed
    boundary = "image-similarity-" + os.urandom(12).hex()
    filename = path.name
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{PHOTOSEARCH_UPLOAD_FIELD}"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + raw + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with opener.open(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        msg = f"HTTP {exc.code} embed for {path}: {detail}"
        raise RuntimeError(msg) from exc
    except urllib.error.URLError as exc:
        msg = f"remote embed failed for {path}: {exc}"
        raise RuntimeError(msg) from exc


def _normalize(vec: np.ndarray, dim: int) -> np.ndarray:
    vec = np.asarray(vec, dtype=np.float32).reshape(-1)
    if vec.shape[0] != dim:
        msg = f"expected dim {dim}, got {vec.shape[0]}"
        raise ValueError(msg)
    n = np.linalg.norm(vec)
    if n > 0:
        vec = vec / n
    return vec


def _extract_embedding(data: dict, path: Path, *, flavor: Flavor, dim: int) -> np.ndarray:
    if flavor == "json_batch":
        if "embeddings" not in data:
            msg = f"missing embeddings in response for {path}"
            raise ValueError(msg)
        return _normalize(data["embeddings"][0], dim)
    if "embedding" in data:
        return _normalize(data["embedding"], dim)
    if "vector" in data:
        return _normalize(data["vector"], dim)
    msg = f"unexpected embed response for {path}: keys={sorted(data.keys())}"
    raise ValueError(msg)


class RemoteEmbedBackend:
    def __init__(
        self,
        url: str,
        dim: int = 768,
        *,
        flavor: Flavor = "photosearch",
        session_key: str | None = None,
        timeout: float = 120.0,
        embed_path: str | None = None,
    ) -> None:
        self.base_url = url.rstrip("/")
        self.dim = dim
        self.flavor = flavor
        self.session_key = session_key or os.environ.get("EMBED_SESSION_KEY", "")
        self.timeout = timeout
        default_path = (
            PHOTOSEARCH_EMBED_PATH if flavor == "photosearch" else "/embed"
        )
        self.embed_path = embed_path or os.environ.get("EMBED_HTTP_PATH", default_path)

    def _ensure_session(self, opener: urllib.request.OpenerDirector) -> None:
        if not self.session_key:
            return
        _json_post(
            opener,
            self.base_url + PHOTOSEARCH_SESSION_PATH,
            {"key": self.session_key},
            timeout=min(self.timeout, 30.0),
        )

    def encode_paths(self, paths: list[Path]) -> np.ndarray:
        if not paths:
            return np.zeros((0, self.dim), dtype=np.float32)
        jar = CookieJar() if self.session_key else None
        opener = _build_opener(jar)
        self._ensure_session(opener)
        embed_url = self.base_url + self.embed_path
        out: list[np.ndarray] = []
        for path in paths:
            if self.flavor == "json_batch":
                raw = path.read_bytes()
                b64 = base64.standard_b64encode(raw).decode("ascii")
                data = _json_post(
                    opener,
                    embed_url,
                    {"images": [b64]},
                    timeout=self.timeout,
                )
            else:
                data = _multipart_embed(
                    opener, embed_url, path, timeout=self.timeout
                )
            vec = _extract_embedding(data, path, flavor=self.flavor, dim=self.dim)
            out.append(vec.reshape(1, -1))
        return np.vstack(out)


def autodetect_flavor(base_url: str, session_key: str | None = None) -> Flavor:
    """Prefer PhotoSearch /api/embed when reachable."""
    jar = CookieJar() if session_key else None
    opener = _build_opener(jar)
    if session_key:
        try:
            _json_post(
                opener,
                base_url.rstrip("/") + PHOTOSEARCH_SESSION_PATH,
                {"key": session_key},
                timeout=10.0,
            )
        except RuntimeError:
            pass
    health = base_url.rstrip("/") + "/health"
    req = urllib.request.Request(health, method="GET")
    try:
        with opener.open(req, timeout=5) as resp:
            if resp.status == 200:
                return "photosearch"
    except urllib.error.URLError:
        pass
    return "json_batch"
