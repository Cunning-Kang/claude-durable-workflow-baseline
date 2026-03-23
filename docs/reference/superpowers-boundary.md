# Superpowers Boundary — Repository Role Definition

> Status: Phase 1 Boundary Anchor | Date: 2026-03-22
> Purpose: Define what this baseline repo is, what it is not, and why it cannot compete with Superpowers.

---

## 1. Repository Positioning

### What this repo is

- A **baseline source repo** and **distribution source** for durable workflow assets
- A single source of truth for `baseline/` skeletons, spec templates, and memory structures
- The distribution point for `/init-claude-workflow` and `/new-feature` command content plus bootstrap scripts
- A thin, portable `global/` layer that seeds user-level runtime surfaces

### What this repo is not

- **Not a plugin runtime** — this repo does not execute; it distributes
- **Not a feature state repository** — it does not track project progress
- **Not a project memory repository** — it provides the memory skeleton, not the memory content
- **Not an orchestration engine** — it has no behavior control surface
- **Not an auto-upgrade system** — upgrades require manual `git pull`

---

## 2. Superpowers vs. This Repository — Responsibility Boundary

### Superpowers: The Control Layer

Superpowers owns the **primary behavior control layer**. This means:

- All skill entry points (`/brainstorming`, `/writing-plans`, `/test-driven-development`, `/verification-before-completion`, `/finish-branch`, `/memory-reflection`)
- Task orchestration and execution state
- Agent spawning and routing decisions
- Any generic workflow automation skill that directs agent behavior

### This Repo: The Knowledge Layer

This repo provides **durable knowledge assets** that Superpowers cannot own — the reproducible, project-agnostic "memory skeleton" that survives across sessions:

- `baseline/` — repo initialization artifacts
- `docs/specs/_template/` — durable spec structures
- `docs/workflow/` — execution protocols (review, memory, execution contracts)
- `memory/` — project memory skeletons (patterns, gotchas)
- `global/` — thin portable runtime surface entries (not control logic)

**The boundary rule**: This repo's assets must never be interpreted as a second control layer. They are passive knowledge structures consumed by Superpowers, not a competing behavior engine.

---

## 3. Forbidden Capability Types

The following categories of capabilities must never be added to this repo or preserved if they exist:

### 3.1 Generic Workflow Control Skills

Any skill, command, or script that directs agent behavior toward a goal (planning, execution, review, memory) **competes with Superpowers**.

Examples of forbidden additions:
- A `/plan` or `/execute` skill in this repo
- Any hook or script that infers next steps
- Any automation that modifies task state or routes agents

### 3.2 Competing Orchestration Logic

Any file that attempts to own:
- Agent spawning or routing rules
- Task queue management
- Execution ordering dependencies
- Workflow graph construction

### 3.3 Project-Specific Memory or State

This repo must not contain:
- Filled-in project memory content (belongs in the project repo)
- Task state files with actual progress (belongs in the project repo)
- Feature instances — only templates belong here

---

## 4. Hooks and Settings Snippets — Scope Principles

Hooks distributed from this repo follow a strict three-layer scope:

| Layer | Description | Distribution |
|-------|-------------|--------------|
| `user` | User-level hooks (run at user home `~/.claude/hooks/`) | Source only, copy manually |
| `project` | Project-specific hooks (distributed via `baseline/` in target repos) | Copied by `/init-claude-workflow` |
| `local example only` | Reference implementations in `global/skills/` | NOT installed automatically; user copies what they need |

### Core principle

Hooks are **distribution snippets**, not global automation. They must never be installed automatically into a user's `~/.claude/` in a way that overrides or shadows Superpowers behavior.

- No hook may register a competing skill entry point
- No hook may redirect the primary control flow
- No automatic global installation of project-level hooks

---

## 5. Where Documentation and Audit Assets Belong

### Reference Documentation — `docs/reference/`

Descriptive boundary and protocol documents live here:
- This file (`superpowers-boundary.md`) — role and boundary definition
- Any protocol-oriented reference docs (not audit reports)

### Audit Documentation — `docs/audits/`

Audit reports and retrospective analyses live here:
- Canonical audit path: `docs/audits/2026-03-22-production-baseline-audit-and-refactor-plan.md`
- `docs/plan/` is no longer an active directory after Phase 1 migration

### What stays out of this repo

- Filled-in project memory (project repo)
- Feature spec instances (project repo)
- Task state (project repo)
- Context-mode MCP tool configurations (belong to the main project, not the baseline)

---

## 6. Maintenance Checklist

Use this checklist before accepting any new asset into this repo:

- [ ] **Does it own or direct behavior?** If yes — reject; belongs in Superpowers.
- [ ] **Does it compete with an existing Superpowers skill?** If yes — reject.
- [ ] **Is it project-agnostic and passive (a skeleton, template, or protocol)?** If yes — eligible.
- [ ] **Does it require global runtime installation hooks?** If yes — verify scope (user/project/local-only).
- [ ] **Is it a filled-in project artifact (memory content, spec instance, task state)?** If yes — reject; belongs in the project repo.
- [ ] **Does it modify `~/.claude/settings.json` env configuration?** If yes — do not add.
- [ ] **Is it a new automation control layer or orchestration skill?** If yes — reject.

---

## References

- D-001: Superpowers is the control layer; this repo must not rebuild parallel workflow control
- D-002: Baseline repo does not provide competing generic workflow skills
- D-003: Hooks must be layered as user / project / local example only, distributed as source/snippets
- D-006: Descriptive boundary docs belong in `docs/reference/`
- D-008: Canonical audit path is `docs/audits/2026-03-22-production-baseline-audit-and-refactor-plan.md`
- R-001: Primary risk is role conflict with Superpowers
- R-002: Secondary risk is hooks mis-globalization
