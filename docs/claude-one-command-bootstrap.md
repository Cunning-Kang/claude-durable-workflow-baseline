# Claude One-Command Bootstrap

> 状态: 正式 | 版本: 1.4.0 | 日期: 2026-04-05
> 目标: 任意新机器 / 任意新 repo，用户只需要一个入口命令

---

## 核心入口

```
/init-claude-workflow
```

这是新机器 / 新 repo 初始化的唯一 bootstrap 入口。它负责：
- 在当前 repo 初始化 baseline/、docs/specs/_template/、docs/workflow/、memory/
- 不覆盖已存在文件
- 输出 next step

---

## 新机器（全新主机）

### 步骤 1: 克隆 source repo 并安装全局资产

```bash
# 克隆 source repo 到本地 cache
git clone https://github.com/Cunning-Kang/claude-durable-workflow-baseline.git \
  ~/.claude/baselines/durable-workflow-v1

# 复制全局 portable 资产到 ~/.claude/
cp -rn ~/.claude/baselines/durable-workflow-v1/global/* ~/.claude/

# 复制 init-claude-workflow 命令到 ~/.claude/commands/
cp ~/.claude/baselines/durable-workflow-v1/distribution/commands/init-claude-workflow.md \
   ~/.claude/commands/init-claude-workflow.md

# 复制 new-feature 命令到 ~/.claude/commands/
cp ~/.claude/baselines/durable-workflow-v1/distribution/commands/new-feature.md \
   ~/.claude/commands/new-feature.md

# Optional: copy reusable dynamic workflow command
cp ~/.claude/baselines/durable-workflow-v1/distribution/commands/subagent-pipeline-workflow.md \
   ~/.claude/commands/subagent-pipeline-workflow.md

# 复制 workflow supporting scripts 到固定 runtime 路径 ~/.claude/scripts/
mkdir -p ~/.claude/scripts
cp ~/.claude/baselines/durable-workflow-v1/distribution/scripts/*.sh \
   ~/.claude/scripts/
```

### 步骤 2: 在每个新 repo 中运行入口命令

```bash
cd /path/to/new-repo
git init  # 如果尚未是 git repo
claude    # 启动 Claude Code
/init-claude-workflow
```

### 完成后得到什么

`/init-claude-workflow` copies the **contents of the cached `baseline/` package** into your repo root — it does not create a top-level `baseline/` directory in the target repo. The following is a representative list of key files, not an exhaustive manifest:

- `docs/specs/_template/` — all spec templates (index, plan, spec, review, verify, tasks/)
- `docs/workflow/` — review-protocol.md, review-checklist.md, execution-contract.md, memory-protocol.md, native-task-translation.md
- `memory/` — MEMORY.md, patterns.md, gotchas.md
- `claude/claude-snippet.md`
- `.claude/workflow-baseline-version` — version marker (written after successful init)

Files that already exist in the repo are skipped. Files that exist but differ are reported as conflicts and are **not** overwritten.

> **Note:** `distribution/hooks/` and `distribution/settings-snippets/` are **not** copied by `/init-claude-workflow`. They are source-only opt-in artifacts — see the Source Repo Asset table below.

---

## 新 Repo（在已有机器上）

```bash
cd /path/to/new-repo
claude
/init-claude-workflow
```

如果 `~/.claude/baselines/durable-workflow-v1/` 不存在，先执行步骤 1（克隆 + 复制命令与脚本）。

---

## 日常使用

### 打开 Claude Code 后

1. 看 `.claude/CLAUDE.md` 或 repo 根目录的 `CLAUDE.md`
2. 用 `/init-claude-workflow` 初始化新 repo（仅首次）


> **区分说明：**
> - `/init-claude-workflow`、`/new-feature` 为本仓库 distribution commands（需复制到 `~/.claude/commands/`）
> - `/subagent-pipeline-workflow` 是 source-only optional command，引用 `distribution/workflows/subagent-pipeline-dynamic.js`，不会被 `/init-claude-workflow` 自动安装。

| 场景 | 入口 |
|------|------|
| 初始化新项目 | `/init-claude-workflow` |
| 初始化新 feature | `/new-feature <feature-slug>` |
| 运行 reusable dynamic workflow | `/subagent-pipeline-workflow <issues>`（optional source-only command） |
| 查询增强层 | `docs/specs/_template/`、`docs/workflow/`、`memory/` |

---

## 仓库边界

**知识 / 协议 / 骨架层**
- `docs/specs/_template/` — durable spec 模板
- `docs/workflow/` — 执行协议（review, memory, execution）
- `memory/` — 项目知识沉淀
- `baseline/` — repo 初始化 baseline


---

## 明确不要做的事

1. **不要**修改 `~/.claude/settings.json` 的 env 配置
2. **不要**将 `docs/workflow/`、`docs/specs/_template/`、`memory/` 作为全局控制层
3. **不要**增加新的全局 automation 控制层

---

## Source Repo 资产清单

```
source repo (canonical distribution source)
├── global/                        → copy to ~/.claude/
│   ├── CLAUDE.md                 (global runtime surface reference)
│   ├── standards/core-standard.md
│   ├── guides/orchestration-extension.md
│   ├── rules/review-workflow.md
│   └── README.md                 (source repo 内部自述，无需复制)
├── distribution/
│   ├── commands/
│   │   ├── init-claude-workflow.md       → copy to ~/.claude/commands/
│   │   ├── new-feature.md                → copy to ~/.claude/commands/
│   │   └── subagent-pipeline-workflow.md → optional copy to ~/.claude/commands/
│   ├── scripts/
│   │   ├── init-claude-workflow.sh  (内部脚本) → copy to ~/.claude/scripts/
│   │   └── instantiate-feature.sh   (feature 初始化脚本) → copy to ~/.claude/scripts/
│   ├── hooks/                     (Phase 3 · source-only · opt-in · 不被 init-claude-workflow 自动安装)
│   │   └── project/               (project-scope deterministic gate templates)
│   ├── settings-snippets/          (Phase 3 · source-only · opt-in · 不被 init-claude-workflow 自动安装)
│   │   └── project/               (project-scope 配置片段模板，与配对 hook 协同)
│   ├── skills/                    (source-only · opt-in · 不被 init-claude-workflow 自动安装)
│   └── workflows/                 (source-only · opt-in · reusable dynamic Workflow scripts)
│       └── subagent-pipeline-dynamic.js
└── baseline/                     → init-claude-workflow 的 source
    ├── docs/specs/_template/    (spec templates: index, plan, spec, review, verify, tasks/)
    ├── docs/workflow/          (review-protocol, execution-contract, memory-protocol, etc.)
    ├── memory/                  (MEMORY.md, patterns.md, gotchas.md)
    └── claude/                 (claude-snippet.md)
```

> **注意：** `distribution/hooks/`, `distribution/settings-snippets/`, `distribution/skills/`, and `distribution/workflows/` are source-only opt-in artifacts — they are **not** copied by `/init-claude-workflow` and must be adopted manually per the opt-in procedures in those directories.

---

## 快速验证清单

新 repo 初始化后，确认：

- [ ] `docs/specs/_template/spec.md` 存在
- [ ] `docs/workflow/` 存在（至少含 review-protocol.md）
- [ ] `memory/MEMORY.md` 存在
- [ ] `claude/claude-snippet.md` 存在
- [ ] `~/.claude/CLAUDE.md` 存在（引用 core-standard）
