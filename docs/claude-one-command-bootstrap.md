# Claude One-Command Bootstrap

> 状态: 正式 | 版本: 1.0.0 | 日期: 2026-03-20
> 目标: 任意新机器 / 任意新 repo，用户只需要一个入口命令

---

## 核心入口

```
/init-claude-workflow
```

这是唯一入口。它负责：
- 在当前 repo 初始化 baseline/、docs/specs/_template/、docs/workflow/、memory/
- 不覆盖已存在文件
- 输出 next step

---

## 新机器（全新主机）

### 步骤 1: 安装 Superpowers 插件

从 Claude Code marketplace 安装 `superpowers` 插件。
这是唯一必须的全局手动安装。

### 步骤 2: 克隆 source repo 并安装全局资产

```bash
# 克隆 source repo 到本地 cache
git clone https://github.com/Cunning-Kang/claude-durable-workflow-baseline.git \
  ~/.claude/baselines/durable-workflow-v1

# 复制全局 portable 资产到 ~/.claude/
cp -n ~/.claude/baselines/durable-workflow-v1/global/* ~/.claude/

# 复制 init-claude-workflow 命令到 ~/.claude/commands/
cp ~/.claude/baselines/durable-workflow-v1/distribution/commands/init-claude-workflow.md \
   ~/.claude/commands/init-claude-workflow.md

# 复制 new-feature 命令到 ~/.claude/commands/
cp ~/.claude/baselines/durable-workflow-v1/distribution/commands/new-feature.md \
   ~/.claude/commands/new-feature.md

# 复制 workflow supporting scripts 到固定 runtime 路径 ~/.claude/scripts/
mkdir -p ~/.claude/scripts
cp ~/.claude/baselines/durable-workflow-v1/distribution/scripts/*.sh \
   ~/.claude/scripts/
```

### 步骤 3: 在每个新 repo 中运行入口命令

```bash
cd /path/to/new-repo
git init  # 如果尚未是 git repo
claude    # 启动 Claude Code
/init-claude-workflow
```

### 完成后得到什么

- `docs/specs/_template/spec.md`
- `docs/workflow/review-protocol.md`
- `docs/workflow/review-checklist.md`
- `docs/workflow/execution-contract.md`
- `docs/workflow/memory-protocol.md`
- `docs/workflow/native-task-translation.md`
- `memory/MEMORY.md`
- `baseline/claude/claude-snippet.md`

---

## 新 Repo（在已有机器上）

```bash
cd /path/to/new-repo
claude
/init-claude-workflow
```

如果 `~/.claude/baselines/durable-workflow-v1/` 不存在，先执行步骤 2（克隆 + 复制命令与脚本）。

---

## 日常使用

### 打开 Claude Code 后

1. 看 `.claude/CLAUDE.md` 或 repo 根目录的 `CLAUDE.md`
2. 用 `/init-claude-workflow` 初始化新 repo（仅首次）
3. 用 Superpowers 技能开始工作

### Superpowers 入口映射

| 场景 | 入口命令 |
|------|----------|
| 初始化新项目 | `/init-claude-workflow` |
| 初始化新 feature | `/new-feature <feature-slug>` |
| 开始任务 | `/brainstorming` |
| 写 spec/plan | `/writing-plans` |
| 实现 | `/test-driven-development` |
| 验证完成 | `/verification-before-completion` |
| 结束分支 | `/finish-branch` |
| 沉淀记忆 | `/memory-reflection` |
| 查询增强层 | `docs/specs/_template/`、`docs/workflow/`、`memory/` |

---

## 主控层 vs 增强层边界

**Superpowers（主控层）**
- 唯一行为控制面
- 所有 skill 入口（brainstorming, writing-plans, TDD, etc.）
- `/finish-branch`、`/memory-reflection`

**增强层（本地知识）**
- `docs/specs/_template/` — durable spec 模板
- `docs/workflow/` — 执行协议（review, memory, execution）
- `memory/` — 项目知识沉淀
- `baseline/` — repo 初始化 baseline

增强层不控制行为，只提供 Superpowers 覆盖不到的 durable 知识复利。

---

## 明确不要做的事

1. **不要**在新 repo 中重建主控命令/skills（与 Superpowers 冲突）
2. **不要**修改 `~/.claude/settings.json` 的 env 配置
3. **不要**在 Superpowers 已有能力的方向继续造轮子
4. **不要**将 `docs/workflow/`、`docs/specs/_template/`、`memory/` 作为全局控制层
5. **不要**增加新的全局 automation 控制层

---

## Source Repo 资产清单

```
source repo (canonical distribution source)
├── global/                        → copy to ~/.claude/
│   ├── CLAUDE.md                 (global runtime surface reference)
│   ├── standards/core-standard.md
│   ├── guides/orchestration-extension.md
│   ├── commands/finish-branch.md
│   └── README.md                 (source repo 内部自述，无需复制)
├── distribution/
│   ├── commands/
│   │   ├── init-claude-workflow.md  → copy to ~/.claude/commands/
│   │   └── new-feature.md           → copy to ~/.claude/commands/
│   └── scripts/
│       ├── init-claude-workflow.sh  (内部脚本) → copy to ~/.claude/scripts/
│       └── instantiate-feature.sh   (feature 初始化脚本) → copy to ~/.claude/scripts/
└── baseline/                     → init-claude-workflow 的 source
    ├── docs/specs/_template/    (spec templates: index, plan, spec, review, verify, tasks/)
    ├── docs/workflow/          (review-protocol, execution-contract, memory-protocol, etc.)
    ├── memory/                  (MEMORY.md, patterns.md, gotchas.md)
    └── claude/                 (claude-snippet.md)
```

---

## 快速验证清单

新 repo 初始化后，确认：

- [ ] `docs/specs/_template/spec.md` 存在
- [ ] `docs/workflow/` 存在（至少含 review-protocol.md）
- [ ] `memory/MEMORY.md` 存在
- [ ] `baseline/claude/claude-snippet.md` 存在
- [ ] Superpowers 插件已激活
- [ ] `~/.claude/CLAUDE.md` 存在（引用 core-standard）
