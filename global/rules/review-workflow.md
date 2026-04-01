---
alwaysApply: true
---

# Review Workflow — PASS / FAIL / BLOCKED Mechanics

> Core review gate semantics — always loaded as part of the review gate protocol.
> Extends core-standard.md §6 with specific operational mechanics.

---

## Independence Requirement

Independent means: reviewer did not implement the reviewed change.
Self-review does not satisfy this gate unless a higher-precedence policy explicitly permits it.

## Required Evidence

- `Reviewer`: <identity>
- `Reference`: <message, task, or artifact containing the review result>

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
