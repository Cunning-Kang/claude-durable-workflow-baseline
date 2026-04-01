# Global Distribution Layer

This directory is a thin portable user-level runtime surface — portable assets that seed `~/.claude/*`, not a behavior control layer.

## Purpose
- Serve as the canonical source for portable user-level assets installed into `~/.claude/*`
- Keep cross-repo durable entrypoints versioned outside any single target repo
- Separate user-level portable surface from repo-local baseline files

## v1 contents (recommended distribution)
- `CLAUDE.md` — Runtime entry point; uses `@~/.claude/` paths references, after installation to `~/.claude/`
- `standards/core-standard.md`
- `guides/ororchestration-extension.md`
- `rules/review-workflow.md`

## rules/

Always-applied workflow rules. These rules load in every session unconditionally.

- `review-workflow.md` — PASS/FAIL/BLOCKED mechanics for the review gate (referenced by core-standard.md §6)

These are not standalone policies; they extend core-standard.md with specific operational mechanics.

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
- `global/` is the thin portable user-level runtime surface (not a behavior control layer)
- installed target for `global/` is `~/.claude/`
- installed target for `baseline/` is the target repo itself

## Installation
```bash
# Sync this repo to local cache
git clone <source-repo-url> ~/.claude/baselines/durable-workflow-v1/

# Copy the global surface (CLAUDE.md, standards/, guides/, rules/) to ~/.claude/
cp -rn ~/.claude/baselines/durable-workflow-v1/global/* ~/.claude/
```

## Current stage
- v1 canonical distribution layer is present
- Superpowers is the primary behavior control layer (installed separately)
- manual installation only
- no auto-sync, no upgrade flow
