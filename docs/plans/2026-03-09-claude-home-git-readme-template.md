# Claude Code Global Config

This repository tracks a curated subset of my global Claude Code configuration from `~/.claude`.

## Purpose
- Roll back global Claude Code configuration changes safely
- Back up important personal Claude Code configuration
- Sync stable, user-authored configuration across machines

## Tracked Content
This repository intentionally tracks only the stable, user-maintained subset of `~/.claude`:

- `CLAUDE.md`
- `settings.json`
- `settings.local.json`
- `standards/`
- `guides/`
- `agents/`
- `skills/financial-statement-generator/`
- `skills/github-to-skill/`
- `skills/mise-bootstrap/`

## Not Tracked
This repository intentionally does **not** track runtime state, generated artifacts, caches, analytics, or externally installed skills.

Examples include:
- transcripts
- tasks and teams state
- project-specific runtime state
- debug logs
- analytics and usage data
- caches and snapshots
- backup files
- third-party installed skills
- `plans/`
- plugin UI config such as `plugins/claude-hud/`

## Self-Authored Skills
These skills are maintained in this repository:
- `financial-statement-generator`
- `github-to-skill`
- `mise-bootstrap`

## Third-Party Skills
Other directories under `~/.claude/skills/` are installed externally via `skills.sh` / `npx` and are intentionally excluded from version control.

## Bootstrap On a New Machine
1. Restore this repository into `~/.claude`, or sync the tracked files into `~/.claude`.
2. Reinstall third-party skills separately.
3. Review `settings.local.json` for any machine-specific values before use.

## Commit Hygiene
Before each commit, review diffs carefully, especially for `settings.local.json`.

Check for:
- tokens
- API keys
- secrets
- absolute paths valid on only one machine
- temporary experiment flags
- machine-specific shell or filesystem overrides

If any such values appear, remove them from the tracked file or stop tracking that field/file.

## Notes
- This repository should remain private.
- The repository is intentionally whitelist-based rather than a full backup of `~/.claude`.
- If the tracked scope changes later, update both `.gitignore` and this README together.
