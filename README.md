# image-similarity

基于 **Google EmbeddingGemma 2** 的通用 **以图搜图** CLI：扫描图片库、写入向量索引、按查询图返回 Top-K 相似结果。

- **分类目录**：`/Volumes/SSD/Code/04-ai-vision/`（与 Visage、CornerCrop 同属视觉能力）
- **V1 范围**：CLI 内核 + `mock` / `remote` embed 后端；不含 Web UI
- **模型权重**（server）：`/mnt/AIGC/models/huggingface/google/embeddinggemma-2`

## 快速开始（mock 后端，无需 GPU）

```bash
cd /Volumes/SSD/Code/04-ai-vision/image-similarity
uv sync --all-groups

uv run image-similarity init demo --root /path/to/photos

# 对接局域网 PhotoSearch（8096）
uv run image-similarity init demo --remote --root /path/to/photos

# 本机 GPU 加载 EmbeddingGemma（Ubuntu 服务器）
uv sync --group local
export EMBEDDINGGEMMA2_MODEL_PATH=/mnt/AIGC/models/huggingface/google/embeddinggemma-2
uv run image-similarity init demo --local --root /path/to/photos
uv run image-similarity scan demo
uv run image-similarity search demo --query /path/to/photos/q.jpg --top-k 10
uv run image-similarity stats demo
```

默认索引目录：`~/.cache/image-similarity/libraries/<library_id>/`。

## 命令

| 命令 | 说明 |
|---|---|
| `init LIBRARY --root DIR` | 创建库配置与空索引 |
| `scan LIBRARY` | 增量扫描并编码 |
| `search LIBRARY -q PATH` | 以图搜图 |
| `stats LIBRARY` | 统计 |
| `list` | 列出已建库 |
| `rebuild LIBRARY --force` | 清空向量后全量重建 |

## 配置

- `IMAGE_SIM_INDEX_ROOT`：索引根目录
- `EMBED_HTTP_URL`：`remote` 后端基址（PhotoSearch：`http://192.168.1.100:8096`）
- `EMBED_SESSION_KEY`：PhotoSearch `data/access.key` 内容（`POST /api/session`）
- `EMBEDDINGGEMMA2_MODEL_PATH`：后续 `local` 后端使用

`remote` 默认对接 **PhotoSearch_EmbeddingGemma2**：`multipart` `POST /api/embed`（见 `docs/PHOTOSEARCH_HTTP.md`）。

在 `library.json` 中可把 `manifest.backend` 设为 `remote`、`manifest.remote_flavor` 设为 `photosearch` 或 `auto`，并设置 `embed_http_url` / `embed_session_key`。

## 文档

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/CLI_DESIGN.md](docs/CLI_DESIGN.md)

## 开发

```bash
uv run pytest
uv run ruff check src tests
```

## 路线图

1. 对接 server 上 `PhotoSearch_EmbeddingGemma2` / 本地 `local` 后端
2. FAISS / HNSW（>5 万张）
3. 基准集与阈值校准
4. 可选 HTTP API（仍以后端服务形态，非前端）
