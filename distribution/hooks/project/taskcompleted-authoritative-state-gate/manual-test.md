# Manual test — `taskcompleted-authoritative-state-gate`

Run these checks from the baseline repo root.

## 0. Common setup

```bash
export HOOK="$PWD/distribution/hooks/project/taskcompleted-authoritative-state-gate/hook.mjs"
export PAYLOAD='{"session_id":"session-1","hook_event_name":"TaskCompleted","task_id":"T-01","task_subject":"Implement H-01 hook"}'
```

Each scenario below creates its own temporary workspace and prints the expected result.

## 1. Block when no tracker matches

```bash
WORKDIR="$(mktemp -d)"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TRACKER_GLOBS='docs/specs/*/index.md' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_OPEN_MARKERS='Current,ready,in_progress' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_CLOSED_MARKERS='done,completed,closed' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions no configured durable tracker files resolved.

## 2. Block when multiple trackers match the same task

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/specs/alpha" "$WORKDIR/docs/specs/beta"
printf '%s\n' '- Task ID: T-01 | status: done' > "$WORKDIR/docs/specs/alpha/index.md"
printf '%s\n' '- Task ID: T-01 | status: done' > "$WORKDIR/docs/specs/beta/index.md"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TRACKER_GLOBS='docs/specs/*/index.md' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_OPEN_MARKERS='Current,ready,in_progress' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_CLOSED_MARKERS='done,completed,closed' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions multiple or ambiguous tracker matches.

## 3. Block when task cannot be mapped

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/specs/alpha"
printf '%s\n' '- Task ID: T-02 | status: done' > "$WORKDIR/docs/specs/alpha/index.md"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TRACKER_GLOBS='docs/specs/*/index.md' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_OPEN_MARKERS='Current,ready,in_progress' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_CLOSED_MARKERS='done,completed,closed' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions target mapping or durable entry lookup failure.

## 4. Block when target task is still open

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/specs/alpha"
printf '%s\n' '- Task ID: T-01 | status: in_progress' > "$WORKDIR/docs/specs/alpha/index.md"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TRACKER_GLOBS='docs/specs/*/index.md' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_OPEN_MARKERS='Current,ready,in_progress' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_CLOSED_MARKERS='done,completed,closed' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions open state.

## 5. Block when authoritative surfaces conflict

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/specs/alpha"
printf '%s\n' '- Task ID: T-01 | status: done' > "$WORKDIR/docs/specs/alpha/index.md"
printf '%s\n' '- Task ID: T-01 | status: in_progress' > "$WORKDIR/docs/specs/alpha/tasks.md"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TRACKER_GLOBS='docs/specs/*/index.md' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_SURFACE_PATHS='docs/specs/alpha/tasks.md' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_OPEN_MARKERS='Current,ready,in_progress' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_CLOSED_MARKERS='done,completed,closed' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions contradictory open/closed state across authoritative surfaces.

## 6. Allow when durable state is self-consistent

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/specs/alpha"
printf '%s\n' '- Task ID: T-01 | status: done' > "$WORKDIR/docs/specs/alpha/index.md"
printf '%s\n' '- Task ID: T-01 | status: completed' > "$WORKDIR/docs/specs/alpha/tasks.md"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TRACKER_GLOBS='docs/specs/*/index.md' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_SURFACE_PATHS='docs/specs/alpha/tasks.md' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_OPEN_MARKERS='Current,ready,in_progress' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_CLOSED_MARKERS='done,completed,closed' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 0"
rm -rf "$WORKDIR"
```

Expected: exit code `0`, no stderr output.

## 7. Block when target mapping is not configured

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/specs/alpha"
printf '%s\n' '- Task ID: T-01 | status: done' > "$WORKDIR/docs/specs/alpha/index.md"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_AUTHORITATIVE_STATE_TRACKER_GLOBS='docs/specs/*/index.md' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_OPEN_MARKERS='Current,ready,in_progress' \
    TASKCOMPLETED_AUTHORITATIVE_STATE_CLOSED_MARKERS='done,completed,closed' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions missing explicit target mapping configuration.
