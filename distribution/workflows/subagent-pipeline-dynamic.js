export const meta = {
  name: 'subagent-pipeline-dynamic',
  description: 'Reusable dynamic workflow for GitHub issue implementation via named subagents, independent gates, global review, and confirm-gated closeout.',
  whenToUse: 'Use for repeatable GitHub issue implementation through task-planner, plan-reviewer, code-implementer, spec-reviewer, test-engineer, and code-reviewer.',
  phases: [
    { title: 'Setup', detail: 'Validate args, read issues with gh issue view, capture BASE_SHA, initialize dispatch ledger' },
    { title: 'Planning', detail: 'Route issue bodies through task-planner and plan-reviewer when task slicing is needed' },
    { title: 'Execute', detail: 'Run code-implementer and independent per-task gates with retry budget' },
    { title: 'Verify', detail: 'Preserve spec-reviewer, test-engineer, and code-reviewer evidence for each task' },
    { title: 'Global Review', detail: 'Run final code-reviewer on BASE_SHA..HEAD_SHA before closeout' },
    { title: 'Closeout', detail: 'Require explicit confirmation before commit, push, gh issue close, and state == "CLOSED" verification' },
    { title: 'Report', detail: 'Return status, ledger, evidence, closeout state, and recovery commands' }
  ]
}

const ROLE_AGENTS = {
  planning: 'task-planner',
  planReview: 'plan-reviewer',
  implementation: 'code-implementer',
  specCompliance: 'spec-reviewer',
  verification: 'test-engineer',
  codeReview: 'code-reviewer',
  closeout: 'deployment-operator',
}

const LEDGER_FIELDS = [
  'stage',
  'required_subagent',
  'identity_source',
  'tool_status',
  'role_status',
  'evidence_refs',
  'route_decision',
]

const RETRY_BUDGET = 3
const RESTATEMENT_BUDGET = 1
const DONE = 'DONE'
const PASS = 'PASS'
const FAIL = 'FAIL'
const BLOCKED = 'BLOCKED'
const READY_FOR_CLOSEOUT = 'READY_FOR_CLOSEOUT'
const IMMUTABLE_ISSUE_SPEC_RULE = 'Issue body is immutable task specification. Before Closeout phase, agents may read gh issue view only; they must not run gh issue edit, gh issue comment, or gh issue close. Implementation must occur in the repository workspace or, for no-op smoke tasks, return evidence-only DONE with no mutation.'

function normalizeArgs(input) {
  const source = input && typeof input === 'object' ? input : {}
  const plan = source.plan === 'force' || source.plan === 'skip' ? source.plan : 'auto'
  // phase3: disabled reports closeout commands without executing them.
  const phase3 = source.phase3 === 'required' || source.phase3 === 'disabled' ? source.phase3 : 'confirm'
  const groups = Array.isArray(source.groups) && source.groups.length
    ? source.groups.map(group => Array.isArray(group) ? group.map(Number).filter(Boolean) : [Number(group)].filter(Boolean)).filter(group => group.length)
    : [Array.isArray(source.issues) ? source.issues.map(Number).filter(Boolean) : []].filter(group => group.length)
  return {
    groups,
    issues: groups.flat(),
    plan,
    phase3,
    parallel: Boolean(source.parallel || groups.some(group => group.length > 1)),
    baseSha: typeof source.baseSha === 'string' ? source.baseSha : '',
    closeoutAuthorized: Boolean(source.closeoutAuthorized),
  }
}

function statusFromText(text, allowed) {
  const body = String(text || '')
  const firstLine = body.split('\n').map(line => line.trim()).find(Boolean) || ''
  const firstStatus = allowed.find(status => firstLine === `STATUS: ${status}` || firstLine.startsWith(`STATUS: ${status} `) || firstLine.startsWith(`${status}:`) || firstLine === status)
  if (firstStatus === FAIL || firstStatus === BLOCKED) return firstStatus
  const explicitBlockingStatus = body.match(/^STATUS:\s*(FAIL|BLOCKED)\b/m)
  if (explicitBlockingStatus && allowed.includes(explicitBlockingStatus[1])) return explicitBlockingStatus[1]
  const explicitStatusLine = body.match(/^STATUS:\s*(DONE|PASS|FAIL|BLOCKED|READY_FOR_CLOSEOUT)\b/m)
  if (explicitStatusLine && allowed.includes(explicitStatusLine[1])) return explicitStatusLine[1]
  const hasBlockingEvidence = /blocking_findings>\s*(?!None\b)|blocking findings?:\s*(?!None\b)|cannot verify|missing evidence/i.test(body)
  if (firstStatus && !hasBlockingEvidence) return firstStatus
  if (hasBlockingEvidence) return allowed.includes(BLOCKED) ? BLOCKED : FAIL
  const anyStatus = allowed.find(status => new RegExp(`\\b${status}\\b`).test(body))
  return anyStatus || ''
}

function downgradeOnlyStatus(text, allowed) {
  // downgrade-only semantic status mapping: never convert FAIL/BLOCKED to PASS/DONE, never fill missing evidence, never infer verification, never treat ambiguous polarity as PASS.
  return statusFromText(text, allowed)
}

function ledgerRow(ledger, stage, requiredSubagent, toolStatus, roleStatus, evidenceRefs, routeDecision) {
  const row = {
    stage,
    required_subagent: requiredSubagent,
    identity_source: 'invocation',
    tool_status: toolStatus,
    role_status: roleStatus,
    evidence_refs: evidenceRefs,
    route_decision: routeDecision,
  }
  ledger.push(row)
  return row
}

function blocked(message, ledger, extra) {
  return Object.assign({ status: BLOCKED, message, ledger }, extra || {})
}

function extractSha(text, label) {
  const pattern = new RegExp(`${label}:?\\s*([0-9a-f]{40})`, 'i')
  const match = String(text || '').match(pattern)
  return match ? match[1] : ''
}

async function dispatch(stage, requiredSubagent, prompt, allowedStatuses, ledger, label) {
  // Required named subagent selection unavailable: <name> => BLOCKED. Workflow runtime must use opts.agentType, not prompt impersonation.
  // No model override for role agents.
  let text = ''
  try {
    text = await agent(prompt, { label: label || `${stage}:${requiredSubagent}`, phase: stage, agentType: requiredSubagent })
  } catch (error) {
    ledgerRow(ledger, stage, requiredSubagent, 'error', BLOCKED, [`error:${String(error && error.message || error)}`], `BLOCKED: Required named subagent selection unavailable: ${requiredSubagent}`)
    return { status: BLOCKED, text: String(error && error.message || error), evidence: [] }
  }
  const roleStatus = downgradeOnlyStatus(text, allowedStatuses)
  if (!roleStatus) {
    ledgerRow(ledger, stage, requiredSubagent, 'success', BLOCKED, ['missing semantic STATUS/handoff evidence'], 'restate once')
    const restated = await agent(`Restate actual role status and evidence only. Do not change files. Allowed statuses: ${allowedStatuses.join(', ')}. Original handoff:\n${text}`, { label: `${stage}:${requiredSubagent}:restate`, phase: stage, agentType: requiredSubagent })
    const restatedStatus = downgradeOnlyStatus(restated, allowedStatuses)
    if (!restatedStatus) {
      ledgerRow(ledger, stage, requiredSubagent, 'success', BLOCKED, ['format budget exhausted after RESTATEMENT_BUDGET = 1'], 'route BLOCKED/FAIL by substance')
      return { status: BLOCKED, text: restated, evidence: [] }
    }
    ledgerRow(ledger, stage, requiredSubagent, 'success', restatedStatus, ['restated handoff'], restatedStatus)
    return { status: restatedStatus, text: restated, evidence: ['restated handoff'] }
  }
  ledgerRow(ledger, stage, requiredSubagent, 'success', roleStatus, ['agent handoff'], roleStatus)
  return { status: roleStatus, text, evidence: ['agent handoff'] }
}

async function dispatchCoordinator(stage, prompt, allowedStatuses, ledger, label) {
  // Coordinator utility dispatch may use default workflow agent for shell-capable setup/capture only.
  // It is not a review/test/spec gate and cannot satisfy named-subagent PASS gates.
  let text = ''
  try {
    text = await agent(prompt, { label: label || `${stage}:coordinator`, phase: stage })
  } catch (error) {
    ledgerRow(ledger, stage, 'coordinator', 'error', BLOCKED, [`error:${String(error && error.message || error)}`], 'BLOCKED')
    return { status: BLOCKED, text: String(error && error.message || error), evidence: [] }
  }
  const roleStatus = downgradeOnlyStatus(text, allowedStatuses)
  ledgerRow(ledger, stage, 'coordinator', 'success', roleStatus || BLOCKED, ['coordinator handoff'], roleStatus || BLOCKED)
  return { status: roleStatus || BLOCKED, text, evidence: ['coordinator handoff'] }
}

async function setupIssues(config, ledger) {
  phase('Setup')
  if (!config.issues.length) return blocked('No issues supplied. Provide args.issues or args.groups.', ledger)
  const setupPrompt = `Read repository state for dynamic subagent pipeline setup.\n\nRequired commands/evidence:\n- BASE_SHA = output of git rev-parse HEAD${config.baseSha ? `, unless supplied baseSha ${config.baseSha} is confirmed usable` : ''}\n- For each issue, run gh issue view <number> --json number,title,body,url,state\n- Report any gh issue view failure and halt.\n\nSafety rule: ${IMMUTABLE_ISSUE_SPEC_RULE}\n\nIssues: ${config.issues.map(n => `#${n}`).join(', ')}\n\nReturn STATUS: DONE with BASE_SHA, issue bodies, issue URLs, and state. Return STATUS: BLOCKED on any command failure.`
  const setup = await dispatchCoordinator('Setup', setupPrompt, [DONE, FAIL, BLOCKED], ledger, 'setup:issue-load')
  if (setup.status !== DONE) return blocked('Setup failed before implementation. gh issue view or BASE_SHA evidence missing.', ledger, { setup })
  const baseSha = config.baseSha || extractSha(setup.text, 'BASE_SHA')
  if (!baseSha) return blocked('Setup completed but BASE_SHA could not be parsed.', ledger, { setup })
  return { status: DONE, baseSha, setup }
}

function needsPlanner(config, issueText) {
  if (config.plan === 'force') return true
  if (config.plan === 'skip') return false
  const text = String(issueText || '')
  const hasSlices = /acceptance criteria|verification expectation|dependencies|blockers/i.test(text) && /task|T\d+|slice/i.test(text)
  const risky = /public contract|schema|CLI|API|config|security|migration|irreversible/i.test(text)
  const multipleAcceptance = (text.match(/acceptance/gi) || []).length > 1
  return risky || multipleAcceptance || !hasSlices
}

async function planIssue(config, issueNumber, setupText, ledger) {
  phase('Planning')
  if (!needsPlanner(config, setupText)) {
    ledgerRow(ledger, 'Planning', 'issue-body', 'success', DONE, [`issue #${issueNumber} structured breakdown`], 'skip task-planner')
    return { status: DONE, issueNumber, tasksText: `Use structured issue body for #${issueNumber}.\n\nSafety rule: ${IMMUTABLE_ISSUE_SPEC_RULE}\n\n${setupText}` }
  }
  if (config.plan === 'skip') {
    return blocked(`Issue #${issueNumber} cannot produce verifiable tasks safely with --no-plan semantics.`, ledger)
  }
  const plan = await dispatch('Planning', ROLE_AGENTS.planning, `Plan issue #${issueNumber} into independently verifiable task slices. Include behavior target, acceptance criteria, verification expectation, dependencies/blockers, likely files/context, and risk tier. Safety rule: ${IMMUTABLE_ISSUE_SPEC_RULE}\n\nSource issue/setup context:\n${setupText}`, [DONE, FAIL, BLOCKED], ledger, `plan:#${issueNumber}`)
  if (plan.status !== DONE) return blocked(`task-planner did not produce executable plan for #${issueNumber}.`, ledger, { plan })
  const review = await dispatch('Planning', ROLE_AGENTS.planReview, `Review this task breakdown for issue #${issueNumber}. PASS only if slices are independently verifiable and reviewer/tester scope is unambiguous. Source context and planner handoff:\n${plan.text}`, [PASS, FAIL, BLOCKED], ledger, `plan-review:#${issueNumber}`)
  if (review.status !== PASS) return blocked(`plan-reviewer did not PASS issue #${issueNumber}.`, ledger, { plan, review })
  return { status: DONE, issueNumber, tasksText: plan.text, plan, review }
}

async function runReviewerFixLoop(taskContext, reviewerResult, reviewerName, ledger, state) {
  state.retries += 1
  if (state.retries > RETRY_BUDGET) return blocked(`Retry budget exhausted after ${reviewerName} finding. RETRY_BUDGET = 3.`, ledger, { taskContext, reviewerResult })
  const fix = await dispatch('Execute', ROLE_AGENTS.implementation, `Fix task using original task context and ${reviewerName} findings. Do not broaden scope. Complete self-review before DONE. Safety rule: ${IMMUTABLE_ISSUE_SPEC_RULE}\n\nIf the task is an explicit no-op smoke task, do not edit files or issue body; return evidence-only STATUS: DONE when repository state and checks prove acceptance.\n\nTask context:\n${taskContext}\n\nFindings:\n${reviewerResult.text}`, [DONE, FAIL, BLOCKED], ledger, `fix:${reviewerName}`)
  if (fix.status !== DONE) return blocked(`code-implementer fix failed after ${reviewerName} finding.`, ledger, { fix })
  return { status: DONE, fix }
}

async function executeTask(taskContext, baseSha, ledger, label) {
  phase('Execute')
  const state = { retries: 0, specFails: 0, testFails: 0, reviewFails: 0 }
  let implementer = await dispatch('Execute', ROLE_AGENTS.implementation, `Implement this task only. Complete self-review for completeness, quality, YAGNI, and testing before STATUS: DONE. Safety rule: ${IMMUTABLE_ISSUE_SPEC_RULE}\n\nIf the task is an explicit no-op smoke task, do not edit files or issue body; return evidence-only STATUS: DONE when repository state and checks prove acceptance.\n\nTask context:\n${taskContext}`, [DONE, FAIL, BLOCKED], ledger, `implement:${label}`)
  if (implementer.status !== DONE) return blocked(`code-implementer did not complete ${label}.`, ledger, { implementer })

  phase('Verify')
  const specPrompt = handoff => `Verify implementation matches task spec. Read source independently. PASS requires matching scope and evidence. Safety rule: ${IMMUTABLE_ISSUE_SPEC_RULE}\n\nFor no-op smoke tasks, issue body is the immutable spec and should not be treated as implementation output.\n\nTask context:\n${taskContext}\n\nImplementer handoff:\n${handoff.text}`
  let spec = await dispatch('Verify', ROLE_AGENTS.specCompliance, specPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `spec:${label}`)
  while (spec.status !== PASS) {
    if (spec.status === BLOCKED) {
      state.retries += 1
      if (state.retries > RETRY_BUDGET) return blocked(`Retry budget exhausted after ${ROLE_AGENTS.specCompliance} BLOCKED. RETRY_BUDGET = 3.`, ledger, { taskContext, spec })
      spec = await dispatch('Verify', ROLE_AGENTS.specCompliance, `${specPrompt(implementer)}\n\nSupplemented context: re-check current repository/issue evidence. Do not ask implementer to change code unless spec mismatch is concrete. Previous BLOCKED handoff:\n${spec.text}`, [PASS, FAIL, BLOCKED], ledger, `spec-reconfirm:${label}`)
      continue
    }
    state.specFails += 1
    const fixed = await runReviewerFixLoop(taskContext, spec, ROLE_AGENTS.specCompliance, ledger, state)
    if (fixed.status !== DONE) return fixed
    implementer = fixed.fix
    spec = await dispatch('Verify', ROLE_AGENTS.specCompliance, specPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `spec-reconfirm:${label}`)
  }

  const testPrompt = handoff => `Verify acceptance criteria with tests or observable checks. Read source and test files independently. PASS requires commands/evidence; BLOCKED if environment prevents verification. Safety rule: ${IMMUTABLE_ISSUE_SPEC_RULE}\n\nFor no-op smoke tasks, verification may be evidence-only: prove no intentional repository mutation and no closeout action occurred.\n\nTask context:\n${taskContext}\n\nImplementer handoff:\n${handoff.text}`
  let test = await dispatch('Verify', ROLE_AGENTS.verification, testPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `test:${label}`)
  while (test.status !== PASS) {
    if (test.status === BLOCKED) {
      state.retries += 1
      if (state.retries > RETRY_BUDGET) return blocked(`Retry budget exhausted after ${ROLE_AGENTS.verification} BLOCKED. RETRY_BUDGET = 3.`, ledger, { taskContext, test })
      test = await dispatch('Verify', ROLE_AGENTS.verification, `${testPrompt(implementer)}\n\nSupplemented context: no-op smoke tasks can PASS with evidence-only checks when no mutation is required. Previous BLOCKED handoff:\n${test.text}`, [PASS, FAIL, BLOCKED], ledger, `test-reconfirm:${label}`)
      continue
    }
    state.testFails += 1
    const fixed = await runReviewerFixLoop(taskContext, test, ROLE_AGENTS.verification, ledger, state)
    if (fixed.status !== DONE) return fixed
    implementer = fixed.fix
    test = await dispatch('Verify', ROLE_AGENTS.verification, testPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `test-reconfirm:${label}`)
  }

  const reviewPrompt = handoff => `Review task diff for correctness, security, scope, maintainability, performance, and evidence. Use diff range BASE_SHA..HEAD_SHA, with BASE_SHA=${baseSha}. PASS requires no blocking findings. Safety rule: ${IMMUTABLE_ISSUE_SPEC_RULE}\n\nFor no-op smoke tasks, no repository diff may be acceptable when evidence proves no intentional mutation and required gates ran.\n\nTask context:\n${taskContext}\n\nImplementer handoff:\n${handoff.text}`
  let review = await dispatch('Verify', ROLE_AGENTS.codeReview, reviewPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `code-review:${label}`)
  while (review.status !== PASS) {
    if (review.status === BLOCKED) {
      state.retries += 1
      if (state.retries > RETRY_BUDGET) return blocked(`Retry budget exhausted after ${ROLE_AGENTS.codeReview} BLOCKED. RETRY_BUDGET = 3.`, ledger, { taskContext, review })
      review = await dispatch('Verify', ROLE_AGENTS.codeReview, `${reviewPrompt(implementer)}\n\nSupplemented context: no-op smoke tasks can PASS with no diff when evidence proves no mutation. Previous BLOCKED handoff:\n${review.text}`, [PASS, FAIL, BLOCKED], ledger, `code-review-reconfirm:${label}`)
      continue
    }
    state.reviewFails += 1
    if (state.reviewFails >= 2) {
      ledgerRow(ledger, 'Execute', ROLE_AGENTS.codeReview, 'success', FAIL, ['same reviewer FAIL twice'], 'full pipeline rewalk from implementer')
    }
    const fixed = await runReviewerFixLoop(taskContext, review, ROLE_AGENTS.codeReview, ledger, state)
    if (fixed.status !== DONE) return fixed
    implementer = fixed.fix
    review = await dispatch('Verify', ROLE_AGENTS.codeReview, reviewPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `code-review-reconfirm:${label}`)
  }

  return { status: PASS, taskContext, implementer, evidence: { spec, test, review } }
}

async function executeIssue(issuePlan, baseSha, ledger) {
  const taskContext = issuePlan.tasksText
  // The planner handoff may contain many task slices. Coordinator keeps prompt full-text so subagents never need to read a plan file.
  return executeTask(taskContext, baseSha, ledger, `issue-${issuePlan.issueNumber}`)
}

async function globalReview(config, baseSha, results, ledger) {
  phase('Global Review')
  const headPrompt = `Capture HEAD_SHA with git rev-parse HEAD. Then run final global review context assembly. Required diff range: BASE_SHA..HEAD_SHA where BASE_SHA=${baseSha}. Return STATUS: DONE with HEAD_SHA and changed files.`
  const head = await dispatchCoordinator('Global Review', headPrompt, [DONE, FAIL, BLOCKED], ledger, 'capture-head')
  if (head.status !== DONE) return blocked('HEAD_SHA capture failed before global review.', ledger, { head })
  const headSha = extractSha(head.text, 'HEAD_SHA') || 'HEAD_SHA from prior handoff'
  const review = await dispatch('Global Review', ROLE_AGENTS.codeReview, `Final global review. Review full diff BASE_SHA..HEAD_SHA before any push. No push before global review PASS. Safety rule: ${IMMUTABLE_ISSUE_SPEC_RULE}\n\nBASE_SHA: ${baseSha}\nHEAD_SHA: ${headSha}\nIssues: ${config.issues.map(n => `#${n}`).join(', ')}\nTask results:\n${JSON.stringify(results)}\n\nPASS only if all task acceptance criteria, verification evidence, and review evidence match current diff. For no-op smoke tasks, no repository diff may be acceptable when evidence proves no intentional mutation and required gates ran.`, [PASS, FAIL, BLOCKED], ledger, 'global-code-review')
  if (review.status !== PASS) return blocked('Global code-reviewer did not PASS.', ledger, { head, review })
  return { status: PASS, head, review }
}

async function closeout(config, global, ledger) {
  phase('Closeout')
  const commands = [
    'git status --short',
    'git add <explicit changed files>',
    `git commit -m "feat(workflow): complete issues ${config.issues.map(n => `#${n}`).join(', ')}"`,
    'git push',
    ...config.issues.map(n => `gh issue close ${n} --comment "Completed in <commit SHA>. <summary>"`),
    ...config.issues.map(n => `gh issue view ${n} --json state,url  # require state == "CLOSED"`),
  ]
  if (config.phase3 === 'disabled') {
    ledgerRow(ledger, 'Closeout', 'coordinator', 'skipped', READY_FOR_CLOSEOUT, commands, 'phase3 disabled; report commands only')
    return { status: READY_FOR_CLOSEOUT, mode: 'disabled', commands }
  }
  if (!config.closeoutAuthorized) {
    ledgerRow(ledger, 'Closeout', 'coordinator', 'blocked', READY_FOR_CLOSEOUT, commands, 'explicit confirmation required before commit/push/close')
    return { status: READY_FOR_CLOSEOUT, mode: config.phase3, message: 'explicit current-session authorization required before commit, push, gh issue close, and state == "CLOSED" verification.', commands }
  }
  const close = await dispatch('Closeout', ROLE_AGENTS.closeout, `Perform authorized closeout only. Authorization was supplied in workflow args closeoutAuthorized=true. Use explicit staging, one atomic commit, push, gh issue close, then verify each issue with gh issue view <number> --json state,url and require state == "CLOSED". If any close fails, retry once; if still not CLOSED, STATUS: BLOCKED with exact command/error/state.\n\nIssues: ${config.issues.map(n => `#${n}`).join(', ')}\nGlobal review handoff:\n${global.review.text}`, [DONE, FAIL, BLOCKED], ledger, 'authorized-closeout')
  if (close.status !== DONE) return blocked('Authorized closeout failed or could not verify CLOSED state.', ledger, { close, commands })
  return { status: DONE, commands, close }
}

phase('Setup')
const config = normalizeArgs(args)
const ledger = []
log(`Dynamic subagent pipeline starting for issues: ${config.issues.map(n => `#${n}`).join(', ') || '(none)'}`)
log(`Ledger fields: ${LEDGER_FIELDS.join(', ')}`)
log(`Retry budget: RETRY_BUDGET = ${RETRY_BUDGET}; restatement budget: RESTATEMENT_BUDGET = ${RESTATEMENT_BUDGET}`)

const setup = await setupIssues(config, ledger)
if (setup.status !== DONE) return setup

const issuePlans = []
for (const group of config.groups) {
  const plannedGroup = await parallel(group.map(issueNumber => () => planIssue(config, issueNumber, setup.setup.text, ledger)))
  const blockedPlan = plannedGroup.find(result => !result || result.status !== DONE)
  if (blockedPlan) return blocked('Planning failed for at least one issue group member.', ledger, { blockedPlan })
  issuePlans.push(...plannedGroup)
}

const issueResults = []
for (const group of config.groups) {
  const plans = issuePlans.filter(plan => group.includes(plan.issueNumber))
  const results = group.length > 1
    ? await parallel(plans.map(plan => () => executeIssue(plan, setup.baseSha, ledger)))
    : [await executeIssue(plans[0], setup.baseSha, ledger)]
  const blockedResult = results.find(result => !result || result.status !== PASS)
  if (blockedResult) return blocked('Execution failed for at least one issue. Halt subsequent issues.', ledger, { blockedResult, issueResults })
  issueResults.push(...results)
}

const global = await globalReview(config, setup.baseSha, issueResults, ledger)
if (global.status !== PASS) return global

const closeoutResult = await closeout(config, global, ledger)

phase('Report')
return {
  status: closeoutResult.status === DONE ? DONE : READY_FOR_CLOSEOUT,
  issues: config.issues,
  groups: config.groups,
  baseSha: setup.baseSha,
  closeout: closeoutResult,
  results: issueResults,
  globalReview: global,
  ledger,
  notes: [
    'Source-only reusable dynamic workflow asset.',
    'Coordinator delegates through named agentType dispatch only; no prompt impersonation and no model override for role agents.',
    'Phase 3 requires explicit current-session authorization before commit, push, gh issue close, and state == "CLOSED" verification.',
  ],
}
