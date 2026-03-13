---
name: spec-kit-execute
description: Execution-only skill for implementing Spec Kit work. Use only when the user explicitly asks to continue, run the next task, execute a small batch, or execute a specific task ID.
argument-hint: "continue | next | batch:1-5 | task:<id>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - Bash
---

# Spec Kit Execute

## Purpose
Use this skill only after Spec Kit definition artifacts are already complete.

Treat the existing spec artifacts as the only source of truth. Execute one explicitly identified task or one very small ready batch, verify it, and report the result. This skill is for execution only.

## Non-purpose
Do not use this skill for discovery, brainstorming, planning, task generation, reprioritization, or product decision-making.

If execution would require any of those activities, stop and surface the gap.

## Hard boundaries
Do not:
- create a new spec, plan, or tasks list
- rewrite priorities or invent a new task tree
- expand scope beyond the selected ready task or batch
- fill product or architecture gaps from intuition
- default to parallel agents or worktrees
- mark work complete before verification
- auto-commit, auto-push, or open a PR unless the user explicitly asks

## Required inputs
Before coding, read the existing execution artifacts that exist in the repo, preferring project-local sources first:
1. `spec.md`
2. `plan.md`
3. `tasks.md`
4. nearest equivalent under `.claude/plans/`, `.planning/`, or `docs/plans/`

Extract only:
- current goal
- selected task or clearly ready next task
- blockers or dependencies explicitly recorded in the artifacts
- acceptance criteria
- explicit constraints

Do not restate, regenerate, or improve the plan.

## Invocation modes
- `continue` — resume the currently active implementation task if one is already identified
- `next` — execute the next task only if the existing artifacts clearly identify a single ready next task; otherwise stop and ask for clarification
- `batch:N` — execute a small batch of `N` ready tasks, where `N` must be between 1 and 5
- `task:<id>` — execute exactly that task

If `batch:N` exceeds 5, stop and ask the user to narrow the batch.

## Default execution path
1. Read the existing artifacts.
2. Identify one explicit task, one clearly ready next task, or one very small ready batch.
3. Restate the execution target in one short block: task, likely files, acceptance, blockers.
4. If the task changes behavior or fixes a bug, use `test-driven-development` before implementing.
5. Implement the minimum sufficient change.
6. If execution is blocked by a failing test, bug, build issue, or unexpected behavior, use `systematic-debugging` once.
7. Run the required verification for the selected task or batch.
8. Before any completion claim, use `verification-before-completion`.
9. If the change is interface-affecting, schema-affecting, high-risk, or policy-required, use `requesting-code-review`.
10. Report what changed, what passed, and what remains blocked.

## Failure handling
Try one direct fix for the current failure.
If verification still fails or the cause remains unclear, stop execution and report the blocker.
If continuing would require replanning, new tasks, or speculative redesign, stop and surface the exact gap.

## Tool discipline
Prefer the smallest tool surface that can finish the selected task.
Do not introduce a second planning layer through extra task decomposition, ad hoc checklists, or parallel orchestration.
Do not use `using-git-worktrees` or `dispatching-parallel-agents` unless the user explicitly asks for them or isolation is clearly necessary for risk control.

## Spec-gap handling
If the existing artifacts do not clearly support execution, stop and report the exact missing decision, contradiction, or missing acceptance detail.
Do not guess.

## Completion standard
A selected task or batch is complete only when:
- implementation matches the existing artifacts
- relevant tests, checks, or build steps were run when applicable
- results were verified with evidence
- any required review was requested and resolved
- any task-state update happens only after verification
- any remaining risk or assumption is stated explicitly

If any required verification fails or remains inconclusive, do not claim completion.

Completion reporting should stay concise and include:
- selected task or batch
- files changed
- verification run
- review status when applicable
- remaining blockers, risks, or assumptions

If the selected batch is complete, verification is still fresh, and the current diff appears coherent, suggest `/commit-batch` before more changes accumulate.
If the working tree is clean and the scoped work appears complete, suggest `/finish-branch` as the next workflow step.
