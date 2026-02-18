#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOCKET="tmux-layout-$$"
PROJECT="sc"
TASK_ID="TASK-001"

cleanup() {
  tmux -L "$SOCKET" kill-server >/dev/null 2>&1 || true
}
trap cleanup EXIT

# First run should create all sessions and set metadata.
bash "$REPO_ROOT/tmux/scripts/create-vibe-sessions.sh" "$SOCKET" "$PROJECT" "$TASK_ID"

# Second run should be idempotent and not fail.
bash "$REPO_ROOT/tmux/scripts/create-vibe-sessions.sh" "$SOCKET" "$PROJECT" "$TASK_ID"

tmux -L "$SOCKET" has-session -t "${PROJECT}-main"
tmux -L "$SOCKET" has-session -t "${PROJECT}-side"
tmux -L "$SOCKET" has-session -t "${PROJECT}-ops"

PANES=$(tmux -L "$SOCKET" list-panes -t "${PROJECT}-ops:ops" | wc -l | tr -d ' ')
[[ "$PANES" == "2" ]]

MAIN_TASK_ID="$(tmux -L "$SOCKET" show-options -t "${PROJECT}-main" -v @task_id)"
SIDE_TASK_ID="$(tmux -L "$SOCKET" show-options -t "${PROJECT}-side" -v @task_id)"
OPS_TASK_ID="$(tmux -L "$SOCKET" show-options -t "${PROJECT}-ops" -v @task_id)"

[[ "$MAIN_TASK_ID" == "$TASK_ID" ]]
[[ "$SIDE_TASK_ID" == "$TASK_ID" ]]
[[ "$OPS_TASK_ID" == "$TASK_ID" ]]
