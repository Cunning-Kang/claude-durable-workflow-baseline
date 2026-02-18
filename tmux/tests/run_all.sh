#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "${TEST_DIR}/test_01_config_syntax.sh"
bash "${TEST_DIR}/test_02_session_template.sh"
bash "${TEST_DIR}/test_03_logging_modes.sh"
bash "${TEST_DIR}/test_04_upgrade_ports.sh"
bash "${TEST_DIR}/test_05_apply_rollback.sh"

echo "ALL TMUX TESTS PASSED"
