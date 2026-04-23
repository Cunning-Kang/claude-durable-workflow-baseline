# Review Gate Semantics — PASS / FAIL / BLOCKED

> Canonical semantics for the review gate defined in core-standard.md.

This file defines review gate status only. Whether review is required is determined by `core-standard.md`.

---

## Independence Requirement

Independent means: reviewer did not implement the reviewed change.
Self-review does not satisfy this gate unless a higher-precedence policy explicitly permits it.
Not independent: the same assistant in a second pass, or a reviewer that edits the implementation.

## Required Evidence

- `Reviewer`: <identity>
- `Reviewed scope`: <commit, diff range, or exact files>
- `Reference`: <message, task, file, PR comment, or other artifact containing the review result>

Review evidence is valid only if `Reviewed scope` matches the current change being claimed as complete.

## Status Definitions

| Status | Condition |
|--------|-----------|
| `PASS` | Independent review complete; no blocking findings in recorded evidence |
| `FAIL` | Independent review complete; blocking findings in recorded evidence |
| `BLOCKED` | Required independent review cannot currently be completed with recorded evidence |

Without independent review and recorded evidence: `PASS` and `FAIL` are invalid. `BLOCKED` is required.
`N/A` is invalid when review is required.

## Blocked State Rule

`BLOCKED` → status stays `In Progress` unless a higher-precedence policy explicitly permits an alternative.
When entering `BLOCKED`, state what is required to unblock.
