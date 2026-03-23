#!/usr/bin/env node

import { readFileSync, existsSync } from 'node:fs';
import { globSync } from 'node:fs';
import path from 'node:path';

function fail(message) {
  process.stderr.write(`${message}\n`);
  process.exit(2);
}

function parseJsonInput() {
  const input = readFileSync(0, 'utf8').trim();
  if (!input) {
    fail('Blocked: TaskCompleted payload is required on stdin.');
  }

  try {
    return JSON.parse(input);
  } catch {
    fail('Blocked: TaskCompleted payload must be valid JSON.');
  }
}

function parseList(value) {
  return (value ?? '')
    .split(',')
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function readConfig() {
  const signalGlobs = parseList(process.env.TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_GLOBS);
  const signalPaths = parseList(process.env.TASKCOMPLETED_REVIEW_EVIDENCE_GATE_SIGNAL_PATHS);
  const artifactGlobs = parseList(process.env.TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_GLOBS);
  const artifactPaths = parseList(process.env.TASKCOMPLETED_REVIEW_EVIDENCE_GATE_ARTIFACT_PATHS);
  const targetTemplate = (process.env.TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE ?? '').trim();
  const reviewerField = (process.env.TASKCOMPLETED_REVIEW_EVIDENCE_GATE_REVIEWER_FIELD ?? 'Reviewer').trim();
  const referenceField = (process.env.TASKCOMPLETED_REVIEW_EVIDENCE_GATE_REFERENCE_FIELD ?? 'Reference').trim();
  const outcomeField = (process.env.TASKCOMPLETED_REVIEW_EVIDENCE_GATE_OUTCOME_FIELD ?? 'Outcome').trim();
  const placeholderMarkers = parseList(
    process.env.TASKCOMPLETED_REVIEW_EVIDENCE_GATE_PLACEHOLDER_MARKERS ?? 'TBD,TODO,placeholder',
  );
  const passTokens = parseList(process.env.TASKCOMPLETED_REVIEW_EVIDENCE_GATE_PASS_TOKENS ?? 'PASS');

  if (!targetTemplate) {
    fail('Blocked: target mapping configuration is required; set TASKCOMPLETED_REVIEW_EVIDENCE_GATE_TARGET_TEMPLATE explicitly.');
  }

  if (signalGlobs.length === 0 && signalPaths.length === 0) {
    // Hook not active — no signal file configuration
    return null;
  }

  if (artifactGlobs.length === 0 && artifactPaths.length === 0) {
    fail('Blocked: configure at least one review artifact path or glob.');
  }

  if (placeholderMarkers.length === 0) {
    fail('Blocked: configure at least one placeholder marker.');
  }

  if (passTokens.length === 0) {
    fail('Blocked: configure at least one PASS token.');
  }

  return {
    signalGlobs,
    signalPaths,
    artifactGlobs,
    artifactPaths,
    targetTemplate,
    reviewerField,
    referenceField,
    outcomeField,
    placeholderMarkers,
    passTokens,
  };
}

function expandTemplate(template, payload) {
  return template.replaceAll(/\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g, (_, key) => {
    const value = payload[key];
    return value == null ? '' : String(value);
  });
}

function resolveFileList(cwd, paths, globs) {
  const resolved = new Set();

  for (const relativePath of paths) {
    resolved.add(path.resolve(cwd, relativePath));
  }

  for (const pattern of globs) {
    const matches = globSync(pattern, {
      cwd,
      nodir: true,
      withFileTypes: false,
    });

    for (const match of matches) {
      resolved.add(path.resolve(cwd, match));
    }
  }

  return [...resolved].filter((filePath) => existsSync(filePath));
}

function isPlaceholder(value, markers) {
  if (!value || typeof value !== 'string') return false;
  const lower = value.toLowerCase().trim();
  return markers.some((marker) => lower === marker.toLowerCase().trim());
}

function parseFrontMatter(content) {
  const fmMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!fmMatch) return null;

  const [, frontMatter, body] = fmMatch;
  return { frontMatter, body };
}

function parseYaml(content) {
  // Very simple YAML object parser for key: value pairs
  // Keys may contain spaces (e.g., "Task ID" is valid YAML)
  const result = {};
  const lines = content.split(/\r?\n/);
  let currentKey = null;
  let currentIndent = 0;

  for (const rawLine of lines) {
    const line = rawLine.replace(/^#.*/, '').trimEnd();
    if (!line) continue;

    // Detect key: value - key may contain spaces, starts with letter or underscore
    const kvMatch = line.match(/^([a-zA-Z_][a-zA-Z0-9_ ]*)\s*:\s*(.*)$/);
    if (kvMatch) {
      const [, rawKey, rawValue] = kvMatch;
      const key = rawKey.trim();
      let value = rawValue.trim();

      // Remove quotes
      if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
        value = value.slice(1, -1);
      }

      result[key] = value;
      currentKey = key;
      currentIndent = rawLine.length - rawLine.trimStart().length;
      continue;
    }

    // Continuation of previous value (indented)
    if (currentKey !== null && !line.match(/^[\[\]\{\}]/) && rawLine.startsWith(' '.repeat(currentIndent + 2))) {
      result[currentKey] += ' ' + line.trim();
    }
  }

  return result;
}

function parseReviewArtifact(content) {
  const fm = parseFrontMatter(content);
  if (fm) {
    const parsed = parseYaml(fm.frontMatter);
    if (parsed && Object.keys(parsed).length > 0) {
      return parsed;
    }
  }

  // Try JSON
  try {
    const json = JSON.parse(content);
    if (json && typeof json === 'object') {
      return json;
    }
  } catch {
    // Not JSON
  }

  // Fallback: try to find key: value pairs in plain text
  const lines = content.split(/\r?\n/);
  const result = {};
  for (const line of lines) {
    const kvMatch = line.match(/^([a-zA-Z0-9_ ]+):\s*(.*)$/);
    if (kvMatch) {
      result[kvMatch[1].trim()] = kvMatch[2].trim();
    }
  }
  return result;
}

function searchNeedleInFiles(files, needle) {
  const matches = [];

  for (const filePath of files) {
    const content = readFileSync(filePath, 'utf8');
    if (content.includes(needle)) {
      matches.push(filePath);
    }
  }

  return matches;
}

function findReviewEntryInArtifact(content, needle, reviewerField, referenceField, outcomeField) {
  const parsed = parseReviewArtifact(content);
  if (!parsed) return null;

  // Collect all entries from parsed structure
  const entries = [];
  if (Array.isArray(parsed)) {
    for (const item of parsed) {
      if (item && typeof item === 'object') {
        entries.push(item);
      }
    }
  } else if (parsed && typeof parsed === 'object') {
    entries.push(parsed);
  }

  // Search entries for needle
  // Check if needle appears anywhere in the serialized entry (key: value pairs)
  for (const entry of entries) {
    // Serialize entry to check needle presence
    const serialized = Object.entries(entry)
      .map(([k, v]) => `${k}: ${v}`)
      .join(' | ');
    if (serialized.includes(needle)) {
      return entry;
    }
  }

  return null;
}

function analyzeReviewArtifact(filePath, needle, reviewerField, referenceField, outcomeField, placeholderMarkers) {
  const content = readFileSync(filePath, 'utf8');
  const entry = findReviewEntryInArtifact(content, needle, reviewerField, referenceField, outcomeField);

  if (!entry) {
    return { found: false, filePath };
  }

  const reviewerKey = Object.keys(entry).find(
    (k) => k.toLowerCase() === reviewerField.toLowerCase(),
  );
  const referenceKey = Object.keys(entry).find(
    (k) => k.toLowerCase() === referenceField.toLowerCase(),
  );
  const outcomeKey = Object.keys(entry).find(
    (k) => k.toLowerCase() === outcomeField.toLowerCase(),
  );

  const reviewer = reviewerKey ? String(entry[reviewerKey] ?? '') : '';
  const reference = referenceKey ? String(entry[referenceKey] ?? '') : '';
  const outcome = outcomeKey ? String(entry[outcomeKey] ?? '') : '';

  return {
    found: true,
    filePath,
    entry,
    reviewer,
    reference,
    outcome,
  };
}

function main() {
  const payload = parseJsonInput();

  if (payload.hook_event_name !== 'TaskCompleted') {
    fail(`Blocked: expected TaskCompleted hook input, got ${payload.hook_event_name ?? 'unknown'}.`);
  }

  const config = readConfig();
  const cwd = payload.cwd ?? process.cwd();

  // If no signal file configuration, hook is not active
  if (config === null) {
    process.exit(0);
  }

  const targetNeedle = expandTemplate(config.targetTemplate, payload).trim();

  if (!targetNeedle) {
    fail('Blocked: target mapping configuration resolved to an empty target identifier.');
  }

  // Resolve signal files
  const signalFiles = resolveFileList(cwd, config.signalPaths, config.signalGlobs);

  if (signalFiles.length === 0) {
    // No review-required signal present
    process.exit(0);
  }

  // Search for needle in signal files
  const matchingSignalFiles = searchNeedleInFiles(signalFiles, targetNeedle);

  if (matchingSignalFiles.length === 0) {
    // This task is not review-required
    process.exit(0);
  }

  if (matchingSignalFiles.length > 1) {
    fail(`Blocked: multiple signal files matched the target task (${targetNeedle}).`);
  }

  // Resolve review artifact files
  const artifactFiles = resolveFileList(cwd, config.artifactPaths, config.artifactGlobs);

  if (artifactFiles.length === 0) {
    fail(`Blocked: no review artifact files resolved.`);
  }

  // Analyze each artifact file for the target entry
  const matchedEntries = [];

  for (const artifactFile of artifactFiles) {
    const analysis = analyzeReviewArtifact(
      artifactFile,
      targetNeedle,
      config.reviewerField,
      config.referenceField,
      config.outcomeField,
      config.placeholderMarkers,
    );

    if (analysis.found) {
      matchedEntries.push(analysis);
    }
  }

  if (matchedEntries.length === 0) {
    fail(`Blocked: target task not found in review artifact files.`);
  }

  if (matchedEntries.length > 1) {
    fail(`Blocked: ambiguous: multiple review entries matched the target task.`);
  }

  const [selectedEntry] = matchedEntries;

  if (isPlaceholder(selectedEntry.reviewer, config.placeholderMarkers)) {
    fail(`Blocked: Reviewer field is placeholder.`);
  }

  if (isPlaceholder(selectedEntry.reference, config.placeholderMarkers)) {
    fail(`Blocked: Reference field is placeholder.`);
  }

  if (!config.passTokens.includes(selectedEntry.outcome)) {
    fail(`Blocked: Outcome is not PASS (got: ${selectedEntry.outcome}).`);
  }

  process.exit(0);
}

main();
