# Execution Contract

## Purpose
Bridge durable feature artifacts into session execution without creating a custom execution runtime.

## Inputs
Before execution, read only what is necessary:
1. `docs/specs/<feature>/index.md`
2. the active `tasks/T*.md`
3. `plan.md` only if task scope or order is unclear
4. `spec.md` only if acceptance or boundaries are unclear

## Execution rules
- Native Claude Code Task tools are the authoritative session tracker.
- Durable task files are the authoritative cross-session tracker.
- Never keep both as equally detailed trackers.
- Session tasks may be finer-grained than durable tasks, but durable files are updated only at milestone changes.

## Minimum execution bridge
For one durable task:
1. Read the task goal, scope, acceptance, and evidence links.
2. Create the smallest useful native task list for the current session.
3. Execute using native Task tools and subagents when justified.
4. Run verification before claiming task completion.
5. If review is required, complete review before marking the durable task done.
6. Update the durable task status only when the milestone truly changes.

## Milestone updates allowed
- `ready` → `in_progress`
- `in_progress` → `blocked`
- `in_progress` → `done`
- `in_progress` → `split`
- `in_progress` → `dropped`

## What this contract does not do
- It does not create feature tasks automatically.
- It does not auto-sync native tasks to repo files.
- It does not replace planning.
