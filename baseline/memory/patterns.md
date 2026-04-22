# Patterns

Reusable patterns that others can apply directly. Use the repo-local memory protocol and file roles here for classification.

## Entry Format

```
PATTERN: <name>
Trigger: <when to apply this pattern>
Fix:    <what to do>
Why:    <why this approach works>
```

## What Goes In

- Workflow patterns with a demonstrated trigger and a reusable fix
- Recurring implementation approaches confirmed across sessions
- Verification patterns with a stable command sequence

## What Does NOT Go In

- One-liner facts (→ `MEMORY.md`)
- Pitfall descriptions (→ `gotchas.md`)
- Protocol definitions (→ `docs/workflow/`)
- Hook behavior (→ hook source files or `docs/reference/hooks-scope.md`)
- One-off experiences without demonstrated reuse

## How to Add

When a durable pattern is confirmed:
1. Verify D1/D2/D3 (recurrence, reusability, actionability)
2. Route using the repo-local memory protocol and file roles
3. Write in entry format above
4. Do not duplicate `MEMORY.md` or `gotchas.md`

## Current Status

No durable patterns confirmed yet. Entries belong here only after D1/D2/D3 are all satisfied from actual usage.
