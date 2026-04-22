import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const REPO_ROOT = new URL('..', import.meta.url).pathname;
const HOOK_PATH = path.join(
  REPO_ROOT,
  'distribution/hooks/project/taskcompleted-verification-evidence-gate/hook.mjs',
);

function makeWorkspace(t) {
  const dir = mkdtempSync(path.join(tmpdir(), 'taskcompleted-verification-evidence-gate-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  return dir;
}

function writeFile(workspace, relativePath, content) {
  const absolutePath = path.join(workspace, relativePath);
  mkdirSync(path.dirname(absolutePath), { recursive: true });
  writeFileSync(absolutePath, content);
}

function runHook({ workspace, payload, env = {} }) {
  return spawnSync(process.execPath, [HOOK_PATH], {
    cwd: workspace,
    input: JSON.stringify({ cwd: workspace, ...payload }),
    encoding: 'utf8',
    env: {
      ...process.env,
      TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS: 'docs/specs/*/verify.md',
      TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE: 'Task: {{task_id}}',
      TASKCOMPLETED_VERIFICATION_EVIDENCE_SECTION_KEYS: 'Evidence,Verification',
      TASKCOMPLETED_VERIFICATION_EVIDENCE_RECORD_KEYS: 'Command,Check,Result,Date',
      TASKCOMPLETED_VERIFICATION_EVIDENCE_PLACEHOLDER_MARKERS: 'TODO,FIXME,fill in,replace me,[ ],___,your command here,your result here',
      TASKCOMPLETED_VERIFICATION_EVIDENCE_PLACEHOLDER_REGEX: '^\\s*(TODO|F?FIXME|fill in|replace me|\\[ ?\\]|___|your .* here)\\s*$',
      ...env,
    },
  });
}

function makePayload(overrides = {}) {
  return {
    session_id: 'session-1',
    hook_event_name: 'TaskCompleted',
    task_id: 'T-01',
    task_subject: 'Implement feature X',
    ...overrides,
  };
}

// ─── Scenario 1: Block when no artifact files resolved ─────────────────────────

test('blocks when no artifact files resolve from configured globs', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS: 'docs/other/*/verify.md',
    },
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /no verification artifact files resolved/i);
});

// ─── Scenario 2: Block when artifact does not contain target identifier ─────────

test('blocks when artifact exists but does not contain target identifier', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature Y
Task: T-99

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /target identifier|artifact.*contain/i);
});

// ─── Scenario 3: Block when artifact contains only placeholder evidence ─────────

test('blocks when evidence records contain only placeholder values (TODO)', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: TODO
## Result: TODO
## Date: TODO
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /placeholder|evidence records contain only placeholder/i);
});

test('blocks when evidence records contain only placeholder values (FIXME)', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: FIXME
## Result: fill in
## Date: replace me
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /placeholder|evidence records contain only placeholder/i);
});

// ─── Scenario 4: Block when evidence section is missing ────────────────────────

test('blocks when verification artifact has no recognized evidence section', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

No evidence section here.
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /evidence section|recognized.*evidence/i);
});

// ─── Scenario 5: Block when evidence record fields are all blank ──────────────

test('blocks when evidence record fields are all blank', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command:
## Result:
## Date:
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /placeholder|evidence records contain only placeholder/i);
});

// ─── Scenario 6: Allow when evidence is properly filled ────────────────────────

test('allows when evidence is properly filled with real values', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: All 12 tests passed
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

// ─── Scenario 7: Allow with custom placeholder markers and fields ─────────────

test('allows with custom section keys, record keys, and placeholder markers', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Verification

Check: npm run build
Outcome: success
When: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_VERIFICATION_EVIDENCE_SECTION_KEYS: 'Verification',
      TASKCOMPLETED_VERIFICATION_EVIDENCE_RECORD_KEYS: 'Check,Outcome,When',
      TASKCOMPLETED_VERIFICATION_EVIDENCE_PLACEHOLDER_MARKERS: 'TODO,FIXME,fill in',
    },
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

// ─── Scenario 8: Block when configured target template is empty ───────────────

test('blocks when configured target template is empty', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE: '',
    },
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /target.*mapping.*empty|mapping.*required/i);
});

// ─── Scenario 9: Block when multiple artifacts match target (ambiguous) ───────

test('blocks when multiple artifacts contain the target identifier (ambiguous)', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
`);

  writeFile(workspace, 'docs/specs/feature-x/alt-verify.md', `# Verification — Feature X (alt)
Task: T-01

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS: 'docs/specs/*/verify.md,docs/specs/*/alt-verify.md',
    },
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /multiple.*artifact|ambiguous/i);
});

// ─── Additional characterization: edge cases ───────────────────────────────────

test('allows when one record has placeholder but another has real data', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: TODO
## Result: TODO
## Date: TODO

## Command: npm test
## Result: All 12 tests passed
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  // Should pass because at least one record has non-placeholder data
  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('blocks when artifact path is configured but file does not exist', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS: '',
      TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_PATHS: 'docs/specs/feature-x/missing.md',
    },
  });

  // Hook handles missing file gracefully - exit 2 with "target identifier not found" error
  assert.equal(result.status, 2);
  assert.match(result.stderr, /target identifier|artifact.*contain/i);
});

test('allows using artifactPaths when file exists with real evidence', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: All 12 tests passed
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS: '',
      TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_PATHS: 'docs/specs/feature-x/verify.md',
    },
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('allows when at least one glob matches with real evidence (non-matching globs ignored)', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result: OK
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS: 'docs/specs/*/verify.md,docs/missing/*/verify.md',
    },
  });

  // Non-matching globs are ignored; if a matching glob has real evidence, hook passes
  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('handles evidence section with h1 heading', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Evidence

Task: T-01

## Command: npm test
## Result: OK
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_VERIFICATION_EVIDENCE_SECTION_KEYS: 'Evidence',
      TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE: 'Task: {{task_id}}',
    },
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('handles evidence section with h2 heading', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `## Evidence

Task: T-01

## Command: npm test
## Result: OK
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('handles evidence section with h3 heading', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `### Evidence

Task: T-01

## Command: npm test
## Result: OK
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('handles record fields with equals sign separator', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

Command=npm test
Result=All 12 tests passed
Date=2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('handles multiline record values', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test --coverage
## Result: All 12 tests passed
  5 skipped, 2 todo
  Coverage: 85%
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('handles list items in record values', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/specs/feature-x'), { recursive: true });

  writeFile(workspace, 'docs/specs/feature-x/verify.md', `# Verification — Feature X
Task: T-01

## Evidence

## Command: npm test
## Result:
- unit tests: 10 passed
- integration tests: 2 passed
## Date: 2026-03-22
`);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});
