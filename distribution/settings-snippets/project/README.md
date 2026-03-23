# `distribution/settings-snippets/project/` — Project-Level Settings Snippets

> Scope: Phase 3 Skeleton | Date: 2026-03-22
> Purpose: Hold source-only project-level settings fragments distributed from this baseline repo.

---

## What This Is

Files in this directory are **project-level settings snippets** — reusable fragments intended for one repository only, not a user's global runtime.

**Target merge surface after explicit project adoption:** `<project>/.claude/settings.json`

This directory holds **snippets only**. It does **not** ship a live project `settings.json`.

---

## Appropriate Use Cases

- Project-specific permission fragments
- Project-local hook registration snippets
- Repository-specific runtime defaults that should not leak into other repos

---

## Installation Method

Project-level settings snippets are **source-only distribution, not auto-install and not global default**.

1. Confirm the fragment belongs in project scope rather than user scope.
2. Project maintainers manually merge the desired keys into `<project>/.claude/settings.json`.
3. Validate the final merged settings within that project repository.

**This directory is NOT for user-level global merge.** Merging these fragments into `~/.claude/settings.json` would convert them into user-level defaults, which is the wrong scope.

---

## Why Not Default Global

1. **Project boundary respect** — project-level settings encode repo- or team-specific choices.
2. **Non-portability** — a fragment appropriate for one project may be irrelevant or harmful in another.
3. **Superpowers control surface protection** — automatic activation could shadow or override the intended primary control surface.
4. **Opt-in correctness** — project enforcement must be adopted consciously per repository.
5. **Traceability** — explicit manual merge makes it clear what is active in a given project.

---

## Opt-In Principle

Snippets in this directory are **never globally enabled by default**. They require:
- An explicit project-level adoption decision
- A deliberate manual merge into `<project>/.claude/settings.json`
- Validation in the destination project runtime

---

## Cannot Be Installed as Global Default

**Hard rule:** Project-level settings snippets from this directory must never be merged into `~/.claude/settings.json` as a global default.

Doing so would:
- Leak project-specific behavior into unrelated repos
- Blur the user/project scope boundary
- Increase the chance of conflicts with user-level hooks or Superpowers-managed behavior

If you need portable user-level defaults, use `distribution/settings-snippets/user/` instead.

---

## Relationship with Hooks and Superpowers

Project-level settings snippets from this repo must **not**:
- Ship a live `settings.json`
- Auto-enable hooks without explicit project adoption
- Register competing skill entry points
- Redirect or shadow the primary Superpowers control flow
- Override user-level defaults by pretending to be global policy

A snippet may reference project-level hooks only after the project explicitly adopts both the hook source and the settings fragment.

---

## Scope Decision Rule

```
Is it intended to apply across all repos for one user?
  → YES → user settings snippet (distribution/settings-snippets/user/)
  → NO  → Is it intended for one repository through explicit project adoption?
           → YES → project settings snippet (this directory)
           → NO  → local example only; do not add to this directory
```

---

## Phase 3B candidate index

All snippets below are **project-scope, snippet-only, opt-in templates**. They are **not live default wiring** in this baseline repo. Adoption requires explicitly copying the paired hook source into `<project>/.claude/hooks/`, then manually merging the chosen snippet into `<project>/.claude/settings.json`.

### `taskcompleted-authoritative-state-gate.settings.jsonc`

- Event: `TaskCompleted`
- Rule cluster: H-01 — authoritative completion-state consistency
- Purpose: register the H-01 hook with repo-local tracker/surface/marker configuration
- Boundary: only wires deterministic durable-state checks; does not define workflow semantics or backend authority policy
- Snippet file: `distribution/settings-snippets/project/taskcompleted-authoritative-state-gate.settings.jsonc`
- Paired hook source: `distribution/hooks/project/taskcompleted-authoritative-state-gate/hook.mjs`
- Supporting docs:
  - `distribution/hooks/project/taskcompleted-authoritative-state-gate/README.md`
  - `distribution/hooks/project/taskcompleted-authoritative-state-gate/scope.md`
  - `distribution/hooks/project/taskcompleted-authoritative-state-gate/manual-test.md`
  - `distribution/hooks/project/taskcompleted-authoritative-state-gate/rollback.md`

### `taskcompleted-verification-evidence-gate.settings.jsonc`

- Event: `TaskCompleted`
- Rule cluster: H-02 — durable verification evidence presence
- Purpose: register the H-02 hook with repo-local verification artifact, section, field, and placeholder configuration
- Boundary: only wires deterministic evidence-presence checks; does not choose commands, run verification, or judge evidence quality
- Snippet file: `distribution/settings-snippets/project/taskcompleted-verification-evidence-gate.settings.jsonc`
- Paired hook source: `distribution/hooks/project/taskcompleted-verification-evidence-gate/hook.mjs`
- Supporting docs:
  - `distribution/hooks/project/taskcompleted-verification-evidence-gate/README.md`
  - `distribution/hooks/project/taskcompleted-verification-evidence-gate/scope.md`
  - `distribution/hooks/project/taskcompleted-verification-evidence-gate/manual-test.md`
  - `distribution/hooks/project/taskcompleted-verification-evidence-gate/rollback.md`

### `taskcompleted-review-evidence-gate.settings.jsonc`

- Event: `TaskCompleted`
- Rule cluster: H-03 — review-required evidence presence
- Purpose: register the H-03 hook with repo-local review signal, artifact, field, placeholder, and PASS-token configuration
- Boundary: only wires deterministic review-evidence checks after a repo-defined review-required signal; does not infer review policy or assign reviewers
- Snippet file: `distribution/settings-snippets/project/taskcompleted-review-evidence-gate.settings.jsonc`
- Paired hook source: `distribution/hooks/project/taskcompleted-review-evidence-gate/hook.mjs`
- Supporting docs:
  - `distribution/hooks/project/taskcompleted-review-evidence-gate/README.md`
  - `distribution/hooks/project/taskcompleted-review-evidence-gate/scope.md`
  - `distribution/hooks/project/taskcompleted-review-evidence-gate/manual-test.md`
  - `distribution/hooks/project/taskcompleted-review-evidence-gate/rollback.md`

## References

- `docs/reference/hooks-scope.md` — Three-layer scope reference
- `docs/reference/superpowers-boundary.md` — Repository role and Superpowers boundary
- D-003: Hooks must be layered as user / project / local example only
- R-002: Hooks/settings must remain source/snippets only; opt-in per layer
