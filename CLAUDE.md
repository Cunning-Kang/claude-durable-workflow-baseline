## Project Overrides

```yaml
DEFAULT_BRANCH: main
ENV_SETUP_CMD: mise install && mise run install
TEST_CMD: mise run test
LINT_CMD: mise run lint
TYPECHECK_CMD: mise run check
BUILD_CMD: mise run build
```

## Project Runtime Surface

- For orchestration-heavy work, consult `@.claude/guides/orchestration-extension.md`.
- Prefer project subagents in `.claude/agents/` before inventing ad-hoc routing.
