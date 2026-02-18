#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNNER="${REPO_ROOT}/tmux/tests/run_all.sh"

if [[ ! -x "${RUNNER}" ]]; then
  echo "FAIL: missing executable runner at ${RUNNER}" >&2
  exit 1
fi

OUTPUT="$(${RUNNER} 2>&1)"

assert_contains() {
  local needle="$1"
  if [[ "${OUTPUT}" != *"${needle}"* ]]; then
    echo "FAIL: expected output to contain '${needle}'" >&2
    echo "Actual output:" >&2
    echo "${OUTPUT}" >&2
    exit 1
  fi
}

# key PASS outputs from run_all (covers test_01, test_03, test_04, test_05)
assert_contains "PASS: tmux config syntax smoke test passed"
assert_contains "PASS: logging modes test passed"
assert_contains "PASS: plugin upgrade ports test passed"
assert_contains "PASS: apply and rollback config test passed"

# keep summary assertion
assert_contains "ALL TMUX TESTS PASSED"

# test_02 currently has no PASS line; assert it still passes.
bash "${REPO_ROOT}/tmux/tests/test_02_session_template.sh" >/dev/null 2>&1

echo "PASS: run_all summary and key subtests output test passed"
