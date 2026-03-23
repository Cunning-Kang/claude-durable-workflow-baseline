# Memory Protocol

> **Authority:** [`docs/reference/memory-boundary.md`](../../reference/memory-boundary.md) is the boundary document for all memory classification decisions during Phase 4 (P4-T02–P4-T06). This protocol doc governs the *work process* of writing to memory — intake discipline, update/removal mechanics, and anti-patterns to avoid during writing.

This document does not redefine what belongs in memory. It defines how to write memory correctly.

---

## 1. Boundary Authority

All memory content decisions derive from [`docs/reference/memory-boundary.md`](../../reference/memory-boundary.md). Key sections to consult:

| Boundary section | What it governs |
|---|---|
| §4 Durability Criteria | D1/D2/D3 — whether content qualifies as durable memory |
| §5.1–§5.3 File Roles | Scope, non-scope, and typical entry format for each memory file |
| §5.4 Cross-File Duplication | Which file a borderline entry belongs in |
| §7 Routing Table | Where any piece of content belongs; what to do if not durable |
| §9 Anti-Patterns | 8 known failure modes in memory writing |

When classification is unclear, apply D1/D2/D3 (§4 boundary) first, then route via §7.

---

## 2. When to Write — Intake Triggers

Write to memory **only after** one of these events, and **only if** D1/D2/D3 all pass:

| Trigger | Example |
|---|---|
| Feature closeout | `/new-feature user-auth` completed and merged; a durable lesson surfaced |
| Independent review | Reviewer identified a recurring pattern across sessions |
| Blocking issue resolved | Root cause was durable (not a one-off); solution is reusable |
| New convention established | Team agreed on a stable pattern via discussion |

If a triggering event occurred but D1/D2/D3 do not all pass, do not write to memory. Route per §7 instead.

---

## 3. What to Write — Classification

Classification is governed by `docs/reference/memory-boundary.md`. Do not re-apply a separate or parallel classification standard.

This table is for orientation only — the full table in boundary §7 governs all classification decisions. Quick reference:

| Content type | Belongs in | When not durable |
|---|---|---|
| Project convention (how things are done) | `MEMORY.md` | — |
| Enforcement gate or critical requirement | `MEMORY.md` | — |
| Reusable command sequence or template | `patterns.md` | — |
| Workflow approach demonstrated to recur | `patterns.md` | — |
| Failure mode with evasion step | `gotchas.md` | — |
| Setup trap that bites repeatedly | `gotchas.md` | — |
| Hook behavior / installation | `docs/reference/hooks-scope.md` | Hook source files |
| Protocol / workflow definition | `baseline/docs/workflow/` | — |
| Global CLI rule | `global/core-standard.md` | — |
| Skill behavior | Skill's `SKILL.md` | — |

For the full routing table and classification rules, see boundary §7.

---

## 4. Where Each File Lives

```
baseline/memory/
  MEMORY.md      — always-relevant rules, conventions, critical gotchas
  patterns.md    — reusable patterns others can apply directly
  gotchas.md     — recurring pitfalls and how to avoid them
```

File role definitions are in boundary §5.1–§5.3. The short version:

- **MEMORY.md** — concise (1–5 lines), enforcement-level, actionable without additional context
- **patterns.md** — trigger + action, copy-paste applicable
- **gotchas.md** — situation → what goes wrong → why → how to avoid

---

## 5. Cross-File Duplication Prevention

Each durable fact lives **once**. Before adding an entry, check boundary §5.4:

| Situation | Correct file |
|---|---|
| Rule fits in 1–3 lines, no example needed | `MEMORY.md` |
| Rule needs trigger + action, copy-paste applicable | `patterns.md` |
| Rule describes a failure mode to avoid | `gotchas.md` |
| Rule is both a pattern and a gotcha | Primary intent; cross-reference if both significant |
| One-liner that is also a pitfall | Concise rule in `MEMORY.md`; explanation in `gotchas.md` with cross-reference |

If the same fact appears in two files, consolidate into one and cross-reference.

---

## 6. How to Write an Entry

### Before / After pattern

Do not write vague guidance. Write specific, actionable entries:

**Bad:**
> "Be careful with console.log in CI."

**Good:**
> `GOTCHA: Node.js console.log in CI is buffered`
> `console.log` output is buffered in many CI environments, causing interleaved output to appear out of order.
> Fix: use `process.stdout.write()` for scripts that output in CI.

**Bad:**
> "Remember to run tests before committing."

**Good:**
> `GIT COMMIT GATE: mise run lint && mise run test must pass before git commit. CI enforces this — no bypasses.`

---

## 7. How to Update

**Prefer updating over adding a new duplicate** when an existing entry covers the same durable lesson.

Update rules (from boundary §8.2):
- Append new information rather than replacing; preserve the original date
- Add an `Updated: YYYY-MM-DD` marker
- If the update fundamentally changes the entry's intent, treat it as removal + new intake

### Update template

```
Pattern: X
Added: 2026-01-15
Updated: 2026-03-23  ← new update
[appended context or correction]
```

---

## 8. When to Remove

Apply removal criteria proactively — do not wait for P4-T06. From boundary §8.3:

| Condition | Action |
|---|---|
| Entry describes something that no longer recurs | Remove |
| Entry was a misclassification | Remove; re-route to correct destination |
| Entry is duplicated in another memory file | Merge; keep in the file with the more appropriate role |
| Entry has been superseded by a protocol doc or global rule | Remove; reference the authoritative source instead |
| Entry is a one-off that was incorrectly durablefied | Remove; do not replace |

**Age is not a removal criterion.** If it recurs, it stays.

**Before removing any entry**, record what was removed and why for P4-T06 audit.

---

## 9. Anti-Patterns to Avoid

These are memory writing failures. See boundary §9 for full descriptions.

| # | Anti-pattern | What to do instead |
|---|---|---|
| AP-1 | **Durability Inflation** — treating session-specific content as durable | Apply D1/D2/D3 before every addition |
| AP-2 | **Memory Bloat** — entries accumulate without review | Apply removal criteria proactively |
| AP-3 | **Cross-File Duplication** — same fact in two files | Consolidate via §5.4 rules |
| AP-4 | **Memory as Task Log** — feature progress, session summaries | Route to feature spec / issue tracker |
| AP-5 | **Protocol Dumping** — writing protocol definitions into memory | Protocol content goes in `baseline/docs/workflow/` |
| AP-6 | **Hook/Command Content in Memory** — hook installation steps in memory | Hooks belong in hook source files or `docs/reference/hooks-scope.md` |
| AP-7 | **Vague Entries** — entries that say "be careful with X" or "don't forget Y" without enough context to act on | Rewrite to be specific and action-triggering, or delete if it cannot be made specific |
| AP-8 | **One-Off Retention** — keeping entries for blockers or failures that were truly one-off and will not recur | Remove; one-off is a removal signal, not a keep signal |

---

## 10. What This Document Is Not

This protocol does not:
- Redefine D1/D2/D3 (see boundary §4)
- Replicate the routing table (see boundary §7)
- Contain any durable memory content itself
- Substitute for reading `docs/reference/memory-boundary.md`

Its job is to define the **process** of writing, updating, and maintaining memory entries — not the classification criteria, which live in the boundary authority.
