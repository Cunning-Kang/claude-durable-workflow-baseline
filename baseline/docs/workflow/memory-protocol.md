# Memory Protocol

> This protocol defines the repo-local process for deciding what belongs in memory and how to write, update, and remove entries.

---

## 1. Intake — When to Add

Write to memory **only after** one of these triggering events:

| Trigger | Example |
|---|---|
| Feature closeout | Feature completed and merged; a durable lesson surfaced |
| Independent review | Reviewer identified a recurring pattern across sessions |
| Blocking issue resolved | Root cause was durable; solution is reusable |
| New convention established | Team agreed on a stable pattern via discussion |

If a triggering event occurred but the content does not satisfy D1/D2/D3 (recurrence, reusability, actionability), do not write to memory. Route it using the repo-local memory files and protocol.

---

## 2. How to Write an Entry

Do not write vague guidance. Write specific, actionable entries:

**Bad:**
> "Be careful with console.log in CI."

**Good:**
> `GOTCHA: Node.js console.log in CI is buffered`
> `console.log` output is buffered in many CI environments, causing interleaved output to appear out of order.
> Fix: use `process.stdout.write()` for scripts that output in CI.

**Bad:**
> "Remember to run tests before committing."

**Good:**
> `GIT COMMIT GATE: mise run lint && mise run test must pass before git commit. CI enforces this — no bypasses.`

---

## 3. How to Update

Prefer updating over adding a duplicate when an existing entry covers the same durable lesson.

- Append new information; preserve the original date
- Add an `Updated: YYYY-MM-DD` marker
- If the update fundamentally changes the entry's intent, treat it as removal + new intake

---

## 4. When to Remove

| Condition | Action |
|---|---|
| Entry describes something that no longer recurs | Remove |
| Entry was a misclassification | Remove; route to correct destination |
| Entry is duplicated in another memory file | Merge |
| Entry has been superseded by a protocol or global rule | Remove; reference the authoritative source |
| Entry was a one-off incorrectly added | Remove; do not replace |

**Age is not a removal criterion.** If it recurs, it stays.

---

## 5. Anti-Patterns to Avoid

These are known memory writing failures:

| # | Anti-pattern | What to do instead |
|---|---|---|
| AP-1 | **Durability Inflation** — treating session-specific content as durable | Apply D1/D2/D3 before every addition |
| AP-2 | **Memory Bloat** — entries accumulate without review | Apply removal criteria proactively |
| AP-3 | **Cross-File Duplication** — same fact in two files | Consolidate; each fact lives once |
| AP-4 | **Memory as Task Log** — feature progress, session summaries | Route to feature spec / issue tracker |
| AP-5 | **Protocol Dumping** — writing protocol definitions into memory | Protocol content goes in `docs/workflow/` |
| AP-6 | **Hook/Command Content in Memory** | Hooks belong in hook source files or `docs/reference/hooks-scope.md` |
| AP-7 | **Vague Entries** — "be careful with X" without enough context | Rewrite to be specific and actionable, or delete |
| AP-8 | **One-Off Retention** — keeping entries for failures that will not recur | Remove; one-off is a removal signal |

Use this protocol together with the repo-local memory files when classifying entries.

---

## 6. What This Document Is Not

This protocol does not contain durable memory content itself. Its job is the **process** of writing; the active memory files hold the durable content.
