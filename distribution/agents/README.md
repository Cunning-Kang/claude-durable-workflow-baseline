# Custom Subagent Definitions

Source-only, opt-in agent definitions for Claude Code. Not auto-installed.

## What this is

Reusable, version-controlled subagent definitions that users can adopt by copying to `~/.claude/agents/`. This directory is a distribution source and design guide, not a workflow runtime.

These agents are standalone collaborators. They can be composed into a staged workflow, but none requires a mandatory pipeline to be useful.

## Baseline collaborators

| Agent | Model | Effort | Max turns | Role |
|---|---:|---:|---:|---|
| `task-planner` | opus | inherit | 15 | Produces read-only implementation plans, task breakdowns, decision points, and handoff suggestions. |
| `code-implementer` | haiku | xhigh | 35 | Makes bounded code changes, updates focused tests when needed, and reports patch evidence. |
| `test-engineer` | haiku | xhigh | 25 | Designs tests, verifies diffs, triages failures, and reports coverage or evidence gaps. |
| `code-reviewer` | sonnet | xhigh | 20 | Performs strictly read-only review of diffs, proposals, risk areas, or evidence quality. |
| `deployment-operator` | haiku | xhigh | 15 | Runs documented operational checks or authorized deployment actions for explicit ops requests. |

A common development composition is:

```text
task-planner -> code-implementer -> test-engineer -> code-reviewer -> main final verification
```

This is a composition pattern, not a requirement. `deployment-operator` is an opt-in operations specialist, not a default development stage.

## Agent definition skeleton

Each baseline agent uses the same prompt shape:

```text
## Role
## What you produce
## Workflow
## Guardrails
## Handoff
## Principles this agent follows
```

The shared skeleton creates predictable prompts without forcing every agent into one output schema. Each agent defines role-specific artifacts and handoff needs.

## Main session responsibility

The main session stays as controller and final verifier:

- Selects and sequences agents.
- Maintains task state.
- Owns final verification and user-facing completion claims.
- Schedules independent read-only specialists when useful.
- Extracts useful handoff context and passes it to the next collaborator.
- Treats subagent results as inputs, not completion claims.

## Shared handoff and stop principles

Subagents should make the next useful action clear to the main session. A useful handoff usually names:

- What was produced, changed, found, or verified.
- Evidence that matters: files, commands, outputs, reviewed scope, observed state, or citations.
- Unknowns, risks, or unverified claims.
- Whether the main session can continue, must decide, or should stop.
- Suggested next collaborator or action when useful.

Do not require a universal field template. Incomplete handoff is not automatically blocked; real blockers are authorization gaps, unsafe guesswork, missing scope, unavailable evidence, destructive actions, or external effects that need user approval.

Teammate idle notifications are not completion evidence.

## Parallelism boundary

Only independent read-only tasks may run in parallel. File-writing work remains serial unless the main session explicitly separates non-overlapping scopes.

For a given change, only one active collaborator should modify production code at a time. If production-code ownership passes between collaborators, the main session must make the handoff explicit and re-run review on the resulting diff.

## Tool and permission matrix

| Agent | Write/Edit | Bash | MCP codebase | Task state | Git commit |
|---|---:|---:|---:|---:|---:|
| `task-planner` | no | no | yes | no | no |
| `code-implementer` | production plus focused tests | targeted smoke/codegen/test commands | yes | no | explicit authorization only |
| `test-engineer` | test assets only | test commands only | yes | no | no |
| `code-reviewer` | no | no | yes | no | no |
| `deployment-operator` | no | documented ops only | no | no | no |

When available, code-oriented agents prefer `codebase-memory-mcp` for structural code discovery and fall back to `Grep`, `Glob`, and `Read` when needed. Project memory is only a clue; any referenced file, command, function, or rule must be verified against the current repository.

## Planning and durable artifacts

`task-planner` returns plans in the Agent result. If a persistent plan artifact is required, the main session writes it explicitly.

Subagents do not write phase reports, plan artifacts, or review files unless the user-requested deliverable itself is a file. The main session owns task state and durable notes.

## Deployment safety

`deployment-operator` may run documented read-only status checks when the request includes a clear target and runbook/script/CI source. Mutating deployment, release, rollback, or infrastructure actions require explicit current-session authorization plus the safety gates in the agent definition.

The operator must block rather than infer when approval gates, rollback procedure, environment, or documented command source are unclear.

## Claude Code model parameters and actual control

Agent frontmatter declares intended `model`, `effort`, `permissionMode`, and related runtime fields. Current Claude Code tool schema or UI behavior may still inject a `model` parameter when calling subagents.

Hook-level model gates are the effective enforcement layer. README guidance is advisory: callers should follow hook feedback, retry with the required model when instructed, or omit explicit model parameters when possible.

## Adding a specialist agent

New specialist agents should stay outside the baseline collaborator set unless they are part of an explicitly approved redesign. Prefer precise `description` routing and a clear handoff protocol. Specialists may recommend handoffs, but the main session remains the orchestrator.

## Installation

```bash
# Copy selected agents to your user-level agents directory
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/*.md ~/.claude/agents/

# Or copy individual agents
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/task-planner.md ~/.claude/agents/
```

## Relationship to other layers

- `global/guides/orchestration-extension.md` — orchestration decision guide.
- `global/standards/core-standard.md` — core verification and review gates.
- These agents do not replace global runtime principles; they provide opt-in staged collaborators.
- Superpowers remains the primary behavior control layer.
