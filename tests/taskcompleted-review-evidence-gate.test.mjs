import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const REPO_ROOT = new URL('..', import.meta.url).pathname;
const HOOK_PATH = path.join(
  REPO_ROOT,
  'distribution/hooks/project/taskcompleted-review-evidence-gate/hook.mjs',
);

function makeWorkspace(t) {
  const dir = mkdtempSync(path.join(tmpdir(), 'taskcompleted-review-evidence-gate-'));
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
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS: 'docs/reviews/signal.md',
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS: 'docs/reviews/evidence/*.md',
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE: 'Task ID: {{task_id}}',
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
    task_description: 'Add feature X to the codebase',
    ...overrides,
  };
}

test('allows when no signal configuration is present (hook not active)', (t) => {
  const workspace = makeWorkspace(t);

  writeFile(workspace, 'docs/reviews/evidence/entry.md', '---\nReviewer: alice\nReference: PR #42\nOutcome: PASS\n---');

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS: '',
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_PATHS: '',
    },
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('allows when signal file does not exist (no review-required signal)', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews'), { recursive: true });

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('allows when signal file exists but task not mentioned (not review-required)', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-02 requires review\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('blocks when signal file mentions task but no artifact files resolve', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS: 'docs/reviews/signal.md',
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS: 'docs/reviews/evidence/*.md',
    },
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /artifact|resolve/i);
});

test('blocks when artifact exists but no entry for target task', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nReviewer: alice\nReference: PR #42\nOutcome: PASS\n---\n\nTask ID: T-02 reviewed\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /not found|entry/i);
});

test('blocks when entry found but Reviewer is placeholder', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // H-03 format: task ID in front matter field
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nTask ID: T-01\nReviewer: TBD\nReference: PR #42\nOutcome: PASS\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /Reviewer|placeholder/i);
});

test('blocks when entry found but Reference is placeholder', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // H-03 format: task ID in front matter field
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nTask ID: T-01\nReviewer: alice\nReference: TODO\nOutcome: PASS\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /Reference|placeholder/i);
});

test('blocks when entry found but Outcome = FAIL', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // H-03 format: task ID in front matter field
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nTask ID: T-01\nReviewer: alice\nReference: PR #42\nOutcome: FAIL\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /Outcome|PASS/i);
});

test('blocks when entry found but Outcome = BLOCKED', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // H-03 format: task ID in front matter field
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nTask ID: T-01\nReviewer: alice\nReference: PR #42\nOutcome: BLOCKED\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /Outcome|PASS/i);
});

test('allows when entry found with Reviewer + Reference + PASS', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // H-03 format: task ID in front matter field
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nTask ID: T-01\nReviewer: alice\nReference: PR #42\nOutcome: PASS\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('allows when configured PASS tokens override works', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // H-03 format: task ID in front matter field
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nTask ID: T-01\nReviewer: alice\nReference: PR #42\nOutcome: APPROVED\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_PASS_TOKENS: 'PASS,APPROVED',
    },
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('allows when configured field names override works', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // H-03 format: task ID in JSON field
  writeFile(
    workspace,
    'docs/reviews/evidence/reviews.json',
    JSON.stringify({
      'Task ID': 'T-01',
      reviewed_by: 'alice',
      pr_link: 'PR #42',
      status: 'PASS',
    }),
  );

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS: 'docs/reviews/evidence/*.json',
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_REVIEWER_FIELD: 'reviewed_by',
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_REFERENCE_FIELD: 'pr_link',
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_OUTCOME_FIELD: 'status',
    },
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});

test('blocks when multiple signal files matched (ambiguous)', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal-a.md', 'Task ID: T-01 requires review\n');
  writeFile(workspace, 'docs/reviews/signal-b.md', 'Task ID: T-01 requires review\n');
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nReviewer: alice\nReference: PR #42\nOutcome: PASS\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS: 'docs/reviews/signal-*.md',
    },
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /multiple|signal/i);
});

test('blocks when target template is not configured', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nReviewer: alice\nReference: PR #42\nOutcome: PASS\n---');

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE: '',
    },
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /target.*mapping|mapping.*required/i);
});

test('blocks when no placeholder markers configured', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nReviewer: alice\nReference: PR #42\nOutcome: PASS\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_REVIEW_EVIDENCE_GATE_PLACEHOLDER_MARKERS: '',
    },
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /placeholder/i);
});

// --- Unit 2: new regression tests for empty-field bypass and front-matter edge case ---

test('blocks when Reviewer field is present but empty string', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // Reviewer is explicitly empty — current implementation treats this as non-placeholder
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nTask ID: T-01\nReviewer: \nReference: PR #42\nOutcome: PASS\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  // Should block because Reviewer is blank/empty, not because it matches a placeholder marker
  assert.equal(result.status, 2);
  assert.match(result.stderr, /Reviewer|blank|empty/i);
});

test('blocks when Reference field is present but empty string', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // Reference is explicitly empty — current implementation treats this as non-placeholder
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nTask ID: T-01\nReviewer: alice\nReference: \nOutcome: PASS\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  // Should block because Reference is blank/empty, not because it matches a placeholder marker
  assert.equal(result.status, 2);
  assert.match(result.stderr, /Reference|blank|empty/i);
});

test('blocks when Reviewer key is entirely absent from artifact', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // Reviewer key missing entirely — analyzeReviewArtifact returns empty string for missing key
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nTask ID: T-01\nReference: PR #42\nOutcome: PASS\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /Reviewer|blank|empty|required/i);
});

test('blocks when Reference key is entirely absent from artifact', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // Reference key missing entirely
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', '---\nTask ID: T-01\nReviewer: alice\nOutcome: PASS\n---\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /Reference|blank|empty|required/i);
});

test('parses front matter that ends exactly at closing --- with no trailing newline', (t) => {
  const workspace = makeWorkspace(t);
  mkdirSync(path.join(workspace, 'docs/reviews/evidence'), { recursive: true });
  writeFile(workspace, 'docs/reviews/signal.md', 'Task ID: T-01 requires review\n');
  // File content ends exactly at --- with no trailing newline
  // writeFileSync does not add a newline, so this creates the exact edge case
  const content = '---\nTask ID: T-01\nReviewer: alice\nReference: PR #42\nOutcome: PASS\n---';
  writeFile(workspace, 'docs/reviews/evidence/reviews.md', content);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  // Should pass: the front matter should be recognized and parsed correctly
  // even though the file ends at closing --- without a trailing newline
  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});
