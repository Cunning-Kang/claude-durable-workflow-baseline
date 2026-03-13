# ~/.claude Git Versioning Execution Plan

## Context
你希望把 `/Users/cunning/.claude` 中“稳定、可回滚、可迁移”的全局 Claude Code 配置纳入 git 版本管理，用于后续测试、回滚和备份；同时明确排除运行态、缓存、转录、统计、插件缓存与第三方安装 skills 等高噪声内容。当前边界已经确认：纳入 `CLAUDE.md`、`settings.json`、`settings.local.json`、`standards/**`、`guides/**`、`agents/**`，以及 3 个自建 skills；明确不纳入 `plans/**` 与 `plugins/claude-hud/**`。

## Goal
在 `/Users/cunning/.claude` 中初始化一个白名单式 git 仓库，只追踪已确认的配置资产，并通过 `.gitignore` 严格屏蔽非目标内容。

## Scope
- 创建 `/Users/cunning/.claude/.gitignore`
- 如尚未存在 git 仓库，则在 `/Users/cunning/.claude` 执行 `git init`
- 可选创建 `/Users/cunning/.claude/README.md`（使用已确定模板）
- 显式暂存允许纳管的文件与目录
- 验证没有误纳入 `plans/`、`plugins/claude-hud/`、第三方 skills、缓存、日志、统计、转录等内容
- 如你批准，创建初始 commit

## Non-goals
- 不修改 `~/.claude` 下现有业务配置内容
- 不纳入第三方 skills 源码
- 不纳入 `plans/**`
- 不纳入 `plugins/claude-hud/**`
- 不执行 push，除非你后续单独授权

## Risks
- `settings.local.json` 已被你决定纳入 git，但它属于高审查文件，可能包含机器专属路径或敏感值
- `skills/` 下存在第三方安装内容，必须通过白名单避免误提交
- 若 `~/.claude` 已有未预期文件模式，需通过 `git status` / `git diff --cached --name-only` 再次确认

## Rollback
- 若只完成 `git init` 和新增 `.gitignore` / `README.md`，可删除 `/Users/cunning/.claude/.git` 恢复到未纳管状态
- 若已创建 commit，但尚未推送，可保留仓库并通过新的反向 commit 撤销
- 不使用 `git reset --hard` 等破坏性操作

## Execution order
1. 只读检查 `/Users/cunning/.claude` 当前状态与目标路径是否存在
2. 创建或确认 git 仓库
3. 写入最终 `.gitignore`
4. （如你批准包含）写入 `README.md`
5. 用显式 `git add` 暂存允许路径
6. 运行验证命令确认暂存范围准确
7. 向你汇报结果并在你授权下创建初始 commit

## Final `.gitignore`
将以下内容写入 `/Users/cunning/.claude/.gitignore`：

```gitignore
# Base policy: ignore everything by default
*
!*/

# Keep the repository policy files
!.gitignore
!README.md

# Keep core managed config
!CLAUDE.md
!settings.json
!settings.local.json

!standards/
!standards/**

!guides/
!guides/**

!agents/
!agents/**

# Keep only self-authored skills
!skills/
skills/*
!skills/financial-statement-generator/
!skills/financial-statement-generator/**
!skills/github-to-skill/
!skills/github-to-skill/**
!skills/mise-bootstrap/
!skills/mise-bootstrap/**

# Always ignore runtime / cache / generated / local-only
plans/
plugins/
backups/
cache/
context-mode/
debug/
file-history/
ide/
paste-cache/
projects/
session-env/
shell-snapshots/
statsig/
tasks/
teams/
todos/
transcripts/
usage-data/

history.jsonl
stats-cache.json

# Plugin metadata and caches
plugins/cache/
plugins/installed_plugins.json
plugins/known_marketplaces.json
plugins/install-counts-cache.json
plugins/blocklist.json

# Mac / backup artifacts
.DS_Store
**/.DS_Store
*.backup
*.backup.*
*.bak
*.bak-*
```

## Critical files to modify
- `/Users/cunning/.claude/.gitignore`
- `/Users/cunning/.claude/README.md` (recommended, if approved)

## Reuse / prior artifacts
- Existing design reference: `docs/plans/2026-03-09-claude-home-git-versioning-design.md`
- Existing README template: `docs/plans/2026-03-09-claude-home-git-readme-template.md`

## Planned execution steps

### Step 1: Verify current target paths
Run readonly checks for existence of:
- `/Users/cunning/.claude/CLAUDE.md`
- `/Users/cunning/.claude/settings.json`
- `/Users/cunning/.claude/settings.local.json`
- `/Users/cunning/.claude/standards/`
- `/Users/cunning/.claude/guides/`
- `/Users/cunning/.claude/agents/`
- `/Users/cunning/.claude/skills/financial-statement-generator/`
- `/Users/cunning/.claude/skills/github-to-skill/`
- `/Users/cunning/.claude/skills/mise-bootstrap/`

### Step 2: Initialize repository safely
If `/Users/cunning/.claude/.git/` does not exist:
- run `git init`
- run `git branch -M main`

### Step 3: Write repository policy files
- create `/Users/cunning/.claude/.gitignore` with the final content above
- create `/Users/cunning/.claude/README.md` from the approved final template

### Step 4: Stage only approved content explicitly
Use explicit staging only:
- `git add .gitignore README.md`
- `git add CLAUDE.md settings.json settings.local.json`
- `git add standards guides agents`
- `git add skills/financial-statement-generator`
- `git add skills/github-to-skill`
- `git add skills/mise-bootstrap`

### Step 5: Verify staged scope before commit
Run verification commands and inspect results:
- `git status --short`
- `git diff --cached --name-only`
- `git check-ignore -v plans/*`
- `git check-ignore -v plugins/claude-hud/*`
- `git check-ignore -v skills/agent-browser/*`

Expected outcome:
- staged files only include approved config files, directories, and README / `.gitignore`
- `plans/**`, `plugins/claude-hud/**`, and third-party skills remain ignored

### Step 6: Commit only after explicit approval
If you separately approve commit creation, create a new commit with a concise English message, for example:
- `chore: track curated Claude Code global config`

## Verification
### Environment
- Verify `/Users/cunning/.claude` is accessible and target paths exist

### Test
- Manual verification via `git status --short`, `git diff --cached --name-only`, and `git check-ignore -v` on representative excluded paths

### Static
- N/A for this task; no code build/test/lint/typecheck pipeline applies

### Traceability
- Report the final tracked file set and exact `.gitignore` used

### Review
- User approval required before execution
- User approval required again before creating any commit
