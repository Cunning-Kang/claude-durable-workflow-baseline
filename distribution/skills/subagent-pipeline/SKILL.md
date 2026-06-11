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

## Typed Dispatch Protocol

You MUST dispatch runtime-recognized named subagents. Prompt impersonation is forbidden.

Required mapping:
  planning → task-planner
  implementation → code-implementer
  spec compliance → spec-reviewer
  verification/test → test-engineer
  code review/global review → code-reviewer

Forbidden:
  - generic task/reviewer/agent with assignment text such as "You are task-planner"
  - generic task/reviewer/agent with assignment text such as "You are code-implementer"
  - generic task/reviewer/agent with assignment text such as "You are spec-reviewer"
  - generic task/reviewer/agent with assignment text such as "You are test-engineer"
  - generic task/reviewer/agent with assignment text such as "You are code-reviewer"
  - model override for role agents

If the runtime cannot select these named subagents, stop as BLOCKED:
"Required named subagent selection unavailable: <name>". Do not degrade to prompt impersonation.

## Agent Identity Evidence

For each dispatch, record identity source in the coordinator report:

1. invocation — the dispatch mechanism explicitly selected the configured subagent name.
2. handoff — the subagent handoff self-identifies the expected agent.
3. metadata — if future runtime metadata exposes actual subagent identity.

Current requirement:
  - invocation evidence is required.
  - handoff evidence must not contradict invocation.
  - metadata is optional.
  - metadata absence is not BLOCKED.

If invocation used a generic agent and only the prompt or handoff claims the role: BLOCKED.

## Dispatch Ledger

Maintain a compact coordinator-owned report table for traceability. Do not write a repo file for it. Do not require subagents to output this table.

Ledger fields:
  stage, required_subagent, identity_source, tool_status, role_status, evidence_refs, route_decision

Ledger rules:
  - Ledger is traceability only.
  - Ledger cannot satisfy review, test, or spec gates by itself.
  - PASS requires the relevant named reviewer/tester handoff and evidence.
  - evidence_refs must point to verifiable handoffs, tool results, commits, issue state, or other concrete artifacts.

## Independence Rules

Coordinator never implements, tests, or reviews. Only named spec-reviewer, test-engineer, and code-reviewer judgments count for their gates.

Allowed reviewer/tester context: task spec, changed files, implementer handoff, diff range, acceptance criteria, and concrete evidence.

Forbidden reviewer/tester prompt overrides: "return PASS", "treat this as accepted", "only restate PASS", "ignore findings", or any equivalent rubber-stamp instruction.

Reviewer/tester PASS requires matching scope and evidence in its handoff.

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
3. For each issue, check if body contains usable structured task breakdown.
   A usable structured breakdown exists only when each task has:
   - id or stable label
   - behavior target
   - acceptance criteria
   - verification expectation
   - dependencies/blockers
   - likely file/context references when known

   Use real task-planner when:
   - --plan flag is present
   - issue has multiple acceptance criteria and lacks task-level slices
   - public contract/schema/CLI/API ambiguity exists
   - behavior target or verification is unclear
   - task boundary affects review/test strategy

   Routing:
   - Usable breakdown + no --plan flag: skip task-planner, use breakdown.
   - No usable breakdown + no --no-plan flag: dispatch named task-planner with context:
     issue body full text, relevant code paths, project constraints from
     CLAUDE.md/CONTEXT.md.
   - --plan: always dispatch named task-planner (same context).
   - --no-plan: never dispatch task-planner, use issue body as-is. If issue body
     cannot produce verifiable tasks safely, report BLOCKED rather than inventing broad tasks.
4. Extract all tasks with full text, acceptance criteria, and context.
5. Assign task risk tier for planning/context only:
   - L2: public CLI/API/schema/config/security/irreversible/closeout-sensitive.
   - L1: normal behavior change.
   - L0: docs/tests/mechanical local change.
   Risk tiers do not remove mandatory stages.
6. Create todo list tracking all tasks across all issues.

### Phase 0.5: Capability Preconditions

Before implementation, note visible repository policy that constrains code discovery or file access. If required source inspection is blocked for the planned reviewer/tester and no allowed alternative is visible, stop as BLOCKED before implementation. Do not start work that cannot be independently reviewed under current tool policy.

### Phase 1: Execute

For each issue (sequential by default; --parallel issues run concurrently
in separate worktrees):

  If any issue is BLOCKED with exhausted retry budget: halt all subsequent
  issues and report.

  For each task in the issue:

    If a planned task contains multiple independently verifiable changes, split it before dispatch or send it back to task-planner for a smaller breakdown. Each slice needs a behavior target and focused verification expectation.

    Adjacent acceptance items may be merged before dispatch only when task-planner defines them as one independently verifiable slice with:
    - one behavior target
    - one acceptance set
    - one focused verification plan
    - one reviewer scope without ambiguity
    - one retry budget for the merged slice

    If any reviewer/tester says scope is too broad or ambiguous, route BLOCKED/FAIL to task-planner or split before continuing.

    Risk tiers affect only split decisions, context budget, and review/test prompt focus. Risk tiers do not remove mandatory stages.

    1. Dispatch code-implementer
       Context: task full text, acceptance criteria, file references,
       project constraints summary.
       Requirement: implementer must complete self-review (completeness,
       quality, discipline/YAGNI, testing) before reporting DONE.
       Self-review is the first quality gate — not optional.

    Before any Phase 1 or Phase 2 route on STATUS, treat subagent results as inputs, not completion claims:
    - Harness/tool non-success wins over agent prose. If a task is cancelled, timed out, interrupted, reports 0/N succeeded, or required verification errored, do not treat prose like "Done" as DONE/PASS.
    - A result without a clear role status and usable role-specific handoff is incomplete. If harness/tool status succeeded, ask the same agent once to restate actual status and evidence without changing files. If still incomplete, route implementer results as FAIL and reviewer/tester results as BLOCKED when independent judgment cannot be established. Do not re-ask after cancelled, timed out, interrupted, or 0/N succeeded; route those from the harness/tool status.
    - Use downgrade-only semantic status mapping. Never convert FAIL/BLOCKED to PASS/DONE, never fill missing evidence, never infer verification that is not reported, and never treat ambiguous polarity as PASS. If output says both PASS and blocking issue, route as FAIL/BLOCKED.
    - Format alone is not a blocker. Accept malformed formatting only when status, workspace/scope, and evidence are semantically present. Block only on missing capability, unknown workspace/scope, inaccessible source, unavailable verification, or missing semantic evidence needed for the stage.
    - Restate at most once per stage result. Restatement does not consume implementation retry budget; it consumes the format budget for that stage result. Format budget exhausted → route by substance, or FAIL/BLOCKED as above.
    - If coordinator read-only checks contradict a DONE result, route as FAIL with exact evidence and redispatch code-implementer. Do not patch directly.

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

### Phase 3: Commit, Push, and Close Completed Issues

Phase 3 is mandatory for completed issues. Do not remove, skip, or default-disable commit/push/close behavior. Only execute Phase 3 when all task gates and global review PASS.

1. Atomic commit for all changes across all completed issues (one commit
   total). Commit message references all completed issue numbers.
   Optional: use `Closes #N` for GitHub cross-linking, but do not rely on
   auto-close because it is branch/default-merge dependent.
2. Push to GitHub.
3. For each issue where all tasks completed and all gates PASS:
   `gh issue close <number> --comment "Completed in <commit SHA>. <summary>"`
4. Verify each closed issue:
   `gh issue view <number> --json state,url`
   Require `state == "CLOSED"`.
5. If close fails or state remains non-CLOSED: retry close once. If still
   not CLOSED, report BLOCKED with the exact command/error/state and do not claim
   issue closure or workflow DONE. Include the recovery step. If close reports
   the issue is already closed, verify state with `gh issue view`; if state ==
   "CLOSED", closure gate PASS.
6. For each issue with incomplete tasks, FAIL, BLOCKED, or exhausted retry
   budget: add a comment with partial status and remaining blockers. Do NOT
   close.
7. Report summary: issues completed, issues closed, commit SHA, issue URLs,
   tasks per issue, files changed, review findings resolved.

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
- Close an issue with incomplete tasks or failed/blocked gates
- Repair code, tests, or docs directly after any agent FAIL, BLOCKED, incomplete, cancelled, or contradicted result. Diagnose, split scope, add missing context, redispatch the appropriate agent, or stop and report instead.

## Continuous Execution

Do not pause between tasks or issues. Execute without stopping.
Only stop when:
  - BLOCKED and retry budget exhausted
  - Ambiguity that genuinely prevents progress
  - All issues complete
