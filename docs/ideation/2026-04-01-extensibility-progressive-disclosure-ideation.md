---
date: 2026-04-01
topic: extensibility-progressive-disclosure
focus: Optimize orchestration-extension.md for future agent extensibility and review-workflow.md progressive disclosure for Sonnet/Haiku adherence
---

# Ideation: Orchestration Extensibility + Review Progressive Disclosure

## Codebase Context

**Project shape**: Baseline source repo distributing durable workflow assets to `~/.claude/`. Not a runtime engine.

**Key files**:
- `global/CLAUDE.md` — 6-line entry point with `@` imports
- `global/standards/core-standard.md` — 169-line core standard, §6 references review-workflow.md
- `global/guides/orchestration-extension.md` — 131-line orchestration decision guide (agent-name-agnostic)
- `global/rules/review-workflow.md` — 31-line review gate mechanics
- `~/.claude/agents/` — 5 agent definitions (3 core + 2 orphaned)

**Grounding research**:
- orchestration-extension.md is already agent-name-agnostic (no hardcoded names)
- Real coupling: agent definitions' self-routing sections reference peers by name (O(n) edits per new agent)
- 2 agents (technical-writer, product-manager) lack self-routing sections entirely
- Claude Code official best practice: CLAUDE.md < 200 lines, concrete verifiable rules, `alwaysApply` for critical rules
- Review-workflow.md is 31 lines (well under bloat threshold), but hidden behind 3-level reference chain
- `taskcompleted-review-evidence-gate` hook exists as programmatic enforcement (opt-in)

## Critical Pre-Condition Discovered by Opus Review

### README Distribution Contradictions (BLOCKER)

`global/README.md` has **three layered problems** that undermine both proposals:

1. **Content declaration contradiction**: v1 contents lists `rules/review-workflow.md`, but later says distribution is "intentionally limited to `CLAUDE.md`, `standards/`, and `guides/`" — excluding `rules/`.

2. **Install command likely broken**: `cp -n global/* ~/.claude/` without `-r` flag may not correctly copy `standards/`, `guides/`, `rules/` directories.

3. **Loading description contradicts alwaysApply intent**: Says "Supplemental workflow rules loaded on-demand by reference" — would need updating if rules become always-applied.

**Impact**: If `rules/` isn't reliably installed, 2A's `alwaysApply` change never reaches the target. This is a **distribution chain integrity issue**, not just a documentation problem.

**Required action**: Fix README distribution model and install command BEFORE implementing 2A.

## Architectural Decision: Agent Distribution Model

**Decision**: Agent definitions will be placed in `distribution/agents/` (opt-in, source-only), following the existing pattern of `distribution/hooks/` and `distribution/settings-snippets/`.

**Rationale**:
- Version-controlled and distributable, but NOT auto-installed
- Users manually copy needed agents to `~/.claude/agents/`
- Does not violate superpowers-boundary.md §3.2 (not auto-distributed, not a competing control layer)
- Follows established repo pattern for opt-in distribution artifacts

**Implications**:
- Proposal 1 now edits files in `distribution/agents/` (repo source), not `~/.claude/agents/` (deployed copies)
- Requires a `distribution/agents/README.md` explaining installation and purpose
- Install command: `cp ~/.claude/baselines/durable-workflow-v1/distribution/agents/*.md ~/.claude/agents/`

## Final Ranked Ideas (Post Opus Review)

### P0. Fix README Distribution Chain Integrity [NEW — Opus Review]

**Description**: Fix `global/README.md` to:
- Resolve the `rules/` inclusion/exclusion contradiction with a single consistent answer
- Fix install command to correctly copy directories (add `-r` flag)
- Update loading description from "on-demand by reference" to reflect actual behavior
- Acknowledge `distribution/agents/` as a new opt-in distribution surface
- Treat this as a blocker for 2A

**Rationale**: Opus reviewer identified this as a potentially higher-priority issue than the proposals themselves. If the distribution chain is broken, any changes to rule loading behavior are theoretical.

**Confidence**: 95%
**Complexity**: Low
**Status**: Unexplored

---

### 1. Two-Tier Agent Routing Protocol [APPROVED WITH MODIFICATIONS — Opus Review + Routing Protocol Decision]

**Description**:
- Create `distribution/agents/` with all 5 agent definitions (migrated from `~/.claude/agents/`)
- Implement **two-tier routing protocol** across all agents:

  **Tier 1 — Core chain (name-based, stable):**
  - `orchestrator-planner` → `execution-implementer` → `mechanical-transformer`
  - These 3 use exact name references (reliable, explicit)
  - Self-routing in core agents retains name-based peer references for this chain only

  **Tier 2 — Generic escalation (description-based, future-extensible):**
  - All agents share a universal fallback: "If task is outside your scope, return to main thread with a clear capability description of what's needed. The main thread will match to an appropriate agent via description-based routing."
  - Domain agents (technical-writer, product-manager) and all FUTURE agents route via Tier 2
  - No agent names specific peers beyond the core chain
  - New agents need zero changes to existing files — just good `description` frontmatter

- **Unify agent naming**: resolve frontmatter `name` inconsistency (core agents use kebab-case; domain agents use Title Case → standardize to kebab-case)
- Add `distribution/agents/README.md` explaining installation, purpose, and routing protocol
- Do NOT modify orchestration-extension.md

**Self-routing template for each agent type:**

```markdown
# Core agents (Tier 1 + Tier 2):
Self-routing:
- [Specific core-chain routing with exact names, e.g.:
  "If execution path is clear, recommend `execution-implementer`"]
- For tasks outside core execution scope: return to main thread
  with capability description (Tier 2).

# Domain/future agents (Tier 2 only):
Self-routing:
- If task requires capabilities beyond your domain, return to main thread
  with: (a) what was attempted, (b) what capability is needed, (c) why
  you cannot complete it.
- If task is within domain but needs implementation, return to main thread
  with implementation request.
- Do not attempt execution outside your domain authority.
```

**Extensibility guarantee**: Adding a new agent only requires:
1. Create file with precise `description` frontmatter
2. Write Tier 2 self-routing (generic, no peer names)
3. Done — no edits to existing agents needed

**Rationale**:
- Root cause: domain agents lack routing discipline, not architecture gap
- Opus reviewer: "只写边界不写去向 = 只会说不，不会回到正确轨道"
- Opus reviewer: agent naming inconsistency between core (kebab-case) and domain (Title Case) creates routing text ambiguity
- The generic "delegate rather than attempt inline" is too abstract for Sonnet/Haiku
- Placing agents in `distribution/` (opt-in) keeps them version-controlled without violating superpowers boundary

**Required modifications from Opus review + routing protocol decision**:
1. Core agent routing text must be **operational** (specify what constitutes domain-specialist tasks, how to identify them, what to delegate)
2. Domain agent self-routing uses **Tier 2 generic escalation** (return to main thread with capability description, not peer names)
3. **Unify agent naming convention** across all 5 agents (standardize to kebab-case)
4. Agent distribution follows opt-in model (not auto-installed)
5. **Two-tier routing protocol**: core chain uses exact names; all other routing is description-based via main thread

**Confidence**: 85%
**Complexity**: Medium
**Status**: Unexplored

---

### 2A. Always-Apply Review Rule [APPROVED WITH MODIFICATIONS — Opus Review]

**Description**:
- Add YAML frontmatter `alwaysApply: true` to review-workflow.md
- Update header: remove "load when review gate is triggered", clarify new role as "常驻 review gate 操作语义" (not "on-demand supplement")
- Update global/README.md to reflect: (a) `rules/` is part of distribution, (b) loading is always-apply, (c) fix install command

**Rationale**:
- 31 lines is well under bloat threshold
- Eliminates reference-chain adherence problem
- Claude Code's `alwaysApply` is the official mechanism for critical rules
- Opus reviewer: "当前三案里逻辑链最完整、最强方案"

**Required modifications from Opus review**:
1. **Fix README first** (see P0) — this is a blocker, not optional cleanup
2. Clarify architectural role change: review-workflow is NOT an "on-demand supplement" anymore, it's **常驻核心规则的一部分**
3. Do NOT claim "根因已证实" — 2A is "高度合理" but evidence of Sonnet/Haiku failure is anecdotal, not measured
4. Add minimum validation plan: given a task requiring review gate, does model stably output `BLOCKED`? Does it avoid writing `review: PASS` without `Reviewer`/`Reference`?

**Confidence**: 90%
**Complexity**: Low (but P0 is prerequisite)
**Status**: Unexplored

---

### 2B. Inline Minimum Critical Rules [REJECTED — Opus Review]

**Description**: Originally conditional follow-up — inline status table into core-standard.md §6.

**Opus review verdict**: **REJECT**

**Reasons**:
- Trigger conditions undefined — "if 2A fails" is vague, not a plan
- Dual-source maintenance risk is real and not mitigated by maintenance notes
- Contradicts core-standard.md's own "one authoritative task state" principle
- If 2A fails, root cause may not be visibility (could be execution discipline, template weight, calling flow)
- Premature architectural pollution

**Resolution**: Removed from final plan. If future evidence warrants, must be re-proposed with:
1. Clear failure threshold
2. Failure sample definition
3. Validation methodology
4. Priority consideration for single-source generation over manual dual-write

**Confidence**: 0% (overridden by Opus review)
**Status**: Rejected

---

## Rejection Summary

| # | Idea | Reason Rejected | Rejected By |
|---|------|-----------------|-------------|
| 1 | Agent Registry File | Over-engineering for current scale | Round 1 |
| 2 | Capability-Tag Routing | No built-in capability matching in Claude Code | Round 1 |
| 3 | Pure Capability Declarations | Cannot remove self-routing from agent prompts | Round 1 |
| 4 | Dynamic Routing from Guide | Too abstract; contradicts guide design | Round 1 |
| 5 | Tier Fallback Manifest | Duplicates registry concept | Round 1 |
| 6 | Routing Integration Test | Orthogonal; post-hoc detection | Round 1 |
| 7 | Templated Agent Definition | Doesn't solve coupling | Round 1 |
| 8 | Agent Group Namespaces | Over-engineered for 5-8 agents | Round 1 |
| 9 | Path-Scoped Review Loading | Wrong direction; makes rule less available | Round 1 |
| 10 | Model-Tier-Tagged Instructions | Model identity detection unreliable | Round 1 |
| 11 | Hook Enforcement Promotion | User asked about progressive disclosure, not hooks | Round 1 |
| 12 | Completion Contract Reinforcement | Symptom-level fix; template fatigue risk | Round 2 |
| 13 | Orchestration Extension Discovery | Contradicts guide's own design | Round 2 |
| 14 | Inline Minimum Critical Rules (2B) | No trigger threshold; dual-source drift; contradicts repo principles | Round 3 (Opus) |

## Review History

### Round 1: Divergent Ideation + Adversarial Filtering
- 16 candidates generated, 3 survived

### Round 2: Independent Adversarial Review (general-purpose agent)
- Proposal 3 rejected (completion contract reinforcement)
- Proposals 1-2 modified
- Split Proposal 2 into 2A (proceed) + 2B (conditional follow-up)

### Round 3: Opus Independent Strict Review
**Key findings not caught in earlier rounds**:
1. **README distribution contradictions** — rules/ inclusion/exclusion conflict, broken install command, loading description inconsistency. Elevated to blocker (P0).
2. **Agent naming inconsistency** — core agents use kebab-case, domain agents use Title Case in frontmatter. Creates routing text ambiguity.
3. **"不做 bidirectional routing" claim is misleading** — adding generic delegation text to core agents IS weak directional core→domain routing. Should be acknowledged honestly.
4. **Domain agent self-routing must include outbound destinations** — not just boundary refusal.
5. **Core agent delegation text must be operational** — "delegate rather than attempt inline" is too abstract for Sonnet/Haiku.
6. **2A is "highly reasonable" but root cause is not confirmed** — anecdotal evidence only, no measurement plan.
7. **2B rejected** — removed from plan; trigger conditions undefined; dual-source risk real.

## Recommended Execution Order (Opus Review)

1. **P0**: Fix README distribution chain (blocker for everything else)
2. **2A**: Implement always-apply review rule (highest value, lowest risk)
3. **1**: Implement domain agent routing contract (after naming unification)

## Session Log
- 2026-04-01: Initial ideation — 16 candidates generated, 3 survived adversarial review
- 2026-04-01: Independent adversarial review (R2) — Proposal 3 rejected, Proposals 1-2 modified, split 2 into 2A+2B
- 2026-04-01: Opus independent strict review (R3) — 2B rejected; P0 (README fix) elevated to blocker; Proposal 1 modified with naming/routing contract requirements; Proposal 2A modified with README prerequisite and validation plan; 14 ideas total rejected
- 2026-04-01: User architectural decision — agents go to `distribution/agents/` (opt-in, not auto-installed), following existing hooks/settings-snippets pattern
- 2026-04-01: User routing protocol decision — two-tier routing (core chain name-based + generic description-based escalation). New agents need zero changes to existing files. Proposal 1 upgraded to "Two-Tier Agent Routing Protocol"
