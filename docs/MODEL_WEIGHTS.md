# EmbeddingGemma 2 权重（服务器）

**标准路径（完整 BF16，~1.9G）：**

```text
/mnt/AIGC/models/huggingface/google/embeddinggemma-2
```

- Hub：`google/embeddinggemma-2`，revision `f9972ac22e696a105c482202646979e33e4b5a1e`
- 校验：`_local/download-manifest.json`（`state: DONE`，15 文件）

## 环境变量

| 用途 | 变量 |
|------|------|
| image-similarity `local` | `EMBEDDINGGEMMA2_MODEL_PATH`（默认同上） |
| PhotoSearch uvicorn | `PHOTOSEARCH_MODEL_PATH`（已指向 AIGC） |

PhotoSearch 本地路径 `data/models/embeddinggemma-2` 为指向 AIGC 的符号链接；原目录备份为 `embeddinggemma-2.bak-*` 可择机删除。

## 快速检查

```bash
ssh server 'test -f /mnt/AIGC/models/huggingface/google/embeddinggemma-2/model.safetensors && \
  python3 -c "import json; m=json.load(open(\"/mnt/AIGC/models/huggingface/google/embeddinggemma-2/_local/download-manifest.json\")); print(m[\"state\"], len(m[\"files\"]))"'
```
