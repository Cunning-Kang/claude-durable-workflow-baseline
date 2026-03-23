# Release-Candidate Adoption Validation Plan v2

**Date**: 2026-03-23
**Version**: v2 (post-refactor closeout)
**Validator**: Independent audit agent
**Status**: In Progress

---

## 1. Goals

### Primary Goal
Validate the baseline source repo from a **new adopter's perspective** to determine if it is ready for release as a stable, adoptable baseline distribution source.

### Secondary Goals
1. Identify adoption-blocking issues that would prevent a new project from successfully using this baseline
2. Assess clarity of entry points, installation paths, and scope boundaries
3. Verify that authoritative context is discoverable and actionable
4. Evaluate whether a new adopter can understand "what to do first, what not to do, and where to find things"

---

## 2. Scope

### In Scope
- **Entry Clarity**: First-look experience and navigation paths for new adopters
- **Installation Path**: Clarity and completeness of setup instructions
- **Scope Clarity**: Distinguishing opt-in from baseline, what's distributed vs. what's live
- **Discoverability**: Finding hooks, snippets, protocols, memory, and reference docs
- **Operational Usability**: Understanding workflows, boundaries, and change-routing
- **Maintainer Usability**: Ability to route changes correctly and avoid anti-patterns

### Out of Scope (Non-Goals)
- Implementing fixes or changes to the repo
- Performing another cleanup round
- Evaluating code quality of hook implementations
- Testing actual installation in a real project
- Assessing long-term maintenance burden
- Reviewing refactor phase documents for historical accuracy

---

## 3. Adopter Personas

### Primary Persona: New Project Lead
- **Context**: Starting a new project or adopting baseline into an existing repo
- **Needs**: Clear entry point, quick setup, understanding of what's being installed
- **Questions**: "Where do I start?", "What will this install?", "Do I need everything?"

### Secondary Persona: Maintenance Contributor
- **Context**: Joining an existing project that uses this baseline
- **Needs**: Understanding boundaries, where to make changes, how to avoid breaking things
- **Questions**: "Where does this change go?", "Is this a baseline change or project change?", "What should I NOT touch?"

### Tertiary Persona: Curious Explorer
- **Context**: Evaluating whether to adopt this baseline
- **Needs**: Quick understanding of what this repo is and isn't
- **Questions**: "What problems does this solve?", "Is this for me?", "What's the commitment?"

---

## 4. Validation Dimensions

### 4.1 Entry Clarity
**Question**: When a new adopter lands on the repo, do they know where to look first?

**Checks**:
- [ ] README.md clearly states what the repo is and isn't
- [ ] README.md provides a clear first action
- [ ] There is an obvious "quick start" path
- [ ] The distinction between baseline source and distribution target is clear
- [ ] References to authoritative docs are present and correct

**Evidence Sources**:
- README.md
- docs/claude-one-command-bootstrap.md
- docs/reference/superpowers-boundary.md

---

### 4.2 Installation Path
**Question**: Can a new adopter install the baseline without ambiguity or errors?

**Checks**:
- [ ] Installation steps are complete and executable
- [ ] All required files and commands are listed
- [ ] The distinction between one-time setup and per-repo setup is clear
- [ ] Paths are correct and consistent
- [ ] The `/init-claude-workflow` command is documented
- [ ] Expected post-installation state is described

**Evidence Sources**:
- README.md (Quick Start section)
- docs/claude-one-command-bootstrap.md
- distribution/commands/init-claude-workflow.md

---

### 4.3 Scope Clarity
**Question**: Can the adopter distinguish what is opt-in from what is baseline-default?

**Checks**:
- [ ] The difference between `global/` (baseline) and project-local is clear
- [ ] Hooks/snippets are clearly marked as opt-in, not default
- [ ] Memory skeleton vs. memory content is distinguished
- [ ] Protocol docs vs. implementation guidance is separated
- [ ] The "NOT live default" concept is explained

**Evidence Sources**:
- README.md (What /is not and What /init-claude-workflow does not do sections)
- docs/reference/hooks-scope.md
- docs/reference/superpowers-boundary.md
- final-refactor-handoff.md (§4.2, §4.3)

---

### 4.4 Discoverability
**Question**: Can the adopter find the authoritative docs for each concern?

**Checks**:
- [ ] Hooks are indexed and discoverable
- [ ] Settings snippets are indexed and discoverable
- [ ] Protocol docs are findable
- [ ] Memory structure is explained
- [ ] Reference docs (boundary docs) are reachable
- [ ] The relationship between layers is clear

**Evidence Sources**:
- distribution/hooks/project/README.md
- distribution/settings-snippets/project/README.md
- docs/reference/* (all boundary docs)
- final-refactor-handoff.md (§2, §4.1)

---

### 4.5 Operational Usability
**Question**: Once installed, can the adopter use the baseline effectively?

**Checks**:
- [ ] The adopter knows what to do first (workflow entry point)
- [ ] The adopter knows what NOT to do (anti-patterns, boundaries)
- [ ] The adopter can route new changes to the correct layer
- [ ] The adopter knows when to use Superpowers vs. baseline assets
- [ ] Memory protocol is clear (what to write, what not to write)

**Evidence Sources**:
- docs/claude-one-command-bootstrap.md (Daily Use section)
- final-refactor-handoff.md (§5, §6)
- baseline/docs/workflow/memory-protocol.md
- docs/reference/memory-boundary.md

---

### 4.6 Maintainer Usability
**Question**: Can a contributor determine where a change belongs without asking?

**Checks**:
- [ ] Change-routing decision tree exists and is clear
- [ ] Layer responsibilities are documented
- [ ] Anti-patterns are documented with "correct approach"
- [ ] Boundary docs provide maintenance checklists
- [ ] Common modification scenarios are covered

**Evidence Sources**:
- final-refactor-handoff.md (§3, §5, §6)
- docs/reference/hooks-scope.md (§7)
- docs/reference/superpowers-boundary.md (§6)
- docs/reference/memory-boundary.md (§7)

---

## 5. Issue Severity Classification

### Blocking
**Definition**: Issues that would prevent a new adopter from successfully installing or understanding the baseline.

**Examples**:
- Broken or incomplete installation instructions
- Missing authoritative boundary docs referenced elsewhere
- Unclear or incorrect paths in critical setup steps
- Contradictory statements about what is opt-in vs. default
- Missing index or README for a major distribution surface

**Threshold**: High confidence that this would cause a new adopter to fail or give up.

---

### Important but Non-Blocking
**Definition**: Issues that would cause confusion, require trial-and-error, or lead to incorrect initial usage but do not prevent adoption.

**Examples**:
- Ambiguous wording that requires re-reading
- Missing cross-references between related docs
- Non-obvious file organization
- Terminology inconsistency
- Examples that would be helpful but are missing

**Threshold**: Medium confidence that this would slow down adoption or cause incorrect usage, but the adopter could recover.

---

### Cosmetic
**Definition**: Minor issues that affect polish but do not impact understanding or usage.

**Examples**:
- Typos
- Formatting inconsistencies
- Minor redundancy
- Non-critical missing examples
- Suboptimal heading structure

**Threshold**: Low impact; would be noticed but would not cause errors or confusion.

---

## 6. Release-Candidate Pass Criteria

The baseline source repo is **Ready for Release** if and only if:

1. **No Blocking Issues** — Zero issues classified as Blocking
2. **Installation Path Verified** — All 4.2 checks pass or have only cosmetic issues
3. **Authority Establishable** — All reference docs exist and are reachable
4. **Scope Clarity Achieved** — Opt-in vs. default distinction is clear across all surfaces
5. **Discoverability Functional** — All major assets are indexed and findable

**Grace Criteria** (allowable shortcomings for v1):
- Up to 5 Important but Non-Blocking issues
- Unlimited Cosmetic issues
- Missing "nice-to-have" examples or tutorials

---

## 7. Validation Method

### Step 1: Read Authoritative Context
Read and internalize:
- final-refactor-handoff.md (handoff requirements, layer responsibilities)
- README.md (repo positioning)
- docs/claude-one-command-bootstrap.md (installation flow)
- All docs/reference/* (boundary authorities)

### Step 2: Simulate New Adopter Journey
For each persona (New Project Lead, Maintenance Contributor, Curious Explorer):
1. Start at README.md
2. Follow the documented path
3. Ask "what would I look for next?"
4. Check if the expected doc exists and is linked
5. Record gaps or confusion points

### Step 3: Cross-Check Consistency
Verify that:
- final-refactor-handoff.md describes actual repo state
- README.md references match actual file locations
- Hook/snippet indexes are complete
- Boundary docs are internally consistent
- Opt-in statements are consistent across surfaces

### Step 4: Assess Each Dimension
For each of the 6 dimensions (4.1–4.6):
1. Answer the dimension question
2. Check all listed checkboxes
3. Collect evidence (specific file references)
4. Classify findings by severity

### Step 5: Synthesize Judgment
1. Count issues by severity
2. Evaluate against Pass Criteria
3. Render Ready / Not Ready decision
4. Provide next-step recommendation

---

## 8. Deliverables

1. **Validation Plan** (this document)
2. **Validation Report** (`release-candidate-adoption-validation-report-v2.md`)
   - Overall judgment
   - Dimension-by-dimension findings
   - Issue inventory with severity
   - Release-candidate decision
   - Next-step recommendation

---

## 9. References

### Authoritative Context (Do Not Modify During Audit)
- `docs/refactor/2026-03-baseline-refactor/final-refactor-handoff.md`
- `README.md`
- `docs/claude-one-command-bootstrap.md`
- `docs/reference/superpowers-boundary.md`
- `docs/reference/hooks-scope.md`
- `docs/reference/memory-boundary.md`

### Distribution Surfaces
- `distribution/hooks/project/`
- `distribution/settings-snippets/project/`
- `distribution/commands/`
- `global/`
- `baseline/`

### Protocol Docs
- `baseline/docs/workflow/memory-protocol.md`
- `baseline/docs/workflow/execution-contract.md`
- `baseline/docs/workflow/review-protocol.md`
- `baseline/docs/workflow/native-task-translation.md`

---

**END OF VALIDATION PLAN**
