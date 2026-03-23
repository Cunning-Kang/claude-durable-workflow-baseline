# `tests/` — Hook Validation Tests

This directory contains **implementation verification tests** for the hook templates in `distribution/hooks/project/`.

## What These Tests Do

Each `*.test.mjs` file validates one hook's gate logic by feeding it controlled payloads and asserting the expected exit codes and error messages.

## How to Run

The authoritative manual-test documentation lives in each hook's `manual-test.md`:

```
distribution/hooks/project/<hook-name>/manual-test.md
```

That file contains step-by-step manual test scenarios with expected outputs.

## Adopter Relevance

These tests are **not part of the adoption surface**. They are:
- **Maintainer-facing** — used to verify hook logic during development
- **Not auto-run** — no CI is configured to run them
- **Untracked** — intentionally not committed; present in the repo as loose validation surface

You do not need to run these to adopt the baseline. You may read them to understand hook gate behavior.
