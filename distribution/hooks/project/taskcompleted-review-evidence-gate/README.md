# `taskcompleted-review-evidence-gate`

> Scope: project | Event: `TaskCompleted` | Status: source-only template

## Purpose

Block `TaskCompleted` when a configured review-required signal is present for the task, but no valid review evidence artifact with a `PASS` outcome exists.

This hook implements the H-03 **review-required evidence presence gate** — it only activates when the repo explicitly provides a machine-checkable signal that a task requires review.

## What it checks

The hook only enforces the H-03 machine-checkable subset:

1. a configured review-required signal file exists and mentions the target task
2. a configured review artifact file contains an entry for that task
3. the entry has a non-placeholder `Reviewer` field
4. the entry has a non-placeholder `Reference` field
5. the entry has an `Outcome` field that matches a configured PASS token

## Why `TaskCompleted`

`TaskCompleted` is the durable completion boundary. This gate blocks task completion when review evidence is required but absent or invalid. It does **not** belong on `UserPromptSubmit`, `PostToolUse`, `Stop`, or `ConfigChange`, because those are not durable task-state transitions.

## Target task mapping

`TaskCompleted` provides `task_id`, `task_subject`, and optional task description fields, but the hook does **not** guess how those map into the signal or artifact files. Instead, the project configures `TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE` explicitly, for example:

- `Task ID: {{task_id}}`
- `## {{task_subject}}`

## Signal file format

The signal file is a simple text file (markdown, plain text) where the presence of `targetNeedle` in the file means "this task requires review". Format is not parsed as structured data — just a text search for the needle.

## Review artifact format

YAML front-matter blocks in markdown files, or standalone JSON/YAML files. The hook parses:
- YAML front-matter (`---` delimited)
- JSON objects
- Plain text with `Key: Value` pairs

## Residual gap

This hook does **not** decide:

- which tasks require review (signal files do this)
- who the reviewer should be
- what the review reference means
- whether the review quality is sufficient
- automatic reviewer assignment or independence assessment

## Why this is not a second control plane

The hook only checks that required evidence exists and is non-placeholder when a signal indicates review is required. It does not:

- determine which tasks need review
- assign reviewers
- evaluate review quality
- replace workflow planning or review judgment

## Adoption model

This artifact family is **project-scope, source-only, snippet-only, and opt-in**.

- Copy the hook into `<project>/.claude/hooks/taskcompleted-review-evidence-gate/hook.mjs`
- Make it executable
- Manually merge the settings snippet into `<project>/.claude/settings.json`
- Configure signal files and artifact files for the project
- Validate in the destination project

Do **not** write live settings from this baseline repo, and do **not** install this as a user-level default.
