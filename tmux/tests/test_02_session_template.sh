#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOCKET="tmux-layout-$$"
PROJECT="sc"
TASK_ID="TASK-001"

PROJECT_DIR="$(mktemp -d "$REPO_ROOT/.tmux-project-test.XXXXXX")"

cleanup() {
  tmux -L "$SOCKET" kill-server >/dev/null 2>&1 || true
  rm -rf "$PROJECT_DIR"
}
trap cleanup EXIT

# First run should create all sessions and set metadata.
bash "$REPO_ROOT/tmux/scripts/create-vibe-sessions.sh" "$SOCKET" "$PROJECT" "$TASK_ID"

# Second run should be idempotent and not fail.
bash "$REPO_ROOT/tmux/scripts/create-vibe-sessions.sh" "$SOCKET" "$PROJECT" "$TASK_ID"

# Path-aware creation: when a project path is passed, new sessions should start there.
PROJECT_WITH_PATH="scpath"
bash "$REPO_ROOT/tmux/scripts/create-vibe-sessions.sh" "$SOCKET" "$PROJECT_WITH_PATH" "" "$PROJECT_DIR"

PATH_MAIN_PANE="$(tmux -L "$SOCKET" list-panes -t "${PROJECT_WITH_PATH}-main:chat" -F '#{pane_id}' | head -n 1)"
PATH_MAIN_DIR="$(tmux -L "$SOCKET" display-message -p -t "$PATH_MAIN_PANE" '#{pane_current_path}')"
if [[ "$PATH_MAIN_DIR" != "$PROJECT_DIR" ]]; then
  echo "FAIL: expected $PROJECT_DIR, got $PATH_MAIN_DIR" >&2
  exit 1
fi

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
