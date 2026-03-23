# Manual test — `taskcompleted-verification-evidence-gate`

Run these checks from the baseline repo root.

## 0. Common setup

```bash
export HOOK="$PWD/distribution/hooks/project/taskcompleted-verification-evidence-gate/hook.mjs"
export PAYLOAD='{"session_id":"session-1","hook_event_name":"TaskCompleted","task_id":"T-01","task_subject":"Implement feature X"}'
```

Each scenario below creates its own temporary workspace and prints the expected result.

## 1. Block when no artifact files resolved

```bash
WORKDIR="$(mktemp -d)"
cd "$WORKDIR"
mkdir -p docs/specs/feature-x
cat > docs/specs/feature-x/verify.md << 'EOF'
# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
EOF

TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS='docs/other/*/verify.md' TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE='Task: {{task_id}}' node "$HOOK" <<< "$PAYLOAD"
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions no verification artifact files resolved.

## 2. Block when artifact does not contain target identifier

```bash
WORKDIR="$(mktemp -d)"
cd "$WORKDIR"
mkdir -p docs/specs/feature-x
cat > docs/specs/feature-x/verify.md << 'EOF'
# Verification — Feature Y
Task: T-99

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
EOF

TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS='docs/specs/*/verify.md' TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE='Task: {{task_id}}' node "$HOOK" <<< "$PAYLOAD"
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions target identifier not found in any artifact.

## 3. Block when artifact contains only placeholder evidence

```bash
WORKDIR="$(mktemp -d)"
cd "$WORKDIR"
mkdir -p docs/specs/feature-x
cat > docs/specs/feature-x/verify.md << 'EOF'
# Verification — Feature X
Task: T-01

## Evidence

## Command: TODO
## Result: TODO
## Date: TODO
EOF

TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS='docs/specs/*/verify.md' TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE='Task: {{task_id}}' node "$HOOK" <<< "$PAYLOAD"
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions evidence records contain only placeholder values.

## 4. Block when evidence section is missing

```bash
WORKDIR="$(mktemp -d)"
cd "$WORKDIR"
mkdir -p docs/specs/feature-x
cat > docs/specs/feature-x/verify.md << 'EOF'
# Verification — Feature X
Task: T-01

No evidence section here.
EOF

TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS='docs/specs/*/verify.md' TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE='Task: {{task_id}}' node "$HOOK" <<< "$PAYLOAD"
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions no recognized evidence section.

## 5. Block when evidence record fields are all blank

```bash
WORKDIR="$(mktemp -d)"
cd "$WORKDIR"
mkdir -p docs/specs/feature-x
cat > docs/specs/feature-x/verify.md << 'EOF'
# Verification — Feature X
Task: T-01

## Evidence

## Command:
## Result:
## Date:
EOF

TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS='docs/specs/*/verify.md' TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE='Task: {{task_id}}' node "$HOOK" <<< "$PAYLOAD"
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions evidence records contain only placeholder values.

## 6. Allow when evidence is properly filled

```bash
WORKDIR="$(mktemp -d)"
cd "$WORKDIR"
mkdir -p docs/specs/feature-x
cat > docs/specs/feature-x/verify.md << 'EOF'
# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: All 12 tests passed
## Date: 2026-03-22
EOF

TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS='docs/specs/*/verify.md' TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE='Task: {{task_id}}' node "$HOOK" <<< "$PAYLOAD"
echo "exit=$?  # expect 0"
rm -rf "$WORKDIR"
```

Expected: exit code `0`, no error output.

## 7. Allow with custom placeholder markers and fields

```bash
WORKDIR="$(mktemp -d)"
cd "$WORKDIR"
mkdir -p docs/specs/feature-x
cat > docs/specs/feature-x/verify.md << 'EOF'
# Verification — Feature X
Task: T-01

## Verification

Check: npm run build
Outcome: success
When: 2026-03-22
EOF

TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS='docs/specs/*/verify.md' TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE='Task: {{task_id}}' TASKCOMPLETED_VERIFICATION_EVIDENCE_SECTION_KEYS='Verification' TASKCOMPLETED_VERIFICATION_EVIDENCE_RECORD_KEYS='Check,Outcome,When' TASKCOMPLETED_VERIFICATION_EVIDENCE_PLACEHOLDER_MARKERS='TODO,FIXME,fill in' node "$HOOK" <<< "$PAYLOAD"
echo "exit=$?  # expect 0"
rm -rf "$WORKDIR"
```

Expected: exit code `0`, no error output. Custom section keys, record keys, and placeholder markers all respected.

## 8. Block when configured target template is empty

```bash
WORKDIR="$(mktemp -d)"
cd "$WORKDIR"
mkdir -p docs/specs/feature-x
cat > docs/specs/feature-x/verify.md << 'EOF'
# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
EOF

TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS='docs/specs/*/verify.md' TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE='' node "$HOOK" <<< "$PAYLOAD"
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions target mapping configuration resolved to empty.

## 9. Block with multiple artifacts matching target (ambiguous)

```bash
WORKDIR="$(mktemp -d)"
cd "$WORKDIR"
mkdir -p docs/specs/feature-x
cat > docs/specs/feature-x/verify.md << 'EOF'
# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
EOF
cat > docs/specs/feature-x/alt-verify.md << 'EOF'
# Verification — Feature X (alt)
Task: T-01

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
EOF

TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS='docs/specs/*/verify.md,docs/specs/*/alt-verify.md' TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE='Task: {{task_id}}' node "$HOOK" <<< "$PAYLOAD"
echo "exit=$?  # expect 2"
rm -rf "$WORKDIR"
```

Expected: exit code `2`, stderr mentions multiple artifacts contain the target identifier.
