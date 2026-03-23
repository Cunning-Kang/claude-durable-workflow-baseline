# `taskcompleted-authoritative-state-gate`

> Scope: project | Event: `TaskCompleted` | Status: source-only template

## Purpose

Block `TaskCompleted` when the configured durable tracker still shows unresolved or contradictory closure state for the task being completed.

This hook is intentionally limited to **completion-time durable state consistency**.

## What it checks

The hook only enforces the H-01 machine-checkable subset:

1. exactly one configured durable tracker resolves for the completion target
2. the target durable task entry exists in that tracker
3. the selected tracker no longer leaves that task in an obviously open state
4. configured authoritative surfaces do not disagree about the same task being open vs. closed

The implementation uses explicit repo-local configuration for:

- tracker path(s) or glob(s)
- optional additional authoritative surface path(s)
- explicit target-mapping template
- repo-local open markers
- repo-local closed markers

## Why `TaskCompleted`

`TaskCompleted` is the durable completion boundary.

This gate is about blocking incorrect task closure, so it belongs at the moment a task is being marked complete. It does **not** belong on `UserPromptSubmit`, `PostToolUse`, `Stop`, or `ConfigChange`, because those are not durable task-state transitions.

## Target task mapping decision

`TaskCompleted` provides `task_id`, `task_subject`, and optional task description fields, but the hook does **not** guess how those map into a repo’s durable tracker.

Instead, the project must configure `TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE` explicitly, for example:

- `Task ID: {{task_id}}`
- `## {{task_subject}}`

If the mapping template is missing or resolves to an empty target identifier, the hook blocks instead of silently falling back.

## Residual gap

This hook does **not** decide:

- which durable backend a repo should treat as authoritative
- whether a milestone is semantically complete beyond already-written durable state
- what the next task should be
- whether reprioritization or checkpointing should happen

Those remain outside the hook:

- protocol docs define workflow semantics
- Superpowers owns planning, routing, batching, and next-step selection
- humans decide ambiguous repo-local semantics and adoption choices

## Why this is not a second control plane

The hook only reads already-declared durable state at completion time.

It does not:

- create a backlog
- derive next tasks
- reprioritize work
- discover shadow trackers without explicit configuration
- replace workflow planning or review judgment

## Adoption model

This artifact family is **project-scope, source-only, snippet-only, and opt-in**.

- Copy the hook into `<project>/.claude/hooks/taskcompleted-authoritative-state-gate/hook.mjs`
- Make it executable
- Manually merge the settings snippet into `<project>/.claude/settings.json`
- Validate in the destination project

Do **not** write live settings from this baseline repo, and do **not** install this as a user-level default.
