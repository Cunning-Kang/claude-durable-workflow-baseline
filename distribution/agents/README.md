# Custom Agent Definitions

Source-only, opt-in specialist agent definitions for Claude Code. Not auto-installed.

## What this is

Reusable, version-controlled agent definitions that users can adopt by copying to `~/.claude/agents/` or a project `.claude/agents/` directory. This directory is a distribution source and design guide, not a workflow runtime.

Each agent is a standalone specialist. Claude Code routes to agents primarily from frontmatter `description`, so descriptions should state the trigger, scope, and negative cases clearly. Prompt bodies define specialist behavior and quality bars; they do not define transport, orchestration, or task-state protocols.

## Baseline specialists

| Agent | Model | Effort | Max turns | Role |
|---|---:|---:|---:|---|
| `task-planner` | opus | inherit | 15 | Produces read-only implementation plans, task breakdowns, decision points, and acceptance criteria. |
| `code-implementer` | haiku | xhigh | 35 | Makes bounded code changes and updates focused tests when they directly prove the patch. |
| `test-engineer` | haiku | xhigh | 25 | Designs tests, verifies diffs, triages failures, and reports coverage or evidence gaps. |
| `code-reviewer` | sonnet | xhigh | 20 | Performs strictly read-only review of diffs, proposals, risk areas, or evidence quality. |
| `deployment-operator` | haiku | xhigh | 15 | Runs documented operational checks or authorized deployment actions for explicit ops requests. |

## Agent definition shape

Baseline agents use a small, official-style prompt shape:

```text
## Role
## What you produce
## Workflow
## Guardrails
```

The sections describe specialist behavior and output quality. They intentionally avoid runtime-specific instructions such as `Agent result`, teammate idle notifications, or task-state ownership. Claude Code runtime owns how agent output is routed; the agent owns the work product.

Frontmatter `tools` may still expose runtime collaboration primitives such as `TaskList`, `TaskGet`, `TaskCreate`, `TaskUpdate`, and `SendMessage`. Tool availability lets adopted agents participate in team mode; prompt bodies should still avoid hard-coding orchestration protocols.

## Design principles

- Keep `description` precise: action, scope, and when not to use the agent.
- Keep prompts role-focused: what the specialist does, how it works, and what it must not do.
- Do not encode orchestration pipelines in agent definitions.
- Do not make one specialist depend on another specialist to be useful.
- Do not add transport-specific handoff protocols unless the agent's explicit purpose is orchestration.
- Prefer repository evidence over memory or generic stack assumptions.

## Tool and permission matrix

| Agent | Write/Edit | Bash | MCP codebase | Git commit |
|---|---:|---:|---:|---:|
| `task-planner` | no | no | yes | no |
| `code-implementer` | production plus focused tests | targeted smoke/codegen/test commands | yes | explicit authorization only |
| `test-engineer` | test assets only | test commands only | yes | no |
| `code-reviewer` | no | no | yes | no |
| `deployment-operator` | no | documented ops only | no | no |

When available, code-oriented agents prefer `codebase-memory-mcp` for structural code discovery and fall back to `Grep`, `Glob`, and `Read` when needed. Project memory is only a clue; any referenced file, command, function, or rule must be verified against the current repository.

## Deployment safety

`deployment-operator` may run documented read-only status checks when the request includes a clear target and runbook/script/CI source. Mutating deployment, release, rollback, or infrastructure actions require explicit current-session authorization plus the safety gates in the agent definition.

The operator must block rather than infer when approval gates, rollback procedure, environment, or documented command source are unclear.

## Claude Code model parameters and actual control

Agent frontmatter declares intended `model`, `effort`, `permissionMode`, and related runtime fields. Current Claude Code tool schema or UI behavior may still inject a `model` parameter when calling subagents.

Hook-level model gates are the effective enforcement layer. README guidance is advisory: callers should follow hook feedback, retry with the required model when instructed, or omit explicit model parameters when possible.

## Adding a specialist agent

New specialists should use precise `description` routing and role-focused prompts. Add orchestration language only for agents whose explicit job is orchestration.

## Installation

```bash
# Copy selected agents to your user-level agents directory
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/*.md ~/.claude/agents/

# Or copy individual agents
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/task-planner.md ~/.claude/agents/
```

## Relationship to other layers

- `global/standards/core-standard.md` — core verification and review gates.
- These agents do not replace global runtime principles; they provide opt-in specialists.
