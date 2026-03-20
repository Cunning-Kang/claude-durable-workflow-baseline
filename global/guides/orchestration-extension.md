# Orchestration Extension

> Global on-demand extension for orchestration-heavy work
> Scope: expand the core standard only when delegation, fanout, reconciliation, or execution ordering materially affects execution
> POLICY_PRECEDENCE: global-core > this-extension

---

## 1. Role of This Guide

This guide expands the compact execution defaults in `~/.claude/standards/core-standard.md`.

Use this guide only when deciding whether orchestration is justified. Consulting this guide does not itself justify delegation, parallelism, or planner use.

Do not consult this guide merely because a task is L2, large, multi-file, or architecture-adjacent.

**This is an on-demand extension, not a second always-on standard.**

---

## 2. Default Execution Path

Prefer the simplest workable path:

1. do trivial local work inline,
2. prefer `execution-implementer` as the typical path for bounded non-trivial execution,
3. use `mechanical-transformer` only for explicit deterministic rewrites,
4. use `orchestrator-planner` only when bounded execution cannot safely start without first resolving approach, decomposition, reconciliation, or ordering.

This guide does not override built-in routing or a more fitting configured custom subagent.
Task level alone is not a routing signal.

---

## 3. Consult Triggers

Consult this guide when one or more of the following is true:

- more than one subtask or subagent may be required before execution can safely begin,
- outputs from multiple workstreams may need reconciliation before execution can proceed,
- execution ordering or dependency sequencing may materially affect correctness,
- bounded execution may not yet be safe to start.

Skip this guide for trivial local work that is clearly better done inline.

---

## 4. Agent Intent

Agent intent for the user-level custom subagents in `~/.claude/agents/` is encoded in those definitions.
This guide supplements Claude Code's built-in behavior and configured custom subagents; it does not replace them or redefine runtime precedence.

The routing system is intentionally asymmetric:
- `execution-implementer` is the typical user-level path for bounded non-trivial execution,
- `mechanical-transformer` is a narrow fast path for explicit rewrite-rule work,
- `orchestrator-planner` is an exception layer for blocking orchestration problems.

---

## 5. Escalation and Downgrade Rules

Escalation and downgrade heuristics are embedded in each agent's self-routing rules in `~/.claude/agents/`. When escalating or downgrading, record a brief reason. One sentence is enough if it is specific.

Good reasons to escalate to `orchestrator-planner`:
- multiple viable approaches remain and the trade-off materially affects execution,
- the task boundary cannot yet be stabilized,
- reconciliation across outputs is required before safe execution,
- dependency ordering is itself the blocking problem.

Bad reasons to escalate:
- the task is merely large,
- the task touches multiple files,
- the task is architecture-adjacent but already bounded,
- the task modifies an already-specified shared interface.

Downgrade as soon as a simpler path becomes valid.

---

## 6. Delegation Checklist

Delegate only when the subtask is:
- **bounded** - scope is defined before delegation starts,
- **independent** - it can complete without constant orchestration,
- **recoverable** - failure does not destroy the main plan,
- **worth the overhead** - coordination cost is lower than inline cost.

Do not delegate when:
- the work includes a high-risk operation as defined in `~/.claude/standards/core-standard.md`,
- execution requires live architectural steering,
- the task is trivial and coordination would cost more than doing it directly,
- failure would force total replanning.

Delegation never removes verification obligations. Required verification still applies after delegated work returns.

Default check:

> If this subtask fails, can I recover cleanly without redesigning the whole task?

If the answer is no, do not delegate it yet.

---

## 7. Parallelism and Fanout

Default fanout is **1 active workstream**.

Increase to **2** only when:
- workstreams are clearly independent,
- edit surfaces are unlikely to collide,
- merge order is simple,
- review and reconciliation remain cheap.

Treat **3+ active workstreams** as exceptional.
Use them only when:
- decomposition is already clear,
- ownership boundaries are stable,
- output integration is easy to define in advance.

Reduce fanout immediately when:
- files or interfaces begin to overlap,
- agents need repeated cross-coordination,
- integration becomes the dominant cost,
- review burden grows faster than throughput.

If you are unsure whether to parallelize, stay serial.

---

## 8. Recovery and Failure Handling

### Tool or agent failure

Follow the tool failure rule in `~/.claude/standards/core-standard.md`.

Do not pretend the missing result is implied.

### Low-confidence output

If an agent returns low-confidence output:
- narrow the task,
- reduce scope,
- escalate only if the ambiguity is real,
- or return to clarification.

### Integration failure

If parallel work no longer integrates cheaply:
- stop expanding fanout,
- collapse back to serial integration in the main thread,
- re-sequence the remaining work.

### Context pressure

If context pressure rises:
- stop adding new workstreams,
- prefer bounded delegation or explicit checkpoints,
- protect safe completion of the accepted scope before exploring more.

---

## 9. Common Anti-Patterns

Avoid these failures:

- using `orchestrator-planner` for routine bounded execution,
- using `mechanical-transformer` when meaning materially affects correctness,
- parallelizing work that is only superficially independent,
- increasing fanout without a real throughput gain,
- escalating because of abstract complexity instead of a concrete blocking uncertainty,
- keeping a weak path alive after integration cost has already turned negative,
- treating this guide as always-on policy instead of on-demand expansion.

---
