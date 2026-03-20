# Global Distribution Layer

This directory is the canonical source for user-level Claude Code durable workflow capabilities.

## Purpose
- Provide the formal global package that installs into `~/.claude/*`
- Keep cross-repo durable entrypoints versioned outside any single target repo
- Separate user-level capabilities from repo-local baseline files

## v1 contents
- `CLAUDE.md`
- `standards/core-standard.md`
- `guides/orchestration-extension.md`
- `skills/spec-execute/SKILL.md`
- `commands/finish-branch.md`

## Deferred to repo layer
- `docs/workflow/*`
- `docs/specs/_template/*`
- repo memory files (`memory/`)
- feature durable state
- Superpowers skills (installed separately via marketplace)

## Must not contain
- `settings.json`
- `settings.local.json`
- machine-specific env, hooks, or permissions
- repo workflow protocols under `docs/workflow/*`
- repo spec templates under `docs/specs/_template/*`
- repo memory files
- feature durable state
- sync / upgrade / runtime logic
- Superpowers plugin (installed separately via marketplace)

## Relationship to other layers
- `baseline/` remains the repo-local baseline package
- `global/` is the user-level capability package
- installed target for `global/` is `~/.claude/*`
- installed target for `baseline/` is the target repo itself

## Installation
```bash
# Sync this repo to local cache
git clone <source-repo-url> ~/.claude/baselines/durable-workflow/

# Copy global/ to ~/.claude/
cp -n ~/.claude/baselines/durable-workflow/global/* ~/.claude/
```

## Current stage
- v1 canonical distribution layer is present
- Superpowers is the primary behavior control layer (installed separately)
- manual installation only
- no auto-sync, no upgrade flow
