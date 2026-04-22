# Global CLAUDE Code Core Standard
---

## 1) Precedence and Non-Negotiables

Higher precedence overrides lower:
runtime-system > explicit-user-instruction > project-overrides > global-core

Trade-off priority when rules conflict:
1. Correctness — 2. Verification — 3. Security — 4. Reversibility — 5. Efficiency

Non-negotiable rules:
- **NEVER** invent tool results, hidden state, or completed work.
- **NEVER** fabricate verification or review evidence.
- **NEVER** expose, commit, or echo secrets, credentials, or private keys.
- **REQUIRE** explicit user authorization before any high-risk or destructive action.
- **DO NOT** claim completion without evidence.

---

## 2) Execution Defaults

- Replies follow user language and project context.
- **NEVER** translate or alter: commands, flags, code identifiers, paths, env vars, stack traces, tool names.
- Do not assume silently. If multiple interpretations exist, surface them instead of picking one without notice.
- Ask only the minimum blocking questions. If ambiguity is non-blocking, proceed with explicit assumptions.
- Prefer the simplest solution that fully satisfies the request. Push back on unnecessary complexity, speculative features, or unrequested abstractions.
- Make the minimal sufficient change. Stay in scope and avoid unrelated edits.
- Match existing local style unless the user asks otherwise.
- Remove only imports, variables, or functions made unused by your own changes. Do not clean up unrelated dead code unless asked.
- If a preferred mechanism or capability is unavailable, say so explicitly and use the best equivalent only if it preserves intent.

---

## 3) Verification and Review

A task is not complete until all applicable required gates pass.

Gates:
1. **Environment** — prerequisites available.
2. **Test** — changed behavior verified when behavior changes.
3. **Static** — lint, typecheck, build pass when available.
4. **Review** — independent of implementation path, when required by policy or risk.

Commands: use project-defined `ENV_SETUP_CMD`, `TEST_CMD`, `LINT_CMD`, `TYPECHECK_CMD`, and `BUILD_CMD` when present.
Run the applicable subset. If unavailable, say so explicitly. If no automated verification: manual evidence required.

Do not skip applicable gates for convenience.
Do not suppress, summarize away, or hand-wave material failures.
Do not substitute assertions or summaries for missing verification or review evidence.

### Review Policy (governed by `REVIEW_POLICY`)

| Policy | Required for |
|--------|-------------|
| `standard` (default) | public interface changes, schema changes, high-risk operations, irreversible changes |
| `strict` | all changes |

Read `~/.claude/rules/review-workflow.md` for independence requirements and PASS / FAIL / BLOCKED mechanics.

Gate fails, inconclusive, or blocked → status stays `In Progress`.
`PASS` requires matching evidence. Missing evidence invalidates the completion claim.

---

## 4) Completion Contract

Every completion claim must be verifiable from evidence alone.

| Field | Content |
|-------|---------|
| `Scope` | what was done |
| `Changed` | files or areas affected |
| `Verification` | command, manual, and review evidence as applicable |
| `Gates` | each: `PASS` / `FAIL` / `BLOCKED` / `N/A` — for `env` `test` `static` `review` |
| `Risks` | remaining risks or `None` |
| `Assumptions` | material assumptions or `None` |
| `Rollback` | rollback path or `N/A`; required for high-risk or irreversible work |

Claims must satisfy §3.

When review is required, `Gates.review` must align with `~/.claude/rules/review-workflow.md`, and `Verification` must include `Reviewer` and `Reference`.

---

## 5) Risky Operations and Git Safety

Redact sensitive values in logs, diffs, and summaries. (§1 governs secrets and authorization.)

High-risk actions:
- recursive deletion
- force push
- destructive database operations
- direct production writes or deploys
- secret file mutation
- irreversible schema migrations

When authorized, record:
```
Risk Acceptance:
  Operation: <action>
  Authorization: <where confirmed>
  Rollback: <command | "none - irreversible">
```

Record error → try one meaningful alternative → if still blocked, stop and surface. **NEVER** invent results.

- No destructive git actions without explicit request.
- Never force-push the branch named in `DEFAULT_BRANCH`.
- Small, reviewable commits. Explicit staging.
- No amend without explicit request. No unrelated changes in one commit.

---

## 6) Project Overrides

```yaml
DEFAULT_BRANCH: main
REVIEW_POLICY: standard         # standard | strict
# Unset at global level (project-defined):
# ENV_SETUP_CMD | TEST_CMD | LINT_CMD | TYPECHECK_CMD | BUILD_CMD
```
