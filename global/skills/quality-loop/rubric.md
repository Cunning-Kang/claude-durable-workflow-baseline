# Quality Loop Rubric

Use this rubric during refinement.
Do not try to maximize every dimension equally.
Select the dimensions that matter most for the current draft.

This rubric is for finding the highest-value weaknesses.
It is not an exhaustive checklist.

---

## Evidence readiness check

Before refinement, ask:
- Would missing source, docs, tests, or user constraints materially change the answer?
- Am I refining a supported answer, or polishing a guess?

If missing evidence could change the conclusion, stop refinement and gather evidence first.

---

## A. Task fit

Questions:
- Does the answer directly address the user’s real ask?
- Is the requested deliverable actually provided?
- Are hard constraints respected?
- Has the answer drifted into a different problem?

Failure signals:
- answers a nearby but easier question
- gives analysis without a conclusion when a recommendation is needed
- ignores user constraints
- over-focuses on style or theory

---

## B. Correctness

Questions:
- Are the factual claims sound?
- Are the logical steps coherent?
- Are there contradictions?
- Is confidence proportional to evidence?

Failure signals:
- unsupported assertions
- internal inconsistency
- false precision
- reasoning gaps hidden by fluent prose

---

## C. Completeness

Questions:
- Are the critical parts of the ask covered?
- Are obvious omissions resolved?
- Are important caveats present?
- Is the answer missing the part that matters most?

Failure signals:
- answers only one part of a multi-part ask
- omits key tradeoffs
- ignores implementation constraints
- leaves out the recommendation

---

## D. Decision value

Questions:
- Does the answer help the user decide or act?
- Are tradeoffs explicit?
- Are the best and second-best options distinguishable?
- Does the answer clarify when each option is appropriate?

Failure signals:
- vague “it depends” without decision structure
- alternatives listed without ranking
- recommendations without conditions
- analysis that does not change action

---

## E. Real-world feasibility

Questions:
- Would this work under realistic constraints?
- Are maintenance cost, adoption cost, and operational friction considered?
- Are dependencies and hidden prerequisites surfaced?
- Is the recommendation robust outside ideal conditions?

Failure signals:
- theoretically elegant but operationally weak
- ignores migration cost
- ignores failure modes
- relies on unavailable capabilities

---

## F. Assumption handling

Questions:
- What assumptions is the answer making?
- Are those assumptions stated or hidden?
- Are fragile assumptions clearly marked?
- Are relevant counterexamples considered?

Failure signals:
- hidden assumptions treated as facts
- no mention of uncertainty
- no recognition of edge cases
- over-generalization

---

## G. Compression and signal

Questions:
- Is every paragraph earning its place?
- Are repeated points removed?
- Is the answer sharper after revision?
- Is the conclusion easy to find?

Failure signals:
- duplicated ideas
- bloated framing
- delayed recommendation
- too much setup for too little payoff

---

## H. Reviewer resistance

Questions:
- What would a strict reviewer attack first?
- Is there an obvious weak link?
- Is the answer relying on hand-waving?
- Would a strong reviewer challenge a major unsupported step?

Failure signals:
- one fragile central claim
- vague evidence language
- recommendation without criteria
- no handling of the strongest objection

---

## How to select dimensions

Prefer 2 to 4 dimensions per round.
Pick the ones most likely to improve the current draft.
Skip dimensions that are already clearly strong unless a later round exposes a dependency.

Illustrative round pattern only:
- Round 1: Task fit + Correctness
- Round 2: Decision value + Real-world feasibility + Assumption handling
- Round 3: Compression and signal + Reviewer resistance

This pattern is only a quick heuristic.
The task-type priority guidance below is the primary selection rule.
If you stop early, only quick-check skipped high-priority dimensions that could plausibly change the answer.

---

## Priority guidance

Not every task needs the same emphasis.

### For architecture / tooling / implementation tasks
Prioritize:
1. Task fit
2. Correctness
3. Real-world feasibility
4. Decision value
5. Assumption handling

This ranking guides selection.
It does not mean every dimension must be reviewed if lower-priority dimensions are already clearly strong.

### For research synthesis / comparison tasks
Prioritize:
1. Correctness
2. Completeness
3. Decision value
4. Reviewer resistance
5. Compression and signal

### For strategy / advisory tasks
Prioritize:
1. Decision value
2. Task fit
3. Real-world feasibility
4. Assumption handling
5. Compression and signal

### For important writing tasks
Prioritize:
1. Task fit
2. Compression and signal
3. Correctness
4. Decision value
5. Reviewer resistance

---

## Minimal pass condition

An answer-layer response is ready to finalize when:

- the core ask is directly answered
- no major constraint is violated
- required evidence has already been gathered, or missing evidence would not change the conclusion
- no material factual or logical weakness remains
- the recommendation is explicit when needed
- further revision would mostly be cosmetic

This condition only governs answer refinement.
It does not replace source review, execution, tests, static checks, independent review, or any project completion gate.
If those gates are required and unmet, do not claim the work is complete.

If these are true, stop refining.
