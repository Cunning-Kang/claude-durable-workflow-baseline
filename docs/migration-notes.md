# Migration Notes

## Current source
This repo contains the current baseline source package for the durable workflow baseline.

## Intentionally excluded from this repo
- round-by-round analysis documents
- pilot feature instances
- repo-specific patch drafts
- project memory actual content
- review and verification instance outputs

## Current operating model
- This repo is the single source of truth
- Local machine caches are derived copies
- `/init-claude-workflow` initializes repos from cache only

## Current non-goals
- automatic sync
- automatic upgrade
- remote execution
- feature generation
