#!/usr/bin/env bash
set -euo pipefail

# init-claude-workflow.sh
#
# Purpose:
# - Read a local cached baseline package
# - Initialize missing durable workflow files in the current repo
# - Produce patch suggestions for conflicting files
# - Optionally write a lightweight baseline version marker
#
# Current stage:
# - This is an interface stub only.
# - It does NOT implement full sync, upgrade, or merge behavior.
#
# Explicit non-goals:
# - Do not sync the baseline source repo.
# - Do not upgrade existing initialized repos.
# - Do not create feature instances.
# - Do not overwrite modified repo files by default.
# - Do not act as an orchestration engine.

REPO_ROOT="${1:-$(pwd)}"
BASELINE_CACHE_ROOT="${CLAUDE_WORKFLOW_BASELINE_PATH:-$HOME/.claude/baselines/durable-workflow-v1}"
BASELINE_DIR="$BASELINE_CACHE_ROOT/baseline"
VERSION_FILE="$BASELINE_CACHE_ROOT/VERSION"
REPO_VERSION_MARKER="$REPO_ROOT/.claude/workflow-baseline-version"

# Future responsibilities:
# 1. Verify REPO_ROOT is a git repository.
# 2. Verify BASELINE_DIR exists and contains the expected baseline layout.
# 3. Create missing files from BASELINE_DIR into REPO_ROOT.
# 4. Detect conflicting files and print patch/diff guidance instead of overwriting.
# 5. Write REPO_VERSION_MARKER with the current baseline version if safe.
# 6. Print a summary of created / skipped / conflicting files.
# 7. Print project-specific follow-up actions for the user.

# Suggested future checks:
# - git rev-parse --is-inside-work-tree
# - existence of baseline/docs/workflow, baseline/docs/specs/_template, baseline/memory
# - presence of VERSION file

# Suggested future creation behavior:
# - create missing files only
# - skip identical files
# - never overwrite repo files unless an explicit future force mode allows template-only replacement

# Suggested future conflict behavior:
# - output patch suggestions
# - report manual review required
# - avoid destructive edits

printf '%s\n' "init-claude-workflow stub: not implemented yet"
printf '%s\n' "repo_root=$REPO_ROOT"
printf '%s\n' "baseline_cache_root=$BASELINE_CACHE_ROOT"
printf '%s\n' "baseline_dir=$BASELINE_DIR"
printf '%s\n' "version_file=$VERSION_FILE"
printf '%s\n' "repo_version_marker=$REPO_VERSION_MARKER"
