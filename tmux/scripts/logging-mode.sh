#!/usr/bin/env bash
set -euo pipefail

SOCKET=""
PROJECT=""
MODE=""
LOG_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --socket)
      SOCKET="${2:-}"
      shift 2
      ;;
    --project)
      PROJECT="${2:-}"
      shift 2
      ;;
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --log-root)
      LOG_ROOT="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$SOCKET" || -z "$PROJECT" || -z "$MODE" ]]; then
  echo "Usage: logging-mode.sh --socket <socket> --project <project> --mode <l1|l2|off> [--log-root <dir>]" >&2
  exit 1
fi

if [[ "$SOCKET" == */* ]]; then
  TMUX_CMD=(tmux -S "$SOCKET")
else
  TMUX_CMD=(tmux -L "$SOCKET")
fi

run_tmux() {
  "${TMUX_CMD[@]}" "$@"
}

pipe_is_on() {
  local target="$1"
  [[ "$(run_tmux display-message -p -t "$target" '#{pane_pipe}')" == "1" ]]
}

disable_pipe() {
  local target="$1"
  if pipe_is_on "$target"; then
    run_tmux pipe-pane -t "$target"
  fi
}

set_pipe() {
  local target="$1"
  local logfile="$2"

  disable_pipe "$target"
  run_tmux pipe-pane -t "$target" "cat >> '$logfile'"
}

MAIN_TARGET="${PROJECT}-main:chat.0"
SIDE_TARGET="${PROJECT}-side:compare.0"
OPS_TARGET="${PROJECT}-ops:ops.0"

case "$MODE" in
  l1)
    LOG_ROOT="${LOG_ROOT:-$PWD/.tmux-logs/$(date +%F)}"
    mkdir -p "$LOG_ROOT"
    : > "$LOG_ROOT/${PROJECT}-ops.log"

    disable_pipe "$MAIN_TARGET"
    disable_pipe "$SIDE_TARGET"
    set_pipe "$OPS_TARGET" "$LOG_ROOT/${PROJECT}-ops.log"
    run_tmux set-option -g @vibe_logging_mode "l1"
    ;;
  l2)
    LOG_ROOT="${LOG_ROOT:-$PWD/.tmux-logs/$(date +%F)}"
    mkdir -p "$LOG_ROOT"
    : > "$LOG_ROOT/${PROJECT}-main.log"
    : > "$LOG_ROOT/${PROJECT}-side.log"
    : > "$LOG_ROOT/${PROJECT}-ops.log"

    set_pipe "$MAIN_TARGET" "$LOG_ROOT/${PROJECT}-main.log"
    set_pipe "$SIDE_TARGET" "$LOG_ROOT/${PROJECT}-side.log"
    set_pipe "$OPS_TARGET" "$LOG_ROOT/${PROJECT}-ops.log"
    run_tmux set-option -g @vibe_logging_mode "l2"
    ;;
  off)
    disable_pipe "$MAIN_TARGET"
    disable_pipe "$SIDE_TARGET"
    disable_pipe "$OPS_TARGET"
    run_tmux set-option -g @vibe_logging_mode "off"
    ;;
  *)
    echo "mode must be l1|l2|off" >&2
    exit 1
    ;;
esac
