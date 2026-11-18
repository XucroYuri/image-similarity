# P1 双树 diff 报告 (Github)

**状态：P1 已收口（2026-11-19）** — NewsSentry 已 Dev 合并并 `c60e126`；`APP-SSD/Code/Github` 已 symlink 至 Dev，备份目录已删。

生成时间: 2026-11-18 09:25 +0800

## 路径

| 树 | 路径 | .git 仓库数 |
|----|------|-------------|
| **Dev（canonical）** | `/mnt/Dev/code/Github` | 195 |
| APP-SSD（遗留） | `/media/xuyu/APP-SSD/Code/Github` | 192 |

挂载: APP-SSD 与 `/mnt/Dev` 同盘 (nvme2n1p1)。

## 汇总

- 路径交集: **192** 仓
- 仅 Dev 有: **3** 仓
- 仅 APP 有: **0** 仓
- HEAD 一致: **191** 仓
- HEAD 不一致: **1** 仓
- Dev 工作区脏: **5** 仓
- APP 工作区脏: **4** 仓

### 仅 Dev 存在的仓库

- `03-工具与实验/图像视频/image-similarity` — 265f358 docs: Document AIGC canonical embeddinggemma-2 weights
- `03-工具与实验/图像视频/math-wallpapers` — d2dfb7a Record wallpaper loops frame by frame.
- `04-第三方参考/图像视频/mesh-avatar-studio` — 3619620 Merge pull request #95 from shinshin86/changeset-release/main

### Dev 工作区脏（canonical 侧先清理）

- `01-核心产品/办公自动化/NewsSentry` — ?? .review/77-claude.md
- `01-核心产品/影视制作/A11` — M AGENTS.md
- `01-核心产品/影视制作/ScriptOS/reference/filmgame` — M .gitignore
- `01-核心产品/影视制作/ScriptOS/reference/how-to-make-script` — M .github/CODEOWNERS
- `01-核心产品/影视制作/ScriptOS/reference/inkos` — M .env.example

### APP 工作区脏

- `01-核心产品/办公自动化/NewsSentry` — M check.sh
- `01-核心产品/影视制作/ScriptOS/reference/filmgame` — M .gitignore
- `01-核心产品/影视制作/ScriptOS/reference/how-to-make-script` — M .github/CODEOWNERS
- `01-核心产品/影视制作/ScriptOS/reference/inkos` — M .env.example

### HEAD 不一致分类

| 类型 | 数量 | 含义 |
|------|------|------|
| DEV_AHEAD | 0 | 以 Dev 为真源时应对策略见下 |
| APP_AHEAD | 0 | 以 Dev 为真源时应对策略见下 |
| DIVERGED | 1 | 以 Dev 为真源时应对策略见下 |

- **DEV_AHEAD**: APP 是 Dev 祖先 → APP 树可直接放弃或硬重置到 Dev HEAD
- **APP_AHEAD**: Dev 落后于 APP → 在 Dev 上 `git fetch` + cherry-pick/merge APP 独有提交后再弃 APP
- **DIVERGED**: 真分叉 → 逐仓人工合并，默认 **Dev 为准 push**

### HEAD 不一致明细（全部）

| 仓库 | 类型 | Dev HEAD | APP HEAD | Dev 最近 | APP 最近 |
|------|------|----------|----------|----------|----------|
| `01-核心产品/办公自动化/NewsSentry` | DIVERGED | `9ff7815f` | `bd0abfa7` | 9ff7815 fix(cloudflare): Access 用户 OTP JWT (type=app 无 commo | bd0abfa test: align source-health workflow assertions with e |

## 工作区文件 diff（`diff -rq`，排除 `.git`）

- **约 834 条** 差异行（未跟踪构建产物、`node_modules`、运行日志、`data/` 临时文件等）。
- 典型源：**NewsSentry**（两树 HEAD 已分叉，且 Dev 有 `build/`、`node_modules/`、各自 `data/italy/logs/*.json`）。
- **191/192** 交集仓 `git HEAD` 相同，但仍有 **4** 仓因**未提交工作区**在双树同时变脏（含 ScriptOS `reference/*` 子仓）。

## P1 建议动作（按优先级）

1. **NewsSentry**：在 **Dev** 上完成合并 → 测试 → **push**；对照 `NewsSentry-MERGE-MAC-UBUNTU`；APP 路径该仓 **不再单独编辑**。
2. **仅 Dev 的 3 仓**：在 APP 树 **无需** 拷贝；统一从 Dev 开发 `image-similarity` / `math-wallpapers` / `mesh-avatar-studio`。
3. **清理 Dev 脏仓**：`NewsSentry` `.review/`、`A11` 等 — commit 或 `git checkout --`。
4. **收敛 APP `Github` 根**：`ln -sfn /mnt/Dev/code/Github /media/xuyu/APP-SSD/Code/Github.migrated` 或文档禁止在 APP 路径 `git commit`；全树 `diff -rq` 仅作审计，不要求 0 行（忽略 `node_modules` 更佳）。
5. **ScriptOS reference 子模块**：双树同脏 — 在 **Dev** 单次处理，勿在 APP 重复改。

## 复现扫描

```bash
ssh -o BatchMode=yes server 'python3 /mnt/Dev/code/Github/03-工具与实验/图像视频/image-similarity/docs/reports/p1_dual_tree_scan.py'  # 若日后入库
# 或重新跑本次会话中的 inventory 脚本（见 Git 提交说明）
```
