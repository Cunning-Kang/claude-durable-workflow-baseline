#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONF_FILE="${ROOT_DIR}/tmux.conf"
SOCKET_NAME="task1-smoke-$$"
TMUX_TMPDIR="${TMPDIR:-/private/tmp/claude-501/}"
mkdir -p "${TMUX_TMPDIR}"

cleanup() {
  TMUX_TMPDIR="${TMUX_TMPDIR}" tmux -L "${SOCKET_NAME}" kill-server >/dev/null 2>&1 || true
}
trap cleanup EXIT

if [[ ! -f "${CONF_FILE}" ]]; then
  echo "FAIL: missing tmux config at ${CONF_FILE}" >&2
  exit 1
fi

if ! grep -Fxq 'set -g @session_model "main-side-ops"' "${CONF_FILE}"; then
  echo 'FAIL: tmux.conf must contain exact line: set -g @session_model "main-side-ops"' >&2
  exit 1
fi

if ! TMUX_TMPDIR="${TMUX_TMPDIR}" tmux -f "${CONF_FILE}" -L "${SOCKET_NAME}" start-server; then
  echo "FAIL: tmux could not parse config syntax" >&2
  exit 1
fi

TMUX_TMPDIR="${TMUX_TMPDIR}" tmux -L "${SOCKET_NAME}" kill-server >/dev/null 2>&1 || true

echo "PASS: tmux config syntax smoke test passed"