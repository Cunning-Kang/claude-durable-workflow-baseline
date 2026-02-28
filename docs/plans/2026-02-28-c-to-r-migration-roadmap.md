# C → R Migration Roadmap

- Date: 2026-02-28
- Last updated: 2026-02-28
- Status: Active — Phase 1 complete, Phase 2 partial
- Scope: Convention layer (C) to Runtime surface (R) migration strategy
- Depends-on: [Global v1 Architecture Design](./2026-02-28-global-v1-architecture-design.md)

---

## 1. Current State Snapshot

### Architecture: B + C + R

| Layer | File | Lines | Role | Status |
|-------|------|-------|------|--------|
| B | `~/.claude/standards/core-standard.md` | 291 | Always-on core | Stable |
| C | `~/.claude/guides/orchestration-extension.md` | **150** | On-demand orchestration guide | Active, 9 sections (2 migrated) |
| R | `~/.claude/agents/{orchestrator-planner,execution-implementer,mechanical-transformer}.md` | **44+41+40** | Self-routing subagents | Operational, enriched |
| Entry | `~/.claude/CLAUDE.md` | 6 | Thin entry | Stable |

### C Section Status

| § | Section | Lines | Content Type | Status |
|---|---------|-------|-------------|--------|
| 1 | Role of This Guide | 9 | Meta | Active |
| 2 | Consult Triggers | 12 | Routing judgment | Active — permanent C resident |
| 3 | Tier Intent | ~~44~~ → **3** | ~~Agent routing rules~~ → Pointer | **Migrated to R** |
| 4 | Escalation and Downgrade | ~~16~~ → **3** | ~~Decision heuristics~~ → Pointer | **Migrated to R** |
| 5 | Delegation Checklist | 20 | Decision gate | Active — permanent C resident |
| 6 | Parallelism and Fanout | 24 | Constraint rules | Active — next migration candidate |
| 7 | Recovery and Failure Handling | 30 | Error branching | Active — future migration candidate |
| 8 | Common Anti-Patterns | 12 | Educational | Active — permanent C resident |
| 9 | Migration Status | 10 | Migration log | Active |

---

## 2. First-Principles Analysis

### Why migrate C to R?

Four structural reasons, ordered by impact:

1. **Prose is probabilistic, runtime is deterministic.** An agent definition executes its constraints every time it runs. A guide section must be recalled by the model, read correctly, and applied under attention pressure. The more a rule matters, the less it should depend on recall.

2. **Context budget is finite.** Every line of C that loads into context competes with task-specific content. R mechanisms (agents, hooks) activate only when invoked, and their behavioral rules are scoped to the invocation.

3. **Composability.** Agents can be overridden per-project by placing a same-name file in `.claude/agents/`. Prose in a guide is harder to selectively override without forking the entire guide.

4. **Observability.** Agent routing is visible in tool call traces. Prose rule application is invisible — you cannot tell whether the model actually followed §6's fanout cap or ignored it.

### What makes a C rule "ready for R"?

A rule is ready when ALL four conditions hold:

1. **Stable** — applied consistently across 5+ tasks without reinterpretation.
2. **Mechanizable** — expressible as agent constraint, routing rule, or hook condition without losing critical nuance.
3. **Self-contained** — does not require cross-section reasoning to be correct.
4. **Failure-costly** — if the model forgets this rule, the outcome is materially worse.

### What should permanently remain in C?

Some content is inherently non-mechanizable:

- **Judgment heuristics** that require weighing multiple contextual factors (e.g., "is orchestration overhead worth it?")
- **Anti-pattern warnings** that are educational rather than enforceable
- **Novel situation guidance** that covers edge cases no agent prompt can anticipate
- **Meta-rules** about when to consult the guide itself

The target end state is **C ≈ 40-60 lines** of pure judgment guidance, not zero.

---

## 3. Migration Log

### Phase 1: Agent Self-Awareness + Escalation Embedding — COMPLETE

**Executed:** 2026-02-28

**What was migrated:**
- §3 Tier Intent → each agent now declares "Use this agent when", "Do not use this agent when", and cross-references to peer agents
- §4 Escalation/Downgrade → each agent now has a "Self-routing" section with explicit escalation/downgrade heuristics
- `execution-implementer` now declares "This is the default tier. When uncertain which agent to use, use this one."

**What was added to R:**

| Agent | New content |
|-------|-----------|
| `orchestrator-planner` | "Do not use when" guards, self-routing (downgrade to execution, collapse to inline, defer mechanical) |
| `execution-implementer` | Default-tier declaration, "Do not use when" guards, self-routing (escalate to orchestrator, downgrade to mechanical) |
| `mechanical-transformer` | Self-routing expanded to 3 explicit rules (escalate to execution, escalate to orchestrator, stop on ambiguity) |

**What was removed from C:**
- §3: 44 lines of tier descriptions → 3-line pointer to agent definitions
- §4: 16 lines of escalation rules → 3-line pointer to agent self-routing

**Result:** C 206 → 150 lines (−27%). Agent lines 33+33+38 → 44+41+40 (each still < 50).

**Pending verification:** Run 3-5 orchestration-heavy tasks in new sessions to confirm tier routing quality is same or better without C §3/§4 prose.

---

## 4. Remaining Migration Phases

### Phase 2 remainder: Fanout Constraint Embedding

**Goal:** Migrate §6 (Parallelism and Fanout) into `orchestrator-planner`.

**Current §6 content (24 lines):**
- Default fanout: 1 workstream
- Increase to 2: 4 conditions
- Exceptional 3+: 3 conditions
- Reduce triggers: 4 conditions
- Uncertainty default: stay serial

**Migration approach:**

Embed as a "Fanout constraints" section in `orchestrator-planner`:
```
Fanout constraints:
- Default: 1 active workstream.
- Increase to 2 only when workstreams are clearly independent, edit surfaces are unlikely to collide, merge order is simple, and review remains cheap.
- 3+ workstreams are exceptional — require clear decomposition, stable ownership, and easy-to-define integration.
- Reduce fanout immediately when files overlap, agents need repeated cross-coordination, integration becomes dominant cost, or review burden grows faster than throughput.
- If unsure, stay serial.
```

**Readiness assessment:**

| Condition | Status | Notes |
|-----------|--------|-------|
| Stable | Medium | Fanout rules have not been stress-tested in enough multi-agent tasks |
| Mechanizable | High | Rules are constraint-shaped, not judgment-shaped |
| Self-contained | High | No cross-section dependencies |
| Failure-costly | Medium | Over-constraining could reduce planning quality |

**When to execute:** When you have observed 3+ multi-agent orchestration tasks where fanout decisions were made. If all decisions aligned with §6 without needing reinterpretation, the rules are stable enough.

**Observation checklist before executing:**
- [ ] Observed fanout decision in task A: aligned / deviated?
- [ ] Observed fanout decision in task B: aligned / deviated?
- [ ] Observed fanout decision in task C: aligned / deviated?
- [ ] If all aligned → execute. If any deviated → analyze whether the rule or the deviation was correct, then decide.

**Risk:** If embedded rules prove too rigid, `orchestrator-planner` will over-constrain parallelism. Mitigation: keep a 2-line fallback in C ("For exceptional fanout situations, apply judgment over mechanical rules.").

---

### Phase 3: Recovery Embedding

**Goal:** Migrate §7 (Recovery and Failure Handling) into R.

**Prerequisite:** Phase 2 complete and verified.

**Current §7 content (30 lines):**
- Tool/agent failure: 3-step recovery (already in B as tool failure rule)
- Low-confidence output: narrow → reduce → raise tier → clarify
- Integration failure: stop fanout → collapse to serial → re-sequence
- Context pressure: stop workstreams → bounded delegation → protect scope

**Migration approach:**

Embed low-confidence, integration failure, and context pressure handling into `orchestrator-planner` as a "Recovery" section. Tool failure stays in B (no duplication).

**Readiness assessment:**

| Condition | Status | Notes |
|-----------|--------|-------|
| Stable | Medium | Recovery paths rarely triggered — insufficient observation data |
| Mechanizable | Medium | Context pressure detection is inherently subjective |
| Self-contained | High | Each recovery path is independent |
| Failure-costly | High | Wrong recovery → cascading failure or wasted work |

**When to execute:** When you have observed 2+ real recovery situations (agent failure, low-confidence output, or integration failure) and the §7 rules were followed correctly. If recovery was handled well with the prose rules, they are stable enough to embed.

**Observation checklist before executing:**
- [ ] Observed recovery situation A: §7 followed? outcome?
- [ ] Observed recovery situation B: §7 followed? outcome?
- [ ] If both followed with good outcomes → execute. If not → analyze what went wrong.

**Risk:** Context pressure detection is the hardest to mechanize. Consider keeping context pressure as a 2-line C residual even after migrating the other three recovery paths.

---

### Phase 4: C Convergence

**Goal:** C reaches its steady-state form (~40-60 lines).

**Prerequisite:** Phases 2-3 complete and verified.

**Projected residual C content:**

```
§1  Role of This Guide           — 3-4 lines (reduced meta)
§2  Consult Triggers             — 8-10 lines (unchanged, judgment-dependent)
§5  Delegation Checklist         — 10-12 lines (unchanged, judgment-dependent)
§8  Common Anti-Patterns         — 10-12 lines (unchanged, educational)
§9  Migration Status             — 5-8 lines (final log)
```

**Estimated: ~40-50 lines**, down from 206.

**Verification:** New session test — run a full L2 orchestration task with only B + reduced-C + enriched-R. Confirm no regression in routing, delegation, escalation, recovery, or fanout quality.

---

## 5. Observation Metrics

### 5.1 Post-Migration Regression Signals

Monitor these in every session. If detected, consider reverting the relevant migration:

| Signal | Indicates | Severity | Action |
|--------|-----------|----------|--------|
| Wrong agent tier selected for a task | Tier intent migration (§3) incomplete | High | Review agent "Use when" / "Do not use when" clauses. If pattern is systematic, restore §3 in C. |
| Escalation/downgrade not happening when it should | Self-routing rules (§4) insufficient | High | Review agent "Self-routing" sections. Add missing trigger or restore §4 in C. |
| Agent prompts becoming > 60 lines | Over-embedding; agents losing focus | Medium | Extract lowest-value rules back to C or consider creating a specialized agent. |
| Novel orchestration situations handled worse than before | C judgment guidance was needed | Medium | Restore relevant C section. Document why it resisted migration. |

### 5.2 Future Migration Trigger Signals

These indicate a remaining C rule is ready for migration:

| Signal | Target | Action |
|--------|--------|--------|
| Fanout decisions consistently match §6 across 3+ tasks | §6 → R | Execute Phase 2 remainder |
| Recovery paths followed correctly in 2+ failure situations | §7 → R | Execute Phase 3 |
| C consulted but not changing the decision | Any remaining § | Evaluate for migration |

### 5.3 Health Metrics

Track after each significant orchestration task:

| Metric | Current Value | Healthy Range | Alert |
|--------|---------------|---------------|-------|
| C line count | **150** | Decreasing toward 40-50 | > 160 = drift |
| orchestrator-planner lines | **44** | 30-60 | > 60 = over-embedded |
| execution-implementer lines | **41** | 30-60 | > 60 = over-embedded |
| mechanical-transformer lines | **40** | 30-50 | > 50 = scope creep |
| Tier routing accuracy | Pending verification | Same or better than pre-migration | Any regression |

---

## 6. Decision Framework

When evaluating whether to migrate a specific rule:

```
Is the rule stable across 5+ tasks?
├── No  → Keep in C. Revisit after more usage.
└── Yes
    Can it be expressed as agent constraint without losing critical nuance?
    ├── No  → Keep in C permanently (judgment/educational content).
    └── Yes
        Is failure to follow this rule costly?
        ├── No  → Low priority. Migrate when convenient.
        └── Yes → High priority. Migrate in next phase.
```

---

## 7. End-State Architecture

```
B (core-standard.md)        ~290 lines   Always-on. Stable.
C (orchestration-extension)  ~40-50 lines On-demand. Pure judgment.
R (agents/)                  ~50-70 each  Runtime. Self-routing, self-recovering.
```

The system's effective governance becomes **B + R** for routine work, with **C** consulted only for genuinely ambiguous orchestration decisions. This matches the architecture design's stated long-term direction:

> "The likely end state is a system where the effective architecture is mostly B + R, with C remaining as a small judgment guide rather than a large policy layer."

---

## 8. Non-Goals

- **Zero C is not a goal.** Judgment guidance that resists mechanization should stay as prose. Forcing it into agent prompts would degrade quality.
- **Agent proliferation is not a goal.** Do not create new agents just to absorb C rules. Prefer enriching existing agents.
- **Automation of migration itself is not a goal.** Each migration phase requires human judgment about stability and quality. The decision to migrate is manual.

---

## 9. Recommendations

### Immediate (next 1-3 sessions)

1. **Verify Phase 1 in real tasks.** Pick 2-3 naturally occurring L1/L2 tasks and observe whether agent routing is correct without C §3/§4 prose. Record observations.
2. **Do not rush Phase 2 remainder.** Fanout constraints have not been stress-tested. Premature embedding risks over-constraining the planner.

### Medium-term (after 5+ orchestration tasks)

3. **Evaluate §6 readiness** using the observation checklist in Phase 2 remainder. Execute only when 3+ tasks show consistent alignment.
4. **Watch for agent bloat.** If any agent approaches 60 lines, stop embedding and re-evaluate. The agents' strength is focus, not completeness.

### Long-term

5. **Consider hooks as an R mechanism.** Claude Code hooks (pre-tool, post-tool) could enforce some constraints more reliably than agent prompts. For example, a fanout cap could theoretically be enforced via a hook that rejects Task tool calls above a threshold. This is speculative but worth investigating when the hook system matures.
6. **Monitor Claude Code platform evolution.** If the platform adds native agent routing configuration, tier constraints, or delegation policies, those would supersede the current agent-prompt-based R layer. Track platform releases for relevant features.
7. **C should never grow.** If you find yourself adding new prose to C, ask whether it belongs in B (if always-on) or R (if mechanizable). C is a holding area for judgment guidance, not a dumping ground.

---

## 10. Execution Notes

- Each phase should be a separate session or branch.
- Verify before and after each phase with a real orchestration task, not synthetic tests.
- If a phase causes regression, revert and add the problematic rule back to C with a note about why it resisted migration.
- This roadmap is a reference document. It does not prescribe timing. Migration should happen when evidence supports it, not on a schedule.
