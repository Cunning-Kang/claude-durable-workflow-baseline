# Custom Subagent Definitions

Source-only, opt-in agent definitions for Claude Code. Not auto-installed.

## What this is

Reusable, version-controlled subagent definitions that users can adopt by copying to `~/.claude/agents/`. Follows the same distribution pattern as `distribution/hooks/` and `distribution/settings-snippets/`.

## Two-Tier Routing Protocol

All agents in this directory follow a two-tier routing protocol:

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

## Adding a New Agent

1. Create a new `.md` file in this directory
2. Set frontmatter: `name` (kebab-case), `description` (precise capability statement), `tools`, `model`, `effort`
3. Write the agent body with role definition, explicit non-goals, and a return protocol
4. Done — no edits to existing agents needed

## Installation

```bash
# Copy selected agents to your user-level agents directory
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/*.md ~/.claude/agents/

# Or copy individual agents
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/orchestrator-planner.md ~/.claude/agents/
```

## Agent Inventory

| Agent | Model | Effort | Role | Routing Tier |
|-------|-------|--------|------|-------------|
| `orchestrator-planner` | opus | high | Resolve blocking uncertainty before execution | Tier 1 (core chain) |
| `execution-implementer` | sonnet | high | Bounded implementation, debugging, test repair | Tier 1 (core chain) |
| `mechanical-transformer` | haiku | high | Deterministic mechanical rewrites | Tier 1 (core chain) |
| `technical-writer` | haiku | high | Technical documentation and developer content | Tier 2 (domain specialist) |
| `product-manager` | opus | high | Product strategy and requirements | Tier 2 (domain specialist) |
| `docker-expert` | sonnet | high | Production Docker images and orchestration | Tier 2 (domain specialist) |

## Relationship to Other Layers

- `global/guides/orchestration-extension.md` — orchestration decision guide (agent-name-agnostic)
- `global/standards/core-standard.md` — core verification and review gates
- These agents do not replace built-in subagents; they supplement them for specialized workflows
- Superpowers is the primary behavior control layer; these agents are opt-in tooling
