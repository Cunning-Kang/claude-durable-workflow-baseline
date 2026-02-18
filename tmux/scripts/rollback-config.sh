#!/usr/bin/env bash
set -euo pipefail

TARGET_HOME="${TARGET_HOME:-$HOME}"
TARGET_FILE="$TARGET_HOME/.tmux.conf"
BACKUP_DIR="$TARGET_HOME/.tmux-backups"

if [[ ! -d "$BACKUP_DIR" ]]; then
  echo "No backup directory found: $BACKUP_DIR" >&2
  exit 1
fi

shopt -s nullglob
MARKERS=("$BACKUP_DIR"/.tmux.conf.*.bak "$BACKUP_DIR"/.tmux.conf.*.absent)
shopt -u nullglob

if [[ ${#MARKERS[@]} -eq 0 ]]; then
  echo "No backups found in: $BACKUP_DIR" >&2
  exit 1
fi

IFS=$'\n' SORTED_MARKERS=($(ls -1t "${MARKERS[@]}"))
unset IFS
LATEST_MARKER="${SORTED_MARKERS[0]}"

if [[ "$LATEST_MARKER" == *.absent ]]; then
  rm -f "$TARGET_FILE"
else
  cp "$LATEST_MARKER" "$TARGET_FILE"
fi
