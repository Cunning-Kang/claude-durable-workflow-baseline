---
description: |
  Launch or reuse the source-only dynamic workflow at distribution/workflows/subagent-pipeline-dynamic.js.
  Use this when you want GitHub issue work coordinated through named subagents with planner,
  implementation, spec, test, code review, global review, and confirm-gated closeout.
allowed-tools:
  - Read
  - Workflow
argument-hint: "[#issue ...] [--parallel #1,#2 #3] [--plan|--no-plan] [--no-closeout]"
---

Usage: Run `/subagent-pipeline-workflow <issues>` to launch the reusable dynamic workflow script.

Examples:
- `/subagent-pipeline-workflow #1`
- `/subagent-pipeline-workflow #1 #2 #3`
- `/subagent-pipeline-workflow --parallel #1,#2 #3`
- `/subagent-pipeline-workflow --plan #1`
- `/subagent-pipeline-workflow --no-plan #1`
- `/subagent-pipeline-workflow --no-closeout #1`

What it does:
1. Uses `distribution/workflows/subagent-pipeline-dynamic.js` as the workflow script.
2. Parses issue arguments into workflow args:
   - `issues`: all issue numbers
   - `groups`: comma-separated issues run as one parallel group; space-separated groups run sequentially
   - `plan`: `force` for `--plan`, `skip` for `--no-plan`, otherwise `auto`
   - `phase3`: `disabled` for `--no-closeout`, otherwise `confirm`
3. Invokes the Workflow tool with the script path and parsed args.
4. The workflow coordinates named subagents only:
   `task-planner`, `plan-reviewer`, `code-implementer`, `spec-reviewer`, `test-engineer`, `code-reviewer`.
5. The workflow stops before commit, push, or `gh issue close` unless explicit current-session closeout authorization is supplied.

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
    issues: [1],
    groups: [[1]],
    plan: "auto",
    phase3: "confirm"
  }
})
```

## Non-goals
- Do not auto-install named agents, hooks, settings snippets, or workflow scripts.
- Do not bypass planner, review, test, or global review gates.
- Do not commit, push, or close GitHub issues without explicit current-session authorization.
- Do not treat the dispatch ledger as review, test, or spec evidence.
