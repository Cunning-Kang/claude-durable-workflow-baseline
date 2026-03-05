## Project Overrides

```yaml
DEFAULT_BRANCH: main
ENV_SETUP_CMD: mise install && mise run install
TEST_CMD: mise run check && mise run test
LINT_CMD: mise run lint
TYPECHECK_CMD: mise run check
BUILD_CMD: mise run build
```
