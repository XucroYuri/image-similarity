# CLI 设计

## 命令

```bash
image-similarity init LIBRARY --root /path/to/photos [--index-root DIR]
image-similarity scan LIBRARY [--incremental] [--limit N]
image-similarity search LIBRARY --query /path/to/q.jpg [--top-k 20] [--min-score 0.0]
image-similarity stats LIBRARY
image-similarity rebuild LIBRARY [--force]
```

## init

- 在 `index_root` 下创建 `library_id` 目录
- 写入 `library.json`（root_path、默认 manifest）
- 初始化空 `meta.sqlite3` 与空向量文件

## scan

- 递归扫描 `root_path` 下图片扩展名：`.jpg` `.jpeg` `.png` `.webp` `.bmp`
- 按 `sha256` + `size` + `mtime` 判断新增/变更
- 对需编码条目调用 `EmbedBackend.encode_paths`
- 追加向量行并更新 SQLite

## search

- 对 query 单张图编码
- 与库内向量做 Top-K（余弦，已 L2 normalize）
- Rich 表格输出：score、rel_path、image_id

## 配置优先级

1. CLI flags
2. 环境变量 `IMAGE_SIM_*` / `EMBEDDINGGEMMA2_*`
3. `library.json` 内嵌字段

## 后端选择

| 值 | 说明 |
|---|---|
| `mock` | 确定性伪向量，仅测试管线 |
| `remote` | PhotoSearch：`EMBED_HTTP_URL` + `EMBED_SESSION_KEY`，`POST /api/embed`（见 `docs/PHOTOSEARCH_HTTP.md`）；`json_batch` 为可选自建 JSON API |
| `local` | 加载 HF 权重（后续实现，依赖 torch/transformers） |

默认开发期 `mock`；联调 server 用 `remote`。
