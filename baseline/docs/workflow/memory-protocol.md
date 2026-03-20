# Memory Protocol

## Purpose
Convert stable lessons from durable work into project memory without turning memory into a task log.

## When to write
Write to memory **only after** one of these events:

| Event | Example |
|-------|---------|
| Feature closeout | `/new-feature user-auth` completed and merged |
| Review with findings | Independent review found a recurring pattern |
| Blocking issue resolved | Root cause was a durable decision, not a one-off |
| New convention established | Team agreed on a stable pattern via discussion |

**Decision tree** — ask in order; stop at first "yes":

1. **Stable?** Will this same situation occur again in future sessions? If no → don't write.
2. **Reusable?** Is this a pattern others can follow, or just my local preference? If personal only → don't write.
3. **Actionable?** Can a future session act on this without asking me? If not actionable → don't write.

If all three are yes, write it.

## What belongs in memory
Write only:
- stable project conventions (how things are done here, not just what's done)
- recurring pitfalls (this fails when X; use Y instead)
- reusable workflow or verification patterns (template snippet, command sequence)
- durable decisions (why this approach was chosen over alternatives)

## What does not belong in memory
Do not write:
- feature progress or implementation notes
- one-off blockers that won't recur
- temporary experiments that didn't work
- raw execution logs or command output
- speculative ideas not yet validated

## Where to write
- `memory/MEMORY.md` — always-relevant rules, conventions, critical gotchas
- `memory/patterns.md` — reusable patterns others can apply directly
- `memory/gotchas.md` — recurring pitfalls and how to avoid them

**Rule of thumb:** If it fits in 1–3 lines, MEMORY.md. If it needs explanation or an example, patterns.md.

## What to write — before/after examples

### Example A — belongs in MEMORY.md
> **Before (too vague):** "Remember to run tests before committing."
> **After:** "GIT COMMIT GATE: `mise run lint && mise run test` must pass before `git commit`. CI enforces this."

### Example B — belongs in patterns.md
> **Pattern: Restart-dependent services after config change**
> Some services (e.g., tmux plugins, mise tools) only reload after a full restart.
> Trigger: editing any `.tmux.conf` or `mise.toml` runtime section.
> Fix: `tmux source-file ~/.tmux.conf` or `mise trust mise.toml`.

### Example C — belongs in gotchas.md
> **Node.js: `console.log` in CI is buffered.** Use `process.stdout.write()` for interleaved output in scripts.

### Example D — does NOT belong (task log)
> ~~"Implemented OAuth login, took 3 hours, found bug in token refresh."~~
> → Feature progress. Close the feature spec instead.

## Update rule
Prefer updating an existing entry over adding a new duplicate entry.
When updating, append to the entry (don't replace) with a date marker:

```
Pattern: X
Added: 2026-01-15
Updated: 2026-03-20  ← new update
```
