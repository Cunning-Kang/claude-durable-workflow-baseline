# Review Gate Semantics — PASS / FAIL / BLOCKED

> Canonical semantics for the review gate defined in core-standard.md.

This file defines review gate status only. Whether review is required is determined by `core-standard.md`.

---

## Independence Requirement

Independent means: reviewer did not implement the reviewed change.
Self-review does not satisfy this gate unless a higher-precedence policy explicitly permits it.
Not independent: the same agent reviewing its own prior output.

## Required Evidence

- `Reviewer`: <identity>
- `Reviewed scope`: <commit, diff range, or exact files>
- `Reference`: <message, task, file, PR comment, or other artifact containing the review result>

Review evidence is valid only if `Reviewed scope` matches the current change being claimed as complete.
If the reviewed diff changes after review, the previous review is stale for changed files or behavior affected by those changes.

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
