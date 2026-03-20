---
description: Initialize the Claude durable workflow baseline in the current repo from the local baseline cache without creating feature state.
argument-hint: [--dry-run | --print-patch | --force-template]
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Write
  - Edit
---

<objective>
Initialize the current repo with the durable workflow baseline:
- docs/specs/_template/
- docs/workflow/
- memory/
- baseline/ (repo-local baseline files)

The source is the local baseline cache at `~/.claude/baselines/durable-workflow/baseline/`.
</objective>

## Pre-flight Check

1. Confirm the current directory is a git repository.
2. Check if `~/.claude/baselines/durable-workflow/baseline/` exists (the baseline cache).
3. If the cache does not exist, stop and output the bootstrap sequence for the user.

## Baseline Cache Resolution

```
BASELINE_CACHE="${HOME}/.claude/baselines/durable-workflow/baseline"
```

## Execution

### Step 1: Create directory structure

Ensure these directories exist in the current repo:
- `docs/specs/_template/`
- `docs/workflow/`
- `memory/`
- `baseline/`

### Step 2: Copy baseline files

From `$BASELINE_CACHE/docs/` → `docs/`
- `spec.md` template → `docs/specs/_template/spec.md`

From `$BASELINE_CACHE/memory/` → `memory/`
- `MEMORY.md` → `memory/MEMORY.md`

From `$BASELINE_CACHE/claude/` → `baseline/`
- `claude-snippet.md` → `baseline/claude/claude-snippet.md`

### Step 3: Copy workflow files

From `$BASELINE_CACHE/../docs/workflow/` → `docs/workflow/`
- `review-protocol.md`
- `review-checklist.md`
- `execution-contract.md`
- `memory-protocol.md`
- `native-task-translation.md`

### Step 4: Create version marker

Write `baseline/.workflow-baseline-version` with content:
```
# Workflow Baseline
# Source: ~/.claude/baselines/durable-workflow/
# Initialized: YYYY-MM-DD
```

## Non-overwrite Rule

For any file that already exists in the target repo:
- Do NOT overwrite it.
- Output the file path as "skipped (already exists)".

## Output

Summarize:
- `Created:` list of files created
- `Skipped:` list of files already present
- `Next step:` what the user should do after initialization

## Non-goals
- Do not sync the baseline cache.
- Do not upgrade an already-initialized repo.
- Do not create `docs/specs/<feature>/...` instances.
- Do not overwrite user-modified files.
