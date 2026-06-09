---
name: subagent-pipeline
description: Use when executing implementation tasks via the subagent
  pipeline: implementer → spec-reviewer → test-engineer → code-reviewer,
  with per-task quality gates and final global review. Accepts one or
  more GitHub issues.
---

# Subagent Pipeline

Execute implementation work by dispatching subagents through a quality
pipeline. You are the coordinator — you never implement, test, or review
code yourself.

## Input

Accept one or more GitHub issues:
  /subagent-pipeline #1
  /subagent-pipeline #1 #2 #3
  /subagent-pipeline --parallel #1,#2 #3
  /subagent-pipeline --plan #1       (force task-planner)
  /subagent-pipeline --no-plan #1    (skip task-planner)

Parallel syntax: comma-separated issues run concurrently; space-separated
groups run sequentially.

## Model Assignments

Models are fixed at design time in agent definitions. This prompt does not
override them. Reference: distribution/agents/*.md

## Pipeline Order

Per task:
  code-implementer (with self-review) → spec-reviewer → test-engineer → code-reviewer

After all tasks for all issues complete:
  code-reviewer (global review, full diff)

## Process

### Phase 0: Setup

1. Record BASE_SHA = $(git rev-parse HEAD). For parallel mode, capture
   before any worktree is created.
2. Read each issue body via `gh issue view`. On failure: report and halt.
3. For each issue, check if body contains structured task breakdown.
   - Has breakdown + no --plan flag: skip task-planner, use breakdown.
   - No breakdown + no --no-plan flag: dispatch task-planner with context:
     issue body full text, relevant code paths, project constraints from
     CLAUDE.md/CONTEXT.md.
   - --plan: always dispatch task-planner (same context).
   - --no-plan: never dispatch task-planner, use issue body as-is.
4. Extract all tasks with full text, acceptance criteria, and context.
5. Create todo list tracking all tasks across all issues.

### Phase 1: Execute

For each issue (sequential by default; --parallel issues run concurrently
in separate worktrees):

  If any issue is BLOCKED with exhausted retry budget: halt all subsequent
  issues and report.

  For each task in the issue:

    1. Dispatch code-implementer
       Context: task full text, acceptance criteria, file references,
       project constraints summary.
       Requirement: implementer must complete self-review (completeness,
       quality, discipline/YAGNI, testing) before reporting DONE.
       Self-review is the first quality gate — not optional.

    2. Route on STATUS:
       DONE → dispatch spec-reviewer
       FAIL → diagnose root cause → remediate → redispatch (retry +1)
       BLOCKED → diagnose root cause → remediate → redispatch (retry +1)

    3. Dispatch spec-reviewer
       Context: task spec (full text), implementer handoff summary.
       Permission: may read source files independently to verify.

    4. Route on STATUS:
       PASS → dispatch test-engineer
       FAIL → dispatch implementer with fix context (reviewer findings +
         original task context) → spec-reviewer re-confirms
         (same reviewer confirms, not full pipeline)
       BLOCKED → diagnose → remediate → redispatch same reviewer
         with supplemented context (retry +1)

    5. Dispatch test-engineer
       Context: acceptance criteria, implementer handoff (changed files
       list, verification evidence).
       Permission: may read source and test files independently.

    6. Route on STATUS:
       PASS → dispatch code-reviewer
       FAIL → dispatch implementer with fix context (reviewer findings +
         original task context) → test-engineer re-confirms
         (same reviewer confirms, not full pipeline)
       BLOCKED → diagnose → remediate → redispatch same reviewer
         with supplemented context (retry +1)

    7. Dispatch code-reviewer
       Context: task spec + acceptance, implementer handoff, git diff
       range (BASE_SHA..HEAD_SHA).
       HEAD_SHA captured via $(git rev-parse HEAD) before dispatch.
       Permission: may read source files independently.

    8. Route on STATUS:
       PASS → mark task complete
       FAIL → dispatch implementer with fix context (reviewer findings +
         original task context) → code-reviewer re-confirms
         (same reviewer confirms, not full pipeline)
       BLOCKED → diagnose → remediate → redispatch same reviewer
         with supplemented context (retry +1)

    9. Escalation rule:
       If same reviewer FAILs same task twice consecutively:
       → full pipeline rewalk starting from implementer (with supplemented
         context from diagnosis of both failures).
       → Escalation rewalk does NOT consume retry budget.
       → If rewalk still FAILs at any reviewer, retry budget IS consumed.

    10. Retry budget: 3 per task, across all stages.
       Every implementer redispatch consumes 1 retry — whether caused by
       implementer's own FAIL, or by a reviewer FAIL triggering implementer
       fix. Every reviewer BLOCKED redispatch consumes 1 retry.
       Budget exhausted → stop, report failure and recommendations.

### Phase 2: Global Review

After all issues complete:

1. Collect full diff: BASE_SHA (recorded in Phase 0) to HEAD_SHA
   ($(git rev-parse HEAD)).
2. Dispatch code-reviewer with full diff + all issue specs + all task
   acceptance criteria.
3. Route:
   PASS → proceed to Phase 3
   FAIL → implementer fixes affected tasks → full pipeline rewalk for
     those tasks (using remaining Phase 1 budget) → re-run global review.
     If any affected task has exhausted budget: report as unfixable,
     include in failure summary with specific findings, await instructions.
     Repeat until PASS or BLOCKED.
   BLOCKED → report, await instructions

### Phase 3: Commit and Push

1. Atomic commit for all changes across all issues (one commit total).
   Commit message references all completed issue numbers.
2. Push to GitHub.
3. Report summary: issues completed, tasks per issue, files changed,
   review findings resolved.

## Retry Rules

- Before each retry: diagnose root cause.
- Remediation: supplement context / split task / provide missing info.
- Never upgrade model. Models are fixed at design time.
- Retry budget: 3 per task. Exhausted → stop and report.
- Escalation: consecutive same-reviewer FAIL → full pipeline rewalk
  from implementer. Escalation rewalk does not consume budget.
  Subsequent failures during rewalk DO consume budget.

  Retry accounting example:
    Task enters escalation rewalk with 2 prior retries consumed.
    Rewalk implementer redone (free — escalation does not consume budget).
    Rewalk spec-reviewer FAILs → implementer fix dispatched (retry 3).
    Budget exhausted. Any further FAIL → stop and report.

## Parallel Mode

--parallel #1,#2 #3 means:
  Group 1: #1 and #2 execute concurrently (separate worktrees)
  Group 2: #3 executes after group 1 completes
  Merge order: by issue number (ascending)
  Merge strategy: merge commit. On conflict: halt and report for manual
    resolution.
  Global review: after all merges complete
  BASE_SHA: captured from main worktree before any worktree creation

## What You Never Do

- Implement code yourself
- Skip any Phase 1 pipeline stage
- Proceed past FAIL without remediation
- Push before global review PASS
- Make subagents read the plan file (provide full task text)
- Ignore subagent BLOCKED or FAIL status
- Commit before global review PASS

## Continuous Execution

Do not pause between tasks or issues. Execute without stopping.
Only stop when:
  - BLOCKED and retry budget exhausted
  - Ambiguity that genuinely prevents progress
  - All issues complete
