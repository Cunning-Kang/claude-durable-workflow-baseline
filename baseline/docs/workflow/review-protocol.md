# Review Protocol

## Purpose
Provide a minimal, explicit review gate for durable work without introducing a second workflow engine.

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
1. Confirm review applicability.
2. Give the reviewer the minimum required context:
   - feature spec or task requirement
   - relevant diff or changed files
   - verification evidence if available
3. Record one outcome:
   - `PASS`
   - `FAIL`
   - `BLOCKED`
4. If `FAIL`, fix issues before claiming completion.
5. If `BLOCKED`, task status remains in progress.

## Durable record
When review is required, store the result in `docs/specs/<feature>/review.md`.

## What this protocol does not do
- It does not decide implementation order.
- It does not replace verification.
- It does not require review for every small change.
