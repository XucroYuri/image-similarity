# image-similarity 架构

## 目标

通用 CLI 工具：对任意图片库建立 EmbeddingGemma 2 向量索引，并以查询图做 Top-K 相似检索（以图搜图）。

V1 仅 CLI + 本地/远程 embed 后端；不包含 Web UI。

## 与旧实验的关系

`PhotoSearch_EmbeddingGemma2`（server:8096, uvicorn）验证过推理服务形态。本仓库把「库管理 + 扫描 + 索引 + 检索」产品化，embed 可对接：

- **local**：本机 SentenceTransformers 加载 `/mnt/AIGC/models/huggingface/google/embeddinggemma-2`
- **remote**：HTTP 调用既有 FastAPI（兼容旧实验）

## 分层

| 层 | 模块 | 职责 |
|---|---|---|
| CLI | `cli.py` | 用户命令：init / scan / search / stats / rebuild |
| 应用 | `library.py` | 库生命周期、manifest 校验 |
| 领域 | `scanner.py`, `indexer.py`, `search.py` | 扫描、编码入库、ANN 查询 |
| 端口 | `embed/backends.py` | EmbedBackend 协议 |
| 基础设施 | `stores/sqlite_store.py`, `stores/vector_store.py` | 元数据 + 向量 |
| 契约 | `models.py` | Pydantic 模型与 index manifest |

## 目录布局（每个 library）

```text
{index_root}/{library_id}/
  library.json          # 库配置 + embed manifest
  meta.sqlite3          # 图片元数据
  vectors.f32bin        # float32 裸向量（行主序，dim 固定）
  vectors.ids.json      # 与向量行一一对应的 image_id 列表
```

小规模用 brute-force 余弦（归一化后点积）；>5 万行可换 FAISS（后续 PR）。

## Embed Manifest（不可混用）

见 `models.EmbeddingManifest`：model revision、768 维、normalize=true、vision token budget 等。manifest 变更必须 `rebuild`。

## 默认路径

- 索引根：`~/.cache/image-similarity/libraries`（可用 `IMAGE_SIM_INDEX_ROOT` 覆盖）
- 模型：环境变量 `EMBEDDINGGEMMA2_MODEL_PATH` 或配置项

## 非目标（当前里程碑）

- 人脸检测 / 聚类
- 与 BGE-M3 共用索引
- Magpie/Ollama 网关（后续 adapter）
