# Memory Boundary

**Authoritative reference for memory content classification.**

---

## 1. Purpose

This document defines what belongs in `baseline/memory/*`, what does not, where non-memory content should go instead, and the rules for entering, updating, and removing entries.

---

## 2. What Memory Is For

`baseline/memory/*` stores **durable cross-session lessons**: things a future session would act on, would benefit from knowing, and would otherwise rediscover the hard way.

Specifically, memory captures:

| Category | Description | Example |
|---|---|---|
| Stable conventions | How the project is actually done, not just what's in the codebase | `mise run lint && mise run test` gate on commit |
| Durable decisions | Why one approach was chosen over alternatives, with rationale | Why the project avoids global npm installs |
| Recurring pitfalls | Failures that recur across sessions with known evasion steps | `console.log` buffering in Node.js CI scripts |
| Reusable patterns | Command sequences, templates, or workflows others can apply directly | `tmux source-file` after editing `.tmux.conf` |

Memory is not a log. It is not a notebook. It is not a scratchpad.

---

## 3. What Memory Is NOT For

The following categories **never belong in any memory file**, regardless of how important they seemed during the session in which they arose:

- Feature progress or implementation notes
- One-off blockers that will not recur
- Temporary experiments that did not work (unless the failure mode itself is a durable gotcha)
- Raw execution logs or command output
- Speculative ideas not yet validated
- Session-specific state (current task, in-progress work, open questions)
- Author preferences without demonstrated reusability
- Content that belongs in protocol docs, hooks, commands, or global core

If content falls into one of these categories, route it per the routing table in §7 — do not force it into memory.

---

## 4. Durability Criteria

A piece of content qualifies as durable memory only if it satisfies **all three** of the following criteria:

| # | Criterion | Question to ask |
|---|---|---|
| D1 | **Recurrence** | Will this same situation occur again in future sessions? |
| D2 | **Reusability** | Is this a pattern others can follow, or just my local preference? |
| D3 | **Actionability** | Can a future session act on this without asking me? |

If any answer is "no" or "unknown", the content does not belong in memory.

Additionally, content must be **specific and verifiable** — not vague guidance ("be careful with X") but a concrete rule, command, or decision with enough context to be applied correctly.

---

## 5. File Roles

### 5.1 `baseline/memory/MEMORY.md`

**Role:** Concise always-relevant rules, conventions, and critical gotchas.

**What goes in:**
- Project rules that fit in 1–3 lines
- Enforcement-level facts (gates, tool requirements, non-negotiable conventions)
- Links to the authoritative source for durable decisions (do not duplicate rationale, point to where it lives)
- Critical gotchas that would cause data loss, security issues, or significant time waste if missed

**What does NOT go in:**
- Pattern explanations or examples (use `patterns.md`)
- Pitfall descriptions that need explanation (use `gotchas.md`)
- One-off notes or session summaries
- Duplicate content already in `patterns.md` or `gotchas.md`

**Typical entry:** 1–5 lines. Factual. Actionable without additional context.

**Example:**
```
# Project Memory

Git Commit Gate:
  mise run lint && mise run test must pass before git commit.
  CI enforces this — no bypasses.
```

---

### 5.2 `baseline/memory/patterns.md`

**Role:** Reusable patterns that others can apply directly.

**What goes in:**
- Workflow patterns with a trigger and a fix (when X, do Y)
- Recurring implementation approaches with enough context to be applied correctly
- Verification patterns (how to confirm something is working)
- Patterns surfaced during hook migration

**What does NOT go in:**
- One-liner facts (those belong in `MEMORY.md`)
- Pitfall descriptions (those belong in `gotchas.md`)
- Patterns that worked once but are not demonstrated to be reusable
- Feature-specific implementation details

**Typical entry:** Trigger + context + action or command sequence. Should be copy-paste applicable.

**Example:**
```
PATTERN: Restart-dependent services after config change
Some services (e.g., tmux plugins, mise tools) only reload after a full restart.
Trigger: editing any .tmux.conf or mise.toml runtime section.
Fix: tmux source-file ~/.tmux.conf or mise trust mise.toml.
```

---

### 5.3 `baseline/memory/gotchas.md`

**Role:** Recurring pitfalls and how to avoid them.

**What goes in:**
- Failure modes that recur across sessions
- Setup traps that bite repeatedly
- Misleading assumptions the project has demonstrated
- Context-mode or hook pitfalls surfaced during development

**What does NOT go in:**
- Current task blockers (one-off)
- Temporary experiment failures (unless the failure mode itself is a durable gotcha)
- Solutions or workarounds (those belong in `patterns.md`)
- Content that fits in 1–2 lines (condense into `MEMORY.md`)

**Typical entry:** Situation → what goes wrong → why → how to avoid/solve.

**Example:**
```
GOTCHA: Node.js console.log in CI is buffered
console.log output is buffered in many CI environments, causing
interleaved output to appear out of order.
Fix: use process.stdout.write() for scripts that output in CI.
```

---

### 5.4 Cross-File Duplication Prevention

| Situation | Correct file |
|---|---|
| Rule fits in 1–3 lines, no example needed | `MEMORY.md` |
| Rule needs trigger + action, copy-paste applicable | `patterns.md` |
| Rule describes a failure mode to avoid | `gotchas.md` |
| Rule is both a pattern and a gotcha | Choose the **primary** intent; cross-reference if both are significant |
| Rule is a one-liner but also a pitfall | Put the **concise rule in `MEMORY.md`**; put the explanation in `gotchas.md` with a cross-reference |

**Principle:** Each durable fact lives **once**. If content appears in two files, consolidate into one and cross-reference from the other.

---

## 6. Non-Memory Destinations

Content that does not belong in `baseline/memory/*` must be routed to the appropriate layer:

| Content type | Destination |
|---|---|
| Rules that govern how the CLI tool itself works (not project-specific) | `global/standards/core-standard.md` |
| Protocol definitions for workflow phases, task states, review gates | `baseline/docs/workflow/memory-protocol.md` and other `baseline/docs/workflow/*.md` files |
| Hook installation, configuration, or permission behavior | Hook source files or `docs/reference/hooks-scope.md` (exists) |
| Slash command definitions or command routing | `global/commands/*.md` or `distribution/commands/` |
| Superpowers skill behavior or capability descriptions | The relevant skill's `SKILL.md` |
| Feature specifications, implementation plans, design decisions | Feature spec or project issue tracker |
| Session-specific state, current tasks, in-progress work | Ephemeral — do not persist |
| Speculative ideas, experiments not yet validated | Human judgment — do not persist until validated |
| One-off blockers unlikely to recur | Ephemeral — do not persist |

**Default rule:** When in doubt, do not write it to memory. Error on the side of not durablefying content.

---

## 7. Routing Table

Use this table to classify any piece of content:

| Content | Belongs in | Reason | Goes instead to if not durable |
|---|---|---|---|
| Project convention (how things are done) | `MEMORY.md` | Always-relevant, concise | — |
| Enforcement gate or critical requirement | `MEMORY.md` | High-stakes if missed | — |
| Reusable command sequence or template | `patterns.md` | Trigger + action, copy-paste | — |
| Workflow approach that recurs | `patterns.md` | Demonstrated reusability | — |
| Failure mode with evasion step | `gotchas.md` | Recurring pitfall | — |
| Setup trap that bites repeatedly | `gotchas.md` | Recurring pitfall | — |
| Feature progress note | None | Not durable | Feature spec / issue |
| One-off blocker | None | Won't recur | Ephemeral |
| Temporary experiment failure | None | Not validated | Ephemeral |
| Raw command output / logs | None | Not durable | Ephemeral |
| Speculative idea | None | Not validated | Human judgment |
| Session state / in-progress work | None | Transient | Ephemeral |
| Hook behavior / installation | `docs/reference/hooks-scope.md` | Protocol, not memory | — |
| Protocol / workflow definition | `baseline/docs/workflow/` | Protocol doc | — |
| Global CLI rule | `global/standards/core-standard.md` | Tool governance | — |
| Skill behavior | Skill's `SKILL.md` | Skill layer | — |

---

## 8. Intake, Update, and Removal Rules

### 8.1 Intake — When to Add a New Entry

Add to memory **only after** one of these triggering events:

| Trigger | Description |
|---|---|
| Feature closeout | A feature is completed and merged; a durable lesson emerged |
| Independent review | Reviewer identified a recurring pattern across sessions |
| Blocking issue resolved | Root cause was durable (not a one-off); solution is reusable |
| New convention established | Team agreed on a stable pattern via discussion |

**Intake checklist** (all must be "yes"):
- [ ] Satisfies D1, D2, D3 (§4)
- [ ] Classified to the correct file (§5)
- [ ] Not already covered by an existing entry (check §5.4 before adding)
- [ ] Specific enough to be acted on without additional context
- [ ] Correctly routed if it belongs outside memory (§6)

### 8.2 Update — When to Modify an Existing Entry

- **Prefer updating over adding a new duplicate** when the existing entry covers the same durable lesson
- Append new information rather than replacing; preserve the original date
- Add an `Updated: YYYY-MM-DD` marker when updating
- If the update fundamentally changes the entry's intent (different rule, different pattern), treat it as a removal + new intake

### 8.3 Removal — When to Delete or Merge an Entry

Remove or merge an entry when:

| Condition | Action |
|---|---|
| Entry describes something that no longer recurs | Remove |
| Entry was a misclassification (should have gone elsewhere) | Remove; re-route to correct destination |
| Entry is duplicated in another memory file | Merge; keep in the file with the more appropriate role |
| Entry has been superseded by a protocol doc or global rule | Remove; reference the authoritative source instead |
| Entry is a one-off that was incorrectly durablefied | Remove; do not replace |

**Do not** remove entries merely because they are old. Age is not a removal criterion — recurrence is.

**Before removing any entry**, document what was removed and why.

---

## 9. Anti-Patterns

The following are known failure modes for memory management.

### 9.1 Durability Inflation
Treating session-specific content as durable. Adding "things I learned today" without applying D1/D2/D3. **Mitigation:** Apply the intake checklist before every addition.

### 9.2 Memory Bloat
Entries accumulate indefinitely without review. The file grows but quality does not. **Mitigation:** Apply removal criteria proactively.

### 9.3 Cross-File Duplication
The same durable fact appearing in two or three memory files. **Mitigation:** Use §5.4 consolidation rules. Every fact lives once.

### 9.4 Memory as Task Log
Writing feature progress, session summaries, or implementation notes into memory. **Mitigation:** Route to feature spec / issue tracker. Memory is not a log.

### 9.5 Protocol Dumping
Writing protocol-level content (workflow definitions, phase contracts, review gate descriptions) into memory because "it felt like something to remember." **Mitigation:** Protocol content goes in `baseline/docs/workflow/*.md`. Memory stores durable lessons derived from protocol execution, not the protocol itself.

### 9.6 Hook/Command Content in Memory
Writing hook installation steps or command routing facts into memory instead of documenting them in the hook source or command doc. **Mitigation:** Hooks belong in hook source files or `docs/reference/hooks-scope.md`. Commands belong in `global/commands/`.

### 9.7 Vague Entries
Entries that say "be careful with X" or "don't forget Y" without enough context to be actionable. **Mitigation:** Rewrite to be specific and action-triggering, or delete if it cannot be made specific.

### 9.8 One-Off Retention
Keeping entries for blockers or failures that were truly one-off and will not recur. **Mitigation:** Apply removal criteria. One-off is a removal signal, not a keep signal.

---

*This document is the boundary authority for memory content classification. When in doubt, classify against D1/D2/D3 first, then route against §7.*
