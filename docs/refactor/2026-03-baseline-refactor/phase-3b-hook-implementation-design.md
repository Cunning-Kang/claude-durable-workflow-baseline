# Phase 3B — Hook Implementation Design

> Status: implementation-prep only; no hook source in this phase
> Authoritative inputs: `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`, `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-tasks.md`
> Historical references only: `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementations-plan.md`, `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementations-tasks.md`

## Purpose

Translate the authoritative Phase 3B hooks migration set into implementation-ready design mappings for H-01 / H-02 / H-03 without falling back to event-first candidate selection, live wiring, or broad workflow orchestration.

## Global constraints

- Start from the rule cluster, not from hook event inventory.
- Keep all hook artifacts in `project` scope only.
- Produce source/snippet templates only; no live `settings.json`, no bootstrap integration, no default enablement.
- Narrow every cluster to a deterministic, machine-checkable subset.
- Leave protocol interpretation, Superpowers routing, and human judgment outside the hook.
- Do not turn any hook into a second control plane.

## Standard artifact family

Each approved cluster maps to one project-scoped hook template family:

- `distribution/hooks/project/<candidate>/hook.mjs`
- `distribution/settings-snippets/project/<candidate>.settings.jsonc`
- `distribution/hooks/project/<candidate>/README.md`
- `distribution/hooks/project/<candidate>/scope.md`
- `distribution/hooks/project/<candidate>/manual-test.md`
- `distribution/hooks/project/<candidate>/rollback.md`

---

## H-01 — Authoritative state and milestone integrity

### Machine-checkable subset

H-01 is intentionally narrowed to the completion-time consistency check that a hook can enforce deterministically:

- The completion attempt maps to exactly one configured durable tracker in the destination project.
- The target durable task entry exists in that tracker.
- The durable tracker no longer leaves the just-completed task in an obviously open state such as `Current`, `ready`, `in_progress`, or an equivalent repo-local open marker.
- The tracker does not simultaneously present contradictory milestone state for the same task across the configured authoritative surfaces.

This subset is about **closing a task without leaving contradictory durable state behind**. It is not a generic “manage all workflow state” hook.

### Deliberately not implemented

The following parts of H-01 stay outside hooks:

- choosing the authoritative backend for a repo
- translating durable work into native session tasks
- deciding when a checkpoint should be taken
- reprioritizing tasks or deriving the next ready task
- interpreting ambiguous milestone semantics that are not already externalized in durable state
- discovering every possible shadow tracker anywhere in the repo without explicit configuration

### Implementation design mapping

- **Candidate family:** `taskcompleted-authoritative-state-gate`
- **Enforcement objective:** block `TaskCompleted` when the configured durable tracker still shows unresolved or contradictory milestone state for the target task.
- **Event choice:** `TaskCompleted`
  - The guard belongs on the durable completion boundary, not on a reminder boundary.
  - Not `Stop`: too late, may not fire on interruption, and is better suited to reminders than deterministic denial.
  - Not `UserPromptSubmit`: prompts are not durable state transitions.
  - Not `PostToolUse`: tool execution boundaries are too granular and not equivalent to milestone closure.
  - Not `ConfigChange`: settings mutation is unrelated to task-state closure.
- **Scope:** `project`
  - The rule is repo-local because authoritative tracker shape is repo-local.
  - It must remain explicit opt-in and never become a user-level default.
- **Evidence/state source:**
  - a configured durable tracker path or glob in the destination project
  - default modeled shape: `docs/specs/<feature>/index.md` or equivalent durable task index
  - optional additional configured task artifact paths when a repo splits durable state across multiple known files
- **Allow conditions:**
  - exactly one configured durable tracker resolves for the target task
  - the target task can be mapped to one durable entry
  - the durable state already reflects closure consistently
  - the durable tracker does not still point to the completed task as the active open milestone
- **Block conditions:**
  - zero configured tracker matches or multiple ambiguous matches
  - target task cannot be mapped to durable state
  - durable tracker still marks the task as `Current`, `ready`, `in_progress`, or equivalent open state
  - contradictory open/closed representations remain after the attempted completion
- **Residual gap:**
  - protocol docs and human judgment still decide what the authoritative backend should be and whether a milestone truly changed in the broader semantic sense
  - Superpowers and task tooling still own planning, routing, batching, and next-step selection
- **Why this is not a second control plane:**
  - the hook only reads already-declared durable state at the point of completion
  - it creates no new backlog, no new task ordering, and no new workflow state model
  - it validates a narrow invariant; it does not orchestrate work

---

## H-02 — Verification-before-completion gate

### Machine-checkable subset

H-02 is intentionally narrowed to a **durable verification evidence presence gate**:

- a configured verification artifact exists for the completion target
- the artifact contains at least one populated verification record rather than only template placeholders
- the record exposes machine-checkable fields such as `Command / check`, `Result`, and `Date`, or a repo-local equivalent explicitly configured in the snippet

This means the first implementation guards against **missing or obviously unfilled durable verification evidence**. It does not attempt to compute the entire verification strategy.

### Deliberately not implemented

The following parts stay outside hooks:

- deciding which verification gates are applicable for the task
- choosing which commands should be run
- running tests, builds, or linters from the hook
- interpreting raw logs or evaluating whether the evidence is substantively “good enough”
- proving that the evidence is semantically fresh relative to every code change beyond the durable record the repo chooses to expose
- replacing verification skills, execution protocol, or human judgment

### Implementation design mapping

- **Candidate family:** `taskcompleted-verification-evidence-gate`
- **Enforcement objective:** block `TaskCompleted` when durable verification evidence required for completion is missing, empty, or still placeholder-shaped.
- **Event choice:** `TaskCompleted`
  - Verification is a completion gate, so the denial point should be the completion boundary itself.
  - Not `Stop`: reminders happen after the response path and cannot reliably prevent incorrect completion.
  - Not `UserPromptSubmit` or `PostToolUse`: those are not equivalent to “claiming the task is done”.
- **Scope:** `project`
  - verification artifact location and shape are repo-local
  - adoption must remain opt-in and project-scoped
- **Evidence/state source:**
  - a configured durable verification artifact path in the destination project
  - default modeled shape: `verify.md` referenced from the active durable index, matching the baseline `Summary` and `Evidence` sections
  - first implementation consumes durable written evidence, not raw CLI logs
- **Allow conditions:**
  - configured verification artifact exists
  - required evidence section is present
  - at least one evidence record has non-placeholder values for the configured fields
  - the artifact is no longer just the template stub
- **Block conditions:**
  - verification artifact missing
  - evidence section missing
  - only placeholder text remains
  - required evidence fields are blank or clearly unfilled
- **Residual gap:**
  - `execution-contract.md`, verification skills, and humans still decide applicability, adequacy, and remediation
  - the hook only guards record presence, not verification quality
- **Why this is not a second control plane:**
  - the hook does not decide what to test or how to test it
  - it only refuses completion when the repo’s own durable evidence surface is empty or still placeholder-shaped
  - verification workflow remains outside the hook

---

## H-03 — Independent review evidence gate

### Machine-checkable subset

H-03 is intentionally narrowed to a **review-required evidence presence gate** that only activates when the destination project already exposes a machine-checkable review-required signal.

The deterministic subset is:

- the repo provides an explicit review-required signal outside the hook logic
- when that signal is present, a configured durable review artifact exists
- the review artifact contains non-placeholder `Reviewer`, `Reference`, and `Outcome` fields, or explicitly configured equivalents
- completion is allowed only when the recorded outcome is `PASS`

This keeps the hook focused on **evidence presence and closure status**, not on broader review policy computation.

### Deliberately not implemented

The following parts stay outside hooks:

- deciding whether review is required from diff risk, public interface changes, or schema semantics
- selecting or dispatching the reviewer
- proving true reviewer independence beyond whatever durable signal the repo exposes
- evaluating review quality, findings depth, or technical correctness
- replacing `review-protocol.md`, review skills, or human judgment

### Implementation design mapping

- **Candidate family:** `taskcompleted-review-evidence-gate`
- **Enforcement objective:** when a repo-local review-required signal is present, block `TaskCompleted` unless durable review evidence exists and records a passing outcome.
- **Event choice:** `TaskCompleted`
  - The gate belongs on the same closure boundary where incorrect completion would otherwise occur.
  - Not `Stop`: a post-response reminder cannot be the primary review gate.
  - Not `UserPromptSubmit`: prompt text is not durable review state.
  - Not `PostToolUse`: individual tool runs do not mean the review gate has been satisfied.
- **Scope:** `project`
  - the meaning of review-required and the durable review artifact location are repo-local
  - the template must stay opt-in and project-scoped
- **Evidence/state source:**
  - a configured review-required signal supplied by destination-project durable metadata or snippet configuration
  - a configured durable review artifact path
  - default modeled artifact: `review.md` referenced from the active durable index and shaped like the baseline template with `Reviewer`, `Reference`, and `Outcome`
- **Allow conditions:**
  - no review-required signal is present for the completion target, so the hook has no opinion
  - or: review-required signal is present, the review artifact exists, `Reviewer` and `Reference` are populated, and `Outcome` is `PASS`
- **Block conditions:**
  - review-required signal present but review artifact missing
  - required fields remain placeholder or blank
  - `Outcome` is missing, `FAIL`, `BLOCKED`, or any non-`PASS` value
- **Residual gap:**
  - `review-protocol.md`, review checklisting, and human/agent review still decide if review is required and whether the review was substantively independent and sufficient
  - the hook only guards written evidence presence at closure time
- **Why this is not a second control plane:**
  - the hook consumes a review-required signal that already exists elsewhere; it does not invent policy
  - it does not schedule review, assign reviewers, or interpret findings beyond pass/block outcome shape
  - the repo keeps one review policy surface and one durable review record; the hook only gates completion against them

---

## Why these mappings are implementation-ready now

These mappings are now concrete enough for actual hook implementation because each cluster has all of the following fixed in advance:

- a named candidate family
- a single primary enforcement objective
- one justified event choice
- explicit scope
- explicit evidence/state source
- explicit allow/block conditions
- explicit residual gap
- explicit “do not implement” boundaries

That removes the remaining ambiguity that previously kept Phase 3B at the abstract cluster level while still avoiding the opposite failure mode of turning hook templates into a broad orchestration layer.
