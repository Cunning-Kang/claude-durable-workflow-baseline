# Claude Durable Workflow Baseline

A minimal baseline source repo for Claude Code durable workflow setup.

## What this repo is
- A single source of truth for the durable workflow baseline
- A distribution source for repo-local workflow protocols, spec templates, and memory skeleton files
- The source for `/init-claude-workflow` command content and bootstrap script

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
git clone https://github.com/Cunning-Kang/claude-durable-workflow-baseline.git \
  ~/.claude/baselines/durable-workflow-v1

# 2. 复制全局资产
cp -n ~/.claude/baselines/durable-workflow-v1/global/* ~/.claude/

# 3. 复制命令入口
cp ~/.claude/baselines/durable-workflow-v1/distribution/commands/init-claude-workflow.md \
   ~/.claude/commands/init-claude-workflow.md

# 4. 在新 repo 中初始化
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
3. Copy `distribution/commands/init-claude-workflow.md` to `~/.claude/commands/`
4. Run `/init-claude-workflow` in any new repo to initialize baseline files

## What `/init-claude-workflow` does
- Verifies the current directory is a git repository
- Copies missing baseline files (docs/specs/_template/, docs/workflow/, memory/, baseline/claude/)
- Skips files that already exist
- Reports conflicts for files that exist but differ (does NOT overwrite)
- Writes a `.claude/workflow-baseline-version` marker

## What `/init-claude-workflow` does not do
- It does not sync this baseline repo (manual `git pull` to upgrade)
- It does not upgrade an already-initialized repo
- It does not create feature instances
- It does not infer project commands
- It does not overwrite local modifications by default

## Directory structure

```
baseline/                        ← baseline assets for /init-claude-workflow
  claude/claude-snippet.md
  docs/specs/_template/         (spec templates)
  docs/workflow/                (review, execution, memory protocols)
  memory/                       (MEMORY.md, patterns.md, gotchas.md)

distribution/
  commands/init-claude-workflow.md   ← slash command entry
  scripts/init-claude-workflow.sh    ← actual bootstrap script

global/                         ← portable user-level assets
  CLAUDE.md                     → copy to ~/.claude/CLAUDE.md
  standards/core-standard.md
  guides/orchestration-extension.md
  commands/finish-branch.md

docs/
  claude-one-command-bootstrap.md   ← operator guide
```

## Version

See [VERSION](VERSION) for baseline version and cache path conventions.
