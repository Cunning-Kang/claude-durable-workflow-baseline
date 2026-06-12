# `distribution/hooks/user/` — User-Level Hooks Source

> Scope: Phase 3 Boundary Anchor | Date: 2026-03-22
> Purpose: Hold source-only user-level hooks distributed from this baseline repo.

---

## What This Is

Source files in this directory are **user-level hooks** — portable, project-agnostic scripts that run at user level across all repos on this machine once installed.

**Target install location after manual adoption:** `~/.claude/hooks/`

---

## Appropriate Use Cases

- Global lint helpers or commit-msg normalization applied to every repo
- Workspace-wide time-tracking triggers
- Cross-project enforcement scripts that apply uniformly to all repos

---

## Installation Method

These hooks are **source-only distribution, not auto-install**.

1. Read the hook source.
2. Copy the desired hook manually to `~/.claude/hooks/`.
3. Treat the hook as explicit opt-in source material only; this README does not imply any additional live wiring or settings mutation path.

---

## Why Not Default Enabled

1. **Environment dependency** — hooks run in user environments with varying toolchains, privilege levels, and risk tolerances. A hook that works for one user may break another.
2. **Team boundary differences** — user-level hooks impose one user's preferences on all repos; explicit opt-in respects autonomy.
4. **Opt-in correctness** — deterministic enforcement must be consciously adopted.
5. **Traceability** — explicit installation makes it clear what is running in a given environment.

---

## Opt-In Principle

Hooks in this directory are **never auto-installed**. They require:
- A deliberate copy step by the user
- Explicit activation in the target runtime

---


User-level hooks from this repo must **not**:
- Modify `~/.claude/settings.json` directly


---

## Scope Decision Rule

```
Is it project-agnostic AND intended to run in ALL repos?
  → YES → user scope (this directory)
  → NO  → project scope (distribution/hooks/project/) or local example only
```

---

## References

- `docs/reference/hooks-scope.md` — Three-layer scope reference
- D-003: Hooks must be layered as user / project / local example only
- R-002: Hooks mis-globalization risk — source/snippets only; opt-in per layer


### `validate-agent-artifact-write`

- Event: `PreToolUse`
- Tool: `Write`
- Purpose: restrict read-only subagent artifact writes to `$TMPDIR/agent-artifacts/<agent>-*.md`
- Source: `distribution/hooks/user/validate-agent-artifact-write/hook.mjs`
