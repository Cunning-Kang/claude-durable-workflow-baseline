#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONF_FILE="${REPO_ROOT}/tmux/tmux.conf"

for f in \
  "${REPO_ROOT}/tmux/ports/plugins-recovery.conf" \
  "${REPO_ROOT}/tmux/ports/plugins-navigation.conf" \
  "${REPO_ROOT}/tmux/ports/plugins-logging.conf" \
  "${REPO_ROOT}/tmux/ports/plugins-statusline.conf"; do
  [[ -f "$f" ]]
  grep -q "default: disabled" "$f"
done

grep -Eq '^set -g @port_recovery "off"$' "$CONF_FILE"
grep -Eq '^set -g @port_navigation "off"$' "$CONF_FILE"
grep -Eq '^set -g @port_logging "off"$' "$CONF_FILE"
grep -Eq '^set -g @port_statusline "off"$' "$CONF_FILE"

grep -Eq '^if-shell '\''\[ -n "#\{environ:TMUX_REPO_ROOT\}" \]'\'' '\''source-file "#\{environ:TMUX_REPO_ROOT\}/tmux/ports/plugins-recovery\.conf"'\''$' "$CONF_FILE"
grep -Eq '^if-shell '\''\[ -n "#\{environ:TMUX_REPO_ROOT\}" \]'\'' '\''source-file "#\{environ:TMUX_REPO_ROOT\}/tmux/ports/plugins-navigation\.conf"'\''$' "$CONF_FILE"
grep -Eq '^if-shell '\''\[ -n "#\{environ:TMUX_REPO_ROOT\}" \]'\'' '\''source-file "#\{environ:TMUX_REPO_ROOT\}/tmux/ports/plugins-logging\.conf"'\''$' "$CONF_FILE"
grep -Eq '^if-shell '\''\[ -n "#\{environ:TMUX_REPO_ROOT\}" \]'\'' '\''source-file "#\{environ:TMUX_REPO_ROOT\}/tmux/ports/plugins-statusline\.conf"'\''$' "$CONF_FILE"

# C-v should derive project from current pane path, not hardcode "sc".
grep -Fq '#{pane_current_path}' "$CONF_FILE"
if grep -Fq 'create-vibe-sessions.sh" "#{socket_path}" "sc"' "$CONF_FILE"; then
  echo 'FAIL: C-v binding must not hardcode project name "sc"' >&2
  exit 1
fi

echo "PASS: plugin upgrade ports test passed"
