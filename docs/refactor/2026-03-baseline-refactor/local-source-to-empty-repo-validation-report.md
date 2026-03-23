# local-source-to-empty-repo-validation-report

**Validation Round:** local source repo → fresh empty repo adoption
**Date:** 2026-03-23
**Source repo:** `/Users/cunning/Workspaces/heavy/claude-durable-workflow-baseline`
**Baseline cache:** `~/.claude/baselines/durable-workflow-v1/`
**Adopted test repo:** `/private/tmp/baseline-adoption-test-1774237308/`
**Scope:** Local adoption path only; GitHub remote distribution out of scope
**Independent review rounds:** 2 (agents: rigorous-audit, pov-assessment)

---

## A. Files Created

- `docs/refactor/2026-03-baseline-refactor/local-source-to-empty-repo-validation-plan.md`
- `docs/refactor/2026-03-baseline-refactor/local-source-to-empty-repo-validation-report.md` (this document)

---

## B. Local Adoption Summary

**Result: PASSED with non-blocking issues**

The core local adoption path is fully functional. The source repo correctly produces 23 baseline items (16 files + 7 directories) in the target repo, the init script works, and the version marker is written correctly.

**Blocking issues: None**

**Important non-blocking issues:**

1. **`distribution/hooks/` and `distribution/settings-snippets/` are completely invisible in adoption docs** — the bootstrap doc's "Source Repo Asset Inventory" section does not list these directories at all (grep returns 0 matches for "hooks" and "settings-snippets"). An adopter reading the Quick Start or asset inventory would never know these assets exist.

2. **`global/commands/finish-branch.md` is in git history but not actively documented** — git status shows `deleted: global/commands/finish-branch.md` (removed from working tree but still in committed history). The bootstrap doc's Superpowers entry mapping table says `/finish-branch` is "provided by Superpowers" but the file's prior existence is not explained. Adopters reading git history or older documentation could be confused.

3. **No rollback guidance in init output** — the init output tells adopters to "commit the baseline files" but provides no guidance on how to undo initialization.

4. **Superpowers/baseline boundary not reinforced post-init** — the bootstrap doc clearly explains the boundary, but the init output itself does not mention Superpowers at all.

5. **README Quick Start has no local-path variant** — the README hardcodes `git clone https://github.com/Cunning-Kang/...`. Only the separate `claude-one-command-bootstrap.md` document describes the local `cp -r` approach. An adopter who reads only the README would not know how to proceed without GitHub.

---

## C. What This Validation Proves

1. **The source repo CAN be adopted locally** — without any GitHub remote, an adopter can copy the source repo to `~/.claude/baselines/durable-workflow-v1/`, install global assets, and successfully initialize a new repo.

2. **The init script path resolution works** — `BASELINE_CACHE_ROOT` and `BASELINE_DIR` resolution is correct; the script finds baseline files from the local cache.

3. **All 23 baseline items are created correctly** (16 files + 7 directories) — `docs/specs/_template/`, `docs/workflow/`, `memory/`, `claude/claude-snippet.md`, `.gitignore` all land correctly.

4. **Version marker is written correctly** — `.claude/workflow-baseline-version` contains baseline version, timestamp, and repo path.

5. **The bootstrap doc's local `cp -r` approach is executable** — substituting `git clone https://...` with local `cp -r` yields a working installation. However, the README itself does not document this local path.

6. **`instantiate-feature.sh` has no-overwrite safety** — the script uses `mkdir`-based error guards to prevent overwriting existing feature directories (not `cp -n` as sometimes described — the mechanism is mkdir error-exit, not cp flags).

---

## D. What This Validation Does NOT Prove

### GitHub Remote Distribution (NOT verified)

- Remote clone URL (`https://github.com/Cunning-Kang/claude-durable-workflow-baseline.git`) has not been tested
- Release page / tag / asset download flow has not been tested
- Whether the GitHub URL in bootstrap docs matches the actual repo has not been verified
- No verification that `git clone` from GitHub produces identical structure to local `cp -r`

### Hooks/Settings-Snippets Adoption (NOT implemented — Phase 3 planned)

- `distribution/hooks/project/` exists and has proper structure (README, scope, hook.mjs, manual-test, rollback)
- `distribution/settings-snippets/` exists and has proper structure (settings JSONC files)
- **There is no installation path for hooks/settings-snippets** — both READMEs explicitly state "source-only distribution, not auto-install"
- These are documented as **Phase 3 / Phase 3B planned future work**, not current implementation
- Whether they can be installed into a target repo has NOT been tested — no install script or command exists for them

### Superpowers Integration (NOT verified)

- The baseline is designed to be used WITH Superpowers skills (brainstorming, finish-branch, etc.)
- Whether Superpowers is available/activatable in the adopted repo environment has not been tested
- Whether the `finish-branch` skill in Superpowers is the replacement for the removed `global/commands/finish-branch.md` is implied but not explicitly stated in adoption docs

### Rollback (NOT tested)

- No evidence that rollback was actually exercised during validation
- Source docs show rollback is documented in hooks/settings READMEs but never tested

---

## E. Key Findings

### IMPORTANT (adoption friction, not blocking)

**I-1: Hooks and settings-snippets are undocumented in adoption flow**
- `distribution/hooks/` and `distribution/settings-snippets/` are absent from the bootstrap doc's "Source Repo Asset Inventory" section
- Init output does not mention them
- Quick Start steps do not reference them
- These are explicitly Phase 3 planned features, not a missing bug — but the inventory omission means adopters who need project-level hooks (taskcompleted gates) will not know they exist as source assets

**I-2: `finish-branch.md` in git history creates confusion risk**
- `global/commands/finish-branch.md` was deleted from the working tree (`git status: deleted`) but remains in git history
- The bootstrap doc's Superpowers entry mapping says `/finish-branch` is "provided by Superpowers"
- No documentation explains the transition or why the file was removed
- Risk: adopters reading git history or older docs will find the file and be confused about its status

**I-3: No rollback guidance in init output**
- Init output tells adopter to "commit the baseline files"
- No guidance on how to undo (e.g., `git rm -rf docs/specs docs/workflow memory claude .claude && git commit`)
- Rollback for this L0 change should be trivially reversible

**I-4: Superpowers/baseline boundary not reinforced in init output**
- Init output mentions "use Superpowers skills (e.g., /brainstorming)" as a next step
- But it does not explain that baseline is a passive knowledge layer, not a second control plane
- An adopter who skips the bootstrap doc may treat baseline files as live defaults

**I-5: README has no local-path variant**
- README Quick Start hardcodes `git clone https://github.com/Cunning-Kang/claude-durable-workflow-baseline.git`
- The local `cp -r` approach is only documented in `claude-one-command-bootstrap.md`
- An adopter reading only the README would believe GitHub is required
- This is partially mitigated by the bootstrap doc's existence, but the README is the primary entry point

### MINOR (informational)

**m-1: `instantiate-feature.sh` no-overwrite safety mechanism is mkdir-based, not `cp -n`**
- The original report described "cp -n (no-overwrite) safety" — this is imprecise
- The script uses `mkdir`-based error guards (`if [[ -e "$FEATURE_DIR" ]]` exit) to prevent overwriting
- This is a documentation clarity issue, not a functional defect

**m-2: Bootstrap doc is well-structured for those who read it**
- The "明确不要做的事" section is clear
- The "主控层 vs 增强层边界" section is clear
- The Superpowers entry mapping table is useful
- But adopters who only follow Quick Start steps may never see these sections

---

## F. Final Judgment

**Passed** — The core adoption path is fully functional. All findings are documentation/invisibility gaps, not functional failures. The source repo can be adopted locally right now.

---

## G. Next Recommendation

**Can proceed as local source repo; fix I-1 and I-2 before first push to GitHub**

### Immediate (before GitHub push)

1. **I-1**: Add `distribution/hooks/` and `distribution/settings-snippets/` to the bootstrap doc's "Source Repo Asset Inventory" section, with explicit note: "these are Phase 3 planned assets; source-only distribution, not auto-installed by init-claude-workflow"

2. **I-2**: Add a brief note in the bootstrap doc or `global/README.md` explaining that `global/commands/finish-branch.md` was removed and replaced by the Superpowers `/finish-branch` skill

### Optional improvements (non-blocking)

3. **I-3**: Add a one-liner rollback note to init output: "To rollback: `git rm -rf docs/specs docs/workflow memory claude .claude && git commit -m 'chore: remove baseline'`"

4. **I-4**: Add one sentence to init output: "Baseline files are passive knowledge structure — Superpowers remains the sole control plane"

5. **I-5**: Add a parenthetical to the README Quick Start: "(for local-only adoption without GitHub, see docs/claude-one-command-bootstrap.md)"

### After GitHub push (next validation round)

- Verify remote clone URL works
- Verify release/tag page structure
- Verify adopter experience when cloning from GitHub

---

## Validation Boundary Summary

| Dimension | Status | Notes |
|-----------|--------|-------|
| Local source copy | ✅ PASS | `cp -r` to baseline cache works |
| Global asset install | ✅ PASS | `global/*` → `~/.claude/` works |
| Command/script install | ✅ PASS | commands + scripts land correctly |
| Init script execution | ✅ PASS | 23 items created (16 files + 7 dirs), version marker written |
| Hooks/settings-snippets discoverability | ⚠️ FAIL | Not listed in adoption docs; Phase 3 planned |
| finish-branch.md confusion risk | ⚠️ WARN | Deleted from working tree but in git history |
| Rollback guidance | ⚠️ MISSING | No guidance in init output |
| Superpowers boundary clarity | ⚠️ PARTIAL | Clear in bootstrap doc, absent from init output |
| README local-path variant | ⚠️ MISSING | Only in bootstrap doc, not README |
| GitHub remote clone | ❌ NOT TESTED | Out of scope |
| Release/tag flow | ❌ NOT TESTED | Out of scope |
| Remote URL correctness | ❌ NOT TESTED | Out of scope |

---

## Independent Review Notes

Two independent agent audits were conducted:

**Agent 1 (rigorous-audit)** identified:
- The "cp -n" description was imprecise (uses mkdir error-exit, not cp flags) — confirmed correct
- Hooks/settings are Phase 3 planned, not current — confirmed by source READMEs
- Hooks/settings are correctly identified as "source-only" with no install path — confirmed

**Agent 2 (pov-assessment)** identified:
- README has no local-path variant (only bootstrap doc does) — confirmed; corrected the report's claim
- I-2 finding about finish-branch.md was stale — partially corrected; file is deleted from working tree but still in git history
- 23 baseline items count is CORRECT (16 files + 7 directories = 23 total items) — the agent's disputed claim of "21 items" was wrong; the original report was accurate

**Corrections applied to this revision:**
- I-2 reframed to reflect git history confusion risk rather than "stale file gets copied"
- "Quick Start local variant" claim narrowed to "bootstrap doc's approach is executable; README has no local variant"
- Added Phase 3 planned context to hooks/settings
- Clarified instantiate-feature.sh mechanism as mkdir-based, not cp-n
