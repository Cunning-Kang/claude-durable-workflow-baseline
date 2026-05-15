# Adopt artifact-oriented standalone collaborator design for baseline subagents

We will redesign the five baseline Claude Code subagents as standalone collaborators that can also be composed into staged workflows. The agent definitions will follow an Anthropic-inspired structure: `Role`, `What you produce`, `Workflow`, `Guardrails`, `Handoff`, and `Principles this agent follows`. This replaces the previous shared rigid output block because real Claude Code production use needs main-session-readable handoffs, partial progress, decision points, and role-specific artifacts more than universal field-level parseability.

## Consequences

- Subagents share handoff and stop principles, not a universal output schema.
- The main session remains responsible for orchestration, task state, final verification, and user-facing completion claims.
- Role boundaries become explicit: planners and reviewers are read-only, implementers may write production code plus focused tests, testers may write test assets but not production code, and deployment operators are opt-in operations specialists.
- README and hook guidance must explain runtime caveats such as Claude Code model-parameter injection and hook-level model gates.
