---
name: subagent-pipeline
description: Use when executing implementation work via the subagent
  pipeline: planner → plan-reviewer → implementer → spec-reviewer → test-engineer → code-reviewer,
  with per-task quality gates and final global review. Accepts GitHub issues, plan files, and task text.
---

# Subagent Pipeline

Execute implementation work by dispatching subagents through a quality
pipeline. You are the coordinator — you never implement, test, or review
code yourself.

## Input

Interactive-first behavior:

- With no arguments, ask the user to choose work item source: GitHub issue, plan file, or task text.
- For GitHub issue, ask for one or more issue numbers or URLs.
- For plan file, discover candidate files and ask the user to select one. Default single-select; allow multiple plan files only when the user explicitly asks.
- For task text, ask the user to paste the task. If acceptance or verification is missing, use task-planner unless the user selected --no-plan.

Shortcut arguments remain supported:

  /subagent-pipeline #1
  /subagent-pipeline docs/plans/foo.md
  /subagent-pipeline "Fix auth token expiry"
  /subagent-pipeline #1 docs/plans/foo.md "Fix X"
  /subagent-pipeline --parallel #1,#2 #3
  /subagent-pipeline --plan #1       (force task-planner)
  /subagent-pipeline --no-plan #1    (skip task-planner; BLOCKED if unclear)
  /subagent-pipeline --no-commit #1  (report READY_FOR_COMMIT)
  /subagent-pipeline --push #1       (commit then push)
  /subagent-pipeline --close-issues #1  (commit, push, close, verify CLOSED)

Work items:

- issue: `#N` or issue URL; read with `gh issue view`.
- plan-file: markdown file path; read as immutable spec.
- task: quoted or pasted task text; original user text is immutable spec.

Mixed source types are allowed in one run. Each input is an independent work item in input order. Parallel syntax remains comma-separated issue shortcuts; generic plan/task parallelism is planner-approved only.

Plan file candidate discovery only finds files; it does not judge plan quality. Search candidates:

1. `.claude/plans/*.md`
2. `docs/plans/*.md`
3. `plans/*.md`
4. Recent markdown files with names containing `plan`, `task`, `implementation`, or `roadmap`

## Typed Dispatch Protocol

You MUST dispatch runtime-recognized named subagents. Prompt impersonation is forbidden.

Required mapping:
  planning → task-planner
  plan review/architecture plan review/task breakdown review → plan-reviewer
  implementation → code-implementer
  spec compliance → spec-reviewer
  verification/test → test-engineer
  code review/global review → code-reviewer

Forbidden:
  - generic task/reviewer/agent with assignment text such as "You are task-planner"
  - generic task/reviewer/agent with assignment text such as "You are plan-reviewer"
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

Coordinator never implements, tests, or reviews. Only named plan-reviewer, spec-reviewer, test-engineer, and code-reviewer judgments count for their gates.

Allowed reviewer/tester context: task spec, changed files, implementer handoff, diff range, acceptance criteria, and concrete evidence.

Forbidden reviewer/tester prompt overrides: "return PASS", "treat this as accepted", "only restate PASS", "ignore findings", or any equivalent rubber-stamp instruction.

Reviewer/tester PASS requires matching scope and evidence in its handoff.

## Immutable Work Item Spec

Work item spec is immutable. Pipeline may read but must not modify:

- issue body before authorized Phase 3 (no `gh issue edit`, no `gh issue comment`, no `gh issue close`)
- plan file content
- user-provided task text

Task-planner breakdown becomes immutable after plan-reviewer PASS.

## Pipeline Order

Per task:
  task-planner (when required) → plan-reviewer (when task-planner ran) → code-implementer (with self-review) → spec-reviewer → test-engineer → code-reviewer

After all tasks for all work items complete:
  code-reviewer (global review, full diff)

## Checkpoints

These checkpoints are execution gates, not routine user pauses. Continue automatically when the gate PASSes. Stop only on BLOCKED/FAIL exhaustion, ambiguity that prevents progress, or an outward-facing action that requires authorization.

- 🔴 CHECKPOINT · Task Gate: spec-reviewer, test-engineer, and code-reviewer must PASS before a task is complete.
- 🔴 CHECKPOINT · Global Review Gate: final code-reviewer must PASS before Phase 3.
- 🔴 CHECKPOINT · Commit/Push/Close Gate: commit requires all gates PASS; push and issue close run only when the original command included the matching flag.
- 🛑 STOP · BLOCKED/FAIL Exhaustion: exhausted retry budget, missing required capability, or unsafe ambiguity stops the pipeline and reports recovery steps.

## Process

### Phase 0: Setup

1. Record BASE_SHA = $(git rev-parse HEAD). For parallel mode, capture
   before any patch proposal worker is created.
2. Load each work item spec:
   - issue: `gh issue view <number> --json number,title,body,url,state`
   - plan-file: read the selected markdown file
   - task: preserve pasted task text exactly
   On failure: report and halt.
3. For each work item, determine task breakdown routing:

   Structured breakdown = work item spec where every task has all six fields:
   id or stable label, behavior target, acceptance criteria, verification expectation, dependencies/blockers, likely file/context references.

   Routing (first matching rule wins):
   - --plan flag → always dispatch task-planner, then plan-reviewer.
   - --no-plan flag → never dispatch task-planner. If spec lacks all six fields per task, report BLOCKED.
   - Structured breakdown present → skip task-planner, use breakdown directly.
   - Structured breakdown absent → dispatch task-planner, then plan-reviewer with context: full work item spec, relevant code paths, project constraints from CLAUDE.md/CONTEXT.md.
4. When task-planner ran, dispatch named plan-reviewer with the planner handoff and source context. Continue only on PASS. On FAIL, redispatch task-planner with plan-reviewer findings. On BLOCKED, supplement context once; if still BLOCKED, stop.
5. Extract all tasks with full text, acceptance criteria, and context.
6. Assign task risk tier for planning/context only:
   - L2: public CLI/API/schema/config/security/irreversible/closeout-sensitive.
   - L1: normal behavior change.
   - L0: docs/tests/mechanical local change.
   Risk tiers do not remove mandatory stages.
7. Create todo list tracking all tasks across all work items.
8. Task-planner proposes safe parallel groups when --parallel is requested. Plan-reviewer audits those groups. If --parallel was requested but rejected by plan-reviewer, run sequentially and report the reason unless the user explicitly required parallel.

### Phase 0.5: Capability Preconditions

Before implementation, note visible repository policy that constrains code discovery or file access. If required source inspection is blocked for the planned reviewer/tester and no allowed alternative is visible, stop as BLOCKED before implementation. Do not start work that cannot be independently reviewed under current tool policy.

### Phase 1: Execute

For each work item (sequential by default; --parallel allows planner-approved patch proposal groups):

  If any work item is BLOCKED with exhausted retry budget: halt all subsequent
  work items and report.

  For each task in the work item:

    If a planned task contains multiple independently verifiable changes:
    split before dispatch → each slice gets its own behavior target and focused verification expectation.
    If splitting fails (task-planner cannot decompose) → report BLOCKED.

    Merge adjacent acceptance items into one dispatch only when all five conditions hold:
    one behavior target, one acceptance set, one verification plan, one unambiguous reviewer scope, one shared retry budget.

    If any reviewer/tester reports scope too broad or ambiguous:
    route FAIL/BLOCKED → split the task → redispatch code-implementer on each slice.
    Do not send back to task-planner for scope that reviewers already identified.

    Risk tiers affect only split decisions, context budget, and plan/review/test prompt focus. Risk tiers do not remove mandatory stages.

    1. Dispatch code-implementer
       Context: task full text, acceptance criteria, file references,
       project constraints summary.
       Requirement: implementer must complete self-review (completeness,
       quality, discipline/YAGNI, and testing) before reporting DONE.
       Self-review is the first quality gate — not optional.

    Status interpretation rules (applies to all Phase 1 and Phase 2 routing):
    - Harness/tool non-success (cancelled, timeout, interrupted, 0/N succeeded, verification error) overrides agent prose. Route from harness/tool status directly.
    - Downgrade-only mapping: FAIL/BLOCKED never converts to PASS/DONE. Ambiguous polarity → FAIL/BLOCKED.
    - Missing role status or handoff → ask the same agent once to restate without file changes. Still incomplete → implementer: route FAIL; reviewer/tester: route BLOCKED.
    - Format issues are not blockers when status, scope, and evidence are semantically present. Block on missing capability, unknown scope, inaccessible source, or missing evidence only.
    - Coordinator read-only checks contradict DONE → route FAIL with evidence, redispatch code-implementer. Coordinator does not patch directly.

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

### Parallel Mode

--parallel: parallelize safe slices when plan-reviewer approves. Sequential execution when plan-reviewer rejects or when `--parallel` was not supplied. Parallel is mandatory only when the user explicitly states "parallel is required".

Planner proposes:

- can_parallelize: true/false
- safe_groups
- dependencies
- conflict risks

Plan-reviewer approves or rejects those groups.

Approved parallel groups use patch proposal flow:

1. Dispatch parallel code-implementer workers for safe slices.
2. Each worker returns STATUS plus unified diff patch, changed files, focused verification notes, assumptions, and risks.
3. Coordinator mechanically runs `git apply --check` and `git apply` in declared slice order. Coordinator does not edit patches.
4. On patch apply failure, redispatch affected code-implementer with current main context and patch failure output.
5. Authoritative gates run on the main worktree after apply:
   - spec-reviewer per slice
   - test-engineer per group
   - code-reviewer per group

If plan-reviewer rejects parallelization, execute sequentially and report:
"Parallel requested but rejected by plan-reviewer: <reason>. Executed sequentially."

### Phase 2: Global Review

After all work items complete and before any commit:

1. Collect full diff: BASE_SHA (recorded in Phase 0) to HEAD_SHA
   ($(git rev-parse HEAD)).
2. Dispatch code-reviewer with full diff + all work item specs + all task
   acceptance criteria.
3. Route:
   PASS → proceed to Phase 3
   FAIL → implementer fixes affected tasks → full pipeline rewalk for
     those tasks (using remaining Phase 1 budget) → re-run global review.
     If any affected task has exhausted budget: report as unfixable,
     include in failure summary with specific findings, await instructions.
     Repeat until PASS or BLOCKED.
   BLOCKED → report, await instructions

### Phase 3: Report and Atomic Commit

Phase 3 runs only after all task gates and global review PASS. Default behavior is report plus atomic commit. It does not push or close issues by default.

Flags:

- `--no-commit`: skip commit and return READY_FOR_COMMIT with commit plan.
- `--push`: after commit, push current branch.
- `--close-issues`: after commit, push current branch, close completed issue-source work items, and verify `state == "CLOSED"`. `--close-issues` implies push.

Coordinator owns Phase 3 mechanical actions. `deployment-operator` is not part of default subagent-pipeline.

1. Build commit groups after global review PASS:
   - no file overlap → one commit per work item
   - overlapping changed files → one combined commit for those work items
   - plan-file default → one commit unless plan-reviewer promoted internal slices to separate work items
   - unknown file ownership → one combined commit
2. Stage explicit files only. Do not use `git add .`.
3. Commit message references all completed issue numbers. Use `Refs #N` by default. Use `Closes #N` only when `--close-issues` was supplied.
4. Include `Co-Authored-By: Claude <noreply@anthropic.com>`.
5. Verify commit with `git show --stat --oneline HEAD` and `git status --short`.
6. If `--push`: push current branch.
7. If `--close-issues`: for each completed issue-source work item run:
   `gh issue close <number> --comment "Completed in <commit SHA>. <summary>"`
   then `gh issue view <number> --json state,url`.
   Require `state == "CLOSED"`.
   If close fails or state remains non-CLOSED: retry close once. If still
   not CLOSED, report BLOCKED with the exact command/error/state and do not claim
   issue closure or workflow DONE. Include the recovery step. If close reports
   the issue is already closed, verify state with `gh issue view`; if state ==
   "CLOSED", closure gate PASS.
8. Final report: work items completed, commits, push status, issue URLs,
   tasks per work item, files changed, review findings resolved, risks, and recovery commands.

## Top-Level Status

Use only these top-level statuses:

- DONE: all gates PASS, commits created unless no changes are valid, push/close completed if requested.
- READY_FOR_COMMIT: gates PASS but `--no-commit` skipped commit; report includes commit plan and commands.
- BLOCKED: authorization, tool, environment, unclear spec, git, push, or gh issue close prevents safe continuation.
- FAIL: implementation/spec/test/review quality failure exhausted retry budget.

Phase details belong in fields such as:

```js
phase3: {
  commit: "created" | "skipped" | "blocked" | "not_needed",
  push: "skipped" | "done" | "blocked",
  closeIssues: "skipped" | "done" | "blocked"
}
```

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

## What You Never Do

- Implement code yourself
- Skip any Phase 1 pipeline stage
- Proceed past FAIL without remediation
- Push before global review PASS
- Make subagents read the plan file path only (provide full task text)
- Ignore subagent BLOCKED or FAIL status
- Commit before global review PASS
- Close an issue with incomplete tasks or failed/blocked gates
- Use deployment-operator in the default subagent-pipeline
- Repair code, tests, or docs directly after any agent FAIL, BLOCKED, incomplete, cancelled, or contradicted result. Diagnose, split scope, add missing context, redispatch the appropriate agent, or stop and report instead.

## Continuous Execution

Do not pause between tasks or work items. Execute without stopping.
Only stop when:
  - BLOCKED and retry budget exhausted
  - Ambiguity that genuinely prevents progress
  - All work items complete
