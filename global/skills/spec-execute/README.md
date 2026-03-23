# spec-execute migration note

`spec-execute` is no longer distributed from this baseline repo.

## Why it was removed
- It duplicated the generic execution lane already owned by Superpowers.
- Keeping it here would preserve a competing workflow entrypoint inside the baseline distribution surface.

## Migration
- Use the Superpowers execution lane for implementation work that starts from existing specs, plans, or task artifacts.
- Keep repo-local execution semantics in passive protocol docs under `baseline/docs/workflow/` instead of redistributing a generic execution skill from `global/`.

## Boundary
This directory remains only as a migration note so historical references do not point to a missing path. It is not a skill entrypoint and must not be re-expanded into a workflow control surface.
