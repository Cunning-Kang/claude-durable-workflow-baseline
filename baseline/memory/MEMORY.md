# Project Memory

Baseline durable overview — see [boundary doc][boundary] and [memory protocol][protocol]
for classification rules.  Content here must satisfy D1/D2/D3 (always-relevant,
cross-session, not speculative).

## This File Is For

- Project rules that fit 1–3 lines with no example needed
- Enforcement-level facts (gates, tool requirements, non-negotiable conventions)
- Links to authoritative sources (do not duplicate rationale)
- Critical gotchas (data loss, security, significant time waste)

## This File Is NOT For

- Pattern explanations or reusable templates → [patterns.md](patterns.md)
- Pitfall descriptions that need explanation → [gotchas.md](gotchas.md)
- Protocol/rule definitions → [`baseline/docs/workflow/`](baseline/docs/workflow/)
- Host-wide durable rules → [`global/standards/core-standard.md`](../../global/standards/core-standard.md)
- One-off notes, task logs, session summaries, or speculative content

## Baseline Overview

> These two structural boundary guards are the only durable facts in this file
> that are not rules themselves — they define the repo's role and the
> Superpowers boundary.  Additional §5.1-conforming entries belong in
> **"This File Is For"**, not here.

- This repo is a **baseline source and distribution source** for durable workflow
  knowledge.  It is not a second workflow runtime.
- **Superpowers** (`superpowers:*` skills) is the primary global control layer.
  Do not add generic planning/execution/review skills here that duplicate it.
- For routing questions, consult [boundary doc][boundary] §7.

## Links

- [`patterns.md`](patterns.md) — reusable patterns; triggered by demonstrated copy-paste applicability
- [`gotchas.md`](gotchas.md) — recurring pitfalls with evasion steps; triggered by recurrence across sessions

[boundary]: ../../docs/reference/memory-boundary.md
[protocol]: ../docs/workflow/memory-protocol.md
