export const meta = {
  name: 'subagent-pipeline-dynamic',
  description: 'Reusable dynamic workflow for issue, plan-file, and task work items via named subagents, independent gates, global review, and coordinator-owned commit closeout.',
  whenToUse: 'Use for repeatable work item execution from GitHub issues, plan files, or task text through task-planner, plan-reviewer, code-implementer, spec-reviewer, test-engineer, and code-reviewer.',
  phases: [
    { title: 'Setup', detail: 'Validate workItems, read issue/plan/task specs, capture BASE_SHA, initialize dispatch ledger' },
    { title: 'Planning', detail: 'Route work item specs through task-planner and plan-reviewer when task slicing is needed' },
    { title: 'Execute', detail: 'Run code-implementer and independent per-task gates with retry budget' },
    { title: 'Verify', detail: 'Preserve spec-reviewer, test-engineer, and code-reviewer evidence for each task' },
    { title: 'Global Review', detail: 'Run final code-reviewer on BASE_SHA..HEAD_SHA before commit' },
    { title: 'Closeout', detail: 'After global review PASS, coordinator plans commits, commits by file-group, optionally pushes, and optionally closes issues with state == "CLOSED" verification' },
    { title: 'Report', detail: 'Return DONE, READY_FOR_COMMIT, BLOCKED, or FAIL with ledger, evidence, commit plan, phase3 state, and recovery commands' }
  ]
}

const ROLE_AGENTS = {
  planning: 'task-planner',
  planReview: 'plan-reviewer',
  implementation: 'code-implementer',
  specCompliance: 'spec-reviewer',
  verification: 'test-engineer',
  codeReview: 'code-reviewer',
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
const READY_FOR_COMMIT = 'READY_FOR_COMMIT'
const IMMUTABLE_WORK_ITEM_SPEC_RULE = 'Work item spec is immutable task specification. Before authorized Closeout phase, agents may read issue bodies, plan files, and task text only; they must not run gh issue edit, gh issue comment, gh issue close, or modify plan-file/task specifications. Implementation must occur in the repository workspace or, for no-op smoke tasks, return evidence-only DONE with no mutation.'

function normalizeArgs(input) {
  const source = input && typeof input === 'object' ? input : {}
  const plan = source.plan === 'force' || source.plan === 'skip' ? source.plan : 'auto'
  const workItems = normalizeWorkItems(source)
  const groups = Array.isArray(source.groups) && source.groups.length
    ? source.groups.map(group => Array.isArray(group) ? group.map(normalizeWorkItem).filter(Boolean) : [normalizeWorkItem(group)].filter(Boolean)).filter(group => group.length)
    : workItems.length ? [workItems] : []
  const issues = groups.flat().filter(item => item.type === 'issue').map(item => item.issue)
  const closeIssues = Boolean(source.closeIssues)
  const push = Boolean(source.push) || closeIssues
  return {
    groups,
    workItems: groups.flat(),
    issues,
    plan,
    commit: source.noCommit ? false : true,
    push,
    closeIssues,
    parallel: Boolean(source.parallel || groups.some(group => group.length > 1)),
    requireParallel: Boolean(source.requireParallel),
    baseSha: typeof source.baseSha === 'string' ? source.baseSha : '',
  }
}

function normalizeWorkItems(source) {
  if (Array.isArray(source.workItems) && source.workItems.length) return source.workItems.map(normalizeWorkItem).filter(Boolean)
  const items = []
  for (const issue of Array.isArray(source.issues) ? source.issues : []) items.push(normalizeWorkItem({ type: 'issue', issue }))
  for (const path of Array.isArray(source.planFiles) ? source.planFiles : []) items.push(normalizeWorkItem({ type: 'plan-file', path }))
  for (const text of Array.isArray(source.tasks) ? source.tasks : []) items.push(normalizeWorkItem({ type: 'task', text }))
  return items.filter(Boolean)
}

function normalizeWorkItem(input) {
  if (typeof input === 'number') return { type: 'issue', issue: input, id: `issue-${input}`, label: `issue #${input}` }
  if (typeof input === 'string') {
    const trimmed = input.trim()
    const issue = trimmed.match(/^#?(\d+)$/)
    if (issue) return { type: 'issue', issue: Number(issue[1]), id: `issue-${issue[1]}`, label: `issue #${issue[1]}` }
    if (/\.md$/i.test(trimmed) || trimmed.includes('/')) return { type: 'plan-file', path: trimmed, id: `plan-file-${trimmed}`, label: `plan-file ${trimmed}` }
    return { type: 'task', text: trimmed, id: `task-${trimmed.slice(0, 40)}`, label: `task ${trimmed.slice(0, 40)}` }
  }
  if (!input || typeof input !== 'object') return null
  if (input.type === 'issue') {
    const issue = Number(input.issue || input.number || input.value)
    return issue ? { type: 'issue', issue, id: input.id || `issue-${issue}`, label: input.label || `issue #${issue}` } : null
  }
  if (input.type === 'plan-file') {
    const path = String(input.path || input.value || '').trim()
    return path ? { type: 'plan-file', path, id: input.id || `plan-file-${path}`, label: input.label || `plan-file ${path}` } : null
  }
  if (input.type === 'task') {
    const text = String(input.text || input.value || '').trim()
    return text ? { type: 'task', text, id: input.id || `task-${text.slice(0, 40)}`, label: input.label || `task ${text.slice(0, 40)}` } : null
  }
  return null
}

function statusFromText(text, allowed) {
  const body = String(text || '')
  const firstLine = body.split('\n').map(line => line.trim()).find(Boolean) || ''
  const firstStatus = allowed.find(status => firstLine === `STATUS: ${status}` || firstLine.startsWith(`STATUS: ${status} `) || firstLine.startsWith(`${status}:`) || firstLine === status)
  if (firstStatus === FAIL || firstStatus === BLOCKED) return firstStatus
  const explicitBlockingStatus = body.match(/^STATUS:\s*(FAIL|BLOCKED)\b/m)
  if (explicitBlockingStatus && allowed.includes(explicitBlockingStatus[1])) return explicitBlockingStatus[1]
  const explicitStatusLine = body.match(/^STATUS:\s*(DONE|PASS|FAIL|BLOCKED|READY_FOR_COMMIT)\b/m)
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
  // Coordinator utility dispatch may use default workflow agent for shell-capable setup/capture and Closeout mechanical git/gh actions only.
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

async function setupWorkItems(config, ledger) {
  phase('Setup')
  if (!config.workItems.length) return blocked('No workItems supplied. Interactive collection belongs to the skill/command layer; workflow args need issue, plan-file, or task work items.', ledger)
  const specLines = config.workItems.map(item => {
    if (item.type === 'issue') return `- ${item.label}: run gh issue view ${item.issue} --json number,title,body,url,state`
    if (item.type === 'plan-file') return `- ${item.label}: read plan file ${item.path} as immutable spec`
    return `- ${item.label}: use task text as immutable spec: ${item.text}`
  }).join('\n')
  const setupPrompt = `Read repository state for dynamic subagent pipeline setup.\n\nRequired commands/evidence:\n- BASE_SHA = output of git rev-parse HEAD${config.baseSha ? `, unless supplied baseSha ${config.baseSha} is confirmed usable` : ''}\n- For issue work items, run gh issue view <number> --json number,title,body,url,state\n- For plan-file work items, read the plan file content; report unreadable files and halt.\n- For task work items, preserve the task text exactly as immutable spec.\n- If current branch is the default branch, warn but do not create a branch automatically.\n\nSafety rule: ${IMMUTABLE_WORK_ITEM_SPEC_RULE}\n\nWork items:\n${specLines}\n\nReturn STATUS: DONE with BASE_SHA, work item specs, issue URLs/states when applicable, plan file paths, and task text. Return STATUS: BLOCKED on any command failure.`
  const setup = await dispatchCoordinator('Setup', setupPrompt, [DONE, FAIL, BLOCKED], ledger, 'setup:work-item-load')
  if (setup.status !== DONE) return blocked('Setup failed before implementation. Work item spec or BASE_SHA evidence missing.', ledger, { setup })
  const baseSha = config.baseSha || extractSha(setup.text, 'BASE_SHA')
  if (!baseSha) return blocked('Setup completed but BASE_SHA could not be parsed.', ledger, { setup })
  return { status: DONE, baseSha, setup }
}

function needsPlanner(config, specText) {
  if (config.plan === 'force') return true
  if (config.plan === 'skip') return false
  const text = String(specText || '')
  const hasSlices = /acceptance criteria|verification expectation|dependencies|blockers/i.test(text) && /task|T\d+|slice/i.test(text)
  const risky = /public contract|schema|CLI|API|config|security|migration|irreversible/i.test(text)
  const multipleAcceptance = (text.match(/acceptance/gi) || []).length > 1
  return risky || multipleAcceptance || !hasSlices
}

async function planWorkItem(config, workItem, setupText, ledger) {
  phase('Planning')
  if (!needsPlanner(config, setupText)) {
    ledgerRow(ledger, 'Planning', 'work-item-spec', 'success', DONE, [`${workItem.label} structured breakdown`], 'skip task-planner')
    return { status: DONE, workItem, tasksText: `Use structured work item spec for ${workItem.label}.\n\nSafety rule: ${IMMUTABLE_WORK_ITEM_SPEC_RULE}\n\n${setupText}` }
  }
  if (config.plan === 'skip') {
    return blocked(`Work item ${workItem.label} cannot produce verifiable tasks safely with --no-plan semantics.`, ledger)
  }
  const plan = await dispatch('Planning', ROLE_AGENTS.planning, `Plan work item ${workItem.label} into independently verifiable task slices. Include behavior target, acceptance criteria, verification expectation, dependencies/blockers, likely files/context, risk tier, and safe parallel patch-proposal groups when --parallel is requested. Safety rule: ${IMMUTABLE_WORK_ITEM_SPEC_RULE}\n\nSource setup/spec context:\n${setupText}`, [DONE, FAIL, BLOCKED], ledger, `plan:${workItem.id}`)
  if (plan.status !== DONE) return blocked(`task-planner did not produce executable plan for ${workItem.label}.`, ledger, { plan })
  const review = await dispatch('Planning', ROLE_AGENTS.planReview, `Review this task breakdown for work item ${workItem.label}. PASS only if slices are independently verifiable, reviewer/tester scope is unambiguous, dependencies are ordered, and any proposed parallel groups are safe. If --parallel was requested but parallelization is unsafe, PASS the plan and reject parallelization rather than BLOCKED unless parallel was required. Source context and planner handoff:\n${plan.text}`, [PASS, FAIL, BLOCKED], ledger, `plan-review:${workItem.id}`)
  if (review.status !== PASS) return blocked(`plan-reviewer did not PASS ${workItem.label}.`, ledger, { plan, review })
  if (config.parallel) ledgerRow(ledger, 'Planning', ROLE_AGENTS.planReview, 'success', PASS, ['parallel groups reviewed by plan-reviewer'], 'parallel requested; use approved patch-proposal groups or execute sequentially')
  return { status: DONE, workItem, tasksText: plan.text, plan, review }
}

async function runReviewerFixLoop(taskContext, reviewerResult, reviewerName, ledger, state) {
  state.retries += 1
  if (state.retries > RETRY_BUDGET) return blocked(`Retry budget exhausted after ${reviewerName} finding. RETRY_BUDGET = 3.`, ledger, { taskContext, reviewerResult })
  const fix = await dispatch('Execute', ROLE_AGENTS.implementation, `Fix task using original task context and ${reviewerName} findings. Do not broaden scope. Complete self-review before DONE. Safety rule: ${IMMUTABLE_WORK_ITEM_SPEC_RULE}\n\nIf the task is an explicit no-op smoke task, do not edit files or work item spec; return evidence-only STATUS: DONE when repository state and checks prove acceptance.\n\nTask context:\n${taskContext}\n\nFindings:\n${reviewerResult.text}`, [DONE, FAIL, BLOCKED], ledger, `fix:${reviewerName}`)
  if (fix.status !== DONE) return blocked(`code-implementer fix failed after ${reviewerName} finding.`, ledger, { fix })
  return { status: DONE, fix }
}

async function executeTask(taskContext, baseSha, ledger, label) {
  phase('Execute')
  const state = { retries: 0, specFails: 0, testFails: 0, reviewFails: 0, rewalks: 0 }
  const implementPrompt = extra => `Implement this task only. Complete self-review for completeness, quality, YAGNI, and testing before STATUS: DONE. Safety rule: ${IMMUTABLE_WORK_ITEM_SPEC_RULE}\n\nIf running as a parallel patch-proposal worker, return a unified diff patch, changed files, focused verification notes, assumptions, and risks; coordinator applies patches sequentially on main and authoritative gates run there.\n\nIf the task is an explicit no-op smoke task, do not edit files or work item spec; return evidence-only STATUS: DONE when repository state and checks prove acceptance.${extra ? `\n\n${extra}` : ''}\n\nTask context:\n${taskContext}`
  let implementer = await dispatch('Execute', ROLE_AGENTS.implementation, implementPrompt(''), [DONE, FAIL, BLOCKED], ledger, `implement:${label}`)
  if (implementer.status !== DONE) return blocked(`code-implementer did not complete ${label}.`, ledger, { implementer })

  phase('Verify')
  const specPrompt = handoff => `Verify implementation matches task spec. Read source independently. PASS requires matching scope and evidence. Safety rule: ${IMMUTABLE_WORK_ITEM_SPEC_RULE}\n\nFor no-op smoke tasks, work item spec is immutable and should not be treated as implementation output.\n\nTask context:\n${taskContext}\n\nImplementer handoff:\n${handoff.text}`
  let spec = await dispatch('Verify', ROLE_AGENTS.specCompliance, specPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `spec:${label}`)
  while (spec.status !== PASS) {
    if (spec.status === BLOCKED) {
      state.retries += 1
      if (state.retries > RETRY_BUDGET) return blocked(`Retry budget exhausted after ${ROLE_AGENTS.specCompliance} BLOCKED. RETRY_BUDGET = 3.`, ledger, { taskContext, spec })
      spec = await dispatch('Verify', ROLE_AGENTS.specCompliance, `${specPrompt(implementer)}\n\nSupplemented context: re-check current repository/work item evidence. Do not ask implementer to change code unless spec mismatch is concrete. Previous BLOCKED handoff:\n${spec.text}`, [PASS, FAIL, BLOCKED], ledger, `spec-reconfirm:${label}`)
      continue
    }
    state.specFails += 1
    const fixed = await runReviewerFixLoop(taskContext, spec, ROLE_AGENTS.specCompliance, ledger, state)
    if (fixed.status !== DONE) return fixed
    implementer = fixed.fix
    spec = await dispatch('Verify', ROLE_AGENTS.specCompliance, specPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `spec-reconfirm:${label}`)
  }

  const testPrompt = handoff => `Verify acceptance criteria with tests or observable checks. Read source and test files independently. PASS requires commands/evidence; BLOCKED if environment prevents verification. Safety rule: ${IMMUTABLE_WORK_ITEM_SPEC_RULE}\n\nFor no-op smoke tasks, verification may be evidence-only: prove no intentional repository mutation and no closeout action occurred.\n\nTask context:\n${taskContext}\n\nImplementer handoff:\n${handoff.text}`
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

  const reviewPrompt = handoff => `Review task diff for correctness, security, scope, maintainability, performance, and evidence. Use diff range BASE_SHA..HEAD_SHA, with BASE_SHA=${baseSha}. PASS requires no blocking findings. Safety rule: ${IMMUTABLE_WORK_ITEM_SPEC_RULE}\n\nFor no-op smoke tasks, no repository diff may be acceptable when evidence proves no mutation.\n\nTask context:\n${taskContext}\n\nImplementer handoff:\n${handoff.text}`
  let review = await dispatch('Verify', ROLE_AGENTS.codeReview, reviewPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `code-review:${label}`)
  while (review.status !== PASS) {
    if (review.status === BLOCKED) {
      state.retries += 1
      if (state.retries > RETRY_BUDGET) return blocked(`Retry budget exhausted after ${ROLE_AGENTS.codeReview} BLOCKED. RETRY_BUDGET = 3.`, ledger, { taskContext, review })
      review = await dispatch('Verify', ROLE_AGENTS.codeReview, `${reviewPrompt(implementer)}\n\nSupplemented context: no-op smoke tasks can PASS with no diff when evidence proves no mutation. Previous BLOCKED handoff:\n${review.text}`, [PASS, FAIL, BLOCKED], ledger, `code-review-reconfirm:${label}`)
      continue
    }
    state.reviewFails += 1
    if (state.reviewFails >= 2 && state.rewalks < 1) {
      state.rewalks += 1
      ledgerRow(ledger, 'Execute', ROLE_AGENTS.codeReview, 'success', FAIL, ['same reviewer FAIL twice'], 'full pipeline rewalk from implementer')
      const rewalk = await dispatch('Execute', ROLE_AGENTS.implementation, implementPrompt(`Escalation rewalk after two consecutive code-reviewer FAIL results. Do not broaden scope. Address the reviewer findings, then expect full spec-reviewer, test-engineer, and code-reviewer gates to rerun. Escalation rewalk implementer dispatch does NOT consume retry budget.\n\nLatest code-reviewer findings:\n${review.text}`), [DONE, FAIL, BLOCKED], ledger, `rewalk-implement:${label}`)
      if (rewalk.status !== DONE) return blocked('code-implementer escalation rewalk failed.', ledger, { rewalk })
      implementer = rewalk
      spec = await dispatch('Verify', ROLE_AGENTS.specCompliance, specPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `rewalk-spec:${label}`)
      if (spec.status !== PASS) {
        const fixed = await runReviewerFixLoop(taskContext, spec, ROLE_AGENTS.specCompliance, ledger, state)
        if (fixed.status !== DONE) return fixed
        implementer = fixed.fix
        spec = await dispatch('Verify', ROLE_AGENTS.specCompliance, specPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `rewalk-spec-reconfirm:${label}`)
        if (spec.status !== PASS) return blocked('spec-reviewer did not PASS after escalation rewalk.', ledger, { spec })
      }
      test = await dispatch('Verify', ROLE_AGENTS.verification, testPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `rewalk-test:${label}`)
      if (test.status !== PASS) {
        const fixed = await runReviewerFixLoop(taskContext, test, ROLE_AGENTS.verification, ledger, state)
        if (fixed.status !== DONE) return fixed
        implementer = fixed.fix
        test = await dispatch('Verify', ROLE_AGENTS.verification, testPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `rewalk-test-reconfirm:${label}`)
        if (test.status !== PASS) return blocked('test-engineer did not PASS after escalation rewalk.', ledger, { test })
      }
      review = await dispatch('Verify', ROLE_AGENTS.codeReview, reviewPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `rewalk-code-review:${label}`)
      continue
    }
    const fixed = await runReviewerFixLoop(taskContext, review, ROLE_AGENTS.codeReview, ledger, state)
    if (fixed.status !== DONE) return fixed
    implementer = fixed.fix
    review = await dispatch('Verify', ROLE_AGENTS.codeReview, reviewPrompt(implementer), [PASS, FAIL, BLOCKED], ledger, `code-review-reconfirm:${label}`)
  }

  return { status: PASS, taskContext, implementer, changedFiles: ['<from implementer handoff>'], evidence: { spec, test, review } }
}

async function executeWorkItem(workItemPlan, baseSha, ledger) {
  const taskContext = workItemPlan.tasksText
  return executeTask(taskContext, baseSha, ledger, workItemPlan.workItem.id)
}

async function globalReview(config, baseSha, results, ledger) {
  phase('Global Review')
  const headPrompt = `Capture HEAD_SHA with git rev-parse HEAD. Then run final global review context assembly. Required diff range: BASE_SHA..HEAD_SHA where BASE_SHA=${baseSha}. Return STATUS: DONE with HEAD_SHA and changed files.`
  const head = await dispatchCoordinator('Global Review', headPrompt, [DONE, FAIL, BLOCKED], ledger, 'capture-head')
  if (head.status !== DONE) return blocked('HEAD_SHA capture failed before global review.', ledger, { head })
  const headSha = extractSha(head.text, 'HEAD_SHA') || 'HEAD_SHA from prior handoff'
  const review = await dispatch('Global Review', ROLE_AGENTS.codeReview, `Final global review. Review full diff BASE_SHA..HEAD_SHA before any commit or push. No push before global review PASS. Safety rule: ${IMMUTABLE_WORK_ITEM_SPEC_RULE}\n\nBASE_SHA: ${baseSha}\nHEAD_SHA: ${headSha}\nWork items: ${config.workItems.map(item => item.label).join(', ')}\nTask results:\n${JSON.stringify(results)}\n\nPASS only if all task acceptance criteria, verification evidence, and review evidence match current diff. For no-op smoke tasks, no repository diff may be acceptable when evidence proves no intentional mutation and required gates ran.`, [PASS, FAIL, BLOCKED], ledger, 'global-code-review')
  if (review.status !== PASS) return blocked('Global code-reviewer did not PASS.', ledger, { head, review })
  return { status: PASS, head, review }
}

function buildCommitPlan(config) {
  const issueRefs = config.issues.map(n => `#${n}`)
  const summary = config.workItems.map(item => item.label).join(', ')
  const refs = issueRefs.map(ref => config.closeIssues ? `Closes ${ref}` : `Refs ${ref}`)
  const subject = config.workItems.length === 1 ? `feat(workflow): complete ${summary}` : `feat(workflow): complete ${config.workItems.length} work items`
  return [{
    subject,
    refs,
    files: ['<explicit changed files from git diff --name-only BASE_SHA>'],
    commands: [
      'git status --short',
      'git add <explicit changed files>',
      `git commit -m "${subject}"`,
    ],
  }]
}

async function closeout(config, global, ledger) {
  phase('Closeout')
  const commitPlan = buildCommitPlan(config)
  if (!config.commit) {
    ledgerRow(ledger, 'Closeout', 'coordinator', 'skipped', READY_FOR_COMMIT, ['commit plan ready; --no-commit requested'], 'report READY_FOR_COMMIT')
    return { status: READY_FOR_COMMIT, phase3: { commit: 'skipped', push: 'skipped', closeIssues: 'skipped' }, commitPlan }
  }
  const commit = await dispatchCoordinator('Closeout', `Coordinator-owned mechanical commit after global review PASS. Do not implement, test, or review code.\n\nRequired commands/evidence:\n- git status --short\n- Build file-level commit groups from changed files and work item ownership. If file ownership cannot be mapped safely, create one combined commit.\n- Stage explicit files only; do not use git add .\n- Create atomic commit(s) with issue refs. Use Closes #N only when closeIssues is true; otherwise use Refs #N.\n- Include Co-Authored-By: Claude <noreply@anthropic.com>.\n- Verify with git show --stat --oneline HEAD.\n\nCommit plan seed:\n${JSON.stringify(commitPlan)}\n\nGlobal review handoff:\n${global.review.text}\n\nReturn STATUS: DONE with commit SHA(s), staged files, and git status. Return STATUS: BLOCKED with exact command/error if commit fails.`, [DONE, FAIL, BLOCKED], ledger, 'commit')
  if (commit.status !== DONE) return blocked('Commit failed after global review PASS.', ledger, { commit, commitPlan })

  let push = { status: 'skipped' }
  if (config.push) {
    push = await dispatchCoordinator('Closeout', 'Coordinator-owned mechanical push after commit. Run git push for the current branch. Return STATUS: DONE with remote/ref evidence or STATUS: BLOCKED with exact command/error.', [DONE, FAIL, BLOCKED], ledger, 'push')
    if (push.status !== DONE) return blocked('Push failed after commit.', ledger, { commit, push, commitPlan })
  }

  const closeResults = []
  if (config.closeIssues) {
    for (const n of config.issues) {
      const close = await dispatchCoordinator('Closeout', `Coordinator-owned issue close after commit and push. Run gh issue close ${n} --comment "Completed in <commit SHA>. <summary>" then gh issue view ${n} --json state,url. Require state == "CLOSED". If close fails, retry once; if still not CLOSED, return STATUS: BLOCKED with exact command/error/state.`, [DONE, FAIL, BLOCKED], ledger, `close-issue:${n}`)
      closeResults.push({ issue: n, close })
      if (close.status !== DONE) return blocked('Issue close failed or CLOSED state could not be verified.', ledger, { commit, push, closeResults, commitPlan })
    }
  }

  return { status: DONE, phase3: { commit: 'created', push: config.push ? 'done' : 'skipped', closeIssues: config.closeIssues ? 'done' : 'skipped' }, commitPlan, commit, push, closeResults }
}

phase('Setup')
const config = normalizeArgs(args)
const ledger = []
log(`Dynamic subagent pipeline starting for work items: ${config.workItems.map(item => item.label).join(', ') || '(none)'}`)
log(`Ledger fields: ${LEDGER_FIELDS.join(', ')}`)
log(`Retry budget: RETRY_BUDGET = ${RETRY_BUDGET}; restatement budget: RESTATEMENT_BUDGET = ${RESTATEMENT_BUDGET}`)
log(`Phase 3: commit=${config.commit}; push=${config.push}; closeIssues=${config.closeIssues}`)
if (config.parallel) log('Parallel requested: task-planner must propose safe patch-proposal groups and plan-reviewer must approve; patches apply sequentially on main and gates run on main.')

const setup = await setupWorkItems(config, ledger)
if (setup.status !== DONE) return setup

const workItemPlans = []
for (const group of config.groups) {
  const plannedGroup = await parallel(group.map(workItem => () => planWorkItem(config, workItem, setup.setup.text, ledger)))
  const blockedPlan = plannedGroup.find(result => !result || result.status !== DONE)
  if (blockedPlan) return blocked('Planning failed for at least one work item group member.', ledger, { blockedPlan })
  workItemPlans.push(...plannedGroup)
}

const workItemResults = []
for (const group of config.groups) {
  const plans = workItemPlans.filter(plan => group.some(item => item.id === plan.workItem.id))
  const results = group.length > 1 && config.parallel
    ? await parallel(plans.map(plan => () => executeWorkItem(plan, setup.baseSha, ledger)))
    : await pipeline(plans, plan => executeWorkItem(plan, setup.baseSha, ledger))
  const blockedResult = results.find(result => !result || result.status !== PASS)
  if (blockedResult) return blocked('Execution failed for at least one work item. Halt subsequent work items.', ledger, { blockedResult, workItemResults })
  workItemResults.push(...results)
}

const global = await globalReview(config, setup.baseSha, workItemResults, ledger)
if (global.status !== PASS) return global

const closeoutResult = await closeout(config, global, ledger)

phase('Report')
return {
  status: closeoutResult.status === DONE ? DONE : closeoutResult.status === READY_FOR_COMMIT ? READY_FOR_COMMIT : BLOCKED,
  workItems: config.workItems,
  issues: config.issues,
  groups: config.groups,
  baseSha: setup.baseSha,
  closeout: closeoutResult,
  phase3: closeoutResult.phase3,
  results: workItemResults,
  globalReview: global,
  ledger,
  notes: [
    'Source-only reusable dynamic workflow asset.',
    'Coordinator delegates through named agentType dispatch only; no prompt impersonation and no model override for role agents.',
    'Phase 3 is coordinator-owned mechanical report plus atomic commit by default; push and issue close require --push or --close-issues.',
    'Top-level statuses are DONE, READY_FOR_COMMIT, BLOCKED, and FAIL.',
  ],
}
