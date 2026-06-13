---
description: |
  Launch or reuse the source-only dynamic workflow at distribution/workflows/subagent-pipeline-dynamic.js.
  Use this when you want issue, plan-file, or task work coordinated through named subagents with planner,
  implementation, spec, test, code review, global review, and coordinator-owned report/commit closeout.
allowed-tools:
  - Read
  - Workflow
argument-hint: "[#issue ... | plan-file | 'task'] [--parallel #1,#2 #3] [--plan|--no-plan] [--no-commit] [--push] [--close-issues]"
---

Usage: Run `/subagent-pipeline-workflow <work items>` to launch the reusable dynamic workflow script.

With no arguments: this command layer collects work items interactively (prompt user for issue numbers, plan file paths, or task text) before invoking Workflow. The workflow script itself requires non-empty `workItems` and will return BLOCKED if none are supplied.

Examples:
- `/subagent-pipeline-workflow #1`
- `/subagent-pipeline-workflow docs/plans/foo.md`
- `/subagent-pipeline-workflow "Fix auth token expiry"`
- `/subagent-pipeline-workflow #1 docs/plans/foo.md "Fix X"`
- `/subagent-pipeline-workflow --parallel #1,#2 #3`
- `/subagent-pipeline-workflow --plan #1`
- `/subagent-pipeline-workflow --no-plan #1`
- `/subagent-pipeline-workflow --no-commit #1`
- `/subagent-pipeline-workflow --push #1`
- `/subagent-pipeline-workflow --close-issues #1`

Pipeline phases (aligned with SKILL.md):
0. Setup — load work item specs, capture BASE_SHA, task-planner (retry budget 2) → plan-reviewer; cross-issue merge planner for --parallel multi-work-item
0.5. Capability Preconditions — verify reviewer/tester can access required source before implementation
1. Execute — code-implementer → spec-reviewer → test-engineer → code-reviewer per task; escalation rewalk on 2 consecutive code-reviewer FAILs
2. Global Review — code-reviewer on BASE_SHA..HEAD_SHA (N/A when single task: Phase 1 code-reviewer satisfies this gate)
3. Report and Atomic Commit — coordinator-owned commit by file-group; push and issue close only when --push / --close-issues supplied

What it does:
1. Uses `distribution/workflows/subagent-pipeline-dynamic.js` as the workflow script.
2. Parses work item arguments into workflow args:
   - `workItems`: issue (`#1`), plan-file (`docs/plans/foo.md`), and task text entries
   - `groups`: array of arrays. Comma-separated items form one group (parallel candidates); space-separated groups run sequentially. Example: `--parallel #1,#2 #3` → `groups: [[#1, #2], [#3]]`
   - `plan`: `force` for `--plan`, `skip` for `--no-plan`, otherwise `auto`
   - `commit`: false for `--no-commit`, otherwise true
   - `push`: true for `--push`; also true when `closeIssues` is true
   - `closeIssues`: true for `--close-issues`; implies push
3. Invokes the Workflow tool with the script path and parsed args.
4. The workflow coordinates named subagents only:
   `task-planner`, `plan-reviewer`, `code-implementer`, `spec-reviewer`, `test-engineer`, `code-reviewer`.
5. The workflow performs coordinator-owned mechanical report/commit after global review PASS. It does not push or close GitHub issues unless `--push` or `--close-issues` is supplied in the current request.

Retry budgets:
- Planning: 2 retries per work item (task-planner redispatch with plan-reviewer findings)
- Execution: 3 retries per task across all stages
- Escalation rewalk on 2 consecutive same-reviewer FAILs (does not consume budget; subsequent failures during rewalk do)

Install/adoption model:
- This command is source-only and opt-in.
- Copy this file to `~/.claude/commands/subagent-pipeline-workflow.md` if you want a user-level slash command.
- Keep `distribution/workflows/subagent-pipeline-dynamic.js` available from the baseline cache, or pass its absolute path to the Workflow tool.
- `/init-claude-workflow` does not auto-install this command or workflow.

Equivalent direct Workflow launch:

```js
Workflow({
  scriptPath: "/path/to/claude-durable-workflow-baseline/distribution/workflows/subagent-pipeline-dynamic.js",
  args: {
    workItems: [
      { type: "issue", issue: 1 },
      { type: "plan-file", path: "docs/plans/foo.md" },
      { type: "task", text: "Fix auth token expiry" }
    ],
    groups: [[{ type: "issue", issue: 1 }]],
    plan: "auto",
    noCommit: false,
    push: false,
    closeIssues: false
  }
})
```

## Non-goals
- Do not auto-install named agents, hooks, settings snippets, or workflow scripts.
- Do not bypass planner, review, test, or global review gates.
- Do not commit before global review PASS.
- Do not push or close GitHub issues without explicit current-session authorization via `--push` or `--close-issues`.
- Do not treat the dispatch ledger as review, test, or spec evidence.
