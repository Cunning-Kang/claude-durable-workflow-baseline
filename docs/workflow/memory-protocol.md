# Memory Protocol

> **Status: Reference Only** — Superpowers `memory-reflection` skill 已覆盖此协议的核心功能。此文件保留作为架构说明，不再作为强制操作面。

**When to trigger memory check (operator reminder):**
After completing any durable task (L1/L2), pause and ask:
1. Did this reveal a stable project pattern worth reusing?
2. Did it expose a recurring gotcha future sessions should know?
3. Did it clarify a durable workflow rule?

If any answer is yes → update `memory/patterns.md`, `memory/gotchas.md`, or `memory/MEMORY.md`.

## Purpose
Convert stable lessons from durable work into project memory without turning memory into a task log.

## Reflection trigger
After completing or materially unblocking a durable task, explicitly ask:
1. Did this work reveal a stable project pattern?
2. Did it expose a recurring gotcha?
3. Did it clarify a durable workflow rule worth reusing?

If all three answers are no, do not update memory.

## What belongs in memory
Write only:
- stable project conventions
- recurring pitfalls
- reusable workflow or verification patterns
- durable decisions that future sessions will need

## What does not belong in memory
Do not write:
- feature progress
- one-off blockers
- temporary experiments
- raw execution logs
- speculative ideas

## Where to write
- `memory/MEMORY.md` for concise always-relevant rules
- `memory/patterns.md` for reusable patterns
- `memory/gotchas.md` for recurring pitfalls

## Update rule
Prefer updating an existing entry over adding a new duplicate entry.
