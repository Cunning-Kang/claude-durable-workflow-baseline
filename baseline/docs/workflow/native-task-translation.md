# Native Task Translation

## Goal
Translate one durable task into a small, session-safe native task list.

## Translation rule
For one durable task or one clearly bounded ready batch, extract only:
- goal
- scope
- acceptance
- explicit dependency or immediate blocker, if any
- evidence requirements

Then create the minimum native session tasks needed to move it forward.

## Authoritative state boundary
- Durable task artifacts remain the cross-session milestone tracker.
- Native session tasks exist only to help execute the current run.
- Do not keep both as equally detailed authoritative trackers.

## Good translation
Durable task:
- one durable outcome

Native tasks:
- inspect required files
- implement bounded change
- run verification
- update durable status if milestone changed

## Bad translation
- copy the entire durable task file into native tasks
- create a second long-lived backlog
- mirror every status field
- keep native tasks after the session as authoritative state
- use translation to reprioritize or reinterpret the durable plan

## Relationship to adjacent protocol docs
- `execution-contract.md` defines the overall execution bridge and milestone update rule.
- `review-protocol.md` decides whether review is required.
- translation only reduces execution scope for the current session; it does not change durable task meaning.
