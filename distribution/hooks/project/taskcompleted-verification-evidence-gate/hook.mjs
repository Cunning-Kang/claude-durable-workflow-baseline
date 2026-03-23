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
  const artifactGlobs = parseList(process.env.TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS);
  const artifactPaths = parseList(process.env.TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_PATHS);
  const targetTemplate = (process.env.TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE ?? '').trim();
  const evidenceSectionKeys = parseList(process.env.TASKCOMPLETED_VERIFICATION_EVIDENCE_SECTION_KEYS || 'Evidence,Verification');
  const evidenceRecordKeys = parseList(process.env.TASKCOMPLETED_VERIFICATION_EVIDENCE_RECORD_KEYS || 'Command,Check,Result,Date');
  const placeholderMarkers = parseList(process.env.TASKCOMPLETED_VERIFICATION_EVIDENCE_PLACEHOLDER_MARKERS || 'TODO,FIXME,fill in,replace me,your command here,your result here');
  const placeholderRegexRaw = process.env.TASKCOMPLETED_VERIFICATION_EVIDENCE_PLACEHOLDER_REGEX || '^\\s*(TODO|F?FIXME|fill in|replace me|\\[ ?\\]|___|your .* here)\\s*$';

  if (artifactGlobs.length === 0 && artifactPaths.length === 0) {
    fail('Blocked: configure at least one verification artifact glob or path via TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS or TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_PATHS.');
  }

  if (!targetTemplate) {
    fail('Blocked: target mapping configuration is required; set TASKCOMPLETED_VERIFICATION_EVIDENCE_TARGET_TEMPLATE explicitly.');
  }

  return {
    artifactGlobs,
    artifactPaths,
    targetTemplate,
    evidenceSectionKeys,
    evidenceRecordKeys,
    placeholderMarkers,
    placeholderRegex: new RegExp(placeholderRegexRaw, 'i'),
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

  for (const relativeGlob of globs) {
    const matches = globSync(relativeGlob, { cwd, absolute: true });
    matches.forEach((m) => resolved.add(m));
  }

  return Array.from(resolved);
}

function normalize(text) {
  return text.toLowerCase();
}

function findEvidenceSections(content, sectionKeys) {
  const lines = content.split(/\r?\n/);
  const sections = [];
  let currentSection = null;

  for (const line of lines) {
    const trimmed = line.trim();
    const isHeading = sectionKeys.some((key) => {
      const headingPattern = new RegExp(`^#{1,6}\\s+.*${key}.*`, 'i');
      return headingPattern.test(trimmed);
    });

    if (isHeading) {
      currentSection = { header: trimmed, lines: [] };
      sections.push(currentSection);
    } else if (currentSection) {
      currentSection.lines.push(trimmed);
    }
  }

  return sections;
}

function parseEvidenceRecords(sectionLines, recordKeys) {
  const records = [];
  let currentRecord = {};
  let currentKey = null;
  let currentValue = '';

  for (const line of sectionLines) {
    // Strip markdown heading prefix (## ) before parsing record fields
    const strippedLine = line.replace(/^#{1,6}\s*/, '');
    let keyMatched = null;
    for (const key of recordKeys) {
      const pattern = new RegExp(`^(${key})\\s*[:=]\\s*(.*)`, 'i');
      const match = strippedLine.match(pattern);
      if (match) {
        keyMatched = key;
        break;
      }
    }

    if (keyMatched) {
      if (currentKey && currentValue.trim()) {
        currentRecord[currentKey] = currentValue.trim();
      }
      currentKey = keyMatched;
      const pattern = new RegExp(`^(${keyMatched})\\s*[:=]\\s*(.*)`, 'i');
      const match = strippedLine.match(pattern);
      currentValue = match ? match[2] : '';
    } else if (currentKey) {
      const listItemPattern = /^[-*]\s+(.*)/;
      const listMatch = line.match(listItemPattern);
      if (listMatch) {
        currentValue += '\n' + listMatch[1];
      } else if (line.trim() === '' && currentValue.trim()) {
        // blank line might separate fields
      } else if (currentRecord[currentKey]) {
        currentRecord[currentKey] += ' ' + line;
      } else {
        currentValue += line;
      }
    }
  }

  if (currentKey && currentValue.trim()) {
    currentRecord[currentKey] = currentValue.trim();
  }

  if (Object.keys(currentRecord).length > 0) {
    records.push(currentRecord);
  }

  return records;
}

function isPlaceholderValue(value, placeholderMarkers, placeholderRegex) {
  if (!value || !value.trim()) return true;

  const trimmed = value.trim();

  if (placeholderMarkers.some((marker) => normalize(trimmed).includes(normalize(marker)))) {
    return true;
  }

  if (placeholderRegex.test(trimmed)) {
    return true;
  }

  return false;
}

function recordHasNonPlaceholderFields(record, recordKeys, placeholderMarkers, placeholderRegex) {
  const filledFields = recordKeys.filter((key) => {
    const value = record[key];
    return value && !isPlaceholderValue(value, placeholderMarkers, placeholderRegex);
  });

  return filledFields.length > 0;
}

function analyzeVerificationArtifact(content, config, targetNeedle) {
  const sections = findEvidenceSections(content, config.evidenceSectionKeys);

  if (sections.length === 0) {
    return { hasEvidenceSection: false, records: [], hasPopulatedRecord: false };
  }

  const allRecords = [];
  for (const section of sections) {
    const records = parseEvidenceRecords(section.lines, config.evidenceRecordKeys);
    allRecords.push(...records);
  }

  const populatedRecords = allRecords.filter((record) =>
    recordHasNonPlaceholderFields(record, config.evidenceRecordKeys, config.placeholderMarkers, config.placeholderRegex)
  );

  return {
    hasEvidenceSection: sections.length > 0,
    records: allRecords,
    hasPopulatedRecord: populatedRecords.length > 0,
    totalRecords: allRecords.length,
    populatedCount: populatedRecords.length,
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

  const cwd = payload.cwd ?? process.cwd();
  const artifactFiles = resolveFileList(cwd, config.artifactPaths, config.artifactGlobs);

  if (artifactFiles.length === 0) {
    fail('Blocked: no verification artifact files resolved. Ensure TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_GLOBS or TASKCOMPLETED_VERIFICATION_EVIDENCE_ARTIFACT_PATHS targets existing files in the project.');
  }

  const matchingArtifacts = artifactFiles.filter((filePath) => {
    const content = readFileSync(filePath, 'utf8');
    return content.includes(targetNeedle);
  });

  if (matchingArtifacts.length === 0) {
    fail(`Blocked: no verification artifact contains the target identifier (${targetNeedle}). Configure artifact paths/globs that resolve files where the target task is recorded.`);
  }

  if (matchingArtifacts.length > 1) {
    fail(`Blocked: multiple verification artifacts contain the target identifier (${targetNeedle}). Configure more specific paths to resolve exactly one artifact per task.`);
  }

  const [artifactPath] = matchingArtifacts;
  const artifactContent = readFileSync(artifactPath, 'utf8');
  const analysis = analyzeVerificationArtifact(artifactContent, config, targetNeedle);

  if (!analysis.hasEvidenceSection) {
    fail(`Blocked: verification artifact ${artifactPath} does not contain any recognized evidence section (${config.evidenceSectionKeys.join(', ')}).`);
  }

  if (analysis.totalRecords === 0) {
    fail(`Blocked: verification artifact ${artifactPath} contains an evidence section but no recognizable evidence records with fields (${config.evidenceRecordKeys.join(', ')}).`);
  }

  if (!analysis.hasPopulatedRecord) {
    fail(`Blocked: verification artifact ${artifactPath} evidence records contain only placeholder values. Fill in at least one record with actual command/check, result, and date information.`);
  }

  process.exit(0);
}

main();
