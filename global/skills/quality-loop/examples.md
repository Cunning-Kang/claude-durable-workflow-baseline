# Quality Loop Examples

These examples show when and how to use the quality-loop skill.
They are intentionally compact.
They illustrate decision patterns, not rigid templates.

---

## Example 1 — Architecture recommendation

### User ask
Compare these three agent frameworks and recommend the best one for my setup.

### Why quality-loop applies
This is a high-value decision with tradeoffs, hidden assumptions, and execution constraints.

### Good internal use pattern
- Freeze task context:
  - user wants a recommendation, not just a comparison
  - environment constraints matter
  - maintenance cost matters
- First draft:
  - compare the three options
  - give a provisional winner
- Round 1:
  - verify the answer actually recommends, not just describes
  - check constraints were applied
  - verify the framework characterizations are accurate
- Round 2:
  - strengthen tradeoff analysis
  - surface migration, ops, and maintenance risks
- Round 3:
  - compress repeated points
  - move the recommendation earlier

### Good final shape
- recommendation first
- why this wins for the user’s environment
- why the other options are weaker here
- what would change the recommendation

---

## Example 2 — Research synthesis

### User ask
Read this repo deeply and tell me whether its core idea is genuinely valuable or mostly hype.

### Why quality-loop applies
This requires judgment, criticism, evidence handling, and resistance to surface-level excitement.

### Good internal use pattern
- Freeze task context:
  - user wants evaluation, not summary
  - must separate transferable value from aesthetic appeal
- First draft:
  - summarize the repo briefly
  - give an initial judgment
- Round 1:
  - remove claims not grounded in the material
  - ensure the judgment is actually supported
- Round 2:
  - identify strongest counterarguments
  - separate transferable method from unverifiable claims
- Round 3:
  - tighten the conclusion
  - reduce summary bulk and increase decision value

### Good final shape
- thesis
- what is actually valuable
- what is overstated or unproven
- final recommendation on whether to adopt the idea

---

## Example 3 — Technical strategy

### User ask
Should I build this as a plugin, a skill, or just keep it in the main instruction file?

### Why quality-loop applies
This is a design choice with long-term consequences and hidden maintenance tradeoffs.

### Good internal use pattern
- Freeze task context:
  - user cares about long-term leverage, maintainability, and lifecycle cost
- First draft:
  - recommend one option
- Round 1:
  - check whether the recommendation matches the real constraints
- Round 2:
  - examine reuse frequency, coupling, complexity, and maintenance cost
- Round 3:
  - sharpen the decision rule
  - remove generic filler

### Good final shape
- recommended option
- why it fits the current stage
- when the answer would change
- what not to do yet

---

## Example 4 — High-value writing

### User ask
Rewrite this core instruction file so it is tighter, more stable, and more likely to be followed by the model.

### Why quality-loop applies
This is not a casual rewrite; it needs selection pressure and omission discipline.

### Good internal use pattern
- Freeze task context:
  - optimize for instruction adherence
  - remove low-value, unstable, or verbose rules
- First draft:
  - propose a rewritten file
- Round 1:
  - ensure the draft preserves the essential behavior
- Round 2:
  - remove unstable or redundant rules
  - surface conflicts and hidden assumptions
- Round 3:
  - tighten wording
  - reduce verbosity without losing force

### Good final shape
- concise rewritten file
- short rationale only if useful
- no bloated commentary

---

## Example 5 — When not to use

### User ask
What command do I run to rename this file?

### Why quality-loop should not apply
The task is trivial, low-risk, and one-step.
Extra refinement would add latency without improving the result.

### Correct behavior
Answer directly.
Do not activate the full loop.

---

## Example 6 — Stop early

### User ask
Give me a concise recommendation between tool A and tool B.

### Situation
The first draft is already:
- directly responsive
- constraint-compliant
- clear
- sufficiently justified

### Correct behavior
Run a quick task-fit and correctness check.
If no material issue remains, stop after 1 round.

### Incorrect behavior
Force 3 rounds and turn a sharp answer into a bloated one.

---

## Example 7 — Hidden assumption recovery

### User ask
Which option is best for me?

### Draft problem
The draft assumes the user wants maximum flexibility, but the real constraint is minimum maintenance.

### Correct quality-loop action
In Round 2:
- surface the hidden assumption
- re-rank the options using the real objective
- update the recommendation

### Lesson
A good loop does not just polish prose.
It corrects the decision frame.

---

## Example 8 — Reviewer resistance

### User ask
Give me a final recommendation that can survive strict cross-review from other strong models.

### Good internal use pattern
- identify the most attackable claim
- test whether it is actually supported
- reduce overstatement
- make assumptions explicit
- strengthen comparison criteria
- avoid broad claims that exceed evidence

### Good final shape
- firm but scoped conclusion
- explicit tradeoffs
- clear conditions
- honest uncertainty where needed

---

## Example 9 — Evidence missing, so do not loop yet

### User ask
Tell me whether this API design is good.

### Actual state
The answerer has not read the API spec, code, or current constraints.

### Correct behavior
Do not use quality-loop to compensate for missing evidence.
Read the relevant material first, then use the loop on the resulting answer if the judgment is still high-value.

---

## Example 10 — Another skill should lead

### User ask
Debug this failing test and explain the root cause carefully.

### Actual state
The root cause is not yet known.

### Correct behavior
Use a debugging or implementation skill first to gather evidence and fix the issue.
Use quality-loop only if the final explanation or recommendation needs an extra quality pass.
