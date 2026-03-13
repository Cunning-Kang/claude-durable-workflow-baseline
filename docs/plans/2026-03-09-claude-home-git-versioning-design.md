# ~/.claude Git Versioning Design

## Decision

Use a **whitelist-based git repository** for `~/.claude`.

### Goals
- Support local rollback for config experiments
- Support backup of important Claude Code configuration
- Support cross-machine sync for stable, user-authored assets
- Avoid committing runtime state, caches, logs, transcripts, and other noisy or sensitive data

### Managed Paths
Track these by default:

- `CLAUDE.md`
- `settings.json`
- `settings.local.json`
- `standards/**`
- `guides/**`
- `agents/**`
- `skills/financial-statement-generator/**`
- `skills/github-to-skill/**`
- `skills/mise-bootstrap/**`

Optional later:
- `plans/**`
- `plugins/claude-hud/**`

### Ignored Paths
Ignore runtime, cache, generated, local-state, analytics, transcripts, backups, and external installed skills.

Core examples:
- `projects/**`
- `session-env/**`
- `tasks/**`
- `teams/**`
- `todos/**`
- `transcripts/**`
- `usage-data/**`
- `debug/**`
- `file-history/**`
- `shell-snapshots/**`
- `statsig/**`
- `context-mode/**`
- `backups/**`
- `cache/**`
- `paste-cache/**`
- `plugins/cache/**`
- third-party skills under `skills/` not authored by the user

## Recommended .gitignore

```gitignore
# =========================
# Base policy: ignore everything by default
# =========================
*
!*/

# =========================
# Keep core managed config
# =========================
!CLAUDE.md
!settings.json
!settings.local.json

!standards/
!standards/**

!guides/
!guides/**

!agents/
!agents/**

# =========================
# Keep only self-authored skills
# =========================
skills/*
!skills/financial-statement-generator/
!skills/financial-statement-generator/**

!skills/github-to-skill/
!skills/github-to-skill/**

!skills/mise-bootstrap/
!skills/mise-bootstrap/**

# =========================
# Optional tracked paths
# Uncomment only if needed
# =========================
#!plans/
#!plans/**
#!plugins/
#!plugins/claude-hud/
#!plugins/claude-hud/**

# =========================
# Always ignore runtime / cache / generated / local-only
# =========================
.DS_Store

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

# Plugins metadata and caches
plugins/cache/
plugins/installed_plugins.json
plugins/known_marketplaces.json
plugins/install-counts-cache.json
plugins/blocklist.json

# Backup / temp artifacts
*.backup
*.backup.*
*.bak
*.bak-*
```

## Implementation Steps

### Option A: Initialize git directly in `~/.claude`

1. Create a backup before starting.
2. Initialize a repository in `~/.claude`.
3. Add the `.gitignore` above.
4. Review `settings.local.json` manually to ensure it contains no secrets or machine-only values you do not want synced.
5. Stage only the intended files.
6. Make the initial commit.
7. Optionally add a private remote.
8. On another machine, clone into `~/.claude` only if you are comfortable replacing that machine's existing config layout.

Suggested commands:

```bash
cd ~/.claude
cp -R ~/.claude ~/.claude.backup.$(date +%Y%m%d-%H%M%S)
git init
git branch -M main
```

Create `.gitignore`, then stage explicitly:

```bash
git add CLAUDE.md settings.json settings.local.json
git add standards guides agents
git add skills/financial-statement-generator
git add skills/github-to-skill
git add skills/mise-bootstrap
git status
```

Initial commit:

```bash
git commit -m "chore: track curated Claude Code global config"
```

Optional remote:

```bash
git remote add origin <your-private-repo-url>
git push -u origin main
```

### Option B: Mirror into a separate config repo

Use this if you want stronger isolation.

1. Create a private repo such as `~/dotfiles/claude-config`.
2. Copy only the managed paths into that repo.
3. Keep the same `.gitignore` policy there.
4. Restore onto a new machine with a small sync script or `rsync`.

This option is safer for cross-machine sync, but adds one extra sync step.

## Recommendation Between A and B

- Choose **Option A** if you want the fastest path and primarily care about rollback plus backup.
- Choose **Option B** if you want the cleanest long-term setup and stronger separation from runtime state.

Given the current goal, **Option A is the practical default**.

## README Template

Save this as `README.md` in the `~/.claude` git repository.

```md
# Claude Code Global Config

This repository tracks a curated subset of my global Claude Code configuration from `~/.claude`.

## Purpose
- Roll back global config changes safely
- Back up important Claude Code configuration
- Sync stable personal configuration across machines

## Tracked Content
- `CLAUDE.md`
- `settings.json`
- `settings.local.json`
- `standards/`
- `guides/`
- `agents/`
- `skills/financial-statement-generator/`
- `skills/github-to-skill/`
- `skills/mise-bootstrap/`

## Not Tracked
This repo intentionally excludes runtime state and generated artifacts, including:
- transcripts
- tasks and teams state
- project memory/state
- debug logs
- analytics and usage data
- caches
- third-party installed skills

## Self-Authored Skills
These skills are maintained in this repository:
- `financial-statement-generator`
- `github-to-skill`
- `mise-bootstrap`

## Third-Party Skills
Other skills under `~/.claude/skills/` are installed externally via `skills.sh` / `npx` and are intentionally not committed.

## Bootstrap On a New Machine
1. Restore this repository into `~/.claude` or sync the tracked files into `~/.claude`.
2. Reinstall third-party skills separately.
3. Review `settings.local.json` for machine-specific values if needed.

## Notes
- This repository should stay private.
- Before committing, review diffs carefully to avoid leaking sensitive local configuration.
```

## `settings.local.json` Policy

You chose to version `settings.local.json`.

That is workable, but only if you treat it as a **review-required file**.

Before each commit, check for:
- tokens
- API keys
- secrets
- absolute paths that are valid only on one machine
- temporary experiment flags
- machine-specific shell or filesystem overrides

If such values appear later, move them out of the tracked file or stop tracking the file.
