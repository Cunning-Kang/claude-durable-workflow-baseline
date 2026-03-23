# Phase 4 — Memory: Task Clarification (P4-T01 ~ P4-T06)

> Inheritance:细化了 `tasks.md § Phase 4 — Memory` 的每个 task，不重写
> Date: 2026-03-22

---

## P4-T01 — 补 `docs/reference/memory-boundary.md`

### Input Files
- `baseline/docs/workflow/memory-protocol.md` (current state)
- `baseline/memory/MEMORY.md` (current state)
- `baseline/memory/patterns.md` (current state)
- `baseline/memory/gotchas.md` (current state)
- `plan.md § Phase 4 — Memory / 范围` (authoritative scope)
- `this file` (phase-4-memory-plan.md)

### Output File
- `docs/reference/memory-boundary.md` — NEW file

### Predecessor
- None within Phase 4; this is the first task
- Depends on Phase 3 (Hooks) being complete per `plan.md § 依赖关系`

### Completion Definition
A reference document exists at `docs/reference/memory-boundary.md` that:
1. Defines what qualifies as a **durable** lesson (vs. ephemeral/temporary)
2. Explicitly lists what **belongs** in each of the three memory files
3. Explicitly lists what **does not belong** in any memory file
4. Provides routing guidance for content that doesn't belong in memory (where it should go instead)
5. States the intake criteria (how content enters memory)
6. States the removal/update criteria

### Do NOT Do
- Do NOT write any actual memory content (no patterns, no gotchas, no conventions)
- Do NOT modify any existing memory files
- Do NOT modify `memory-protocol.md` — this is a separate task (P4-T02)
- Do NOT create memory files — they already exist

---

## P4-T02 — 对齐 `baseline/docs/workflow/memory-protocol.md`

### Input Files
- `baseline/docs/workflow/memory-protocol.md` (current state — to be corrected)
- `docs/reference/memory-boundary.md` (P4-T01 output — boundary anchor)
- `baseline/memory/MEMORY.md` (current state)
- `baseline/memory/patterns.md` (current state)
- `baseline/memory/gotchas.md` (current state)
- `this file` (phase-4-memory-task-clarification.md)

### Output File
- `baseline/docs/workflow/memory-protocol.md` (updated in-place)

### Predecessor
- P4-T01 (memory boundary must be defined before protocol can be aligned)

### Completion Definition
The updated `memory-protocol.md`:
1. Has role definitions for each memory file that match the boundary document
2. Explicitly excludes session logging / task logs / one-off notes from scope
3. Has an intake rule aligned with P4-T01's boundary criteria
4. Does NOT contain any durable memory content itself (it's a protocol doc, not a memory file)
5. References `docs/reference/memory-boundary.md` as the boundary authority

### Do NOT Do
- Do NOT add memory content to the protocol doc
- Do NOT change the protocol doc's format/structure beyond what alignment requires
- Do NOT update the memory files themselves — only the protocol

---

## P4-T03 — 强化 `baseline/memory/MEMORY.md`

### Input Files
- `baseline/memory/MEMORY.md` (current state — to be updated)
- `docs/reference/memory-boundary.md` (P4-T01 output)
- `baseline/docs/workflow/memory-protocol.md` (P4-T02 output, aligned version)
- `global/core-standard.md` (extraction source: durable rules currently mixed with transient content)

### Output File
- `baseline/memory/MEMORY.md` (updated in-place)

### Predecessor
- P4-T01 (boundary defined)
- P4-T02 (protocol aligned)

### Completion Definition
The updated `MEMORY.md`:
1. Contains only **stable, always-relevant, cross-session** content
2. Contains **no**:
   - Task logs or implementation notes
   - One-off session state
   - Feature progress notes
   - Temporary experiment results
   - Raw command output
   - Speculative ideas
3. Has an editorial header that defines its purpose and boundary (matches boundary doc)
4. Any additions extracted from global core are documented as extractions (not new content invented)

### Do NOT Do
- Do NOT invent new memory content from scratch — only extract and prune
- Do NOT add content that doesn't meet the durability gate
- Do NOT make MEMORY.md verbose — it must stay "极薄" per `tasks.md`
- Do NOT duplicate content that belongs in patterns.md or gotchas.md

---

## P4-T04 — 强化 `baseline/memory/patterns.md`

### Input Files
- `baseline/memory/patterns.md` (current state — to be updated)
- `docs/reference/memory-boundary.md` (P4-T01 output)
- `baseline/docs/workflow/memory-protocol.md` (P4-T02 output)
- Any patterns surfaced during Phase 3 hook migration (from `docs/refactor/phase-3b-*` files)

### Output File
- `baseline/memory/patterns.md` (updated in-place)

### Predecessor
- P4-T01 (boundary defined)
- P4-T02 (protocol aligned)

### Completion Definition
The updated `patterns.md`:
1. Contains only **reusable patterns others can apply directly**
2. Contains **no**:
   - One-off experiences
   - Temporary experiment results
   - Content that belongs in MEMORY.md (overview rules) or gotchas.md (pitfalls)
3. Each pattern has: name, context when to apply, how to apply, why it works
4. Patterns are extracted/validated — not invented speculatively

### Do NOT Do
- Do NOT turn patterns.md into a log of what worked once
- Do NOT duplicate MEMORY.md content (overview rules belong in MEMORY.md)
- Do NOT add patterns without demonstrated reusability
- Do NOT add pitfall descriptions (those belong in gotchas.md)

---

## P4-T05 — 强化 `baseline/memory/gotchas.md`

### Input Files
- `baseline/memory/gotchas.md` (current state — to be updated)
- `docs/reference/memory-boundary.md` (P4-T01 output)
- `baseline/docs/workflow/memory-protocol.md` (P4-T02 output)
- Any gotchas surfaced during Phase 3 hook migration
- Known misclassification errors (content that was incorrectly written to memory before)

### Output File
- `baseline/memory/gotchas.md` (updated in-place)

### Predecessor
- P4-T01 (boundary defined)
- P4-T02 (protocol aligned)

### Completion Definition
The updated `gotchas.md`:
1. Contains only **durable recurring pitfalls** with known evasion steps
2. Contains **no**:
   - Current task blockers (one-off)
   - Temporary experiment failures
   - Content that belongs in MEMORY.md (one-liners) or patterns.md (solutions)
3. Each gotcha has: situation, what goes wrong, why, how to avoid/solve

### Do NOT Do
- Do NOT add current task notes or one-off blockers
- Do NOT turn gotchas.md into a debugging log
- Do NOT duplicate patterns.md content (patterns describe solutions; gotchas describe problems)
- Do NOT add speculative pitfalls — only demonstrated, recurring ones

---

## P4-T06 — Memory Protocol ↔ Skeleton 一致性复核

### Input Files
- `baseline/docs/workflow/memory-protocol.md` (P4-T02 output)
- `baseline/memory/MEMORY.md` (P4-T03 output)
- `baseline/memory/patterns.md` (P4-T04 output)
- `baseline/memory/gotchas.md` (P4-T05 output)
- `docs/reference/memory-boundary.md` (P4-T01 output)
- `global/core-standard.md` (final check: no experience/environment knowledge mixed with rules)

### Output File
- A review record (inline or separate) documenting the consistency check results

### Predecessor
- P4-T01 through P4-T05 all complete

### Completion Definition
A documented consistency check covering:

| Check | Pass Criteria |
|-------|---------------|
| C1 | `memory-protocol.md` role definitions match `memory-boundary.md` |
| C2 | `MEMORY.md` role matches protocol definition (no pattern-length content) |
| C3 | `patterns.md` role matches protocol definition (reusable solutions, not pitfalls) |
| C4 | `gotchas.md` role matches protocol definition (recurring problems, not solutions) |
| C5 | No content exists in two memory files simultaneously (no duplication) |
| C6 | No durable rules remain in `global/core-standard.md` that belong in memory |
| C7 | No session logs / task logs / ephemeral content in any memory file |

If any check fails: document the failure, fix it (return to the relevant task), and re-review.

### Do NOT Do
- Do NOT skip any of the 7 checks
- Do NOT accept "close enough" — boundaries must be clear
- Do NOT modify global core beyond what is necessary to extract mislocated memory content
- Do NOT write new memory content during this review — only correct existing files

---

## Task Dependency Summary

```
P4-T01 (boundary doc)
  └─► P4-T02 (protocol align) ─┐
       P4-T03 (MEMORY.md)     │
       P4-T04 (patterns.md)  │─► P4-T06 (consistency review)
       P4-T05 (gotchas.md)    │
       (P4-T02 first is ok)  ─┘
```

P4-T03, P4-T04, P4-T05 can run sequentially after P4-T02 (they all need boundary + protocol). P4-T06 gates Phase 4 completion.
