# `distribution/hooks/project/` — Project-Level Hooks Source

> Scope: Phase 3 Boundary Anchor | Date: 2026-03-22
> Purpose: Hold source-only project-level hooks distributed from this baseline repo.

---

## What This Is

Source files in this directory are **project-level hooks** — scripts scoped to a single project repository, not a user's global runtime.

**Target install location after explicit project adoption:** `<project>/.claude/hooks/`

These hooks are distributed as source snippets. They do **not** auto-install into global user space.

---

## Appropriate Use Cases

- Project-specific CI precondition checks
- Repo-local test helpers
- Project-specific enforcement or convention scripts

---

## Installation Method

Project-level hooks are **source-only distribution, not auto-install and not global default**.

1. Once project-level hook adoption is supported in the Phase 3 distribution flow, a project may choose an explicit project-level adoption step.
2. Project maintainers explicitly copy the desired hook to `<project>/.claude/hooks/`.
3. The hook is intended to be active only within that project repository.

**This directory is NOT for global installation.** Installing these hooks into `~/.claude/hooks/` would make them user-level hooks — which is the wrong scope and may produce unexpected behavior across projects.

---

## Why Not Default Global

1. **Project boundary respect** — project-level hooks encode team-specific conventions. Global installation crosses team boundaries and imposes one team's preferences on all.
2. **Non-portability** — a hook appropriate for one project may be irrelevant or harmful in another.
3. **Superpowers control surface protection** — automatic activation could shadow or override Superpowers behavior (see `docs/reference/superpowers-boundary.md`).
4. **Opt-in correctness** — enforcement must be consciously adopted per project, not forced on every repo.
5. **Traceability** — explicit installation makes it clear what is running in a given project.

---

## Opt-In Principle

Hooks in this directory are **never globally enabled by default**. They require:
- An explicit project-level adoption step
- A deliberate copy into `<project>/.claude/hooks/`

---

## Cannot Be Installed as Global Default

**Hard rule:** Project-level hooks from this directory must never be installed as a global default behavior.

Installing to `~/.claude/hooks/` converts them to user-level hooks — this is **not** the intended behavior and may cause:
- Cross-project contamination of hook behavior
- Conflicts with Superpowers skill entry points
- Unexpected enforcement in repos that never opted in

If you need global behavior, use `distribution/hooks/user/` instead.

---

## Relationship with Superpowers

Project-level hooks from this repo must **not**:
- Register competing skill entry points
- Redirect or shadow the primary Superpowers control flow
- Override or shadow hooks in `distribution/hooks/user/`

Hooks that compete with Superpowers or user-level hooks are prohibited. See `docs/reference/superpowers-boundary.md` and `docs/reference/hooks-scope.md`.

---

## Scope Decision Rule

```
Is it project-agnostic AND intended to run in ALL repos?
  → YES → user scope (distribution/hooks/user/)
  → NO  → Is it project-specific AND adopted through an explicit project-level opt-in step?
           → YES → project scope (this directory)
           → NO  → local example only; do not add to this directory
```

---

## Phase 3B candidate index

All candidates below are **project-scope, source-only, opt-in templates**. They are **not live default wiring** in this baseline repo. Adoption requires copying the hook into `<project>/.claude/hooks/` and manually merging the paired snippet from `distribution/settings-snippets/project/` into `<project>/.claude/settings.json`.

### `taskcompleted-authoritative-state-gate`

- Event: `TaskCompleted`
- Rule cluster: H-01 — authoritative completion-state consistency
- Boundary: completion-time durable tracker consistency only; no authoritative-backend selection, no next-task derivation, no backlog orchestration
- Hook source: `distribution/hooks/project/taskcompleted-authoritative-state-gate/hook.mjs`
- Settings snippet: `distribution/settings-snippets/project/taskcompleted-authoritative-state-gate.settings.jsonc`
- Supporting docs:
  - `distribution/hooks/project/taskcompleted-authoritative-state-gate/README.md`
  - `distribution/hooks/project/taskcompleted-authoritative-state-gate/scope.md`
  - `distribution/hooks/project/taskcompleted-authoritative-state-gate/manual-test.md`
  - `distribution/hooks/project/taskcompleted-authoritative-state-gate/rollback.md`

### `taskcompleted-verification-evidence-gate`

- Event: `TaskCompleted`
- Rule cluster: H-02 — durable verification evidence presence
- Boundary: completion-time evidence presence only; no command selection, no test execution, no quality/freshness judgment beyond the durable record
- Hook source: `distribution/hooks/project/taskcompleted-verification-evidence-gate/hook.mjs`
- Settings snippet: `distribution/settings-snippets/project/taskcompleted-verification-evidence-gate.settings.jsonc`
- Supporting docs:
  - `distribution/hooks/project/taskcompleted-verification-evidence-gate/README.md`
  - `distribution/hooks/project/taskcompleted-verification-evidence-gate/scope.md`
  - `distribution/hooks/project/taskcompleted-verification-evidence-gate/manual-test.md`
  - `distribution/hooks/project/taskcompleted-verification-evidence-gate/rollback.md`

### `taskcompleted-review-evidence-gate`

- Event: `TaskCompleted`
- Rule cluster: H-03 — review-required evidence presence
- Boundary: signal-driven review evidence presence only; no review-requirement inference, no reviewer assignment, no review-quality evaluation
- Hook source: `distribution/hooks/project/taskcompleted-review-evidence-gate/hook.mjs`
- Settings snippet: `distribution/settings-snippets/project/taskcompleted-review-evidence-gate.settings.jsonc`
- Supporting docs:
  - `distribution/hooks/project/taskcompleted-review-evidence-gate/README.md`
  - `distribution/hooks/project/taskcompleted-review-evidence-gate/scope.md`
  - `distribution/hooks/project/taskcompleted-review-evidence-gate/manual-test.md`
  - `distribution/hooks/project/taskcompleted-review-evidence-gate/rollback.md`

## References

- `docs/reference/hooks-scope.md` — Three-layer scope reference
- `docs/reference/superpowers-boundary.md` — Repository role and Superpowers boundary
- D-003: Hooks must be layered as user / project / local example only
- R-002: Hooks mis-globalization risk — source/snippets only; opt-in per layer
