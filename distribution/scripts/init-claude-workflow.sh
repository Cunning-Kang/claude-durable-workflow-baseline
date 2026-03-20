#!/usr/bin/env bash
#
# init-claude-workflow.sh
#
# Initializes the durable workflow baseline in a target repo.
# This is the internal script invoked by the /init-claude-workflow command.
#
# What it does:
# 1. Verifies REPO_ROOT is a git repository
# 2. Verifies BASELINE_DIR exists
# 3. Copies missing baseline files into REPO_ROOT
# 4. Detects and reports conflicting files (does NOT overwrite)
# 5. Writes a version marker if safe
# 6. Prints summary and next steps
#
# Path conventions:
#   BASELINE_CACHE_ROOT = ~/.claude/baselines/durable-workflow-v1
#   BASELINE_DIR        = $BASELINE_CACHE_ROOT/baseline
#   REPO_VERSION_MARKER = $REPO_ROOT/.claude/workflow-baseline-version

set -euo pipefail

REPO_ROOT="${1:-$(pwd)}"
BASELINE_CACHE_ROOT="${CLAUDE_WORKFLOW_BASELINE_PATH:-$HOME/.claude/baselines/durable-workflow-v1}"
BASELINE_DIR="$BASELINE_CACHE_ROOT/baseline"
VERSION_FILE="$BASELINE_CACHE_ROOT/VERSION"
REPO_VERSION_MARKER="$REPO_ROOT/.claude/workflow-baseline-version"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()    { printf "${GREEN}[INFO]${NC} %s\n" "$*"; }
warn()    { printf "${YELLOW}[WARN]${NC} %s\n" "$*"; }
error()   { printf "${RED}[ERROR]${NC} %s\n" "$*"; }

# Step 1: Verify REPO_ROOT is a git repository
info "Checking git repository..."
if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    error "Not a git repository: $REPO_ROOT"
    error "Run 'git init' first, then re-execute this script."
    exit 1
fi
info "Git repository confirmed: $REPO_ROOT"

# Step 2: Verify BASELINE_DIR exists
info "Checking baseline cache..."
if [[ ! -d "$BASELINE_DIR" ]]; then
    error "Baseline cache not found at: $BASELINE_DIR"
    error ""
    error "To set up the baseline cache, run:"
    error "  git clone https://github.com/Cunning-Kang/claude-durable-workflow-baseline.git \\"
    error "    ~/.claude/baselines/durable-workflow-v1"
    error ""
    error "Then re-run this script."
    exit 1
fi

# Read baseline version if available
BASELINE_VERSION="unknown"
if [[ -f "$VERSION_FILE" ]]; then
    BASELINE_VERSION="$(grep -E '^baseline-version:' "$VERSION_FILE" 2>/dev/null | cut -d: -f2 | tr -d ' ' || echo 'unknown')"
fi
info "Baseline version: $BASELINE_VERSION"
info "Baseline source: $BASELINE_DIR"

# Step 3: Create baseline files
info "Initializing baseline files..."

CREATED=0
SKIPPED=0
CONFLICTED=0

# Arrays to track results
declare -a CREATED_FILES=()
declare -a SKIPPED_FILES=()
declare -a CONFLICTED_FILES=()

# Function to copy a single baseline file/dir
copy_baseline_item() {
    local src="$1"
    local dst="$2"
    local rel_path="${src#$BASELINE_DIR/}"
    
    if [[ ! -e "$src" ]]; then
        return
    fi
    
    if [[ -d "$src" ]]; then
        if [[ ! -e "$dst" ]]; then
            mkdir -p "$dst"
            info "  Created directory: $rel_path/"
            ((CREATED++))
            CREATED_FILES+=("$rel_path/")
        else
            info "  Skipped directory (exists): $rel_path/"
            ((SKIPPED++))
            SKIPPED_FILES+=("$rel_path/")
        fi
    else
        if [[ ! -e "$dst" ]]; then
            mkdir -p "$(dirname "$dst")"
            cp "$src" "$dst"
            info "  Created file: $rel_path"
            ((CREATED++))
            CREATED_FILES+=("$rel_path")
        else
            # Check if files are identical
            if diff -q "$src" "$dst" >/dev/null 2>&1; then
                info "  Skipped file (identical): $rel_path"
                ((SKIPPED++))
                SKIPPED_FILES+=("$rel_path")
            else
                warn "  Conflict: $rel_path (exists and differs — NOT overwritten)"
                ((CONFLICTED++))
                CONFLICTED_FILES+=("$rel_path")
                # Show diff hint
                diff -u "$dst" "$src" | head -10 >&2
                echo "  (full diff above, use 'git diff $rel_path' to see repo version)"
            fi
        fi
    fi
}

# Ensure .claude directory exists in repo
mkdir -p "$REPO_ROOT/.claude"

# Process all baseline items
while IFS= read -r item; do
    copy_baseline_item "$item" "$REPO_ROOT/${item#$BASELINE_DIR/}"
done < <(find "$BASELINE_DIR" -type f -o -type d | sort)

# Step 4: Write version marker
if [[ $CONFLICTED -eq 0 ]]; then
    mkdir -p "$(dirname "$REPO_VERSION_MARKER")"
    cat > "$REPO_VERSION_MARKER" << EOF
baseline-version: $BASELINE_VERSION
initialized: $(date -u +%Y-%m-%dT%H:%M:%SZ)
repo: $REPO_ROOT
EOF
    info "Version marker written: $REPO_VERSION_MARKER"
else
    warn "Skipping version marker (conflicts present)"
fi

# Step 5: Print summary
echo ""
echo "============================================"
echo "           BASELINE INITIALIZATION          "
echo "============================================"
echo ""
printf "${GREEN}Created:${NC}  %d\n" "$CREATED"
printf "${YELLOW}Skipped:${NC} %d\n" "$SKIPPED"
printf "${RED}Conflict:${NC} %d\n" "$CONFLICTED"
echo ""

if [[ $CREATED -gt 0 ]]; then
    echo "Files created:"
    for f in "${CREATED_FILES[@]}"; do
        echo "  + $f"
    done
    echo ""
fi

if [[ $CONFLICTED -gt 0 ]]; then
    echo "Files with conflicts (NOT overwritten):"
    for f in "${CONFLICTED_FILES[@]}"; do
        echo "  ! $f"
    done
    echo ""
    echo "To resolve conflicts, review each file and merge baseline content manually."
    echo ""
fi

echo "============================================"
echo ""

# Step 6: Print next steps
info "Next steps:"
echo "  1. Review generated files in your repo"
echo "  2. Fill in project-specific values in the templates"
echo "  3. Commit the baseline files: git add . && git commit -m 'feat: initialize durable workflow baseline'"
echo "  4. Start using Superpowers skills (e.g., /brainstorming)"
echo ""
echo "Quick verification:"
echo "  ls docs/specs/_template/"
echo "  ls docs/workflow/"
echo "  ls memory/"
echo ""
