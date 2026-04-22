---
description: |
  Initialize the durable workflow baseline in the current repo from the local baseline cache.
  Invokes ~/.claude/scripts/init-claude-workflow.sh which copies the cached baseline package contents
  (docs/specs/_template/, docs/workflow/, memory/, claude/) into the repo root without creating feature state.
  Use this as the first and only entry command for any new project.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
argument-hint: [--dry-run | --print-patch | --force-template]
---

Usage: Run `/init-claude-workflow` directly — it invokes the script automatically.

What it does:
1. Confirm the current directory is a git repository.
2. Resolve the local baseline cache path.
3. Read the cached baseline package.
4. Create any missing baseline files in the current repo.
5. For existing files that differ, do not overwrite them; produce patch suggestions instead.
6. Write or update `.claude/workflow-baseline-version` only if safe to do so.
7. Summarize:
   - files created
   - files skipped
   - files needing manual review
   - project-specific fields the user must fill in next

After initialization, review files are in:
- `docs/workflow/review-protocol.md`
- `docs/workflow/review-checklist.md`
When review is required, write evidence to `docs/specs/<feature>/review.md`.

## Non-goals
- Do not sync the baseline cache.
- Do not upgrade an initialized repo.
- Do not create `docs/specs/<feature>/...` instances.
- Do not infer repo-specific commands.
- Do not overwrite user-modified files by default.
