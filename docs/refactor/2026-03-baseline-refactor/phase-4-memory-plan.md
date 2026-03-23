# Phase 4 — Memory: Execution-Level Plan

> Status: Phase 4 Clarification | Date: 2026-03-22
> Inheritance: Extends `plan.md § Phase 4 — Memory` without rewriting it
> Authoritative sources: `plan.md` + `tasks.md`

---

## 1. Execution Goal

Implement the Phase 4 objective from `plan.md`:

> 把经验、误用案例、环境差异从 global core 和临时控制面里清出去，沉淀到 `baseline/memory/*` 与对应 protocol 中，但只保留 durable lessons.

Execution-level translation: The goal is a **purge-and-anchor** operation — remove的经验性/环境性知识 from `global/core-standard.md` and any temporary control surfaces, and anchor durable equivalents in the `baseline/memory/*` skeleton under clear protocol rules. No new memory content is created unless it replaces extracted material.

---

## 2. Execution Scope

From `plan.md § Phase 4 — Memory / 范围`:

| Item | Description |
|------|-------------|
| S1 | Define memory boundary (`docs/reference/memory-boundary.md` or equivalent) |
| S2 | Align `baseline/docs/workflow/memory-protocol.md` |
| S3 | Strengthen `baseline/memory/MEMORY.md` |
| S4 | Strengthen `baseline/memory/patterns.md` |
| S5 | Strengthen `baseline/memory/gotchas.md` |
| S6 | Consistency review of protocol ↔ skeleton |

---

## 3. Non-Goals

From `plan.md § Phase 4 — Memory / 非目标`:
- Do NOT write new memory content from scratch — only extract and solidify what already exists in global core or protocol docs
- Do NOT modify `global/core-standard.md` content directly (extraction target only; modifications happen via P4-T03/P4-T04/P4-T05)
- Do NOT create `baseline/memory/*.md` content in this phase — clarification only
- Do NOT touch hooks, commands, or Superpowers entry points

---

## 4. Memory Boundary — Execution Interpretation

### 4.1 What Goes Into `baseline/memory/*`

| File | Durable Criterion | Examples |
|------|-------------------|----------|
| `MEMORY.md` | Stable, always-relevant, cross-session rules | Repo purpose, stable conventions, critical boundary rules |
| `patterns.md` | Reusable patterns others apply directly | Orchestration patterns, tool-selection conventions, effective workflow steps |
| `gotchas.md` | Recurring pitfalls with known solutions | Known误用案例, environment pitfalls, common mistakes with evasion steps |

**Shared durability gate:** Content must be:
- Validated across multiple sessions or multiple contributors
- Not tied to a single task, session, or transient experiment
- Not speculative (must have demonstrated recurrence)

### 4.2 What Does NOT Go Into `baseline/memory/*`

Per `memory-protocol.md § What does not belong in memory`:

- Feature progress or implementation notes
- One-off blockers that won't recur
- Temporary experiments that didn't work
- Raw execution logs or command output
- Speculative ideas not yet validated
- Session-specific state (e.g., current task, in-progress work)
- Author preferences without demonstrated durability

### 4.3 Routing for Non-Memory Content

| Content Type | Destination |
|--------------|-------------|
| Host-wide durable rules | `global/core-standard.md` |
| Per-project durable rules | `baseline/memory/MEMORY.md` |
| Reusable workflow patterns | `baseline/memory/patterns.md` |
| Recurring pitfalls + solutions | `baseline/memory/gotchas.md` |
| Protocol/workflow guidance | `baseline/docs/workflow/*.md` |
| Hook configuration | `distribution/hooks/` |
| Commands | `global/commands/` |
| Superpowers skills | `~/.claude/skills/` or `global/skills/` |
| Execution trace/logs | Session only, not persisted |
| One-off notes | `docs/refactor/` or session scratch |
| Human judgment required | Superpowers / skill guidance |

---

## 5. Candidate Memory Topics Structure

These are **topic placeholders only** — do not write content yet. Topics are surfaced from existing global core and protocol doc tensions.

### 5.1 Topics for `MEMORY.md`
- Repo identity and purpose (already minimal)
- Stable conventions that have proven durable across phases
- Critical boundary rules discovered during Phases 1–3

### 5.2 Topics for `patterns.md`
- Patterns surfaced in Phase 3 hook migration decisions
- Orchestration extension usage patterns (from `global/guides/orchestration-extension.md`)
- Command routing conventions

### 5.3 Topics for `gotchas.md`
- Hook installation/permission pitfalls (surfaced in Phase 3)
- Context-mode tool routing pitfalls
- Memory boundary misclassification errors (what was mistakenly written to memory before)

---

## 6. Intake and Update Rules

From `memory-protocol.md § Update rule`:

### 6.1 Intake Criteria (new content entering memory)
1. Demonstrated recurrence across ≥2 sessions or ≥2 contributors
2. Not a one-off experiment or speculative idea
3. Has a known, validated solution or convention
4. Fits the target file's defined role (MEMORY.md / patterns.md / gotchas.md)

### 6.2 Update Criteria (existing memory content)
1. Still valid — re-validate if repo structure changed
2. Not redundant with other memory files
3. Not superseded by newer protocol documentation

### 6.3 Removal Criteria
1. Found to be speculative or one-off (retroactive correction)
2. Superseded by explicit protocol documentation
3. Duplicative of content in other memory files

---

## 7. Consistency Review Method (P4-T06)

### 7.1 Review Dimensions

| Check | Method |
|-------|--------|
| Protocol ↔ skeleton role alignment | Compare `memory-protocol.md` role definitions against actual `baseline/memory/*` file headers |
| MEMORY.md ↔ patterns.md separation | Verify no pattern-length content in MEMORY.md and no overview content in patterns.md |
| patterns.md ↔ gotchas.md separation | Verify patterns describe reusable solutions; gotchas describe recurring problems |
| gotchas.md ↔ MEMORY.md separation | Verify gotchas are not just one-liners that belong in MEMORY.md |
| Memory ↔ global core separation | Verify no durable rules in global core that belong in `baseline/memory/*` |
| Memory ↔ protocol docs separation | Verify protocol docs don't contain memory content and vice versa |

### 7.2 Review Output
- Signed-off consistency matrix (or explicit gap list)
- Required corrections if any dimension fails

---

## 8. Execution Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Memory bloat — content that should be ephemeral gets durabilified | Medium | High | Strict adherence to intake criteria; P4-T06 review |
| Over-correction — removing content that IS durable | Medium | High | Extract before removal; document what was removed and why |
| Protocol and skeleton diverge after this phase | Low | High | P4-T06 is the final gate; must pass before Phase 4 closes |
| Global core not actually cleaned (only relocated) | Medium | Medium | Verify global core is editorially clean, not just moved |
| Memory files become dumping ground for everything | Medium | High | memory-boundary.md is P4-T01 — boundary must be set before content work |

---

## 9. Completion Criteria

Aligned with `plan.md § Phase 4 — Memory / 验收标准`:

| # | Criterion | Evidence Required |
|---|-----------|-------------------|
| C1 | `docs/reference/memory-boundary.md` exists with clear boundaries | P4-T01 accepted |
| C2 | `memory-protocol.md` aligned with final memory skeleton roles | P4-T02 accepted |
| C3 | `MEMORY.md` contains only stable, long-range, overview-type memory | P4-T03 accepted |
| C4 | `patterns.md` contains only reusable, cross-session patterns | P4-T04 accepted |
| C5 | `gotchas.md` contains only durable recurring pitfalls | P4-T05 accepted |
| C6 | Protocol ↔ skeleton consistency verified | P4-T06 accepted |
| C7 | Global core does not contain experience-based / environment-based knowledge mixed with rules | Manual review of `global/core-standard.md` |

**All six task gates must pass (or formally blocked with recorded reason).**

---

## 10. Execution Order

Per `plan.md § Phase 4 — Memory / 先后顺序`:

```
P4-T01 (boundary) → P4-T02 (protocol) → P4-T03 (MEMORY.md) → P4-T04 (patterns.md) → P4-T05 (gotchas.md) → P4-T06 (consistency review)
```

P4-T01 must complete before P4-T03/P4-T04/P4-T05 begin content work. P4-T02 can run in parallel with P4-T01 once boundary is drafted. P4-T06 is the final gate.
