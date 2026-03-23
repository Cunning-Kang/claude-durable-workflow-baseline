# Post-Phase-3 Adoption / Hardening Validation Plan

## A. Goal

Validate whether the Phase 3B hook adoption surface is genuinely usable by a hypothetical adopter arriving at an empty repo, without prior Phase 3B context, who must discover → configure → test → rollback H-01 / H-02 / H-03.

## B. Scope

### In scope
- `distribution/hooks/project/taskcompleted-authoritative-state-gate/` (H-01)
- `distribution/hooks/project/taskcompleted-verification-evidence-gate/` (H-02)
- `distribution/hooks/project/taskcompleted-review-evidence-gate/` (H-03)
- `distribution/settings-snippets/project/` paired snippets
- `distribution/hooks/project/README.md` and `distribution/settings-snippets/project/README.md`
- All per-hook `README.md`, `scope.md`, `manual-test.md`, `rollback.md`

### Out of scope
- Phase 4 planning or artifacts
- Any new hook candidate or cluster
- Live global or project wiring in baseline repo
- Changes to authoritative Phase 3B design/tasks docs
- Shell-profile or user-level configuration
- Implementation logic changes

## C. Non-goals

- Not a security audit
- Not a code review of hook logic correctness (that was Phase 3B's job)
- Not an expansion of hook capability
- Not a test suite implementation
- Not a live rollout verification

## D. Adopter Assumptions

An adopter who:
1. Has a clean or existing project using Claude Code
2. Has read the baseline `README.md` at root
3. Finds `distribution/hooks/project/README.md` and `distribution/settings-snippets/project/README.md`
4. Chooses to opt in to one or more of H-01 / H-02 / H-03
5. Must follow only the documents provided to adopt, test, and roll back

## E. Validation Dimensions

### A. Discoverability
Can the adopter find each hook, its paired snippet, and all required docs?

### B. Configurability
Can the adopter understand what to configure, where, and why the defaults are not live wiring?

### C. Testability
Can the adopter run the manual-test steps without external tooling, special environment setup, or prior knowledge?

### D. Rollback Safety
Can the adopter cleanly undo adoption without leaving ambiguous state or false impressions?

### E. Boundary Clarity
Will the adopter correctly understand what the hooks do and do not do, and not mistake them for a second control plane?

## F. Validation Steps

### Step 1 — Read all distribution README index files
- Confirm H-01 / H-02 / H-03 are listed with paths and descriptions
- Confirm adoption path (copy hook → merge snippet → test → rollback) is clear

### Step 2 — Read each hook's README
- Confirm purpose, what-it-checks, and what-it-does-not-check are clear
- Confirm "not a second control plane" framing is convincing
- Confirm "Adoption model" section exists and is consistent across all three

### Step 3 — Read each hook's scope.md
- Confirm machine-checkable subset vs. intentionally omitted scope is clear
- Confirm boundary ownership (protocol docs / Superpowers / human judgment) is explicit

### Step 4 — Read each hook's manual-test.md
- Confirm all scenarios are executable with only the described setup
- Confirm all shell commands use correct tool names
- Confirm no typos in commands

### Step 5 — Read each hook's rollback.md
- Confirm rollback steps are unambiguous
- Confirm no mention of mechanisms that don't apply (e.g., shell profiles for project-scope hooks)

### Step 6 — Read each settings snippet
- Confirm snippet comments explain what the snippet does and does not configure
- Confirm no extra mechanisms are implied beyond what's actually in the snippet

### Step 7 — Cross-check closeout follow-up items
- Confirm each follow-up item is correctly classified as blocking vs. non-blocking vs. cosmetic

## G. Acceptance Criteria

- **Blocking issues: 0** — any blocking issue means this validation fails and a patch round is required before Phase 4
- **Important but non-blocking issues: documented** — will be listed in report but do not prevent Phase 4 entry
- **Cosmetic issues: documented** — will be listed in report but do not prevent Phase 4 entry
- **Adoption surface is self-consistent** — a reasonably careful adopter should be able to complete the full adopt → test → rollback cycle using only the provided docs

## H. Issue Severity Definitions

| Severity | Definition | Effect on Phase 4 |
|---|---|---|
| **Blocking** | Prevents adopter from completing any critical adoption step (discover, configure, test, rollback) | Blocks Phase 4 entry until fixed |
| **Important but non-blocking** | Causes meaningful confusion or risk but adopter can work around | Phase 4 entry allowed; fix in future patch |
| **Cosmetic** | Style, wording, or formatting inconsistency | Phase 4 entry allowed; fix in future patch |

## I. Validation Report Structure

The validation report will contain:
1. Overall judgment (PASS / FAIL against acceptance criteria)
2. Per-dimension findings (A through E)
3. Per-issue severity listing (Blocking / Important / Cosmetic)
4. Follow-up item review against adoption impact
5. Clear next-step recommendation
