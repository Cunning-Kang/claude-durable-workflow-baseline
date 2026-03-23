# `distribution/settings-snippets/user/` — User-Level Settings Snippets

> Scope: Phase 3 Skeleton | Date: 2026-03-22
> Purpose: Hold source-only user-level settings fragments distributed from this baseline repo.

---

## What This Is

Files in this directory are **user-level settings snippets** — reusable fragments intended for a user's Claude Code runtime across all repos on that machine, but only after explicit manual adoption.

**Target merge surface after manual adoption:** `~/.claude/settings.json`

This directory holds **snippets only**. It does **not** ship a live `settings.json`.

---

## Appropriate Use Cases

- User-level permission snippets that apply consistently across repos
- User-level hook registration fragments for hooks the user has explicitly adopted
- User-level runtime preferences that are intentionally portable across projects

---

## Installation Method

These snippets are **source-only distribution, not auto-install**.

1. Read the snippet and confirm it belongs in user scope.
2. Manually merge only the desired keys into `~/.claude/settings.json`.
3. Validate the final merged settings in the target runtime.

This README describes a manual merge workflow only. It does not imply any automatic wiring or live settings mutation path.

---

## Why Not Default Enabled

1. **Environment dependency** — user runtimes vary in toolchains, privilege levels, and local policies.
2. **Team boundary differences** — a user-level default may be appropriate for one person but not for every project or team.
3. **Superpowers control surface protection** — default-on settings could shadow or override the intended primary control surface.
4. **Opt-in correctness** — deterministic enforcement and runtime behavior should be consciously adopted.
5. **Traceability** — explicit manual merge makes it clear what is active in a given user runtime.

---

## Opt-In Principle

Snippets in this directory are **never auto-merged**. They require:
- A deliberate review by the user
- A manual merge into `~/.claude/settings.json`
- Validation in the destination runtime

---

## Relationship with Hooks and Superpowers

User-level settings snippets from this repo must **not**:
- Ship a live `settings.json`
- Auto-enable hooks without explicit user adoption
- Register competing skill entry points
- Redirect or shadow the primary Superpowers control flow

A snippet may reference user-level hooks only after the user explicitly adopts both the hook source and the settings fragment.

---

## Scope Decision Rule

```
Is it intended to apply across all repos for one user?
  → YES → user settings snippet (this directory)
  → NO  → project settings snippet (distribution/settings-snippets/project/) or local example only
```

---

## References

- `docs/reference/hooks-scope.md` — Three-layer scope reference
- `docs/reference/superpowers-boundary.md` — Repository role and Superpowers boundary
- D-003: Hooks must be layered as user / project / local example only
- R-002: Hooks/settings must remain source/snippets only; opt-in per layer
