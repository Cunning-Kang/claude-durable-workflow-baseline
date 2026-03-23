# Scope note — `taskcompleted-authoritative-state-gate`

## Machine-checkable subset implemented

This H-01 template implements only the subset that can be checked deterministically at `TaskCompleted` time:

- exactly one configured durable tracker resolves for the completion target
- the target durable task entry exists in that tracker
- the selected tracker does not still mark the task as obviously open
- configured authoritative surfaces do not leave the same task simultaneously open and closed

## Allow conditions

The hook allows completion only when all of the following are true:

- explicit target mapping configuration is present
- at least one configured tracker path/glob resolves
- exactly one resolved tracker contains the mapped task entry
- the selected tracker shows a configured closed marker for that task
- the selected tracker does not show a configured open marker for that task
- no configured additional authoritative surface still shows that task as open or contradictory

## Block conditions

The hook blocks when any of the following occurs:

- target mapping configuration is missing or resolves to an empty target identifier
- zero tracker files resolve
- multiple tracker files match the same completion target
- the mapped task entry does not exist in the resolved tracker set
- the selected tracker still marks the task as `Current`, `ready`, `in_progress`, or another configured open marker
- the selected tracker has no configured closed marker for the mapped task
- configured authoritative surfaces disagree about open vs. closed state for the same task

## Deliberately not implemented

This template does **not** implement:

- authoritative-backend selection for a repo
- task translation into session task tooling
- checkpoint selection
- reprioritization
- next-task derivation
- backlog orchestration
- repo-wide shadow tracker discovery without explicit configuration
- interpretation of ambiguous milestone semantics that are not already externalized in durable state

## Boundary ownership

### Protocol docs

Protocol docs own the workflow meaning around completion, milestone semantics, and durable-record conventions.

### Superpowers

Superpowers owns planning, routing, batching, execution flow, and next-step selection.

### Human judgment

Humans still decide:

- which tracker/surfaces are authoritative for a given repo
- which target-mapping template is trustworthy
- how repo-local markers should be classified
- what ambiguous durable text means when it is not already machine-checkable

## Why this hook is not a second control plane

The hook validates one narrow invariant at completion time against already-written durable state. It does not add a competing workflow model.
