# Patterns

Reusable patterns that others can apply directly. Each entry is **trigger + action + why it works**.

## Role Definition

**What goes in:**
- Workflow patterns with a demonstrated trigger and a reusable fix
- Recurring implementation approaches confirmed across sessions
- Verification patterns with a stable command sequence
- Patterns surfaced during Phase 3 hook migration that are human-applicable (not already hook-enforced)

**What does NOT go in:**
- One-liner facts (→ `MEMORY.md`)
- Pitfall descriptions (→ `gotchas.md`)
- Protocol definitions or rule statements (→ `baseline/docs/workflow/`)
- Hook behavior or installation steps (→ hook source files or `docs/reference/hooks-scope.md`)
- One-off experiences without demonstrated reuse
- Speculative patterns not yet confirmed recurring

**Counterexample** — looks like a pattern, but belongs elsewhere:
> "When the build fails, run `npm run lint && npm run test`" is a one-off
> command sequence, not a durable pattern. If the same failure recurs across
> sessions with the same fix, it may qualify as a gotcha (→ `gotchas.md`) or
> a verification pattern (→ here) only after the trigger is confirmed stable.

## Entry Format

```
PATTERN: <name>
Trigger: <when to apply this pattern>
Fix:    <what to do>
Why:    <why this approach works>
```

## Extracted Patterns

*(none currently — see below)*

### Why patterns.md is currently empty

The Phase 3B hook migration surfaced three deterministic enforcement subsets
(H-01/H-02/H-03 — machine-enforced, not human-applicable). Those are
implemented as hook source and snippets — the enforcement is executable by
machine, not a reusable human workflow pattern.

No durable human-reusable workflow pattern with confirmed D1/D2/D3
(recurrence + reusability + actionability) has been extracted from the
baseline codebase to date.

### What would qualify

A pattern belongs here when all three are true:
- **D1 Recurrence**: the same situation occurs across multiple sessions
- **D2 Reusability**: the pattern can be applied by others without local context
- **D3 Actionability**: a future session can act on it with the entry alone

Example of what belongs here (illustrative — not yet confirmed durable):

```
PATTERN: Restart-dependent services after config change
Trigger: editing mise.toml runtime section or .tmux.conf
Fix:    mise trust mise.toml && tmux source-file ~/.tmux.conf
Why:    mise tools and tmux plugins only reload after a full restart;
        edit-only is insufficient
```

This example appears in `memory-protocol.md` as an illustration of pattern
format. It is NOT yet confirmed as a durable baseline pattern.

### How to add a pattern

When a durable pattern is confirmed during a feature closeout, an independent
review, a blocking issue resolution, or a team-agreed convention:
1. Verify D1/D2/D3
2. Route via the memory boundary protocol (see `docs/reference/memory-boundary.md`)
3. Write in the entry format above
4. Do not duplicate `MEMORY.md` (overview) or `gotchas.md` (failure modes)

**Maintenance:** Patterns that lose D1/D2/D3 over time should be removed or
archived. A pattern that worked for one feature but is not confirmed recurring
is a removal signal, not a keep signal (AP-8).
