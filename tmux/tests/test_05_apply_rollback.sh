#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAKE_HOME="$REPO_ROOT/.tmp-home-apply-$$"

cleanup() {
  rm -rf "$FAKE_HOME"
}
trap cleanup EXIT

mkdir -p "$FAKE_HOME"
BACKUP_DIR="$FAKE_HOME/.tmux-backups"

# scenario 1: multiple backups -> rollback restores latest backup
printf 'set -g status off\n' > "$FAKE_HOME/.tmux.conf"
TARGET_HOME="$FAKE_HOME" bash "$REPO_ROOT/tmux/scripts/apply-config.sh" "$REPO_ROOT"

printf 'set -g status on\n' > "$FAKE_HOME/.tmux.conf"
TARGET_HOME="$FAKE_HOME" bash "$REPO_ROOT/tmux/scripts/apply-config.sh" "$REPO_ROOT"

[[ -f "$FAKE_HOME/.tmux.conf" ]]
grep -Eq "source-file\s+\"?$REPO_ROOT/tmux/tmux\.conf\"?$" "$FAKE_HOME/.tmux.conf"
grep -Eq "set-environment\s+-g\s+TMUX_REPO_ROOT\s+\"?$REPO_ROOT\"?$" "$FAKE_HOME/.tmux.conf"

[[ -d "$BACKUP_DIR" ]]
compgen -G "$BACKUP_DIR/.tmux.conf.*.bak" > /dev/null

TARGET_HOME="$FAKE_HOME" bash "$REPO_ROOT/tmux/scripts/rollback-config.sh"

grep -q "set -g status on" "$FAKE_HOME/.tmux.conf"
! grep -q "set -g status off" "$FAKE_HOME/.tmux.conf"

# scenario 2: no initial .tmux.conf -> rollback safely restores absent state
rm -f "$FAKE_HOME/.tmux.conf"
TARGET_HOME="$FAKE_HOME" bash "$REPO_ROOT/tmux/scripts/apply-config.sh" "$REPO_ROOT"
[[ -f "$FAKE_HOME/.tmux.conf" ]]
compgen -G "$BACKUP_DIR/.tmux.conf.*.absent" > /dev/null

TARGET_HOME="$FAKE_HOME" bash "$REPO_ROOT/tmux/scripts/rollback-config.sh"
[[ ! -f "$FAKE_HOME/.tmux.conf" ]]

echo "PASS: apply and rollback config test passed"
