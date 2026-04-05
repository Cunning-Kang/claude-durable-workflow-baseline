# Orchestration Extension

> When this guide conflicts with core-standard.md, core-standard.md wins.

---

## 1. Role of This Guide

This guide supplements the compact defaults in `~/.claude/standards/core-standard.md`.

Use it only when deciding whether orchestration is justified. It does not create a second execution protocol, does not replace built-in routing, and does not redefine configured custom subagents.

**This is an on-demand decision guide, not a second control surface.**

### Terminology (minimum definitions)

- **bounded execution** — a task or workstream whose scope is fixed before delegation starts
- **workstream** — one parallel line of work with a defined scope
- **fanout** — delegating to multiple workstreams simultaneously

---

## 2. When to Consult It

Consult this guide when one or more of the following is true:

- more than one workstream may be required before safe execution can begin,
- outputs from multiple workstreams may need reconciliation,
- execution ordering or dependency sequencing may materially affect correctness,
- the task boundary is not yet stable enough for bounded execution.

Skip this guide for trivial local work or already-bounded execution.

---

## 3. Decision Heuristics

Prefer the simplest path that preserves correctness.

- Stay inline when the work is trivial or coordination would cost more than execution.
- Prefer a bounded execution path when scope is already stable.
- Escalate only when approach selection, reconciliation, or ordering is the blocking problem.

Task size alone is not a routing signal.
Detailed agent routing and intent live in agent definitions, not in this guide.

---

## 4. Delegation and Parallelism

Delegate only when the subtask is:

- **bounded** — scope is defined before delegation starts,
- **independent** — it can complete without constant steering,
- **recoverable** — failure does not force total redesign,
- **worth the overhead** — coordination cost is lower than inline cost.

Do not delegate when:

- the work includes a high-risk operation as defined in `~/.claude/standards/core-standard.md`,
- execution still needs live architectural steering,
- the task is trivial,
- failure would force full replanning.

Default fanout is **1 active workstream**.
Increase to **2** only when workstreams are clearly independent and integration remains cheap.
Treat **3+ active workstreams** as exceptional.
If unsure, stay serial.

---

## 5. Escalation and Downgrade

Escalate when:

- multiple viable approaches materially affect execution,
- the task boundary cannot yet be stabilized,
- reconciliation across outputs is required before safe execution,
- dependency ordering is itself the blocking problem.

Do not escalate merely because:

- the task is large,
- the task touches multiple files,
- the task is architecture-adjacent but already bounded,
- the task modifies an already-specified shared interface.

Downgrade as soon as a simpler path becomes valid.
When changing path, record a brief reason.

---

## 6. Recovery Signals

If tool or agent failure occurs, follow the tool failure rule in `~/.claude/standards/core-standard.md`.
Do not pretend the missing result is implied.

If output returns low confidence:

- narrow the task,
- reduce scope,
- clarify when ambiguity is real,
- escalate only if the uncertainty is genuinely orchestration-related.

If integration cost becomes dominant:

- stop expanding fanout,
- collapse back to serial integration,
- re-sequence the remaining work.

If general context pressure rises (increased memory or token usage from too many parallel workstreams):

- stop adding new workstreams,
- prefer bounded delegation or explicit checkpoints,
- protect safe completion of the accepted scope first.

---

## 7. Common Anti-Patterns

Avoid these failures:

- treating this guide as always-on policy,
- escalating because of abstract complexity instead of a concrete blocker,
- parallelizing work that is only superficially independent,
- increasing fanout without stable ownership boundaries,
- keeping fanout alive after integration cost has already turned negative,
- using orchestration to avoid making the task boundary explicit.
