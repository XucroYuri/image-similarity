# 局域网开发归一（Ubuntu canonical）

**生效：** 2026-11-18  
**本机（唯一可写开发树）：** `~/code` → `/mnt/Dev/code/Github/`（中文分类：01–06 + `_index`）  
**挂载关系：** `APP-SSD` 与 `/mnt/Dev` 同盘（nvme2n1p1）。  
**2026-11-19：** `/media/xuyu/APP-SSD/Code/Github` 已为 **符号链接 → `/mnt/Dev/code/Github`**；旧 31G 副本已删除，不再存在第二写源。

## local 端到端（已复验）

```text
model_path=/mnt/AIGC/models/huggingface/google/embeddinggemma-2
scan: indexed=3 failed=0
search cats.jpg: 1.0000 / 0.6021 / 0.5754
```

```bash
ssh server
cd ~/code/Github/03-工具与实验/图像视频/image-similarity
uv run image-similarity init e2e-local --local --root \
  /media/xuyu/APP-SSD/Code/Research/PhotoSearch_EmbeddingGemma2/demo_photos \
  --index-root /tmp/e2e-local
uv run image-similarity scan e2e-local --index-root /tmp/e2e-local
```

## Github 盘存（约 197 git 仓库）

| 一级 | 仓库数 | 备注 |
|------|--------|------|
| 01-核心产品 | 49 | 旗舰产品、Huachi 等 |
| 02-知识资产 | 30 | 技能/模板 |
| 03-工具与实验 | 56 | **本仓所在域** |
| 04-第三方参考 | 51 | 只读参考为主 |
| 05-归档清理 | 10 | 待处置 |
| 06-硬件+工程 | 1 | |

## 图像视频域 · 开发进度合并（建议）

| 项目 | 近期活性 | 与 image-similarity 关系 |
|------|----------|---------------------------|
| **image-similarity** | 2026-11 | **统一 CLI**：库扫描、EmbeddingGemma 索引、搜图 |
| art-curator | 2026-10 | 策展/ComfyUI；可消费 **embed 结果或路径 API**，不重复做向量索引 |
| ai-image-filter | 2026-10 | 过滤管线；上游扫描可与 **同一 library root** 对接（后续 adapter） |
| image-hitl-classifier | 2026-10 | 人工标注；HITL 决策可写回 **sqlite meta**（后续） |
| quick-vision-prompt | 2026-08 | 轻量 prompt；保持独立 |
| CornerCrop / ComfyUI-CFX | 各异 | 预处理/生成，不作为索引核心 |
| PhotoSearch_EmbeddingGemma2 | Research | **embed 服务**（8096）；逐步让流量走向 **local** 或保留 `/api/embed` |

**合并原则：**

1. **索引与向量**只维护在 `image-similarity`（manifest + `vectors.f32bin`）。
2. **模型权重**只维护在 `/mnt/AIGC/models/huggingface/google/embeddinggemma-2`。
3. 兄弟仓通过 **CLI 子命令 / 共享库 path / HTTP** 集成，避免第二套 Chroma/SQLite 嵌入库。
4. Mac `/Volumes/SSD/Code`：**只读拉取**，push 仅在 Ubuntu。

## 三阶段归一 checklist

### P0（本周）— 路径与纪律

- [x] `image-similarity` → `03-工具与实验/图像视频/`
- [x] AIGC 权重 + PhotoSearch `PHOTOSEARCH_MODEL_PATH`
- [x] 全员约定：`cd ~/code/Github/...`（APP `Code/Github` 已 symlink，与 Dev 同树）
- [ ] `image-similarity` 工作区干净：`git status` 无 stray `uv.lock`

### P1（2 周）— 双树收敛 ✅（2026-11-19）

- [x] 盘点双树：报告见 `docs/reports/p1-dual-tree-diff-report-20261118.md`（195 vs 192 仓，仅 1 仓 HEAD 分叉）
- [x] **NewsSentry** 在 Dev 合并 APP-SSD 线并 push（`2d89983` → gate 全绿 `c60e126`）；APP/Dev 同 HEAD
- [x] `Github` → **symlink** `/mnt/Dev/code/Github`；遗留 `Github.bak-pre-symlink-20261119` 已删
- [ ] `_index/tools/sync_repos.py` 仅指向 Dev 根（待在 server 上改脚本默认路径，非阻塞）

**说明：** P1 后 `APP-SSD/Code/Github` 与 `~/code/Github` 为同一路径；`Research/`、`Gitee/` 仍在 `APP-SSD/Code/` 下独立保留。

### P2（1–2 月）— 产品整合

- [ ] `art-curator` / `ai-image-filter`：可选依赖或文档链接 `image-similarity` CLI
- [ ] PhotoSearch：仅保留 embed + 人脸实验 UI；生产索引走 CLI
- [ ] Mac SSD：标记 `RETIRED`（见 `DEV-SOURCE-OF-TRUTH-UBUNTU`）

## 环境速查

| 资源 | 路径 |
|------|------|
| 代码根 | `/mnt/Dev/code/Github` |
| 本仓库 | `.../03-工具与实验/图像视频/image-similarity` |
| 权重 | `/mnt/AIGC/models/huggingface/google/embeddinggemma-2` |
| Embed HTTP | `http://192.168.1.100:8096`（PhotoSearch） |
| SSH | `ssh -o BatchMode=yes server '...'` |

详细模型见 `docs/MODEL_WEIGHTS.md`；架构见 `docs/DEVELOPMENT.md`。
