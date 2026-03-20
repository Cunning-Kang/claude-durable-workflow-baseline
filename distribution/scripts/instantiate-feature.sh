#!/usr/bin/env bash
#
# instantiate-feature.sh
#
# Instantiates the _template spec skeleton for a new feature.
# Replaces <feature-slug> placeholders with the actual feature name.
#
# Usage:
#   ./instantiate-feature.sh <feature-slug>
#
# Example:
#   ./instantiate-feature.sh user-auth
#   → creates docs/specs/user-auth/ with index.md, plan.md, spec.md, etc.
#
# Requires:
#   - git repository (checks REPO_ROOT via git rev-parse)
#   - BASELINE_CACHE_ROOT (defaults to ~/.claude/baselines/durable-workflow-v1)
#   - Template source at $BASELINE_CACHE_ROOT/baseline/docs/specs/_template/
#
# Does NOT:
#   - overwrite existing files
#   - create git commits
#   - modify settings or configs

set -euo pipefail

FEATURE_SLUG="${1:-}"
BASELINE_CACHE_ROOT="${CLAUDE_WORKFLOW_BASELINE_PATH:-$HOME/.claude/baselines/durable-workflow-v1}"
TEMPLATE_SRC="$BASELINE_CACHE_ROOT/baseline/docs/specs/_template"

# ── Validation ────────────────────────────────────────────────────────────────

if [[ -z "$FEATURE_SLUG" ]]; then
    echo "Usage: $0 <feature-slug>" >&2
    echo "Example: $0 user-auth" >&2
    exit 1
fi

if [[ "$FEATURE_SLUG" == "_template" ]]; then
    echo "Error: '_template' is reserved. Use a real feature slug." >&2
    exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: not inside a git repository. Run from your project root." >&2
    exit 1
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"

if [[ ! -d "$TEMPLATE_SRC" ]]; then
    echo "Error: template source not found at: $TEMPLATE_SRC" >&2
    echo "Run /init-claude-workflow first to populate the baseline cache." >&2
    exit 1
fi

# ── Destination setup ─────────────────────────────────────────────────────────

FEATURE_DIR="$REPO_ROOT/docs/specs/$FEATURE_SLUG"
TASKS_DIR="$FEATURE_DIR/tasks"

if [[ -e "$FEATURE_DIR" ]]; then
    echo "Error: feature directory already exists: $FEATURE_DIR" >&2
    echo "Remove it first, or choose a different feature slug." >&2
    exit 1
fi

echo "[INFO] Instantiating feature: $FEATURE_SLUG"
echo "[INFO] Target: $FEATURE_DIR"

# ── Copy template files ───────────────────────────────────────────────────────

mkdir -p "$TASKS_DIR"

# Copy all template files, replacing <feature-slug> with actual slug
copy_and_replace() {
    local src="$1"
    local dst="$2"

    if [[ ! -f "$src" ]]; then
        return
    fi

    local dst_dir
    dst_dir="$(dirname "$dst")"
    mkdir -p "$dst_dir"

    # Replace placeholder in content
    sed "s/<feature-slug>/$FEATURE_SLUG/g" "$src" > "$dst"

    echo "  + ${dst#$REPO_ROOT/}"
}

# Process files
for src in "$TEMPLATE_SRC"/*; do
    fname="$(basename "$src")"
    if [[ -f "$src" ]]; then
        copy_and_replace "$src" "$FEATURE_DIR/$fname"
    fi
done

# Copy tasks subdirectory (recursively)
if [[ -d "$TEMPLATE_SRC/tasks" ]]; then
    for tsrc in "$TEMPLATE_SRC/tasks"/*; do
        fname="$(basename "$tsrc")"
        if [[ -f "$tsrc" ]]; then
            copy_and_replace "$tsrc" "$TASKS_DIR/$fname"
        fi
    done
fi

# ── Summary ───────────────────────────────────────────────────────────────────

echo ""
echo "============================================"
echo "      FEATURE INSTANCE CREATED             "
echo "============================================"
echo ""
echo "  Feature: $FEATURE_SLUG"
echo "  Location: docs/specs/$FEATURE_SLUG/"
echo ""
echo "  Next steps:"
echo "  1. Review and fill in spec.md (Goal, Scope, Acceptance)"
echo "  2. Fill in plan.md (Execution Order, Steps)"
echo "  3. Rename tasks/T01-example.md → T01-<feature-slug>.md"
echo "  4. Run /brainstorming to start planning"
echo ""
