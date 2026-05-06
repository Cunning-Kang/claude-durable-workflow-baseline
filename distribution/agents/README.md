# Custom Subagent Definitions

Source-only, opt-in agent definitions for Claude Code. Not auto-installed.

## What this is

Reusable, version-controlled subagent definitions that users can adopt by copying to `~/.claude/agents/`. Follows the same distribution pattern as `distribution/hooks/` and `distribution/settings-snippets/`.

## Official-compatible frontmatter fields

Each agent file uses this frontmatter structure:

```yaml
---
name: <kebab-case-name>
description: <concise trigger-oriented description>
model: <inherit|haiku|sonnet|opus>
color: <optional-ui-color>
tools:
  - Read
  - Grep
  - Glob
---
```

Required: `name`, `description`.
Optional: `model`, `color`, `tools`.

Tool policy — least privilege per role:
- Analysis/review/planning agents: read-only unless their core deliverable requires edits.
- Implementation agents: may include `Edit`, `Write`, `Bash` when explicitly responsible for code changes and verification.
- Web tools (`WebSearch`, `WebFetch`) only for roles that genuinely need external research (e.g. technical writing, product management).

## Two-Tier Routing Protocol

All agents in this directory follow a two-tier routing protocol.

### Tier 1 — Core Execution Chain (name-based)

The three core agents form a stable delegation chain with exact name references:

```
orchestrator-planner → execution-implementer → mechanical-transformer
```

These agents use explicit `subagent_type` references for reliable handoffs within the chain.

### Tier 2 — Generic Escalation (description-based)

All agents share a universal return protocol for handing off when their task boundary is reached:

> Return to the main thread with: (1) what was completed, (2) what capability is needed next — specify the agent name if known, or describe the domain capability needed, (3) why this agent cannot resolve the remainder. Do not attempt to invoke other agents directly.

New agents only need a precise `description` frontmatter and a return protocol — no edits to existing agent files required.

## Agent Inventory

| Agent | Model | Role | Routing Tier |
|-------|-------|------|-------------|
| `orchestrator-planner` | opus | Resolve blocking uncertainty before execution | Tier 1 (core chain) |
| `execution-implementer` | sonnet | Bounded implementation, debugging, test repair | Tier 1 (core chain) |
| `mechanical-transformer` | haiku | Deterministic mechanical rewrites | Tier 1 (core chain) |
| `technical-writer` | haiku | Technical documentation and developer content | Tier 2 (domain specialist) |
| `product-manager` | opus | Product strategy and requirements | Tier 2 (domain specialist) |
| `docker-expert` | sonnet | Production Docker images and orchestration | Tier 2 (domain specialist) |
| `code-reviewer` | haiku | Code quality, security, and pattern review | Tier 2 (domain specialist) |
| `deployment-engineer` | sonnet | Blue-green, canary, rolling deployments | Tier 2 (domain specialist) |
| `fullstack-developer` | sonnet | End-to-end feature across DB, API, and frontend | Tier 2 (domain specialist) |
| `project-planner` | opus | Project plans, WBS, effort estimation | Tier 2 (domain specialist) |
| `qa-automation` | haiku | Test automation frameworks and CI integration | Tier 2 (domain specialist) |

## Adding a New Agent

1. Create a new `.md` file in this directory
2. Set frontmatter: `name` (kebab-case), `description` (precise capability statement), `model`, `color` (optional), `tools` (YAML array, least privilege)
3. Write the agent body with: role definition, use cases, explicit non-goals, output expectations, and a Return Protocol
4. Done — no edits to existing agents needed

## Agent body minimum structure

Every agent body should include:

- **Exact role** — what this agent does and does not do
- **Use cases** — when to invoke this agent
- **Explicit non-goals** — what this agent should never handle
- **Output expectations** — what the agent produces and returns
- **Return Protocol** — return to the main thread with handoff recommendation; never invoke another subagent directly

## Installation

```bash
# Copy selected agents to your user-level agents directory
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/*.md ~/.claude/agents/

# Or copy individual agents
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/orchestrator-planner.md ~/.claude/agents/
```

## Relationship to Other Layers

- `global/guides/orchestration-extension.md` — orchestration decision guide (agent-name-agnostic)
- `global/standards/core-standard.md` — core verification and review gates
- These agents do not replace built-in subagents; they supplement them for specialized workflows
- Superpowers is the primary behavior control layer; these agents are opt-in tooling
- Routing is always via the main thread — subagents return handoff recommendations only, never delegate directly to other subagents