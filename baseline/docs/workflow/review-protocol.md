# Review Protocol

## Purpose
Define the repo-local review gate for durable work without introducing a second workflow engine.

This protocol decides **when review is required, what evidence the reviewer needs, and how the outcome is recorded**. It does not own execution order, planning, or verification strategy.

## Repo-local task levels
These levels are repo-local metadata for durable baseline artifacts. They do not redefine global completion gates.

- `L0` — small, local, reversible work with no public interface or schema change
- `L1` — default durable work tracked in repo artifacts
- `L2` — public interface or schema change, high-risk or irreversible work, or work that needs explicit rollback or review planning

## When review is required
Review is required when any of the following is true:
- the task is L2
- the change affects a public interface or schema
- the work is high-risk under the project or global standard
- the project rule explicitly requires independent review

Review is optional for L0 and most local L1 changes unless risk escalates.

## Reviewer independence
- The reviewer must be independent from the implementer.
- Prefer an independent reviewer subagent when available.
- Self-review does not satisfy an independent review gate unless a higher-priority project rule explicitly allows it.

## Minimum review flow
1. Confirm whether review is required for the active task.
2. Give the reviewer only the minimum required context:
   - task requirement, spec, or equivalent durable acceptance source
   - relevant diff or changed files
   - verification evidence, if already available
3. Record exactly one outcome:
   - `PASS`
   - `FAIL`
   - `BLOCKED`
4. If `FAIL`, fix blocking issues before claiming completion.
5. If `BLOCKED`, keep the task in progress.

## Durable record
When review is required, store the result in the durable review artifact referenced by the active task or spec. The record must identify:
- `Reviewer`
- `Reference`
- final outcome: `PASS` / `FAIL` / `BLOCKED`

## Relationship to adjacent protocol docs
- `execution-contract.md` decides how review fits into the overall execution bridge.
- `review-checklist.md` is a lightweight aid for applying this protocol.
- `native-task-translation.md` does not decide whether review is required.

## What this protocol does not do
- It does not decide implementation order.
- It does not replace verification.
- It does not reprioritize tasks.
- It does not require review for every small change.
