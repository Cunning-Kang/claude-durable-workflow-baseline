# `taskcompleted-verification-evidence-gate`

## Purpose

Blocks `TaskCompleted` when durable verification evidence required for completion is missing, empty, or still placeholder-shaped.

## What it checks

- a configured verification artifact exists and contains the target task identifier
- the artifact contains an evidence section (configurable heading keys)
- at least one evidence record has non-placeholder values for configured fields
- placeholder detection uses configurable markers and regex patterns

## Why `TaskCompleted`

Verification is a completion gate, so the denial point should be the completion boundary itself.

- Not `Stop`: reminders happen after the response path and cannot reliably prevent incorrect completion.
- Not `UserPromptSubmit` or `PostToolUse`: those are not equivalent to "claiming the task is done".

## Verification artifact source

The verification artifact path and shape are repo-local. The hook consumes durable written evidence, not raw CLI logs.

Default modeled shape: `docs/specs/*/verify.md` referenced from the active durable index, matching the baseline `Summary` and `Evidence` sections.

## Target task mapping decision

The target task is resolved by expanding `TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE` with `{{task_id}}` and `{{task_subject}}` from the TaskCompleted payload. The expanded needle is then searched in the configured artifact files.

## Residual gap

This hook does **not** decide:
- which verification gates are applicable for the task
- choosing which commands should be run
- running tests, builds, or linters from the hook
- interpreting raw logs or evaluating whether the evidence is substantively "good enough"
- proving that the evidence is semantically fresh relative to every code change beyond the durable record the repo chooses to expose
- replacing verification skills, execution protocol, or human judgment

## Why this is not a second control plane

H-02 enforces a narrow, declarative boundary: evidence presence. It does not encode verification policy, enforce specific tooling, or replace human judgment about whether the work is actually done.

Verification strategy decisions remain with:
- protocol docs defining workflow semantics
- Superpowers owning planning, routing, and next-step selection
- humans deciding ambiguous repo-local semantics and adoption choices

## Adoption model

This artifact family is **project-scope, source-only, snippet-only, and opt-in**.

- Copy the hook into `<project>/.claude/hooks/taskcompleted-verification-evidence-gate/hook.mjs`
- Make it executable
- Manually merge the settings snippet into `<project>/.claude/settings.json`
- Validate in the destination project

Do **not** write live settings from this baseline repo, and do **not** install this as a user-level default.
