# Execution Contract

## Purpose
Define the repo-local handoff from durable feature artifacts into session execution without turning this repository into a second control layer.

This contract constrains **execution state, verification, and milestone updates**. It does not own planning, routing, or finishing decisions.

## Scope
Use this document only after durable execution artifacts already exist, such as:
- `spec.md` or equivalent requirement/boundary doc
- `plan.md` or equivalent sequencing doc
- `tasks.md`, task files, or equivalent durable task tracker

## Minimum required inputs
Before execution, read only the minimum set needed to move the active task forward:
1. the active durable task entry or task file
2. the acceptance / boundary artifact referenced by that task
3. the sequencing artifact only if task order or dependency is unclear
4. risk, migration, or review artifacts only when the task explicitly depends on them

## Authoritative state rule
Use exactly one authoritative state backend for active execution:
- **session state**: native Claude Code Task tools or the project-native equivalent
- **cross-session state**: durable repo artifacts such as `tasks.md`

Do not keep both trackers at the same level of detail. Durable artifacts record milestone changes; session state may be finer-grained for the current run.

## Minimum execution target
Before implementation, make the active execution target explicit:
- Goal
- Scope
- Acceptance
- Assumptions

For higher-risk work, also make explicit:
- Non-goals
- Risks
- Rollback
- Execution order

## Default execution bridge
For one durable task or one clearly bounded ready batch:
1. Resolve the active task and its explicit dependencies.
2. Choose the authoritative state backend for the current execution.
3. Translate the durable task into the smallest useful session task list when session tracking is needed.
4. Implement the minimum sufficient change.
5. Run all applicable verification gates before claiming milestone completion.
6. If review is required, complete the review gate before marking the durable task done.
7. Update durable artifacts only when the milestone truly changes.

## Verification gates
Apply only the gates relevant to the task:
- **Environment** — required tools, workspace, and prerequisites are available
- **Test** — changed behavior is verified
- **Static** — lint, typecheck, or build passes when relevant
- **Review** — only when required by project policy or task risk

Use project-defined verification commands first when they exist. If a meaningful automated check is unavailable, say so explicitly and record the best available manual evidence instead.

Changed files, evidence, and durable status updates are recorded through the active task artifact and its linked review or verify records, not as a separate gate.

## Durable update rule
Only make mechanical milestone updates that are already supported by the durable task schema in the current repo. Typical examples include:
- `todo` -> `doing`
- `doing` -> `blocked`
- `doing` -> `done`

Do not silently rewrite task meaning, reorder work, or create a second backlog from this contract.

## Relationship to adjacent protocol docs
- `native-task-translation.md` explains how one durable task is reduced into a minimal session task list.
- `review-protocol.md` defines when review is required and how its outcome is recorded.
- `review-checklist.md` is a lightweight review aid, not an execution controller.

## What this contract does not do
- It does not create plans or tasks automatically.
- It does not reprioritize work.
- It does not replace review protocol.
- It does not define a finishing lane or PR workflow.
- It does not replace the primary control layer.
