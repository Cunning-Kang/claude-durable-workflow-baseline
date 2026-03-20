---
name: spec-execute
description: Execution-only skill for implementing work from existing spec artifacts or an OpenSpec change. Use when the user asks to continue implementation, do the next task, run a small batch, execute a specific task ID, or keep moving an OpenSpec change forward from existing tasks or change artifacts. Do not use for discovery, planning, proposal or design authoring, or archive work.
argument-hint: "continue | next | batch:1-5 | task:<id> | change:<name>"
compatibility: OpenSpec-aware execution uses openspec CLI when available; otherwise fall back to static spec artifacts.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - Bash
  - AskUserQuestion
  - Skill
---

# Spec Execute

## Purpose
Use this skill only after execution artifacts already exist.

Treat existing artifacts as the source of truth, whether from:
1. an OpenSpec change, or
2. static artifacts such as `spec.md`, `plan.md`, and `tasks.md`.

Default to one explicit task or one very small ready batch. This skill is execution-only.

## Non-purpose
Do not use this skill for discovery, brainstorming, planning, proposal writing, task generation, reprioritization, or archive work.

If safe execution would require any of those, stop and surface the gap.

## Hard boundaries
Do not:
- create a new spec, proposal, plan, tasks list, or change
- rewrite priorities, invent tasks, or silently choose a different path
- expand scope beyond the selected ready task or batch
- fill product or architecture gaps from intuition
- default to parallel agents or worktrees
- mark work complete before verification
- claim completion without evidence for every applicable required gate
- keep two authoritative task trackers at once
- auto-commit, auto-push, or open a PR unless the user explicitly asks

Automatic artifact updates are limited:
- Allowed after verification: task checkboxes and clearly mechanical progress updates
- Not allowed without confirmation: semantic changes to proposal, spec, design, acceptance, task meaning, or task ordering

## Invocation modes
- `continue` — resume the currently active task if already identified
- `next` — execute the next task only when artifacts clearly identify one ready next task
- `batch:N` — execute a small batch of `N` ready tasks, where `N` is 1-5
- `task:<id>` — execute exactly that task
- `change:<name>` — execute ready tasks for that OpenSpec change until done, blocked, or paused by a guardrail

If `batch:N` exceeds 5, stop and ask the user to narrow the batch.

## Context resolution

### OpenSpec-aware path
Prefer this when:
- invocation is `change:<name>`
- the user clearly names an OpenSpec change
- the active execution context clearly points to one specific change

When a specific change is identified:
1. Run `openspec status --change "<name>" --json`
2. Run `openspec instructions apply --change "<name>" --json`
3. Read every file in `contextFiles`
4. Treat `status`, `instructions apply`, `contextFiles`, progress, and explicit task state as authoritative
5. Follow the returned execution context without inventing workflow stages

Handle returned states explicitly:
- `blocked` — explain blocker and pause
- `all_done` — report completion and suggest archive
- ambiguous or contradictory task state — pause and ask

Never assume fixed file names when `contextFiles` are provided.

### Static-spec fallback
If OpenSpec is unavailable or not the active execution context, fall back to existing repo artifacts, preferring:
1. `spec.md`
2. `plan.md`
3. `tasks.md`
4. nearest equivalent under `.claude/plans/`, `.planning/`, or `docs/plans/`

Extract only:
- current goal
- selected task or clearly ready next task
- explicit blockers or dependencies
- acceptance criteria
- explicit constraints

Do not restate, regenerate, or improve the plan.

## Execution targeting
Default behavior is always small-step:
- `continue`, `next`, `batch:N`, and `task:<id>` stay scoped to one explicit task or one very small ready batch
- only `change:<name>` may continue across multiple ready tasks in the same change

If there is no single clear task or ready batch, stop and ask.

## Default execution path
1. Resolve the authoritative execution context.
2. Identify the exact task, ready next task, or very small ready batch.
3. Select exactly one authoritative state backend:
   - OpenSpec change state
   - project task backend
   - inline status reporting

   Never keep two authoritative trackers at once.
4. Declare applicable gates:
   - `env`
   - `test`
   - `static`
   - `traceability`
   - `review`
   - `risk_authorization`
   - `rollback_required`
5. Determine gate applicability from behavior change, public contract change, schema change, risk, reversibility, and project policy — not only from file type.
6. Determine execution level conservatively:
   - `L0`: small, local, reversible, no contract change
   - `L1`: default for non-trivial work
   - `L2`: multi-module, public interface or schema change, high-risk, irreversible, or scope-expanded work
7. Keep the execution target visible:
   - `Goal`
   - `Scope`
   - `Acceptance`
   - `Assumptions`

   For `L2`, also keep:
   - `Non-goals`
   - `Risks`
   - `Rollback`
   - `Execution order`
8. Restate the execution target briefly:
   - task
   - level
   - authoritative state backend
   - applicable gates
   - likely files
   - acceptance
   - blockers
   - permitted artifact updates
   - assumptions, if any
9. Run the environment gate first:
   - confirm required tools, workspace, runtime, and prerequisites
   - if a required capability is missing, state the capability drop explicitly
   - if it blocks safe execution or verification, stop and report the blocker
10. If behavior changes are expected, use `test-driven-development` before implementation when feasible.
11. Implement the minimum sufficient change.
12. If blocked by a failing test, bug, build issue, or unexpected behavior, try one direct fix, then use `systematic-debugging` once if needed.

## Verification Gates (MANDATORY)

### Verification is gate-driven
1. **Environment**
   - confirm required tools, workspace, runtime, and prerequisites

2. **Project-command-first**
   If project-defined commands are present, use the applicable subset first:
   - `ENV_SETUP_CMD`
   - `TEST_CMD`
   - `LINT_CMD`
   - `TYPECHECK_CMD`
   - `BUILD_CMD`

   Rules:
   - run only the relevant subset
   - if a command is unavailable or irrelevant, state that explicitly
   - do not silently skip a relevant command

3. **Fallback verification**
   If project-defined commands are absent or incomplete, use the best available fallback that preserves the same verification intent:
   - behavior change -> relevant tests
   - static quality impact -> relevant lint / typecheck / build
   - documentation or decision change -> consistency with authoritative specs, architecture docs, migration docs, and described behavior
   - infrastructure / configuration -> safest relevant validation command
   - migration / irreversible change -> backup, dry-run, integrity checks, and explicit rollback recording

   Project-specific examples may be used only when they are actually the relevant validation path in the current repo.

4. **Manual evidence path**
   If no meaningful automated verification exists:
   - explicitly state `No meaningful automated verification available`
   - perform the best available manual verification
   - record the evidence
   - if meaningful verification still depends on user-side confirmation, request it explicitly

**GATE: All applicable verification gates MUST pass before proceeding.**
- If any applicable gate fails, remains inconclusive, or lacks evidence, stop and report the blocker.
- Any gate marked `PASS` must have matching evidence.
- Missing evidence invalidates the completion claim.

Update only allowed task or progress artifacts, and only after verification succeeds.

## Review Gates (MANDATORY)

### Determine review requirement
Use:
- `REVIEW_POLICY`
- execution level (`L0` / `L1` / `L2`)
- public interface change
- schema change
- high-risk or irreversible operation
- explicit project policy

Use file paths only as supporting signals, not as the primary decision rule.

Policy rules:
- If `REVIEW_POLICY=strict`:
  - review is required for all `L1` and `L2` changes
  - review is optional for `L0` unless risk escalates
- If `REVIEW_POLICY=standard`:
  - review is required for:
    - public interface changes
    - schema changes
    - high-risk operations
    - irreversible changes
  - review is recommended otherwise

If review is required:
- use `requesting-code-review`
- valid review states are exactly:
  - `PASS`
  - `FAIL`
  - `BLOCKED`
- `PASS` and `FAIL` require:
  - independent review
  - recorded review evidence
- review evidence must identify:
  - `Reviewer`
  - `Reference`
- self-review does not satisfy the gate unless a higher-precedence policy explicitly allows it
- if independent review with recorded evidence cannot currently be established, status is `BLOCKED`
- when review is required, `N/A` is invalid

If review is `FAIL` or `BLOCKED`, do NOT claim completion.

## Risk and authorization
If an applicable gate includes `risk_authorization`, require explicit user authorization before any high-risk action.

High-risk actions include:
- recursive deletion
- force push
- destructive database operations
- direct production writes or deploys
- secret file mutation
- irreversible schema migrations

When authorized, record:

Risk Acceptance:
- `Operation`: <action>
- `Authorization`: <where it was confirmed>
- `Rollback`: <command or "none - irreversible">

Do not perform the high-risk step without this authorization record.

## Outcome reporting
When reporting outcome, include:
- `Scope`
- `Changed`
- `Verification`
- `Gates`
  - `env`
  - `test`
  - `static`
  - `traceability`
  - `review`
- `Risks`
- `Assumptions`
- `Rollback`

Rules:
- mark non-applicable gates as `N/A`
- keep the format concise
- preserve evidence-to-gate mapping
- do not claim completion unless every applicable required gate is `PASS`

## change:<name> loop rules
Only `change:<name>` allows continuous execution across multiple tasks.

For that mode:
- work only on clearly ready tasks within the named change
- keep each step minimal and task-scoped
- update verified checkboxes or clearly mechanical progress entries after each completed task
- refresh change state if readiness or progress becomes unclear
- checkpoint at meaningful phase changes
- checkpoint before high-risk operations
- checkpoint after any required gate failure
- stop immediately on blockers, semantic artifact changes, required-review blockage, or verification failure
- if work expands into multi-module, public-interface, schema, or otherwise high-risk scope, treat the affected step as `L2`
- if diff coherence degrades or scope starts to sprawl, pause and checkpoint

Do not turn `continue`, `next`, `batch:N`, or `task:<id>` into an implicit full-change loop.

## Pause conditions
Pause and ask instead of guessing when:
- the change or task selection is ambiguous
- more than one next task appears equally plausible and the ambiguity is blocking
- implementation exposes a new product decision or architecture tradeoff
- tasks need to be split, merged, reordered, or reinterpreted
- proposal, spec, or design needs semantic edits
- implementation cannot be mapped to one task or one clearly bounded batch
- verification fails after the direct fix and debugging fallback
- artifacts conflict with each other
- a required high-risk action needs explicit authorization

If uncertainty is non-blocking and does not require semantic artifact edits, proceed with explicit assumptions instead of opening another clarification loop.

When pausing, explain:
- what blocked execution
- which artifact or decision needs attention
- whether the needed update is mechanical or semantic
- the exact next decision needed from the user
- the safest resume point

## Artifact update policy
Allowed automatic updates:
- verified task checkbox updates such as `- [ ]` → `- [x]`
- clearly mechanical execution-progress updates, status notes, or checklist items that do not change meaning

Require confirmation before editing:
- proposal content
- spec content
- design content
- acceptance criteria
- task wording that changes meaning
- task ordering, splitting, merging, or reprioritization

If implementation reveals a semantic artifact problem, suggest the exact update needed, but do not silently edit it.

## Failure handling
Try one direct fix for the current failure.
If verification still fails or the cause remains unclear, stop execution and report the blocker.
If continuing would require replanning, new tasks, or speculative redesign, stop and surface the exact gap.

On repeated tool failure:
- record the error
- try one meaningful alternative
- if still blocked, stop and surface the blocker

Never invent results after a failed call.

## Tool discipline
Prefer the smallest tool surface that can finish the selected task.
Do not introduce a second planning layer through extra decomposition, ad hoc checklists, or parallel orchestration.
Do not use `using-git-worktrees` or `dispatching-parallel-agents` unless the user explicitly asks for them or isolation is clearly necessary for risk control.

## Completion standard
A selected task, batch, or change segment is complete only when:

### Verification Gate
- [ ] Applicable gates were declared before implementation
- [ ] Environment and prerequisites were checked
- [ ] Applicable project-defined verification commands were used first when present
- [ ] Applicable test and static checks passed
- [ ] Verification evidence is recorded
- [ ] If no meaningful automated verification exists: best available manual verification evidence is recorded
- [ ] If user-side confirmation is still required for meaningful verification: that confirmation was explicitly obtained

### Review Gate
- [ ] Review requirement was determined from `REVIEW_POLICY`, level, and gate impact
- [ ] If review is required: final review status is exactly `PASS`, `FAIL`, or `BLOCKED`
- [ ] If review is required and status is `PASS` or `FAIL`: independent review evidence with `Reviewer` and `Reference` is recorded
- [ ] If review is not required: the outcome report states why

### Execution Gate
- [ ] Implementation matches existing artifacts
- [ ] Exactly one authoritative state backend was used
- [ ] Task-state or progress updates happened only after verification
- [ ] Remaining risks or assumptions are stated explicitly
- [ ] `Rollback` is stated for `L2` or `N/A` otherwise

### Traceability Gate
- [ ] Outcome report includes `Scope`
- [ ] Outcome report includes `Changed`
- [ ] Outcome report includes `Verification`
- [ ] Outcome report includes `Gates`
- [ ] Outcome report includes `Risks`
- [ ] Outcome report includes `Assumptions`
- [ ] Outcome report includes `Rollback`

**GATE: If any applicable required gate fails, remains inconclusive, lacks evidence, or required review is `BLOCKED`, do NOT claim completion.**

If the selected batch is complete, verification is still fresh, and the current diff appears coherent, suggest `/commit-batch`.
If the working tree is clean and the scoped work appears complete, suggest `/finish-branch`.
Do not imply that local hooks override command-level readiness checks.