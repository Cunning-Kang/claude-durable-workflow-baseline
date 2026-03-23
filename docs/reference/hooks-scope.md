# Hooks Scope — Three-Layer Reference

> Status: Phase 3 Boundary Anchor | Date: 2026-03-22
> Purpose: Define scope boundaries and decision rules for hooks distributed from this repo.

---

## 1. Three Scopes Defined

### 1.1 `user` — User-Level Hooks

Hooks that live in `~/.claude/hooks/` and run at user level, across all projects.

**Characteristics:**
- Portable, project-agnostic
- Installed once, active for all repos using this baseline
- Examples: global lint helpers, commit-msg normalization, workspace-wide time-tracking triggers

**Planned Phase 3 source location:** `distribution/hooks/user/` — once the Phase 3 skeleton is materialized, this path holds source files only; users still copy them manually and opt in explicitly.

**Prohibited:**
- No automatic `~/.claude/` installation via bootstrap
- No competing with Superpowers skill entry points
- No modifying `~/.claude/settings.json` directly

---

### 1.2 `project` — Project-Level Hooks

Hooks that live in `<project>/.claude/hooks/` and run scoped to a single project repository.

**Characteristics:**
- Project-specific enforcement or conventions
- Intended for project adoption through the baseline flow once the Phase 3 distribution skeleton exists
- Examples: project-specific CI precondition checks, repo-local test helpers

**Planned Phase 3 source location:** `distribution/hooks/project/` — target path for source-only project hooks, still opt-in per project rather than default-on.

**Prohibited:**
- Not installed globally; tied to the project repo
- No automatic activation without explicit project adoption
- No competing with Superpowers or user-level hooks

---

### 1.3 `local example only` — Reference Implementations

Hooks that exist as learning references in documentation-adjacent locations such as `global/skills/`, or in a future Phase 3 example-only path if one is added. They are NOT installed automatically and do not ship as active distribution output.

**Characteristics:**
- Documentation/reference only
- User reads and copies what they need, manually
- Examples: annotated hook templates, commented enforcement snippets

**Reference surface:** `global/skills/*/hooks/` or an equivalent example-only location if Phase 3 later adds one — never part of any install path.

**Prohibited:**
- Never installed automatically
- Never distributed via `distribution/hooks/{user,project}/`
- Never shipped as part of baseline bootstrap

---

## 2. Decision Rule

Use this rule to classify any hook proposed for this repo:

```
Is it project-agnostic AND intended to run in ALL repos?
  → YES → user scope (distribution/hooks/user/)
  → NO  → Is it project-specific AND adopted through an explicit project-level opt-in step?
           → YES → project scope (distribution/hooks/project/)
           → NO  → Is it a reference / learning artifact only?
                    → YES → local example only
                    → NO  → do not add
```

**Hard stops — any of these disqualifies a hook from this repo:**
- Competes with a Superpowers skill entry point
- Modifies `~/.claude/settings.json` directly
- Auto-installs into a user's runtime without explicit opt-in
- Redirects or shadows primary control flow

---

## 3. Distribution Surface

| Scope | Source location | Install method | Auto-installed? | Lives in |
|-------|-----------------|----------------|-----------------|----------|
| `user` | `distribution/hooks/user/` (Phase 3 target) | Manual copy to `~/.claude/hooks/` after explicit adoption | **No** | `~/.claude/hooks/` |
| `project` | `distribution/hooks/project/` (Phase 3 target) | Project adopts into `<project>/.claude/hooks/` through an explicit init/copy step once supported | **No** (opt-in per project) | `<project>/.claude/hooks/` |
| `local example only` | `global/skills/*/hooks/` or equivalent example-only path | User reads and copies manually if needed | **No** | Source repo only |

---

## 4. Why Not Default Global?

Hooks are **not** globally enabled by default because:

1. **Environment dependency** — hooks run in user environments with varying toolchains, privilege levels, and risk tolerances. A hook that works for one user may break another.

2. **Team boundary differences** — project-level hooks encode team-specific conventions. Global installation crosses team boundaries and imposes one team's preferences on all.

3. **Superpowers control surface protection** — automatic hook installation could shadow or override Superpowers behavior, creating a competing control layer (R-002 risk).

4. **Opt-in correctness** — deterministic enforcement must be consciously adopted. Default-on enforcement is a policy decision that belongs to the user or team, not the distribution source.

5. **Traceability** — opt-in makes it explicit what is running in a given environment, which is critical for debugging and audit.

---

## 5. Relationship with Settings Snippets

Settings snippets follow the same three-layer scope and opt-in principle as hooks. In Phase 3, their intended source surface is `distribution/settings-snippets/`, but this document treats that as target layout rather than current implementation.

| Layer | Purpose | Install target | Auto-installed? |
|-------|---------|----------------|-----------------|
| `user` | User-level settings fragments | `~/.claude/settings.json` (merged manually) | **No** |
| `project` | Project-level settings fragments | `<project>/.claude/settings.json` (merged through an explicit project adoption step once supported) | **No** (opt-in) |
| `local example only` | Reference snippet templates | Not installed | **No** |

**Shared rules with hooks:**
- Both are source/template only, never live config
- Both must state "why not default global" in their README
- Both require explicit opt-in before entering a user environment
- Both must not compete with Superpowers entry points

---

## 6. Prohibited Patterns

The following patterns are forbidden in any hook or snippet from this repo:

- `~/.claude/settings.json` written directly (use snippets + manual merge)
- Automatic installation into `~/.claude/` without user action
- Default-on behavior that runs without opt-in
- Hooks that register competing skill entry points
- Hooks that redirect the primary Superpowers control flow
- Project-level hooks that run without the project's explicit adoption

---

## 7. Maintenance Checklist

Before accepting any new hook into this repo:

- [ ] Does it follow the decision rule in Section 2?
- [ ] Is it placed in the correct scope directory?
- [ ] Does its README state "why not default global"?
- [ ] Is it source/template only — no live config?
- [ ] Does it avoid all prohibited patterns in Section 6?
- [ ] Is it opt-in, not auto-installed?
- [ ] Does it coexist with Superpowers without competing?

---

## References

- D-003: Hooks must be layered as user / project / local example only
- D-006: Descriptive boundary docs belong in `docs/reference/`
- R-002: Hooks mis-globalization risk — only source/snippets; opt-in per layer
- Phase 3 plan: `docs/refactor/2026-03-baseline-refactor/plan.md`
