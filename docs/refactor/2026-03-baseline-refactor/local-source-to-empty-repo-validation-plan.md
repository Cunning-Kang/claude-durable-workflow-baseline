# local-source-to-empty-repo-validation-plan

**Validation Round:** local source repo → fresh empty repo adoption
**Date:** 2026-03-23
**Validator:** Claude (adoption simulation)
**Scope:** Local adoption path only; GitHub remote distribution out of scope

---

## Validation Objective

From a completely empty new directory, test whether the current local baseline source repo can serve as a source repo for adoption, without relying on any GitHub remote URL.

---

## What WILL Be Tested

1. **Entry clarity** — Can adopter find the adoption entry point from local docs?
2. **Local installation path** — Do the Quick Start / bootstrap steps work with local source (no GitHub)?
3. **Init script functionality** — Does `init-claude-workflow.sh` work from local cache?
4. **Baseline file creation** — Are all baseline files (docs/specs/_template/, docs/workflow/, memory/, claude/) correctly placed?
5. **Opt-in clarity for hooks/settings-snippets** — Are these assets discoverable?
6. **Scope/boundary understanding** — Is Superpowers vs baseline boundary clear to adopter?
7. **Operational usability** — Does adopter know how to verify successful adoption?
8. **Rollback guidance** — Is there guidance on how to undo the adoption?

---

## What Will NOT Be Tested

- GitHub remote clone URL
- Release/tag/download flow
- Remote distribution experience
- Any GitHub Pages or URL-based browsing

---

## Execution Steps

1. Create fresh empty git repo at `/private/tmp/baseline-adoption-test-<timestamp>/`
2. Copy source repo to `~/.claude/baselines/durable-workflow-v1/` (simulating local clone)
3. Copy global assets to `~/.claude/`
4. Copy commands and scripts to `~/.claude/`
5. Run `init-claude-workflow.sh` in the fresh empty repo
6. Inspect resulting file structure
7. Check documentation for discoverability of all assets (hooks, settings-snippets)
8. Assess scope/boundary clarity

---

## Success Criteria

- [ ] Fresh repo can be initialized without errors
- [ ] All 23 baseline files are created
- [ ] Version marker is written correctly
- [ ] No hooks/settings-snippets mention in init output (expected — they are opt-in)
- [ ] Bootstrap doc clearly lists all distributed assets
- [ ] Rollback guidance exists (or absence is documented)
