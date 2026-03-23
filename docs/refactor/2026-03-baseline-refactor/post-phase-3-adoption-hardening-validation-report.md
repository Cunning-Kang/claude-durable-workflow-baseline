# Post-Phase-3 Adoption / Hardening Validation Report

**Validation date:** 2026-03-22
**Phase:** Post-Phase-3B
**Validator:** Claude Code (adoption-survey mode)

---

## 1. Overall Judgment

**Result: FAIL — 1 blocking issue found**

The adoption surface is structurally sound and the vast majority of the content is correct and usable. However, one concrete error was found that would prevent an adopter from completing the manual-test verification step for H-03. This must be fixed before Phase 4 can be entered, as the validation gates require zero blocking issues.

---

## 2. Dimension Findings

### A. Discoverability — PASS

**Finding:** The root-level `distribution/hooks/project/README.md` and `distribution/settings-snippets/project/README.md` correctly serve as entry points. Each H-01 / H-02 / H-03 hook is listed with:
- Hook name and event (`TaskCompleted`)
- Rule cluster reference (H-01 / H-02 / H-03)
- Boundary summary
- Paired snippet path
- Per-doc paths (`README`, `scope.md`, `manual-test.md`, `rollback.md`)

The discovery path (choose hook → copy source → find paired snippet → merge → test → rollback) is clear and unambiguous.

**No issues.**

---

### B. Configurability — PASS

**Finding:** All three settings snippets correctly express:
- They are source-only example configuration, not live baseline wiring
- They must be merged into `<project>/.claude/settings.json`
- The `env \` prefix in the `command` string correctly shows environment-variable-based configuration
- Required vs. optional configuration is distinguishable via presence/absence of defaults in the hook code

The distinction between project-scope (adopted by copying) and global/user-scope (not applicable here) is clearly stated in both root READMEs.

**No blocking issues.** One cosmetic inconsistency noted below.

---

### C. Testability — **FAIL (blocking)**

**Finding for H-03:** Scenario 11 of `distribution/hooks/project/taskcompleted-review-evidence-gate/manual-test.md` contains a shell command typo:

```
WORKDIR="$(mntmp -d)"
```

The correct command is `mktemp -d`. Running `mntmp -d` in a bash shell produces a "command not found" error, which means the entire scenario — and therefore the H-03 PASS-token override verification path — cannot be executed as documented.

**Impact:** An adopter following the manual-test.md exactly will fail at scenario 11, preventing them from verifying one of H-03's core configurable behaviors (custom PASS tokens).

**Severity: Blocking**
**Affected step:** H-03 → manual-test.md → scenario 11 ("Configured PASS tokens override works")

**No issues found in H-01 or H-02 manual-test.md.**

---

### D. Rollback Safety — PASS

**Finding:** All three rollback.md files correctly describe:
- Removing the `TaskCompleted` registration from `<project>/.claude/settings.json`
- Removing the copied hook file from `<project>/.claude/hooks/<hook-name>/hook.mjs`
- Confirming task completion is no longer gated after removal

The "what rollback does not include" section in each file is accurate.

**No blocking issues.** One non-blocking wording issue noted for H-02 (see §3 below).

---

### E. Boundary Clarity — PASS

**Finding:** All three hooks correctly state:
- They only enforce machine-checkable deterministic subsets
- They do not encode policy or replace human judgment
- They are not a second control plane
- Boundary ownership maps correctly to: protocol docs (boundary definition) / Superpowers (orchestration) / human judgment (subjective decisions)

**No issues.**

---

## 3. Issue Listing

### Blocking

| # | Location | Issue | Impact | Fix |
|---|---|---|---|---|
| B-1 | `distribution/hooks/project/taskcompleted-review-evidence-gate/manual-test.md` line 260 | `mntmp -d` should be `mktemp -d` | Scenario 11 of H-03 manual-test fails with "command not found" | One-word fix: replace `mntmp` with `mktemp` |

### Important but Non-blocking

| # | Location | Issue | Impact | Fix |
|---|---|---|---|---|
| N-1 | `distribution/settings-snippets/project/taskcompleted-verification-evidence-gate.settings.jsonc` | Header comment includes extra explanatory text ("H-02 checks durable verification evidence presence... It does NOT run tests...") not present in H-01 or H-03 snippets | Slight inconsistency in snippet style; adopter may wonder why H-02 has extra preamble | Align H-02 snippet header style with H-01/H-03 (minimal header only) |
| N-2 | `distribution/hooks/project/taskcompleted-verification-evidence-gate/rollback.md` step 2 | Mentions "shell profiles" for removing env exports | Project-scope hooks configure env vars inline in `settings.json` command string, not via shell profile files. The wording could mislead adopters into looking for a shell profile file | Change "shell profiles" wording to: "Remove any env var exports added to your project shell configuration if you configured them as persistent environment variables rather than inline in settings.json" |
| N-3 | `distribution/hooks/project/taskcompleted-verification-evidence-gate/README.md` | Lacks a visible "Adoption model" section (H-01 and H-03 both have one) | Inconsistency across hook READMEs may cause slight confusion | Add "Adoption model" section to H-02 README consistent with H-01/H-03 |

### Cosmetic

| # | Location | Issue | Impact |
|---|---|---|---|
| C-1 | `distribution/hooks/project/taskcompleted-verification-evidence-gate/README.md` | "Adoption model" section heading absent; the content may be present under different heading | Minor style inconsistency |

---

## 4. Follow-up Item Review

The Phase 3B closeout listed three follow-up items:

| Follow-up Item | Classification | Adoption Impact | Verdict |
|---|---|---|---|
| **H-02 supporting docs 文案一致性** (H-02 README/rollback style differs from H-01/H-03) | Cosmetic / Important non-blocking | Low — adopters can still understand H-02; consistency issue only | Confirmed non-blocking; captured as N-1 and N-3 above |
| **H-02 rollback 中 shell-profile env exports 表述** | Important non-blocking | Medium — could mislead adopter looking for shell profile file | Confirmed non-blocking; captured as N-2 above |
| **H-03 manual-test scenario 11 `mntmp -d` 拼写** | **Blocking** | High — makes scenario 11 unrunnable | **Elevated to blocking; must fix before Phase 4** |

**Conclusion on follow-up items:** Two of the three follow-up items are genuinely non-blocking. One (`mntmp -d`) is blocking and was not fully estimated in the closeout — it prevents the adopter from completing the H-03 verification step.

---

## 5. Adoption Surface Overall Assessment

| Dimension | Status | Notes |
|---|---|---|
| Discoverability | ✅ PASS | Index structure, hook naming, and path layout are correct |
| Configurability | ✅ PASS | Snippet format, env-var config, and opt-in language are clear |
| Testability | ❌ FAIL | One blocking error in H-03 manual-test |
| Rollback Safety | ✅ PASS | Rollback steps are clear and accurate |
| Boundary Clarity | ✅ PASS | Hook purpose and limits are well-documented |

**Overall: Usable but not yet stable.** The blocking issue must be resolved.

---

## 6. Next-Step Recommendation

### Recommended: Very small hardening patch round (not Phase 4 entry)

**Rationale:** The validation acceptance criteria require zero blocking issues before Phase 4 entry. Exactly one blocking issue exists (`mntmp -d` in H-03 scenario 11). Fixing this is a single-word change. No other adoption-blocking problems were found.

**Scope of patch round:**
- Fix `mntmp` → `mktemp` in H-03 `manual-test.md` scenario 11
- Optionally address N-1, N-2, N-3 in the same round if low-effort (N-2 is also a small wording fix)
- Do NOT expand scope beyond these items
- Do NOT touch hook logic or Phase 3B authoritative docs

**After patch:** Re-run a focused re-check on the fixed items, then Phase 4 may begin.

---

## Appendix: Files Reviewed

### Hook sources
- `distribution/hooks/project/taskcompleted-authoritative-state-gate/hook.mjs`
- `distribution/hooks/project/taskcompleted-verification-evidence-gate/hook.mjs`
- `distribution/hooks/project/taskcompleted-review-evidence-gate/hook.mjs`

### Hook docs (per hook)
- `distribution/hooks/project/*/README.md`
- `distribution/hooks/project/*/scope.md`
- `distribution/hooks/project/*/manual-test.md`
- `distribution/hooks/project/*/rollback.md`

### Snippets
- `distribution/settings-snippets/project/taskcompleted-authoritative-state-gate.settings.jsonc`
- `distribution/settings-snippets/project/taskcompleted-verification-evidence-gate.settings.jsonc`
- `distribution/settings-snippets/project/taskcompleted-review-evidence-gate.settings.jsonc`

### Index docs
- `distribution/hooks/project/README.md`
- `distribution/settings-snippets/project/README.md`

### Phase 3B closeout
- `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementation-closeout.md`
