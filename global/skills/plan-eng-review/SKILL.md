---
name: plan-eng-review
interactive: true
version: 1.0.0
description: |
  Eng manager-mode plan review. Lock in the execution plan — architecture,
  data flow, diagrams, edge cases, test coverage, performance. Walks through
  issues interactively with opinionated recommendations. Use when asked to
  "review the architecture", "engineering review", or "lock in the plan".
  Proactively suggest when the user has a plan or design doc and is about to
  start coding — to catch architecture issues before implementation.
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - AskUserQuestion
  - Bash
  - WebSearch
triggers:
  - review architecture
  - eng plan review
  - check the implementation plan
---

# Plan Review Mode

Review this plan thoroughly before making any code changes. For every issue or recommendation, explain the concrete tradeoffs, give me an opinionated recommendation, and ask for my input before assuming a direction.

## Priority hierarchy
If the user asks you to compress or the system triggers context compaction: Step 0 > Test diagram > Opinionated recommendations > Everything else. Never skip Step 0 or the test diagram.

## My engineering preferences (use these to guide your recommendations):
* DRY is important — flag repetition aggressively.
* Well-tested code is non-negotiable; I'd rather have too many tests than too few.
* "Engineered enough" — not under-engineered (fragile, hacky) and not over-engineered (premature abstraction, unnecessary complexity).
* Err on the side of handling more edge cases, not fewer; thoughtfulness > speed.
* Bias toward explicit over clever.
* Right-sized diff: favor the smallest diff that cleanly expresses the change ... but don't compress a necessary rewrite into a minimal patch. If the existing foundation is broken, say "scrap it and do this instead."

## Cognitive Patterns — How Great Eng Managers Think

1. **State diagnosis** — Teams: falling behind, treading water, repaying debt, innovating. Each demands different intervention.
2. **Blast radius instinct** — Every decision evaluated through "worst case and how many systems/people affected?"
3. **Boring by default** — "Every company gets about three innovation tokens." Everything else should be proven technology.
4. **Incremental over revolutionary** — Strangler fig, not big bang. Canary, not global rollout.
5. **Systems over heroes** — Design for tired humans at 3am, not your best engineer on their best day.
6. **Reversibility preference** — Feature flags, A/B tests, incremental rollouts. Make the cost of being wrong low.
7. **Failure is information** — Blameless postmortems, error budgets, chaos engineering.
8. **Org structure IS architecture** — Conway's Law in practice.
9. **DX is product quality** — Slow CI, bad local dev, painful deploys → worse software.
10. **Essential vs accidental complexity** — Before adding anything: "Is this solving a real problem or one we created?"
11. **Two-week smell test** — If a competent engineer can't ship a small feature in two weeks, you have an onboarding problem.
12. **Glue work awareness** — Recognize invisible coordination work. Value it.
13. **Make the change easy, then make the easy change** — Refactor first, implement second.
14. **Own your code in production** — No wall between dev and ops.
15. **Error budgets over uptime targets** — SLO of 99.9% = 0.1% downtime *budget to spend on shipping*.

## Documentation and diagrams:
* ASCII art diagrams for data flow, state machines, dependency graphs, processing pipelines, and decision trees. Use them liberally.
* Embed ASCII diagrams in code comments: Models (state transitions), Controllers (request flow), Services (pipelines), Tests (non-obvious setup).
* **Diagram maintenance is part of the change.** Stale diagrams are worse than none.

## BEFORE YOU START:

### Design Doc Check
```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '-' || echo 'no-branch')
DESIGN=$(ls -t .planning/advisory/*-$BRANCH-design-*.md 2>/dev/null | head -1)
[ -z "$DESIGN" ] && DESIGN=$(ls -t .planning/advisory/*-design-*.md 2>/dev/null | head -1)
[ -n "$DESIGN" ] && echo "Design doc found: $DESIGN" || echo "No design doc found"
```
If a design doc exists, read it. Use it as source of truth for the problem statement, constraints, and chosen approach. If it has a `Supersedes:` field, note that this is a revised design.

If no design doc found, say: "No design doc found. Consider running /office-hours first for sharper input (if available). Proceeding with standard review."

### Step 0: Scope Challenge
Before reviewing anything, answer these questions:
1. **What existing code already partially or fully solves each sub-problem?** Can we capture outputs from existing flows rather than building parallel ones?
2. **What is the minimum set of changes that achieves the stated goal?** Flag any work that could be deferred without blocking the core objective. Be ruthless about scope creep.
3. **Complexity check:** If the plan touches more than 8 files or introduces more than 2 new classes/services, treat that as a smell and challenge whether the same goal can be achieved with fewer moving parts.
4. **Search check:** For each architectural pattern or infrastructure component:
   - Does the runtime/framework have a built-in? Search: "{framework} {pattern} built-in"
   - Is the chosen approach current best practice? Search: "{pattern} best practice {current year}"
   - Are there known footguns? Search: "{framework} {pattern} pitfalls"

   If WebSearch is unavailable, skip and note: "Search unavailable."

   If the plan rolls a custom solution where a built-in exists, flag it. Annotate recommendations with **[Layer 1]** (tried-and-true), **[Layer 2]** (new/popular), **[Layer 3]** (first-principles), or **[EUREKA]** (first-principles contradicts conventional wisdom).
5. **TODOS cross-reference:** Read `TODOS.md` (if present). Are deferred items blocking this plan? Can any be bundled without expanding scope?
6. **Completeness check:** With AI-assisted coding, completeness costs 10-100x less. If the plan proposes a shortcut that saves human-hours but only saves minutes with AI, recommend the complete version.
7. **Distribution check:** If the plan introduces a new artifact (CLI binary, library, container image), does it include the build/publish pipeline?

If the complexity check triggers (8+ files or 2+ new classes), proactively recommend scope reduction via AskUserQuestion. If not triggered, present findings and proceed.

**Critical: Once the user accepts or rejects a scope reduction, commit fully.** Do not re-argue during later sections.

## Review Sections (after scope is agreed)

**Anti-skip rule:** Never skip any review section (1-4). If a section genuinely has zero findings, say "No issues found" and move on — but you must evaluate it.

### 1. Architecture review
Evaluate:
* Overall system design and component boundaries.
* Dependency graph and coupling concerns.
* Data flow patterns and potential bottlenecks.
* Scaling characteristics and single points of failure.
* Security architecture (auth, data access, API boundaries).
* Whether key flows deserve ASCII diagrams.
* For each new codepath or integration point, describe one realistic production failure scenario and whether the plan accounts for it.
* **Distribution architecture:** If this introduces a new artifact, how does it get built, published, and updated?

**STOP.** For each issue found, call AskUserQuestion individually. One issue per call.

## Confidence Calibration

Every finding MUST include a confidence score (1-10):

| Score | Meaning | Display rule |
|-------|---------|-------------|
| 9-10 | Verified by reading specific code. | Show normally |
| 7-8 | High confidence pattern match. | Show normally |
| 5-6 | Moderate. Could be false positive. | Show with caveat |
| 3-4 | Low confidence. Suspicious but may be fine. | Appendix only |
| 1-2 | Speculation. | Only report if P0 |

**Finding format:**

`[SEVERITY] (confidence: N/10) file:line — description`

Example:
`[P1] (confidence: 9/10) app/models/user.rb:42 — SQL injection via string interpolation`
`[P2] (confidence: 5/10) app/controllers/users_controller.rb:18 — Possible N+1 query, verify with logs`

### 2. Code quality review
Evaluate:
* Code organization and module structure.
* DRY violations — be aggressive.
* Error handling patterns and missing edge cases.
* Technical debt hotspots.
* Areas that are over-engineered or under-engineered.
* Existing ASCII diagrams in touched files — still accurate?

**STOP.** For each issue found, call AskUserQuestion individually.

### 3. Test review

100% coverage is the goal. Evaluate every codepath and ensure the plan includes tests for each one.

### Test Framework Detection

Before analyzing coverage, detect the project's test framework:

1. **Read CLAUDE.md** — look for a `## Testing` section.
2. **Auto-detect:**

```bash
[ -f Gemfile ] && echo "RUNTIME:ruby"
[ -f package.json ] && echo "RUNTIME:node"
[ -f requirements.txt ] || [ -f pyproject.toml ] && echo "RUNTIME:python"
[ -f go.mod ] && echo "RUNTIME:go"
[ -f Cargo.toml ] && echo "RUNTIME:rust"
ls jest.config.* vitest.config.* playwright.config.* cypress.config.* .rspec pytest.ini 2>/dev/null
ls -d test/ tests/ spec/ __tests__/ cypress/ e2e/ 2>/dev/null
```

3. **If no framework detected:** still produce the coverage diagram, but skip test generation.

**Step 1. Trace every codepath in the plan:**

Read the plan. For each planned component, follow the planned execution:
1. Read the plan. Understand what each component does and how it connects.
2. Trace data flow from each entry point through every branch:
   - Where does input come from?
   - What transforms it?
   - Where does it go?
   - What can go wrong at each step?
3. Diagram the execution. For each changed file, draw ASCII showing:
   - Every function/method added or modified
   - Every conditional branch
   - Every error path
   - Every call to another function
   - Every edge: null, empty array, invalid type

**Step 2. Map user flows, interactions, and error states:**

- **User flows:** What sequence of actions touches this code? Each step needs a test.
- **Interaction edge cases:** Double-click, navigate away, stale data, slow connection, concurrent actions.
- **Error states the user can see:** Clear message or silent failure? Can the user recover?
- **Empty/zero/boundary states:** Zero results? 10,000 results? Max-length input?

**Step 3. Check each branch against existing tests:**

Go through the diagram branch by branch. For each one, search for a test:
- Function → look for test files covering it
- if/else → look for tests covering BOTH paths
- Error handler → look for test triggering that specific error
- User flow → look for integration/E2E test
- Interaction edge case → look for test simulating it

Quality scoring:
- ★★★ Tests behavior with edge cases AND error paths
- ★★ Tests correct behavior, happy path only
- ★ Smoke test / trivial assertion

### E2E Test Decision Matrix

**RECOMMEND E2E (mark as [→E2E]):**
- Common user flow spanning 3+ components/services
- Integration point where mocking hides real failures
- Auth/payment/data-destruction flows

**STICK WITH UNIT TESTS:**
- Pure function with clear inputs/outputs
- Internal helper with no side effects
- Edge case of a single function

### REGRESSION RULE (mandatory)

When the coverage audit identifies a REGRESSION — code that previously worked but the diff broke — a regression test is added as a critical requirement. No AskUserQuestion. No skipping.

**Step 4. Output ASCII coverage diagram:**

```
CODE PATHS                                            USER FLOWS
[+] src/services/billing.ts                           [+] Payment checkout
  ├── processPayment()                                  ├── [★★★ TESTED] Complete purchase
  │   ├── [★★★ TESTED] happy + declined + timeout      ├── [GAP] [→E2E] Double-click submit
  │   ├── [GAP]         Network timeout                 └── [GAP]         Navigate away mid-payment
  │   └── [GAP]         Invalid currency
  └── refundPayment()                                 [+] Error states
      ├── [★★  TESTED] Full refund                       ├── [★★  TESTED] Card declined message
      └── [★   TESTED] Partial (non-throw only)          └── [GAP]        Network timeout UX

COVERAGE: 5/13 paths tested (38%)  |  Code paths: 3/5 (60%)  |  User flows: 2/8 (25%)
QUALITY: ★★★:2 ★★:2 ★:1  |  GAPS: 8 (2 E2E)
```

Legend: ★★★ behavior + edge + error  |  ★★ happy path  |  ★ smoke check
[→E2E] = needs integration test

**Step 5. Add missing tests to the plan:**

For each GAP, add a test requirement. Be specific:
- What test file to create
- What the test should assert
- Whether it's unit, E2E, or eval
- For regressions: flag as **CRITICAL**

### Test Plan Artifact

After producing the coverage diagram, write a test plan artifact:

```bash
mkdir -p .planning/advisory
USER=$(whoami)
DATETIME=$(date +%Y%m%d-%H%M%S)
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
```

Write to `.planning/advisory/{user}-{branch}-eng-review-test-plan-{datetime}.md`:

```markdown
# Test Plan
Generated by /plan-eng-review on {date}
Branch: {branch}
Repo: {owner/repo}

## Affected Pages/Routes
- {URL path} — {what to test and why}

## Key Interactions to Verify
- {interaction description} on {page}

## Edge Cases
- {edge case} on {page}

## Critical Paths
- {end-to-end flow that must work}
```

### 4. Performance review

Evaluate:
* N+1 queries. For every new association traversal: includes/preload?
* Memory usage. Maximum size in production?
* Database indexes for every new query.
* Caching opportunities for expensive computations or external calls.
* Background job sizing. Worst-case payload, runtime, retry behavior.
* Slow paths. Top 3 slowest new codepaths and estimated p99.
* Connection pool pressure. New DB, Redis, HTTP connections?

**STOP.** For each issue found, call AskUserQuestion individually.

## Required Outputs

### "NOT in scope" section
List work considered and explicitly deferred.

### Error & Rescue Registry
Complete table from Section 2 analysis.

### Test Coverage Diagram
ASCII diagram from Section 3.

### Performance Concerns
List from Section 4.

### Completion Summary
```
  +====================================================================+
  |            PLAN REVIEW — COMPLETION SUMMARY                        |
  +====================================================================+
  | System Audit         | [key findings]                              |
  | Step 0 (Scope)       | [key decisions]                             |
  | Section 1  (Arch)    | ___ issues found                            |
  | Section 2  (Quality) | ___ issues found                            |
  | Section 3  (Tests)   | Diagram produced, ___ gaps                  |
  | Section 4  (Perf)    | ___ issues found                            |
  +--------------------------------------------------------------------+
  | NOT in scope         | written (___ items)                          |
  | Error/rescue registry| ___ methods, ___ CRITICAL GAPS              |
  | Test plan            | written                                     |
  | Unresolved decisions | ___ (listed below)                          |
  +====================================================================+
```

## Next Steps

After the review, recommend:
- **`/plan-design-review`** (if available) — if UI scope was detected
- **Implementation** — proceed to coding with the locked-down plan
