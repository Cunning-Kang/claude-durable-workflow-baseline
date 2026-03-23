# Rollback — `taskcompleted-verification-evidence-gate`

## Rollback steps in an adopted project

1. Remove the H-02 hook entry from the project's `.claude/settings.json` `hooks.TaskCompleted` array.
2. Remove any `TASKCOMPLETED_VERIFICATION_EVIDENCE_*` environment variable exports added to your project shell configuration if you configured them as persistent environment variables rather than inline in settings.json.
3. The hook script at `.claude/hooks/taskcompleted-verification-evidence-gate/hook.mjs` can remain in the project — it will not be invoked once removed from settings.

## What rollback does not include

- Removal of verification artifacts already written to the project repo (they are project content, not hook content).
- Restoration of any task state that was blocked by this hook — blocked completions simply did not advance; the tasks remain in their prior state.

## Source repo note

This artifact lives in `distribution/hooks/project/taskcompleted-verification-evidence-gate/` as source-only content. Rollback in the source repo means removing or renaming the hook directory to prevent it from being distributed further.
