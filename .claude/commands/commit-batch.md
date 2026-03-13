---
description: Review the current verified batch and create one atomic commit only when the diff is coherent
argument-hint: [message or scope]
allowed-tools:
  - Bash
  - Read
  - Grep
---

<objective>
Review the current working tree and decide whether the verified change set is safe to commit as one atomic batch.

Purpose: keep commit history reviewable, coherent, and easy to revert.
Output: either one atomic commit or a clear explanation of what must be split or cleaned up first.
</objective>

<context>
User input:
- Optional message or scope hint from the slash command arguments

Available signals to inspect:
- git status
- staged and unstaged diff
- recent commit messages for style
</context>

<process>
1. Inspect the current status and diff before taking any git write action.
2. Decide whether the current changes form one logical, reviewable, revertable batch.
3. If unrelated changes are mixed together:
   - do not commit
   - explain the split needed
   - recommend the smallest safe next action
4. If the batch appears coherent:
   - stage only the relevant files for that batch
   - write a concise commit message
   - use the user argument only as a hint and improve it if needed
   - create exactly one commit
5. Treat recent verification as a claim to cross-check, not as guaranteed truth:
   - verify that the diff appears consistent with a recently verified batch
   - if the diff appears to include unrelated or unverified changes, do not commit
6. Never stage speculative, unrelated, or convenience-only files just to clean the working tree.
</process>

<success_criteria>
- If safe: one coherent atomic commit is created and the final commit message is reported.
- If not safe: no commit is created and the user gets an exact explanation of what must be split, staged, or cleaned first.
</success_criteria>

<critical_rules>
- Prefer atomic change sets over forcing a commit.
- Do not assume every modified file belongs in the same batch.
- Do not claim the batch is verified unless the observed diff supports that claim.
- Do not auto-push or perform any branch-finishing action here.
</critical_rules>
