# Claude Workflow Baseline

This context defines the domain language for designing reusable Claude Code workflow subagents in this baseline source repo.

## Language

**Standalone collaborator**:
A subagent designed to complete a coherent role independently and report useful handoff information to the main session.
_Avoid_: Pipeline-only worker, rigid stage executor

**Staged workflow**:
A composition pattern where multiple standalone collaborators are sequenced by the main session for planning, implementation, testing, review, or operations.
_Avoid_: Mandatory pipeline runtime, hardcoded agent chain

**Handoff principles**:
Shared semantic requirements that make subagent results usable by the main session without requiring fixed field names or a universal output format.
_Avoid_: Shared output contract, universal schema, rigid XML block

**Stop principles**:
Shared guardrails for handing control back to the main session when continuing would require authorization, guesswork, destructive action, or unverifiable claims.
_Avoid_: Format failure as blocker, silent continuation

**Artifact-oriented output**:
A subagent result organized around role-specific deliverables, evidence, risks, and next actions rather than a fixed machine-parsed schema.
_Avoid_: Fixed output block, schema-first report

**Agent definition skeleton**:
The shared prompt structure for baseline subagents: frontmatter, Role, What you produce, Workflow, Guardrails, Handoff, and Principles this agent follows.
_Avoid_: Output-first template, universal report schema

## Relationships

- A **Standalone collaborator** can participate in a **Staged workflow**.
- A **Staged workflow** is coordinated by the main session, not by subagents.
- **Handoff principles** and **Stop principles** are shared across agents; **Artifact-oriented output** differs by agent role.
- The baseline **Standalone collaborators** keep their existing names: `task-planner`, `plan-reviewer`, `code-implementer`, `test-engineer`, `code-reviewer`, `deployment-operator`, and `spec-reviewer`.
- Every baseline subagent uses the same **Agent definition skeleton**, but each defines role-specific deliverables and handoff needs.
- Agent distribution docs explain standalone collaborators, invocation guidance, runtime caveats, and safety boundaries rather than centering a mandatory pipeline or shared output schema.
- The agent redesign should migrate all six baseline agent files and `distribution/agents/README.md` together so the shared design model stays consistent.
- Only one active collaborator should modify production code for a given change at a time; production-code handoffs must be explicit and followed by fresh review of the resulting diff.
- `code-implementer` may update focused tests that directly prove its patch; `test-engineer` owns independent verification, coverage strengthening, and failure classification.
- `test-engineer` does not modify production code; production fixes discovered during testing are handed back to the main session or `code-implementer` with failing evidence.
- `test-engineer` supports pre-implementation test design, post-implementation verification, and failure triage modes.
- `code-reviewer` is strictly read-only; findings may recommend fixes, but any code or test changes require a separate implementation pass and a fresh review.
- `code-reviewer` may review final diffs, patch proposals, targeted risk areas, or evidence quality when scope is explicit.
- `deployment-operator` is an opt-in operations specialist, not a default development pipeline stage.
- `deployment-operator` may run documented read-only status checks with a clear target and source; mutating deploy, release, rollback, or infrastructure actions require explicit current-session authorization and safety gates.
- Tool permissions follow role boundaries: planners and reviewers stay read-only, implementers may write production plus focused tests, testers may write test assets but not production code, and deployment operators run documented ops commands without file writes.
- Subagent results are inputs to the main session, not user-facing completion claims; the main session owns final verification and completion reporting.
- Subagent handoff should be concise but may include reasoning when it affects the next decision, risk, or verification; rigid bans on process narration are avoided.
- Incomplete handoff is not automatically `BLOCKED`; `BLOCKED` is reserved for real blockers, while unclear or missing evidence should be surfaced as incomplete or unverified.
- Claude Code may inject a `model` parameter through current tool schema or UI behavior; hook-level model gates are the effective enforcement layer, while README guidance is advisory.
- Agent prompt bodies do not discuss `model`, `effort`, or `max_turns`; those stay in frontmatter, hooks, and README runtime guidance.
- The main session owns task state; subagents may recommend task-state updates in handoff but should not maintain task state unless explicitly equipped and asked.
- Subagents do not write phase reports, plan artifacts, or review files unless the user-requested deliverable itself is a file; durable notes are owned by the main session.
- `task-planner` may suggest safe parallelization and specialist handoffs, but the main session remains responsible for invoking and coordinating agents.
- `plan-reviewer` reviews plan artifacts, task breakdowns, and architecture proposals for executability, boundedness, verification, dependency order, rollback, and architecture fit; it does not generate plans or implement work.
- `code-implementer` may work standalone on bounded implementation tasks; if scope, risk, or acceptance is unclear, it hands back the missing decision or recommends planning first.

## Example dialogue

> **Dev:** "Should every workflow agent return the same `<AGENT_OUTPUT>` block?"
> **Domain expert:** "No — they should share **Handoff principles**, but each **Standalone collaborator** should produce role-specific, **Artifact-oriented output**."

## Flagged ambiguities

- "LLM-friendly output" was ambiguous between fixed machine-readable schema and main-session-readable structured text; resolved: prefer artifact-oriented structured markdown with stable semantic anchors, not a universal rigid schema.
- "Planner readiness" was ambiguous between requiring requester-provided acceptance criteria and letting `task-planner` propose verifiable criteria; resolved: `task-planner` should draft criteria and surface decision points, blocking only when the goal, risk, authorization, or scope cannot be safely bounded.
- "Agent description" was ambiguous between routing trigger and full capability contract; resolved: frontmatter `description` should primarily support Claude Code routing, while `Role`, `Workflow`, and `Guardrails` carry full behavior details.
