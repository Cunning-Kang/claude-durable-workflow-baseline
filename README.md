# Claude Durable Workflow Baseline

A minimal baseline source repo for Claude Code durable workflow setup.

## What this repo is
- A single source of truth for the durable workflow baseline
- A distribution source for repo-local workflow protocols, spec templates, and memory skeleton files
- The source for `/init-claude-workflow` command content and its supporting script stub

## What this repo is not
- Not a plugin runtime
- Not a feature state repository
- Not a project memory repository
- Not an orchestration engine
- Not an auto-upgrade system

## How distribution works
1. This repository is the canonical source.
2. Each machine syncs it into a local cache, for example:
   `~/.claude/baselines/durable-workflow-v1/`
3. `/init-claude-workflow` reads from that local cache and initializes a target repo.

## What `/init-claude-workflow` does
- Creates missing baseline files in a repo
- Skips identical files
- Produces patch suggestions for conflicting files
- Prompts the user to fill project-specific values

## What `/init-claude-workflow` does not do
- It does not sync this baseline repo
- It does not upgrade an initialized repo
- It does not create feature instances
- It does not infer project commands
- It does not overwrite local modifications by default

## Current stage boundaries
- Manual sync only
- No automatic upgrade
- No feature auto-instantiation
- No hook-based orchestration
