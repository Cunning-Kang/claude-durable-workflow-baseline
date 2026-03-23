import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const REPO_ROOT = new URL('..', import.meta.url).pathname;
const HOOK_PATH = path.join(
  REPO_ROOT,
  'distribution/hooks/project/taskcompleted-authoritative-state-gate/hook.mjs',
);

function makeWorkspace(t) {
  const dir = mkdtempSync(path.join(tmpdir(), 'taskcompleted-authoritative-state-gate-'));
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
      TASKCOMPLETED_AUTHORITATIVE_STATE_TRACKER_GLOBS: 'docs/specs/*/index.md',
      TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE: 'Task ID: {{task_id}}',
      TASKCOMPLETED_AUTHORITATIVE_STATE_OPEN_MARKERS: 'Current,ready,in_progress',
      TASKCOMPLETED_AUTHORITATIVE_STATE_CLOSED_MARKERS: 'done,completed,closed',
      ...env,
    },
  });
}

function makePayload(overrides = {}) {
  return {
    session_id: 'session-1',
    hook_event_name: 'TaskCompleted',
    task_id: 'T-01',
    task_subject: 'Implement H-01 hook',
    task_description: 'Add completion-time authoritative state gate',
    ...overrides,
  };
}

test('blocks when target mapping configuration is missing instead of guessing from TaskCompleted payload', (t) => {
  const workspace = makeWorkspace(t);

  writeFile(workspace, 'docs/specs/alpha/index.md', '- Task ID: T-01 | status: done\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE: '',
    },
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /target.+mapping|target.+template|mapping.+required/i);
});

test('blocks when no tracker files resolve from configured tracker paths or globs', (t) => {
  const workspace = makeWorkspace(t);

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /tracker/i);
});

test('blocks when the completion target maps to multiple tracker files', (t) => {
  const workspace = makeWorkspace(t);

  writeFile(workspace, 'docs/specs/alpha/index.md', '- Task ID: T-01 | status: done\n');
  writeFile(workspace, 'docs/specs/beta/index.md', '- Task ID: T-01 | status: done\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /multiple|ambiguous/i);
});

test('blocks when a tracker exists but the completion target cannot be mapped to a durable entry', (t) => {
  const workspace = makeWorkspace(t);

  writeFile(workspace, 'docs/specs/alpha/index.md', '- Task ID: T-02 | status: done\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /map|entry/i);
});

test('blocks when the selected tracker still marks the target task as open', (t) => {
  const workspace = makeWorkspace(t);

  writeFile(workspace, 'docs/specs/alpha/index.md', '- Task ID: T-01 | status: in_progress\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /open|in_progress|ready|current/i);
});

test('blocks when configured authoritative surfaces disagree about open and closed state for the same task', (t) => {
  const workspace = makeWorkspace(t);

  writeFile(workspace, 'docs/specs/alpha/index.md', '- Task ID: T-01 | status: done\n');
  writeFile(workspace, 'docs/specs/alpha/tasks.md', '- Task ID: T-01 | status: in_progress\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_AUTHORITATIVE_STATE_SURFACE_PATHS: 'docs/specs/alpha/tasks.md',
    },
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /contradict|open.*closed|closed.*open/i);
});

test('blocks when the selected tracker maps the task but has no configured closed marker', (t) => {
  const workspace = makeWorkspace(t);

  writeFile(workspace, 'docs/specs/alpha/index.md', '- Task ID: T-01 | status: archived\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
  });

  assert.equal(result.status, 2);
  assert.match(result.stderr, /closed|closure|not reflect/i);
});

test('allows completion when durable state is consistently closed across configured surfaces', (t) => {
  const workspace = makeWorkspace(t);

  writeFile(workspace, 'docs/specs/alpha/index.md', '- Task ID: T-01 | status: done\n');
  writeFile(workspace, 'docs/specs/alpha/tasks.md', '- Task ID: T-01 | status: completed\n');

  const result = runHook({
    workspace,
    payload: makePayload(),
    env: {
      TASKCOMPLETED_AUTHORITATIVE_STATE_SURFACE_PATHS: 'docs/specs/alpha/tasks.md',
    },
  });

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
});
