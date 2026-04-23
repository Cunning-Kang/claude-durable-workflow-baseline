---
name: quality-loop
description: Use this skill for high-stakes, complex, ambiguous, or quality-sensitive tasks that benefit from a bounded multi-pass refinement loop. Best for research synthesis, architecture choices, technical strategy, implementation planning, difficult writing, and other outputs where judgment quality matters.
---

# Quality Loop

## Purpose

This skill improves the quality of an answer through a bounded refinement process.

Use it when a quick first pass is likely to be shallow, under-argued, or insufficiently robust for the user’s actual decision.

This skill does **not** simulate hidden reasoning.
It aims to produce a final answer that is:
- more correct
- more aligned to constraints
- more decision-useful
- more explicit about tradeoffs
- more resistant to obvious criticism

Reference files:
- `rubric.md`: review dimensions and prioritization rules
- `examples.md`: compact usage patterns and stop cases

---

## Use this skill when

Use this skill when one or more of the following is true:

- the task is high-stakes or expensive to get wrong
- the task is complex, ambiguous, or multi-constraint
- the user asks for stronger quality, deeper analysis, stricter review, or more rigorous judgment
- the output will influence implementation, architecture, tool choice, planning, or external communication
- the answer needs tradeoff analysis, counterarguments, prioritization, or risk surfacing
- the result is likely to be scrutinized by a strong human reviewer or another strong model

Good fits:
- architecture recommendations
- tooling / framework comparisons
- technical strategy
- implementation planning
- research synthesis
- prompt / instruction / agent design
- important user-facing writing
- any answer where correctness and judgment matter more than speed

---

## Do not use this skill when

Do not use this skill when:

- the task is trivial, mechanical, or one-step
- the user clearly wants a quick draft only
- the answer surface is tiny and refinement will not materially improve it
- the main problem is missing facts, not weak reasoning
- the task requires execution, testing, or source verification that has not happened yet
- extra review would mostly add latency, repetition, or inflated prose

If the missing facts could change the conclusion, gather them first.
If the facts are already gathered and the weakness is mainly in judgment, structure, or prioritization, the loop is appropriate.

Poor fits:
- simple formatting
- extracting a single fact
- straightforward code transformation
- obvious shell command answers
- low-stakes wording tweaks

If the real gap is evidence or implementation, do that work first.
Use quality-loop on the answer, not as a substitute for the work.

---

## What this skill does not replace

Quality-loop improves the answer layer.
It does **not** replace:

- reading source code or documentation
- running tests or verification commands
- independent review requirements
- asking clarifying questions when blocking ambiguity remains
- domain-specific skills that are a better fit for the task itself

Quality-loop rounds are self-review only.
They do not satisfy any independent review gate or policy requirement.

If another skill is needed to gather evidence or do the work, use that first or alongside this one.

---

## Core operating model

The loop has five phases:

1. Task representation
2. First draft
3. Bounded refinement rounds
4. Stop decision
5. Final integration

The goal is quality convergence, not repeated rewriting.

---

## Phase 1 — Task representation

Before drafting, extract and keep fixed:

- the user’s actual goal
- the requested deliverable
- hard constraints
- soft preferences
- evaluation standard
- likely failure modes

Treat this as the **fixed task definition**.

If refinement reveals that this definition was based on a wrong assumption about the user’s goal, correct the task definition explicitly before continuing.

During refinement:
- do not drift from the original ask
- do not silently change the deliverable or success metric
- do not optimize for elegance over the user’s real objective

If the request contains tension or hidden tradeoffs, preserve them as review constraints.

---

## Phase 2 — First draft

Produce a first draft that is good enough to critique.

The first draft should:
- directly answer the user’s ask
- cover the core problem
- include a provisional judgment when judgment is needed
- stay concrete enough to pressure-test

Do not try to make it perfect in one pass.
The purpose of the draft is to expose where the answer is still weak.

---

## Phase 3 — Bounded refinement rounds

Run up to **3 refinement rounds**.
Use fewer when the answer converges early.
Do not nest quality-loop inside quality-loop.
If a sub-question appears during refinement, handle it inside the current round instead of starting a new loop.

Each round must have a distinct purpose.
Do not rerun the same review with slightly different wording.

Before each round, re-check the fixed task definition from Phase 1.
Then consult `rubric.md` and select the highest-value dimensions for the task.
Use the task-type priority lists in `rubric.md` as the primary selection aid; treat any round pattern there as a quick heuristic only.
If you stop early, make sure no high-priority dimension for the task type was skipped without at least a quick check.

### Round 1 — correctness and task fit

Check for:
- misunderstanding of the request
- direct-answer failure
- factual or logical errors
- constraint violations
- major omissions
- conclusions that do not follow from the evidence

Fix only material problems.

### Round 2 — depth and decision value

Check for:
- hidden assumptions
- weak tradeoff analysis
- unrealistic recommendations
- missing alternatives
- missing execution constraints
- unsupported confidence
- missing risks, edge cases, or counterexamples

Strengthen only where this materially improves decision quality.

### Round 3 — compression and sharpness

Check for:
- unnecessary verbosity
- duplicated points
- weak ordering
- vague conclusions
- diluted recommendations
- low-signal phrasing
- abstraction that hides actionability

Tighten without reducing substance.

---

## Round discipline

In every round:

- identify only the highest-value issues
- revise only where revision materially improves the answer
- preserve sections that are already working
- prefer local repair over full reconstruction
- do not make the answer longer unless length adds clear value
- do not inflate tone to fake depth

Increase judgment density, not word count.

---

## Stop conditions

Stop early if any of the following is true:

- no material issue remains
- the next round would mostly repeat the current answer
- more editing would add polish but not better judgment
- the answer already meets the user’s requested standard
- further rewriting would risk drift, repetition, or dilution

The minimal pass condition in `rubric.md` is the authoritative readiness check.
The checklist below is optional and supportive only.

Do not use all 3 rounds by default.
A sharp 1-round answer is better than a bloated 3-round answer.

---

## Final integration

Return only the final integrated answer unless the user explicitly asks for drafts or intermediate critique.

The final answer should usually:
- lead with the core judgment or recommendation
- make the key reasoning visible
- show important tradeoffs
- surface uncertainty honestly
- avoid fake certainty and padding
- stay aligned with the fixed task definition

Preferred output shapes:

### Advisory tasks
- conclusion first
- rationale
- alternatives / caveats / execution guidance

### Analytical tasks
- thesis
- evidence
- critique
- synthesis
- recommendation

Architecture, implementation, and research tasks usually default to this shape unless the ask is primarily advisory.

### Important writing tasks
- final rewritten text first
- short rationale only if useful

For compact concrete patterns, consult `examples.md`.

---

## Style requirements

When using this skill:

- optimize for decision value, not decorative sophistication
- make hidden assumptions explicit when they matter
- call out weak premises when warranted
- prefer concrete claims over vague tone
- prefer clear structure over performative eloquence
- avoid generic “best practices” filler
- avoid hand-wavy uncertainty
- keep the final answer as short as the task allows

The result should feel sharper and more review-resistant than a first pass.

---

## Important anti-patterns

These are reminders of the rules above, not a second source of authority.

- faux depth
- infinite polishing
- task drift
- full rewrites by reflex
- style over substance
- evidence substitution

---

## Output quality target

A successful result should survive strong scrutiny on:

- correctness
- completeness relative to the ask
- realism
- tradeoff handling
- explicit constraints
- recommendation quality
- concision relative to task needs

If these are strong and no material weakness remains, stop.

---

## Optional lightweight checklist

This checklist is optional.
It does not override the stop conditions here or the minimal pass condition in `rubric.md`.

If you want one final sanity check before finalizing, ask:
- Did I answer the actual question?
- Did I preserve the hard constraints?
- Did I make the key judgment explicit?
- Did I remove the most attackable weak spots?
- Did I stop before over-rewriting?
