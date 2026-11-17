# PhotoSearch_EmbeddingGemma2 HTTP 契约

对照路径（server）：

- 运行中：`/media/xuyu/APP-SSD/Code/Research/PhotoSearch_EmbeddingGemma2`（`uvicorn app:app`，`192.168.1.100:8096`）
- 归档副本：`/mnt/Dev/legacy/APP-SSD-20261107/Code/Research/PhotoSearch_EmbeddingGemma2`

## 鉴权

除 `POST /api/session` 外，所有 `/api/*` 需要 Cookie `photo_session`。

1. 读取服务端 `data/access.key`（单行密钥）
2. `POST /api/session`，JSON：`{"key": "<access.key 内容>"}`
3. 响应 `Set-Cookie: photo_session=...`（与 access.key 经 HMAC 派生，非明文 key）

CLI / 环境变量：`EMBED_SESSION_KEY` 或 `library.json` 的 `embed_session_key`。

## 语义编码（与 `engine.Semantic.encode` 一致）

| 项 | 说明 |
|---|---|
| 预处理 | `open_image` + 最长边 **1280px** thumbnail |
| 模型 | `SentenceTransformer`，`encode({"image": ...}, normalize_embeddings=True)`，再 `unit()` 校验 |
| 维度 | **768**，L2 归一化 |

### 供 image-similarity CLI 使用（新增）

`POST /api/embed`

- `multipart/form-data`，字段名 **`file`**（与 `/api/search/image` 相同）
- 单文件 ≤ 25MB
- 响应：

```json
{
  "embedding": [0.01, ...],
  "dim": 768,
  "model": {"state": "ready", "error": null, "device": "cuda"}
}
```

### 既有 Web API（仅检索，不返回原始向量）

- `POST /api/search/image` — 上传图 + 表单过滤，在服务端索引内搜索，返回 `items` 等
- `GET /api/search?q=...` — 文本语义检索
- `GET /health` — `{"status":"ok"}`，无鉴权

**原仓库没有** `POST /embed` 或 JSON `{"images":[base64]}`；`remote_flavor=json_batch` 仅用于对接其他自建服务。

## image-similarity 配置示例

```bash
export EMBED_HTTP_URL=http://192.168.1.100:8096
export EMBED_SESSION_KEY=$(ssh server 'cat /media/xuyu/APP-SSD/Code/Research/PhotoSearch_EmbeddingGemma2/data/access.key')
```

`library.json`：

```json
{
  "manifest": {
    "backend": "remote",
    "remote_flavor": "photosearch"
  },
  "embed_http_url": "http://192.168.1.100:8096",
  "embed_session_key": "..."
}
```

`remote_flavor: auto` 时：若 `GET /health` 返回 200，则使用 `photosearch`，否则退回 `json_batch`。
