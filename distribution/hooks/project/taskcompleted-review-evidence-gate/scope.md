# Scope note — `taskcompleted-review-evidence-gate`

## Machine-checkable subset implemented

This H-03 template implements only the subset that can be checked deterministically at `TaskCompleted` time:

- a configured signal file glob or path resolves
- the resolved signal file contains the target task needle
- a configured artifact file glob or path resolves
- exactly one review entry in the artifact matches the target task
- the matched entry has a non-placeholder `Reviewer` field
- the matched entry has a non-placeholder `Reference` field
- the matched entry has an `Outcome` field that matches a configured PASS token

## Allow conditions

The hook allows completion only when all of the following are true:

- no signal file configuration is present (hook not active), OR
- signal files exist but none mention the target task (task not review-required), OR
- signal file mentions target task AND a matching review entry exists with all required fields AND Outcome is PASS

## Block conditions

The hook blocks when any of the following occurs:

- signal file mentions target task but no review artifact files resolve
- signal file mentions target task but no review entry exists for the target task
- signal file mentions target task and review entry exists but `Reviewer` is a placeholder
- signal file mentions target task and review entry exists but `Reference` is a placeholder
- signal file mentions target task and review entry exists but `Outcome` is not a PASS token
- multiple signal files mention the target task (ambiguous)
- multiple review entries match the target task (ambiguous)

## Deliberately not implemented

This template does **not** implement:

- automatic determination of which tasks need review
- diff-size / file-type / risk-level / schema-change inference
- automatic reviewer assignment
- automatic reviewer independence assessment
- automatic review quality evaluation
- automatic review comment semantic interpretation
- broad review orchestration / policy engine logic

## Boundary ownership

### Protocol docs

Protocol docs own the workflow meaning around review requirements, review semantics, and durable-record conventions.

### Superpowers

Superpowers owns planning, routing, batching, execution flow, and next-step selection.

### Human judgment

Humans still decide:

- which tasks require review (signal file content)
- who the reviewer should be
- what the review reference means
- whether review quality is sufficient

## Why this hook is not a second control plane

The hook validates one narrow invariant: when a signal says "this task needs review", evidence of that review must be present and non-placeholder. It does not add a competing workflow model.
