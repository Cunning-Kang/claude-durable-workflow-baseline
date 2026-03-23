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
3. **Superpowers control surface protection** — automatic hook installation could shadow or override Superpowers behavior (see `docs/reference/superpowers-boundary.md`).
4. **Opt-in correctness** — deterministic enforcement must be consciously adopted.
5. **Traceability** — explicit installation makes it clear what is running in a given environment.

---

## Opt-In Principle

Hooks in this directory are **never auto-installed**. They require:
- A deliberate copy step by the user
- Explicit activation in the target runtime

---

## Relationship with Superpowers

User-level hooks from this repo must **not**:
- Register competing skill entry points (e.g., `/brainstorming`, `/finish-branch` — the latter was removed from this baseline repo and is owned by Superpowers)
- Redirect or shadow the primary Superpowers control flow
- Modify `~/.claude/settings.json` directly

Hooks that compete with Superpowers are prohibited. See `docs/reference/superpowers-boundary.md` and `docs/reference/hooks-scope.md`.

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
- `docs/reference/superpowers-boundary.md` — Repository role and Superpowers boundary
- D-003: Hooks must be layered as user / project / local example only
- R-002: Hooks mis-globalization risk — source/snippets only; opt-in per layer
