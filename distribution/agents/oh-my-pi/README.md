# Custom Agent Definitions

Source-only, opt-in specialist agent definitions for Oh My Pi. Not auto-installed.

## What this is

Reusable, version-controlled agent definitions that users can adopt by copying to `~/.omp/agent/agents/` or a project `.omp/agents/` directory. This directory is a distribution source and design guide, not a workflow runtime.

Each agent is a standalone specialist. Oh My Pi routes to agents by exact `name` at execution time and exposes `description` for selection guidance, so descriptions should state the trigger, scope, and negative cases clearly. Prompt bodies define specialist behavior and quality bars; they do not define transport, orchestration, or task-state protocols.

## Baseline specialists

| Agent | Model | Thinking | Tools | Role |
|---|---:|---:|---|---|
| `task-planner` | opus | inherit | read-only | Principal engineer/TPM for ambiguous work; turns fuzzy intent into executable, verifiable plans. |
| `code-implementer` | haiku | high | edit/write/bash/eval/debug | Senior product engineer for constrained high-signal patches and smallest provable production changes. |
| `test-engineer` | haiku | high | tests + verification commands | Staff test engineer for behavior proof, false-positive prevention, and RED/GREEN evidence quality. |
| `code-reviewer` | sonnet | high | read-only | Principal hostile reviewer for correctness, security, scope, and evidence failures. |
| `deployment-operator` | haiku | high | read/search/find/bash | Senior SRE for documented operations where authorization, rollback, and health evidence are explicit. |
| `spec-reviewer` | haiku | high | read-only | Compliance auditor verifying delivery matches spec contract. Read-only, no code quality evaluation. |
| `mavis` | haiku | inherit | Mavis Team Plan MCP only | Mavis Team Plan operator for bounded worker/verifier execution evidence without final acceptance. |

## Agent definition shape

Baseline agents use a short hard prompt shape:

```text
## Role
## Boundaries
## Workflow
## What you produce
## Artifact and final handoff
```

`## Artifact and final handoff` is always the last section. It defines the Bookend XML transport contract for gate-critical fields only. Agent-specific evidence remains agent-specific.

## Design principles

- Keep `name` exact and stable; Oh My Pi task execution resolves agents by exact name.
- Keep `description` precise: action, scope, and when not to use the agent.
- Keep prompts role-focused: what the specialist does, how it works, and what it must not do.
- Do not encode orchestration pipelines in agent definitions.
- Do not make one specialist depend on another specialist to be useful.
- Do not add transport-specific handoff protocols unless the agent's explicit purpose is orchestration.
- Prefer repository evidence over memory or generic stack assumptions.

## Tool and permission matrix

| Agent | OMP `tools` allowlist | Write/Edit | Bash | MCP/codebase | Git commit |
|---|---|---:|---:|---:|---:|
| `task-planner` | `read, search, find, lsp, ast_grep, web_search` | no | no | via read-only tools | no |
| `code-implementer` | `read, search, find, lsp, ast_grep, ast_edit, edit, write, bash, eval, debug` | production plus focused tests | targeted smoke/codegen/test commands | via tools | explicit authorization only |
| `test-engineer` | `read, search, find, lsp, ast_grep, ast_edit, edit, write, bash, eval, debug` | test assets only | test commands only | via tools | no |
| `code-reviewer` | `read, search, find, lsp, ast_grep, web_search` | no | no | via read-only tools | no |
| `deployment-operator` | `read, search, find, bash` | no | documented ops only | no | no |
| `spec-reviewer` | `read, search, find, lsp, ast_grep` | no | no | via read-only tools | no |
| `mavis` | Mavis Team Plan MCP tools only | no | no | no (Mavis MCP only) | no |

## Routing and workspace rules

- Oh My Pi discovers agents from `.omp`, `.claude`, `.codex`, and `.gemini`; `.omp` has highest precedence. Project `.omp/agents/` overrides user `~/.omp/agent/agents/` for the same agent name.
- Tasks that must change the caller's current workspace must not use worktree isolation. If worktree isolation is used, the handoff must report the workspace root and changed-file roots.
- Review handoffs must start with `PASS`, `FAIL`, or `BLOCKED: ...`. Missing verdict means the review gate is blocked, not passed or failed.
- `mavis` is a Team Plan operator. It must use Mavis MCP Team Plan tools rather than direct file edits, shell commands, or non-Team-Plan fallback paths.
- Mavis timeout or empty worker output does not prove no side effects occurred. Treat side effects as unknown until reconciled with plan/session evidence.
- Mavis verifier output is execution evidence, not an independent review gate.

Project memory is only a clue; any referenced file, command, function, or rule must be verified against the current repository.

## Deployment safety

`deployment-operator` may run documented read-only status checks when the request includes a clear target and runbook/script/CI source. Mutating deployment, release, rollback, or infrastructure actions require explicit current-session authorization plus the safety gates in the agent definition.

The operator must block rather than infer when approval gates, rollback procedure, environment, or documented command source are unclear.

## Oh My Pi runtime fields

Agent frontmatter keeps only fields Oh My Pi consumes: `name`, `description`, `model`, optional `thinkingLevel`, optional `tools`, and optional `spawns`. Unsupported Claude Code fields such as `disallowedTools`, `effort`, `permissionMode`, `memory`, `color`, `maxTurns`, and per-agent `hooks` are removed. Tool access is an allowlist, not a denylist.

## Adding a specialist agent

New specialists should use precise `description` routing and role-focused prompts. Add orchestration language only for agents whose explicit job is orchestration.

## Installation

```bash
# Copy selected agents to your user-level agents directory
mkdir -p ~/.omp/agent/agents
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/oh-my-pi/*.md ~/.omp/agent/agents/

# Or copy individual agents
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/oh-my-pi/task-planner.md ~/.omp/agent/agents/
```

## Relationship to other layers

- `global/standards/core-standard.md` — core verification and review gates.
- These agents do not replace global runtime principles; they provide opt-in specialists.


## Final handoff rules

- First line is `STATUS: ...`.
- Envelope attributes are only `agent`, `status`, `workspace`, and `artifact`.
- Final line is `<handoff-end ... />`.
- No text appears after the end marker.
- Workspace is observed absolute path, or `UNVERIFIED` with `BLOCKED`.
- Default artifact path is `$TMPDIR/omp-agent-artifacts/<agent>-*.md`.
- Project artifacts require explicit request and gitignored `.omp/agent-artifacts/`.

## Read-only artifact writes

Read-only agents do not include `write` or `bash` in their Oh My Pi tool allowlists. If a future read-only agent needs artifact files, add `write` explicitly and enforce destination safety with an Oh My Pi extension or hook before distribution.
