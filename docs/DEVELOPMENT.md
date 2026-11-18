# 开发归仓

与 `Github/` 工作区分类一致：**03-工具与实验 → 图像视频**（与 CornerCrop、quick-vision-prompt 等同域）。

**Canonical clone（Ubuntu `server`）：**

```text
/mnt/Dev/code/Github/03-工具与实验/图像视频/image-similarity
# 等同 ~/code/Github/03-工具与实验/图像视频/image-similarity
```

```bash
ssh server
cd ~/code/Github/03-工具与实验/图像视频/image-similarity
uv sync --all-groups
uv run pytest -q
```

**Mac 工作副本（可选）：**

```text
/Volumes/SSD/Code/04-ai-vision/image-similarity
```

与 `Github/03-工具与实验/图像视频` 语义对齐；日常以 server 目录为准 `git pull`。

PhotoSearch embed 服务（独立实验，非本仓）：

```text
/media/xuyu/APP-SSD/Code/Research/PhotoSearch_EmbeddingGemma2
```

远程：`https://github.com/XucroYuri/image-similarity`

局域网归并与双树收敛：`docs/LAN_DEV_CONSOLIDATION.md`（**P1 已完成**；`APP-SSD/Code/Github` = symlink → Dev）。
