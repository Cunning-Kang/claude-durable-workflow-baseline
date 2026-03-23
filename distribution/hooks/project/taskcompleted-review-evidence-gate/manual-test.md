# Manual test — `taskcompleted-review-evidence-gate`

Run these checks from the baseline repo root.

## 0. Common setup

```bash
export HOOK="$PWD/distribution/hooks/project/taskcompleted-review-evidence-gate/hook.mjs"
export PAYLOAD='{"session_id":"session-1","hook_event_name":"TaskCompleted","task_id":"T-01","task_subject":"Implement feature X"}'
```

Each scenario below creates its own temporary workspace and prints the expected result.

## 1. Allow when no signal configuration is present (hook not active)

```bash
WORKDIR="$(mktemp -d)"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 0"
rm -rf "$WORKDIR"
```

Expected: exit code `0`, no stderr output.

## 2. Allow when signal file does not exist (no review-required signal)

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 0"
rm -rf "$WORKDIR"
```

Expected: exit code `0`, no stderr output.

## 3. Allow when signal file exists but task not mentioned (not review-required)

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews"
printf '%s\n' 'Task ID: T-02 requires review' > "$WORKDIR/docs/reviews/signal.md"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 0"
rm -rf "$WORKDIR"
```

Expected: exit code `0`, no stderr output.

## 4. Block when signal file mentions task but artifact missing

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal.md"
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/evidence/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions no review artifact files resolved.

## 5. Block when artifact exists but no entry for target task

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews/evidence"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal.md"
cat > "$WORKDIR/docs/reviews/evidence/reviews.md" <<'EOF'
---
Reviewer: alice
Reference: PR #42
Outcome: PASS
---
EOF
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/signal.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/evidence/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions target task not found in review artifact.

## 6. Block when entry found but Reviewer is placeholder

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews/evidence"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal.md"
cat > "$WORKDIR/docs/reviews/evidence/reviews.md" <<'EOF'
---
Task ID: T-01
Reviewer: TBD
Reference: PR #42
Outcome: PASS
---
EOF
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/signal.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/evidence/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions Reviewer field is placeholder.

## 7. Block when entry found but Reference is placeholder

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews/evidence"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal.md"
cat > "$WORKDIR/docs/reviews/evidence/reviews.md" <<'EOF'
---
Task ID: T-01
Reviewer: alice
Reference: TODO
Outcome: PASS
---
EOF
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/signal.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/evidence/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions Reference field is placeholder.

## 8. Block when entry found but Outcome = FAIL

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews/evidence"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal.md"
cat > "$WORKDIR/docs/reviews/evidence/reviews.md" <<'EOF'
---
Task ID: T-01
Reviewer: alice
Reference: PR #42
Outcome: FAIL
---
EOF
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/signal.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/evidence/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions Outcome is not PASS.

## 9. Block when entry found but Outcome = BLOCKED

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews/evidence"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal.md"
cat > "$WORKDIR/docs/reviews/evidence/reviews.md" <<'EOF'
---
Task ID: T-01
Reviewer: alice
Reference: PR #42
Outcome: BLOCKED
---
EOF
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/signal.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/evidence/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions Outcome is not PASS.

## 10. Allow when entry found with Reviewer + Reference + PASS

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews/evidence"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal.md"
cat > "$WORKDIR/docs/reviews/evidence/reviews.md" <<'EOF'
---
Task ID: T-01
Reviewer: alice
Reference: PR #42
Outcome: PASS
---
EOF
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/signal.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/evidence/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 0"
rm -rf "$WORKDIR"
```

Expected: exit code `0`, no stderr output.

## 11. Configured PASS tokens override works

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews/evidence"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal.md"
cat > "$WORKDIR/docs/reviews/evidence/reviews.md" <<'EOF'
---
Task ID: T-01
Reviewer: alice
Reference: PR #42
Outcome: APPROVED
---
EOF
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/signal.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/evidence/*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_PASS_TOKENS='PASS,APPROVED' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 0"
rm -rf "$WORKDIR"
```

Expected: exit code `0` with custom PASS token.

## 12. Configured field names override works

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews/evidence"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal.md"
cat > "$WORKDIR/docs/reviews/evidence/reviews.json" <<'EOF'
{
  "Task ID": "T-01",
  "reviewed_by": "alice",
  "pr_link": "PR #42",
  "status": "PASS"
}
EOF
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/signal.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/evidence/*.json' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_REVIEWER_FIELD='reviewed_by' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_REFERENCE_FIELD='pr_link' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_OUTCOME_FIELD='status' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 0"
rm -rf "$WORKDIR"
```

Expected: exit code `0` with custom field names.

## 13. Block when multiple signal files matched (ambiguous)

```bash
WORKDIR="$(mktemp -d)"
mkdir -p "$WORKDIR/docs/reviews"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal-a.md"
printf '%s\n' 'Task ID: T-01 requires review' > "$WORKDIR/docs/reviews/signal-b.md"
cat > "$WORKDIR/docs/reviews/evidence.md" <<'EOF'
---
Task ID: T-01
Reviewer: alice
Reference: PR #42
Outcome: PASS
---
EOF
(
  cd "$WORKDIR" &&
  env \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS='docs/reviews/signal-*.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS='docs/reviews/evidence.md' \
    TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE='Task ID: {{task_id}}' \
    node "$HOOK" <<< "$PAYLOAD"
)
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions multiple signal files matched.
