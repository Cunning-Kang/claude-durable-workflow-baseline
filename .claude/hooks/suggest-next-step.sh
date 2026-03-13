#!/usr/bin/env bash
set -euo pipefail

# UserPromptSubmit hook: add conservative next-step suggestions to model context.
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$PROJECT_DIR"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

status="$(git status --short || true)"
changed_entries_count="$(printf "%s\n" "$status" | sed '/^$/d' | wc -l | tr -d ' ')"
untracked_count="$(printf "%s\n" "$status" | grep -c '^??' || true)"

if [ "${changed_entries_count:-0}" -gt 0 ] && [ "${changed_entries_count:-0}" -le 8 ] && [ "${untracked_count:-0}" -le 2 ]; then
  cat <<'EOF'
{
  "hookSpecificOutput": {
    "additionalContext": "Heuristic signal: the current changes may be a coherent verified batch. If the just-finished work completed a small implementation slice and checks are still fresh, consider running /commit-batch before accumulating more changes."
  }
}
EOF
  exit 0
fi

if [ -z "$status" ]; then
  cat <<'EOF'
{
  "hookSpecificOutput": {
    "additionalContext": "Heuristic signal: the working tree is clean. If the scoped work is fully implemented, reviewed, and task state is accurate, consider running /finish-branch as the next workflow step."
  }
}
EOF
  exit 0
fi

exit 0
