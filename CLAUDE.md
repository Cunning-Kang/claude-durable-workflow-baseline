# Claude Durable Workflow Baseline — Source Repo

## What this repo is
Baseline source + distribution source for Claude Code workflow assets. Not a runtime.

## Key commands
- Validate distribution: `python tests/test_distribution_contract.py`
- Run gate tests: `node tests/taskcompleted-*.test.mjs` (requires Node)

## Directory map
- `baseline/` — copied into new repos via `/init-claude-workflow`
- `distribution/` — commands, scripts, agents, hooks, settings-snippets (source-only)
- `global/` — copied to `~/.claude/` (host-wide runtime surface)
- `docs/` — operator guides
- `tests/` — distribution contract + gate validation tests
- `CONTEXT.md` — domain language and design relationships (authoritative)
- `VERSION` — baseline version + cache path

## Constraints
- `global/CLAUDE.md` is a distribution artifact — edits there propagate to all installed hosts
- `CONTEXT.md` is the domain model authority; agent prompts must stay consistent with it
- No competing workflow skills or runtime behavior in this repo
- Agent definitions live in `distribution/agents/`; changes must update that directory

## Agent skills

### Issue tracker

Issues tracked via GitHub Issues using the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role label vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `CONTEXT.md` + `docs/adr/` at repo root. See `docs/agents/domain.md`.
