# Custom Subagent Definitions

Source-only, opt-in agent definitions for Claude Code. Not auto-installed.

## What this is

Reusable, version-controlled subagent definitions that users can adopt by copying to `~/.claude/agents/`. This directory is a distribution source, not a workflow runtime.

## Core staged workflow agents

These five agents form the default staged workflow for non-trivial software work:

```text
task-planner -> code-implementer -> test-engineer -> code-reviewer -> main final verification
```

| Agent | Model | Effort | Max turns | Role |
|---|---:|---:|---:|---|
| `task-planner` | opus | inherit | 15 | Returns the plan and handoff contract in Agent result only. |
| `code-implementer` | haiku | xhigh | 35 | Makes the planned code change and runs codegen, formatting, and local smoke checks. |
| `test-engineer` | haiku | xhigh | 25 | Updates test assets, runs relevant tests, and classifies failures conservatively. |
| `code-reviewer` | sonnet | xhigh | 20 | Reviews final code and test changes plus tester evidence without modifying files. |
| `deployment-operator` | haiku | xhigh | 15 | Executes only documented runbook/script/CI operational commands for explicit ops requests. |

Legacy names `planner`, `implementer`, `tester`, `reviewer`, and `ops-deploy` were removed rather than kept as aliases to avoid duplicate routing targets. Other existing specialist agents in this directory are separate agents, not aliases for these five core workflow stages.

Claude Code subagent frontmatter supports `effort`. The non-`opus` workflow agents set `effort: xhigh` to compensate for weaker mapped models; actual behavior still depends on the active model's supported effort levels.

## Main session responsibility

The main session stays as the controller and final verifier:

- Selects and sequences agents.
- Runs only evidence audit and minimal re-verification before completion claims.
- Maintains any task state.
- Schedules independent read-only specialists when useful.
- Does not become the implementation, testing, review, or deployment worker.

## Parallelism boundary

Only independent read-only tasks may run in parallel. File-writing stages remain serial:

```text
code-implementer -> test-engineer -> code-reviewer
```

This keeps the reviewed scope stable and prevents test changes from escaping review.

## Shared output contract

Each core workflow agent ends with the same compact evidence shell:

```text
<AGENT_OUTPUT>
status: <role-specific enum>
summary:
  - <1-3 concise bullets>
artifacts:
  - <files, plan paths, commands, diffs, runbook refs>
evidence:
  - <command/manual/review evidence>
risks:
  - <remaining risk or None>
assumptions:
  - <material assumption or None>
next_action: <what main session should do next>
role_specific:
  <compact role-specific fields>
</AGENT_OUTPUT>
```

Status values are role-specific:

| Agent | Status values |
|---|---|
| `task-planner` | `READY`, `BLOCKED` |
| `code-implementer` | `DONE`, `PARTIAL`, `BLOCKED` |
| `test-engineer` | `PASS`, `PASS_WITH_WARNINGS`, `FAIL`, `BLOCKED` |
| `code-reviewer` | `PASS`, `FAIL`, `BLOCKED` |
| `deployment-operator` | `DONE`, `BLOCKED`, `ABORTED` |

`PASS_WITH_WARNINGS` can proceed only if warnings are non-blocking and the main session records them in final risks or assumptions.

## Delivery protocol

- Final deliverables are returned through Agent result in the `<AGENT_OUTPUT>` block.
- Teammate idle notifications are not completion evidence.
- The main session owns task state. Agents without task-state tools must not be asked to update tasks.
- The main session extracts AGENT_OUTPUT fields and passes relevant context to the next stage.
- Unrecognized status values must be treated as `BLOCKED`.

## Tool and permission matrix

| Agent | Write/Edit | Bash | MCP codebase | Task state | Git commit |
|---|---:|---:|---:|---:|---:|
| `task-planner` | no | no | yes | no | no |
| `code-implementer` | production/generation only | targeted smoke/codegen only | yes | no | explicit authorization only |
| `test-engineer` | test assets only | test commands only | yes | no | no |
| `code-reviewer` | no | no | yes | no | no |
| `deployment-operator` | no | documented ops only | no | no | no |

Single-writer rule: at most one agent may modify production code files in a pipeline run. The main session remains the sole orchestrator.

When available, code-oriented agents prefer `codebase-memory-mcp` for structural code discovery and fall back to `Grep`, `Glob`, and `Read` when needed. Project memory is only a clue; any referenced file, command, function, or rule must be verified against the current repository.

## Planning artifacts

`task-planner` returns the plan in AGENT_OUTPUT only. If a persistent plan artifact is required, the invoker extracts the plan from Agent result and writes it explicitly.

Other agents do not write phase reports. They report phase results only through `AGENT_OUTPUT`.

## Deployment safety

`deployment-operator` requires an explicit action, target environment, and runbook/script/CI clue. It must block rather than infer when approval gates, rollback procedure, environment, or documented command source are unclear.

## Adding a specialist agent

New specialist agents should stay outside the core staged workflow unless they are part of an explicitly approved redesign. Prefer precise `description` routing and a clear return protocol. Specialists may recommend handoffs, but the main session remains the orchestrator.

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
- These agents do not replace global runtime principles; they provide opt-in staged workers.
- Superpowers remains the primary behavior control layer.
