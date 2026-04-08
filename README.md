# Claude Durable Workflow Baseline

A minimal baseline source repo for Claude Code durable workflow setup.

## What this repo is
- A single source of truth for the durable workflow baseline
- A distribution source for repo-local workflow protocols, spec templates, and memory skeleton files
- A baseline source repo and distribution source for durable workflow assets
- The source for `/init-claude-workflow` and `/new-feature` command content plus bootstrap scripts

## What this repo is not
- Not a plugin runtime
- Not a feature state repository
- Not a project memory repository
- Not an orchestration engine
- Not an auto-upgrade system

## Quick Start

### 新机器 / 新 Repo（一步入口）

```bash
# 1. 克隆到本地 baseline cache
# 重要：scripts 硬编码了 ~/.claude/baselines/durable-workflow-v1 路径。
# 如需自定义位置，可设置 CLAUDE_WORKFLOW_BASELINE_PATH 环境变量指向你的克隆目录。
git clone https://github.com/Cunning-Kang/claude-durable-workflow-baseline.git \
  ~/.claude/baselines/durable-workflow-v1

# 2. 复制全局资产（-n 不覆盖已有文件，-r 递归复制目录）
cp -rn ~/.claude/baselines/durable-workflow-v1/global/* ~/.claude/

# 3. 复制命令入口
cp ~/.claude/baselines/durable-workflow-v1/distribution/commands/init-claude-workflow.md \
   ~/.claude/commands/init-claude-workflow.md
cp ~/.claude/baselines/durable-workflow-v1/distribution/commands/new-feature.md \
   ~/.claude/commands/new-feature.md

# 4. 复制 supporting scripts 到固定 runtime 路径
mkdir -p ~/.claude/scripts
cp ~/.claude/baselines/durable-workflow-v1/distribution/scripts/*.sh \
   ~/.claude/scripts/

# 5. 在新 repo 中初始化
cd /path/to/new-repo
git init  # if not already a git repo
claude    # start Claude Code
/init-claude-workflow
```

### 完整操作手册

See [docs/claude-one-command-bootstrap.md](docs/claude-one-command-bootstrap.md) for the full operator guide.

## How distribution works
1. Clone this repository to your local cache: `~/.claude/baselines/durable-workflow-v1/`
2. Copy `global/*` to `~/.claude/` for global runtime surface
3. Copy `distribution/commands/init-claude-workflow.md` and `distribution/commands/new-feature.md` to `~/.claude/commands/`
4. Copy `distribution/scripts/*.sh` to `~/.claude/scripts/` as the fixed runtime script location
5. Run `/init-claude-workflow` in any new repo to initialize baseline files
6. Run `/new-feature <feature-slug>` when you need a feature spec instance
7. (Optional) Copy `distribution/agents/*.md` to `~/.claude/agents/` for custom subagent definitions

## What `/init-claude-workflow` does
- Verifies the current directory is a git repository
- Copies missing baseline files (docs/specs/_template/, docs/workflow/, memory/, baseline/claude/)
- Skips files that already exist
- Reports conflicts for files that exist but differ (does NOT overwrite)
- Writes a `.claude/workflow-baseline-version` marker

## What `/init-claude-workflow` does not do
- It does not sync this baseline repo (manual `git pull` to upgrade)
- It does not upgrade an already-initialized repo
- It does not create feature instances (see `/new-feature` below)
- It does not infer project commands
- It does not overwrite local modifications by default

## Starting a new feature

```bash
# After /init-claude-workflow, instantiate a feature spec skeleton:
/new-feature <feature-slug>

# Example:
/new-feature user-auth
# → creates docs/specs/user-auth/ from _template/
# → replaces <feature-slug> placeholders automatically
```

This runs `~/.claude/scripts/instantiate-feature.sh`, which:
- Reads template files from `~/.claude/baselines/durable-workflow-v1/baseline/docs/specs/_template/`
- Copies them to `docs/specs/<feature-slug>/`
- Replaces `<feature-slug>` in all generated files
- Skips if the feature directory already exists (never overwrites)

After instantiation, fill in `spec.md`, `plan.md`, and the task files, then use the Superpowers `/brainstorming` skill to start planning.

## Directory structure

```
baseline/                        ← copied into new repos by /init-claude-workflow
  claude/claude-snippet.md
  docs/specs/_template/         (spec templates)
  docs/workflow/               (review, execution, memory protocols)
  memory/                      (MEMORY.md, patterns.md, gotchas.md)
  .gitignore

distribution/
  commands/
    init-claude-workflow.md    ← /init-claude-workflow entry
    new-feature.md             ← /new-feature entry
  scripts/
    init-claude-workflow.sh    ← bootstrap script
    instantiate-feature.sh     ← _template instantiation script
  hooks/                       ← source-only · opt-in · NOT copied by /init-claude-workflow
    project/                  (project-scope hook templates)
  settings-snippets/           ← source-only · opt-in · NOT copied by /init-claude-workflow
    project/                  (project-scope settings fragments)
  agents/                     ← source-only · opt-in · NOT auto-installed
    README.md                (installation and routing protocol guide)
    orchestrator-planner.md
    execution-implementer.md
    mechanical-transformer.md
    technical-writer.md
    product-manager.md
    docker-expert.md

global/                        ← copied to ~/.claude/ (host-wide surface)
  CLAUDE.md                    (runtime entry — copy to ~/.claude/CLAUDE.md)
  standards/core-standard.md
  guides/orchestration-extension.md
  rules/review-workflow.md

docs/
  claude-one-command-bootstrap.md  (operator guide)
```

**What auto-enters a new repo:** `baseline/` tree (via `/init-claude-workflow`).

**What does NOT auto-enter:** `distribution/hooks/`, `distribution/settings-snippets/`, and `distribution/agents/` — these are source-only opt-in artifacts you adopt manually.

## Version

See [VERSION](VERSION) for baseline version and cache path conventions.
