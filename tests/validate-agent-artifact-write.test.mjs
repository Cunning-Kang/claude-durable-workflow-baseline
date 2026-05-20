import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const HOOK = path.resolve('distribution/hooks/user/validate-agent-artifact-write/hook.mjs');

function runHook(agent, payload, env = {}) {
  return spawnSync(process.execPath, [HOOK, agent], {
    input: JSON.stringify(payload),
    text: true,
    env: { ...process.env, ...env },
  });
}

function writePayload(filePath) {
  return { hook_event_name: 'PreToolUse', tool_name: 'Write', tool_input: { file_path: filePath, content: 'x' } };
}

test('allows non-Write tool', () => {
  const result = runHook('code-reviewer', { tool_name: 'Read' });
  assert.equal(result.status, 0);
});

test('blocks invalid json', () => {
  const result = spawnSync(process.execPath, [HOOK, 'code-reviewer'], { input: '{', text: true });
  assert.equal(result.status, 2);
});

test('blocks missing file_path', () => {
  const result = runHook('code-reviewer', { tool_name: 'Write', tool_input: {} });
  assert.equal(result.status, 2);
});

test('blocks relative path', () => {
  const result = runHook('code-reviewer', writePayload('claude-agent-artifacts/code-reviewer-a.md'));
  assert.equal(result.status, 2);
});

test('allows temp artifact for matching agent', () => {
  const tmp = mkdtempSync(path.join(os.tmpdir(), 'artifact-hook-'));
  const result = runHook('code-reviewer', writePayload(path.join(tmp, 'claude-agent-artifacts', 'code-reviewer-abc.md')), { TMPDIR: tmp });
  assert.equal(result.status, 0, result.stderr);
});

test('blocks outside temp root', () => {
  const tmp = mkdtempSync(path.join(os.tmpdir(), 'artifact-hook-'));
  const result = runHook('code-reviewer', writePayload(path.join(tmp, 'other', 'code-reviewer-abc.md')), { TMPDIR: tmp });
  assert.equal(result.status, 2);
});

test('blocks traversal outside temp root', () => {
  const tmp = mkdtempSync(path.join(os.tmpdir(), 'artifact-hook-'));
  const result = runHook('code-reviewer', writePayload(path.join(tmp, 'claude-agent-artifacts', '..', 'code-reviewer-abc.md')), { TMPDIR: tmp });
  assert.equal(result.status, 2);
});

test('blocks wrong agent prefix', () => {
  const tmp = mkdtempSync(path.join(os.tmpdir(), 'artifact-hook-'));
  const result = runHook('code-reviewer', writePayload(path.join(tmp, 'claude-agent-artifacts', 'task-planner-abc.md')), { TMPDIR: tmp });
  assert.equal(result.status, 2);
});

test('blocks wrong extension', () => {
  const tmp = mkdtempSync(path.join(os.tmpdir(), 'artifact-hook-'));
  const result = runHook('code-reviewer', writePayload(path.join(tmp, 'claude-agent-artifacts', 'code-reviewer-abc.txt')), { TMPDIR: tmp });
  assert.equal(result.status, 2);
});

test('blocks project artifact path by default', () => {
  const result = runHook('code-reviewer', writePayload(path.resolve('.claude/agent-artifacts/code-reviewer-abc.md')));
  assert.equal(result.status, 2);
});
