# Rollback — `taskcompleted-authoritative-state-gate`

This candidate is project-scope and opt-in, so rollback is only about reversing explicit project adoption.

## Rollback steps in an adopted project

1. Remove the `TaskCompleted` registration that was manually merged into `<project>/.claude/settings.json`
2. Remove the copied hook file from `<project>/.claude/hooks/taskcompleted-authoritative-state-gate/hook.mjs`
3. If desired, remove any related repo-local configuration comments or adoption notes
4. Re-run the project without the hook and confirm task completion is no longer gated by this template

## What rollback does not include

Rollback for this candidate does **not** involve:

- editing user-level `~/.claude/settings.json`
- touching global hook directories
- bootstrap/init changes
- destructive cleanup outside the adopting project

## Source repo note

No live wiring is added in this baseline repo, so there is nothing to disable here beyond deleting or replacing the source artifacts in a future refactor.
