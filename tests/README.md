# `tests/` — Contract and Hook Verification Tests

This directory contains **implementation verification tests** for the distribution contract and hook templates in `distribution/hooks/project/`.

## What These Tests Do

### Python Contract Tests (`test_distribution_contract.py`)
Validates distribution install behavior: the init script, slash command docs, global install semantics, and agent inventory consistency. Run with:
```
python -m pytest tests/test_distribution_contract.py -v
```

### Node.js Hook Tests (`*.test.mjs`)
Each `*.test.mjs` file validates one TaskCompleted hook's gate logic by feeding it controlled payloads and asserting the expected exit codes and error messages. Run with:
```
node --test tests/*.test.mjs
```

## Committed Test Files

| File | Purpose |
|------|---------|
| `test_distribution_contract.py` | Distribution install contract (init script, commands, global/* install) |
| `taskcompleted-authoritative-state-gate.test.mjs` | Authoritative state tracker gate |
| `taskcompleted-review-evidence-gate.test.mjs` | Review evidence gate (empty-field enforcement) |
| `taskcompleted-verification-evidence-gate.test.mjs` | Verification evidence gate |

## How to Run

The authoritative manual-test documentation lives in each hook's `manual-test.md`:
```
distribution/hooks/project/<hook-name>/manual-test.md
```
That file contains step-by-step manual test scenarios with expected outputs.

## Adopter Relevance

These tests are **not part of the adoption surface**. They are:
- **Maintainer-facing** — used to verify distribution contract and hook logic during development
- **Not auto-run** — no CI is configured to run them by default
- **Committed to the repo** — tracked in version control to prevent regression

You do not need to run these to adopt the baseline. You may read them to understand the distribution contract and hook gate behavior.
