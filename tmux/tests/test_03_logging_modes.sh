#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SOCKET="tmux-log-$$"
PROJECT="sc"
LOG_ROOT_A="$REPO_ROOT/.tmux-logs/test-$SOCKET-a"
LOG_ROOT_B="$REPO_ROOT/.tmux-logs/test-$SOCKET-b"

cleanup() {
  tmux -L "$SOCKET" kill-server >/dev/null 2>&1 || true
  rm -rf "$LOG_ROOT_A" "$LOG_ROOT_B"
}
trap cleanup EXIT

bash "$REPO_ROOT/tmux/scripts/create-vibe-sessions.sh" "$SOCKET" "$PROJECT" "TASK-001"

resolve_primary_pane() {
  local window_target="$1"
  local pane_id=""

  while IFS= read -r pane_id; do
    break
  done < <(tmux -L "$SOCKET" list-panes -t "$window_target" -F '#{pane_id}')

  if [[ -z "$pane_id" ]]; then
    echo "FAIL: no pane found for $window_target" >&2
    exit 1
  fi

  printf '%s\n' "$pane_id"
}

MAIN_PANE="$(resolve_primary_pane "${PROJECT}-main:chat")"
SIDE_PANE="$(resolve_primary_pane "${PROJECT}-side:compare")"
OPS_PANE="$(resolve_primary_pane "${PROJECT}-ops:ops")"

# L1: ops only (root A)
bash "$REPO_ROOT/tmux/scripts/logging-mode.sh" --socket "$SOCKET" --project "$PROJECT" --mode l1 --log-root "$LOG_ROOT_A"
[[ -f "$LOG_ROOT_A/${PROJECT}-ops.log" ]]
[[ ! -f "$LOG_ROOT_A/${PROJECT}-main.log" ]]
[[ ! -f "$LOG_ROOT_A/${PROJECT}-side.log" ]]

# write marker in l1 (must go to root A ops log)
L1_MARKER="L1_A_$$"
tmux -L "$SOCKET" send-keys -t "$OPS_PANE" "echo $L1_MARKER" Enter
sleep 0.2
grep -q "$L1_MARKER" "$LOG_ROOT_A/${PROJECT}-ops.log"

# L2: main + side + ops (switch to root B)
bash "$REPO_ROOT/tmux/scripts/logging-mode.sh" --socket "$SOCKET" --project "$PROJECT" --mode l2 --log-root "$LOG_ROOT_B"
[[ -f "$LOG_ROOT_B/${PROJECT}-main.log" ]]
[[ -f "$LOG_ROOT_B/${PROJECT}-side.log" ]]
[[ -f "$LOG_ROOT_B/${PROJECT}-ops.log" ]]

# write markers after switching root, all should go to root B
MAIN_B_MARKER="MAIN_B_$$"
SIDE_B_MARKER="SIDE_B_$$"
OPS_B_MARKER="OPS_B_$$"

tmux -L "$SOCKET" send-keys -t "$MAIN_PANE" "echo $MAIN_B_MARKER" Enter
tmux -L "$SOCKET" send-keys -t "$SIDE_PANE" "echo $SIDE_B_MARKER" Enter
tmux -L "$SOCKET" send-keys -t "$OPS_PANE" "echo $OPS_B_MARKER" Enter
sleep 0.2

grep -q "$MAIN_B_MARKER" "$LOG_ROOT_B/${PROJECT}-main.log"
grep -q "$SIDE_B_MARKER" "$LOG_ROOT_B/${PROJECT}-side.log"
grep -q "$OPS_B_MARKER" "$LOG_ROOT_B/${PROJECT}-ops.log"

# switched root must take effect for ops too (no stale pipe to root A)
if grep -q "$OPS_B_MARKER" "$LOG_ROOT_A/${PROJECT}-ops.log"; then
  echo "FAIL: ops pane still logs to old root after mode switch" >&2
  exit 1
fi

# off: disable pane pipes and set mode metadata
bash "$REPO_ROOT/tmux/scripts/logging-mode.sh" --socket "$SOCKET" --project "$PROJECT" --mode off --log-root "$LOG_ROOT_B"
[[ "$(tmux -L "$SOCKET" show-options -gv @vibe_logging_mode)" == "off" ]]

[[ -z "$(tmux -L "$SOCKET" display-message -p -t "$MAIN_PANE" '#{pane_pipe}')" ]]
[[ -z "$(tmux -L "$SOCKET" display-message -p -t "$SIDE_PANE" '#{pane_pipe}')" ]]
[[ -z "$(tmux -L "$SOCKET" display-message -p -t "$OPS_PANE" '#{pane_pipe}')" ]]

echo "PASS: logging modes test passed"
