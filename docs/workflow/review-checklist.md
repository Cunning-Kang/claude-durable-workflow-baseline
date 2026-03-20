# Review Checklist

> **Status: Active** — Required gate for all L1/L2 durable tasks with implementation. Use alongside `review-protocol.md`.

**When to use:** Trigger `superpowers:requesting-code-review` when:
- Task is L1 or L2 (durable, multi-session, or affects public interfaces)
- Implementation is complete and verified
- You need independent verification before claiming done

**When NOT to use:** L0 changes, one-off fixes, or trivial cosmetic updates.

- Is review actually required for this task?
- Did an independent reviewer perform the review?
- Did the reviewer see the relevant requirement or spec?
- Did the reviewer see the relevant diff or changed files?
- Is the result clearly one of: PASS / FAIL / BLOCKED?
- If FAIL, were blocking issues fixed before completion was claimed?
- If BLOCKED, did the task remain in progress?
