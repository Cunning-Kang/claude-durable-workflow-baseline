# Custom Subagent Definitions

Source-only, opt-in agent definitions for Claude Code. Not auto-installed.

## What this is

Reusable, version-controlled subagent definitions that users can adopt by copying to `~/.claude/agents/`. This directory is a distribution source, not a workflow runtime.

## Core staged workflow agents

These five agents form the default staged workflow for non-trivial software work:

```text
task-planner -> code-implementer -> test-engineer -> code-reviewer -> main final verification
```

| Agent | Model | Max turns | Role |
|---|---:|---:|---|
| `task-planner` | opus | 15 | Writes the plan artifact and handoff contract before implementation. |
| `code-implementer` | sonnet | 35 | Makes the planned code change and runs codegen, formatting, and local smoke checks. |
| `test-engineer` | sonnet | 25 | Updates test assets, runs relevant tests, and classifies failures conservatively. |
| `code-reviewer` | haiku | 20 | Reviews final code and test changes plus tester evidence without modifying files. |
| `deployment-operator` | haiku | 15 | Executes only documented runbook/script/CI operational commands for explicit ops requests. |

Legacy names `planner`, `implementer`, `tester`, `reviewer`, and `ops-deploy` were removed rather than kept as aliases to avoid duplicate routing targets. Other existing specialist agents in this directory are separate agents, not aliases for these five core workflow stages.

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
| `code-implementer` | `DONE`, `BLOCKED` |
| `test-engineer` | `PASS`, `PASS_WITH_WARNINGS`, `FAIL`, `BLOCKED` |
| `code-reviewer` | `PASS`, `PASS_WITH_WARNINGS`, `FAIL`, `BLOCKED` |
| `deployment-operator` | `DONE`, `BLOCKED`, `ABORTED` |

`PASS_WITH_WARNINGS` can proceed only if warnings are non-blocking and the main session records them in final risks or assumptions.

## Tool and evidence policy

Tool access is least-privilege by role:

- `task-planner`: read/discovery tools plus write access for the plan file.
- `code-implementer`: edit tools and Bash for codegen, formatting, and local smoke checks.
- `test-engineer`: edit tools for test assets and Bash for relevant test commands.
- `code-reviewer`: read-only tools and safe no-write static checks.
- `deployment-operator`: read plus Bash execution of documented runbook/script/CI commands only.

When available, code-oriented agents prefer `codebase-memory-mcp` for structural code discovery and fall back to `Grep`, `Glob`, and `Read` when needed. Project memory is only a clue; any referenced file, command, function, or rule must be verified against the current repository.

## Planning artifacts

`task-planner` always writes a plan file. It uses the project’s established planning location when one exists; otherwise it writes `.claude/plans/<task-slug>.md`. Without a project template, the fallback is a one-page plan containing Goal, Scope, Acceptance, Assumptions, Execution order, Target files or areas, and Verification gates.

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
