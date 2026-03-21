name: new-feature
description: |
  Create a new feature spec directory from the _template skeleton.

  Use this when starting any new feature, bugfix, or refactor that needs
  a spec/plan/review/verify structure.

  What it does:
  1. Runs ~/.claude/scripts/instantiate-feature.sh <feature-slug>
  2. Creates docs/specs/<feature-slug>/ from _template/
  3. Replaces <feature-slug> placeholders in all generated files

  After instantiation, fill in:
  - spec.md: Goal, Scope, Acceptance, Non-goals, Risks, Rollback
  - plan.md: Execution Order, Steps, Risks/Blockers
  - tasks/: Rename T01-example.md to match your first step
  - review.md: Fill in Reviewer (before starting implementation)
  - verify.md: Add verification commands for each acceptance condition

  Does NOT overwrite existing files or create git commits.

allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep

argument-hint: <feature-slug>

example: |
  /new-feature user-auth
  /new-feature payment-gateway
  /new-feature fix-session-timeout
