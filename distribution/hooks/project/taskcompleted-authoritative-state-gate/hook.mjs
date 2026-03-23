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
  const trackerPaths = parseList(process.env.TASKCOMPLETED_AUTHORITATIVE_STATE_TRACKER_PATHS);
  const trackerGlobs = parseList(process.env.TASKCOMPLETED_AUTHORITATIVE_STATE_TRACKER_GLOBS);
  const surfacePaths = parseList(process.env.TASKCOMPLETED_AUTHORITATIVE_STATE_SURFACE_PATHS);
  const targetTemplate = (process.env.TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE ?? '').trim();
  const openMarkers = parseList(process.env.TASKCOMPLETED_AUTHORITATIVE_STATE_OPEN_MARKERS);
  const closedMarkers = parseList(process.env.TASKCOMPLETED_AUTHORITATIVE_STATE_CLOSED_MARKERS);

  if (!targetTemplate) {
    fail('Blocked: target mapping configuration is required; set TASKCOMPLETED_AUTHORITATIVE_STATE_TARGET_TEMPLATE explicitly.');
  }

  if (trackerPaths.length === 0 && trackerGlobs.length === 0) {
    fail('Blocked: configure at least one durable tracker path or glob.');
  }

  if (openMarkers.length === 0 || closedMarkers.length === 0) {
    fail('Blocked: configure explicit open and closed markers.');
  }

  return {
    trackerPaths,
    trackerGlobs,
    surfacePaths,
    targetTemplate,
    openMarkers,
    closedMarkers,
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

function normalize(text) {
  return text.toLowerCase();
}

function analyzeSurface(content, targetNeedle, openMarkers, closedMarkers) {
  const lines = content.split(/\r?\n/);
  const targetLines = lines.filter((line) => line.includes(targetNeedle));

  if (targetLines.length === 0) {
    return {
      hasTarget: false,
      state: 'missing',
    };
  }

  const normalizedLines = targetLines.map((line) => normalize(line));
  const hasOpen = normalizedLines.some((line) => openMarkers.some((marker) => line.includes(normalize(marker))));
  const hasClosed = normalizedLines.some((line) => closedMarkers.some((marker) => line.includes(normalize(marker))));

  if (hasOpen && hasClosed) {
    return {
      hasTarget: true,
      state: 'contradictory',
      lines: targetLines,
    };
  }

  if (hasOpen) {
    return {
      hasTarget: true,
      state: 'open',
      lines: targetLines,
    };
  }

  if (hasClosed) {
    return {
      hasTarget: true,
      state: 'closed',
      lines: targetLines,
    };
  }

  return {
    hasTarget: true,
    state: 'unclassified',
    lines: targetLines,
  };
}

function main() {
  const payload = parseJsonInput();

  if (payload.hook_event_name !== 'TaskCompleted') {
    fail(`Blocked: expected TaskCompleted hook input, got ${payload.hook_event_name ?? 'unknown'}.`);
  }

  const config = readConfig();
  const targetNeedle = expandTemplate(config.targetTemplate, payload).trim();

  if (!targetNeedle) {
    fail('Blocked: target mapping configuration resolved to an empty target identifier.');
  }

  const trackerFiles = resolveFileList(payload.cwd ?? process.cwd(), config.trackerPaths, config.trackerGlobs);

  if (trackerFiles.length === 0) {
    fail('Blocked: no configured durable tracker files resolved for this completion attempt.');
  }

  const trackerAnalyses = trackerFiles.map((filePath) => ({
    filePath,
    ...analyzeSurface(
      readFileSync(filePath, 'utf8'),
      targetNeedle,
      config.openMarkers,
      config.closedMarkers,
    ),
  }));

  const mappedTrackers = trackerAnalyses.filter((entry) => entry.hasTarget);

  if (mappedTrackers.length === 0) {
    fail(`Blocked: target task could not be mapped to durable state using configured target mapping (${targetNeedle}).`);
  }

  if (mappedTrackers.length > 1) {
    fail(`Blocked: multiple configured durable trackers matched the completion target (${targetNeedle}).`);
  }

  const [selectedTracker] = mappedTrackers;

  if (selectedTracker.state === 'open') {
    fail(`Blocked: durable tracker still marks the target task as open in ${selectedTracker.filePath}.`);
  }

  if (selectedTracker.state === 'contradictory') {
    fail(`Blocked: durable tracker shows contradictory open and closed state in ${selectedTracker.filePath}.`);
  }

  if (selectedTracker.state !== 'closed') {
    fail(`Blocked: durable tracker does not yet reflect clear closure for the target task in ${selectedTracker.filePath}.`);
  }

  const additionalSurfaces = resolveFileList(payload.cwd ?? process.cwd(), config.surfacePaths, []);
  const additionalAnalyses = additionalSurfaces.map((filePath) => ({
    filePath,
    ...analyzeSurface(
      readFileSync(filePath, 'utf8'),
      targetNeedle,
      config.openMarkers,
      config.closedMarkers,
    ),
  }));

  const contradictorySurface = additionalAnalyses.find((entry) => entry.state === 'open' || entry.state === 'contradictory');
  if (contradictorySurface) {
    fail(`Blocked: configured authoritative surfaces still disagree about open/closed state for the target task (${contradictorySurface.filePath}).`);
  }

  process.exit(0);
}

main();
