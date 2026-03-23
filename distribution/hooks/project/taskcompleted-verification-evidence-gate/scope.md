# Scope note — `taskcompleted-verification-evidence-gate`

## Machine-checkable subset implemented

This H-02 template implements only the subset that can be checked deterministically at `TaskCompleted` time:

- configured verification artifact files exist and contain the target task identifier
- the artifact contains at least one recognized evidence section heading
- the evidence section contains at least one record with field labels matching configured keys
- at least one record has non-placeholder values in those fields
- placeholder detection is configurable and uses both marker list and regex

## Allow conditions

- configured verification artifact exists and is readable
- artifact contains the target task identifier (via configured template expansion)
- exactly one artifact matches the target (ambiguous multiple matches are blocked)
- artifact contains an evidence section with recognized heading keys
- at least one evidence record has non-blank, non-placeholder values for configured fields

## Block conditions

- no verification artifact files resolved from configured globs/paths
- no artifact contains the target task identifier
- multiple artifacts contain the target identifier (ambiguous)
- artifact contains no recognized evidence section heading
- evidence section exists but contains no recognizable records
- all evidence records contain only placeholder values

## Deliberately not implemented

The following stay outside this hook:

- deciding which verification gates are applicable for the task
- choosing which commands should be run
- running tests, builds, or linters from the hook
- interpreting raw logs or evaluating whether evidence is substantively "good enough"
- proving semantic freshness relative to code changes beyond the durable record
- replacing verification skills, execution protocol, or human judgment

## Boundary ownership

### Protocol docs

Verification policy, strategy applicability, and gate selection are defined in protocol docs, not in hooks.

### Superpowers

Planning, routing, batching, and next-step selection are owned by Superpowers. The hook does not interfere with those decisions.

### Human judgment

Adoption decisions, ambiguous cases, and repo-local semantics remain with humans.

## Why this hook is not a second control plane

H-02 is a narrow declarative presence check. It does not:
- encode verification policy
- enforce specific tooling
- evaluate result quality
- replace human judgment

It only confirms that something resembling evidence has been written down.
