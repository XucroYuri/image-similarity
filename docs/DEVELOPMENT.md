# 开发归仓

**Canonical clone（在 Ubuntu `server` 上开发与联调）：**

```text
/mnt/Dev/code/Github/image-similarity
# 等同 ~/code/Github/image-similarity
```

```bash
ssh server
cd ~/code/Github/image-similarity
uv sync --all-groups
uv run pytest -q
```

PhotoSearch 实验服务目录（独立，仅 embed HTTP）：

```text
/media/xuyu/APP-SSD/Code/Research/PhotoSearch_EmbeddingGemma2
```

新功能 PR 以 GitHub `XucroYuri/image-similarity` 为准；Mac SSD 目录为工作副本，定期 `git pull`。
