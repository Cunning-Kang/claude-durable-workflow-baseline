---
description: Review whether the current branch or worktree appears ready to finish after implementation, verification, and review
argument-hint: [scope or short summary]
allowed-tools:
  - Bash
  - Read
  - Grep
---

<objective>
Review the current branch or worktree and determine whether it appears ready for a clean finish.

Purpose: help the user assess implementation completeness, review completeness, and repo hygiene before any final branch workflow step.
Output: a readiness assessment plus the smallest clean next action.
</objective>

<context>
User input:
- Optional scope or short summary from the slash command arguments

Available signals to inspect:
- current branch name
- working tree state
- diff summary
- recent commit history
</context>

<process>
1. Review the current branch state and working tree cleanliness.
2. Check whether any remaining diff appears expected, relevant, and reviewable.
3. Assume the implementation was guided by approved spec artifacts, but do not create or revise plans, specs, or task lists here.
4. Decide whether the branch or worktree appears ready to finish:
   - changes are coherent
   - no obvious stray files are present
   - recent progress is reviewable
   - nothing obvious suggests unresolved blockers
5. If the branch is not ready:
   - explain the minimum remaining work
   - identify whether another atomic commit is likely needed
6. If the branch is ready:
   - summarize what appears complete
   - summarize what changed recently
   - say whether another atomic commit is needed before finishing
   - recommend the clean next action for the user’s workflow
</process>

<success_criteria>
- The user gets a clear ready / not-ready assessment.
- The assessment distinguishes implementation completeness, working tree hygiene, and likely next action.
- No destructive branch action is taken automatically.
</success_criteria>

<critical_rules>
- Do not merge, delete branches, or perform destructive cleanup unless the user explicitly asks.
- Keep this command focused on review and next-step guidance.
- If the working tree is not clean, evaluate whether that is expected rather than assuming readiness.
</critical_rules>
