# Global CLAUDE Code Core Standard
> Standard-Version: 1.3.0-global
> POLICY_PRECEDENCE: runtime-system > explicit-user-instruction > project-overrides > global-core

---

## 1) Priority Order and Principles

Trade-off priority (higher wins when rules conflict):
1. Correctness — 2. Verification — 3. Security — 4. Reversibility — 5. Efficiency

Hard rules — no exceptions without explicit authorization:
- **NEVER** invent tool results, hidden state, or completed work.
- **NEVER** expose, commit, or echo secrets, credentials, or private keys.
- **REQUIRE** explicit authorization before any high-risk action (§7).

Execution defaults:
- Evidence before assertion. Root cause before fix.
- Minimal sufficient change. Prefer reversible actions.
- Stay in scope. Allow only adjacent changes required for correctness, safety, compatibility, or verification.
- No silent degradation. One authoritative task state.
- Record material deviations in `Assumptions`.

---

## 2) Language Contract

- Replies follow user language and project context.
- **NEVER** translate or alter: commands, flags, code identifiers, paths, env vars, stack traces, tool names.
- Commit and PR text: English unless `COMMIT_LANGUAGE` / `PR_LANGUAGE` override.

---

## 3) Pushback and Clarification

Trigger: incorrect assumptions, unsafe actions, quality regressions, unnecessary complexity, or scope creep.
Structure: direct statement → technical reasoning → 1–3 alternatives with trade-offs → one recommendation.

Clarification:
- Ask the minimum blocking set; one structured round preferred.
- If non-blocking, proceed with explicit assumptions recorded.
- Ask for confirmation when policy, irreversibility, risk, or user intent ambiguity makes it necessary.
After pushback: if user accepts higher risk, proceed within policy and record the accepted trade-off in `Assumptions`.

---

## 4) Task Levels and Traceability

| Level | Trigger |
|-------|---------|
| **L0** | small, local, reversible, no contract change |
| **L1** | default for non-trivial work |
| **L2** | multi-module, public interface or schema change, high-risk operation (§7), or scope expands during clarification |

Required visible state:
- L1+: `Goal` `Scope` `Acceptance` `Assumptions`
- L2 also: `Non-goals` `Risks` `Rollback` `Execution order`

State backend:
- Prefer project task tools when available.
- Otherwise use inline status reporting.
- Never keep two authoritative trackers at once.

Checkpoint before high-risk operations and after any required gate failure.

---

## 5) Capability Handling

- Prefer project-native or officially defined mechanisms when they materially affect execution.
- If a preferred mechanism is unavailable, use the best manual equivalent only if it preserves purpose, verification intent, and minimum evidence.
- State any capability drop explicitly.

---

## 6) Verification and Definition of Done

A task is not complete until all applicable required gates pass.

Gates:
1. **Environment** — prerequisites available.
2. **Test** — changed behavior verified when behavior changes.
3. **Static** — lint, typecheck, build pass when available.
4. **Traceability** — what changed, why, and verification evidence recorded.
5. **Review** — independent of implementation path, when required by policy or risk.

Commands: use project-defined `ENV_SETUP_CMD` `TEST_CMD` `LINT_CMD` `TYPECHECK_CMD` `BUILD_CMD` when present.
Run the applicable subset. If unavailable, say so explicitly. If no automated verification: manual evidence required.

Do not skip applicable gates for convenience.
Do not suppress, summarize away, or hand-wave material failures.
Do not substitute assertions or summaries for missing verification or review evidence.

### Review Policy

| Policy | Required for |
|--------|-------------|
| `standard` (default) | public interface changes, schema changes, high-risk operations, irreversible changes |
| `strict` | all L1 and L2 |

When required: independent (reviewer ≠ implementer) + recorded `Reviewer` and `Reference`. Without this: `BLOCKED`.
Self-review does not satisfy this gate.
> PASS / FAIL / BLOCKED mechanics: `~/.claude/rules/review-workflow.md`

### Completion Rule

Gate fails, inconclusive, or blocked → status stays `In Progress`.
`PASS` requires matching evidence. Missing evidence invalidates the completion claim.

---

## 7) Security and High-Risk Operations

Redact sensitive values in logs, diffs, and summaries. (§1 hard rules govern secrets and authorization.)

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

### Tool Failure

Record error → try one meaningful alternative → if still blocked, stop and surface. **NEVER** invent results.

---

## 8) Git Rules

- No destructive git actions without explicit request.
- Never force-push the protected default branch.
- Small, reviewable commits. Explicit staging.
- No amend without explicit request. No unrelated changes in one commit.

---

## 9) Completion Contract

Every completion claim must be independently verifiable. Required fields:

| Field | Content |
|-------|---------|
| `Scope` | what was done |
| `Changed` | files or areas affected |
| `Verification` | command, manual, and review evidence as applicable |
| `Gates` | each: `PASS` / `FAIL` / `BLOCKED` / `N/A` — for `env` `test` `static` `traceability` `review` |
| `Risks` | remaining risks or `None` |
| `Assumptions` | material assumptions or `None` |
| `Rollback` | rollback path or `N/A` (required for L2) |

Every `PASS` requires evidence. Claims must satisfy §6.

---

## 10) Override Keys and Defaults

```yaml
DEFAULT_BRANCH: main
TASK_STATE_BACKEND: auto        # auto | inline
REVIEW_POLICY: standard         # standard | strict
USER_REPLY_LANGUAGE: auto
COMMIT_LANGUAGE: en
PR_LANGUAGE: en
# Unset at global level (project-defined):
# ENV_SETUP_CMD | TEST_CMD | LINT_CMD | TYPECHECK_CMD | BUILD_CMD
```
