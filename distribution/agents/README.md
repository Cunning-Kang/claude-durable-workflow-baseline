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

All agents share a universal fallback for routing outside their scope:

> If a task is outside your scope, return to the main thread with: (a) what was attempted, (b) what capability is needed, (c) why you cannot complete it. The main thread will match to an appropriate agent via description-based routing.

New agents only need a precise `description` frontmatter and Tier 2 self-routing — no edits to existing agent files required.

## Adding a New Agent

1. Create a new `.md` file in this directory
2. Set frontmatter: `name` (kebab-case), `description` (precise capability statement), `tools`, `model`
3. Write the agent body with role definition, explicit non-goals, and Tier 2 self-routing
4. Done — no edits to existing agents needed

## Installation

```bash
# Copy selected agents to your user-level agents directory
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/*.md ~/.claude/agents/

# Or copy individual agents
cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/orchestrator-planner.md ~/.claude/agents/
```

## Agent Inventory

| Agent | Model | Role | Routing Tier |
|-------|-------|------|-------------|
| `orchestrator-planner` | opus | Resolve blocking uncertainty before execution | Tier 1 (core chain) |
| `execution-implementer` | sonnet | Bounded implementation, debugging, test repair | Tier 1 (core chain) |
| `mechanical-transformer` | haiku | Deterministic mechanical rewrites | Tier 1 (core chain) |
| `technical-writer` | sonnet | Technical documentation and developer content | Tier 2 (domain specialist) |
| `product-manager` | opus | Product strategy and requirements | Tier 2 (domain specialist) |

## Relationship to Other Layers

- `global/guides/orchestration-extension.md` — orchestration decision guide (agent-name-agnostic)
- `global/standards/core-standard.md` — core verification and review gates
- These agents do not replace built-in subagents; they supplement them for specialized workflows
- Superpowers is the primary behavior control layer; these agents are opt-in tooling
