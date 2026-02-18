#!/usr/bin/env bash
set -euo pipefail

SOCKET="${1:?socket required}"
PROJECT="${2:?project required}"
TASK_ID="${3:-}"
PROJECT_PATH="${4:-}"

if [[ -z "$PROJECT_PATH" ]]; then
  PROJECT_PATH="$PWD"
fi

MAIN_SESSION="${PROJECT}-main"
SIDE_SESSION="${PROJECT}-side"
OPS_SESSION="${PROJECT}-ops"

if [[ "$SOCKET" == */* ]]; then
  TMUX_CMD=(tmux -S "$SOCKET")
else
  TMUX_CMD=(tmux -L "$SOCKET")
fi

run_tmux() {
  if ! "${TMUX_CMD[@]}" "$@"; then
    echo "ERROR: tmux command failed (socket=$SOCKET project=$PROJECT): tmux $*" >&2
    return 1
  fi
}

session_exists() {
  "${TMUX_CMD[@]}" has-session -t "$1" >/dev/null 2>&1
}

if ! session_exists "$MAIN_SESSION"; then
  run_tmux new-session -d -c "$PROJECT_PATH" -s "$MAIN_SESSION" -n chat
fi

if ! session_exists "$SIDE_SESSION"; then
  run_tmux new-session -d -c "$PROJECT_PATH" -s "$SIDE_SESSION" -n compare
fi

if ! session_exists "$OPS_SESSION"; then
  run_tmux new-session -d -c "$PROJECT_PATH" -s "$OPS_SESSION" -n ops
fi

OPS_PANES=$("${TMUX_CMD[@]}" list-panes -t "${OPS_SESSION}:ops" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$OPS_PANES" == "1" ]]; then
  run_tmux split-window -t "${OPS_SESSION}:ops" -v -p 35
fi

if [[ -n "$TASK_ID" ]]; then
  run_tmux set-option -t "$MAIN_SESSION" @task_id "$TASK_ID"
  run_tmux set-option -t "$SIDE_SESSION" @task_id "$TASK_ID"
  run_tmux set-option -t "$OPS_SESSION" @task_id "$TASK_ID"
fi
