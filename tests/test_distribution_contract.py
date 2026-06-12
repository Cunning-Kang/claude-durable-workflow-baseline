import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = REPO_ROOT / "distribution/scripts/init-claude-workflow.sh"
NEW_FEATURE_SCRIPT = REPO_ROOT / "distribution/scripts/instantiate-feature.sh"
NEW_FEATURE_COMMAND = REPO_ROOT / "distribution/commands/new-feature.md"
SUBAGENT_PIPELINE_WORKFLOW_COMMAND = REPO_ROOT / "distribution/commands/subagent-pipeline-workflow.md"
SUBAGENT_PIPELINE_DYNAMIC_WORKFLOW = REPO_ROOT / "distribution/workflows/subagent-pipeline-dynamic.js"
README = REPO_ROOT / "README.md"
BOOTSTRAP_DOC = REPO_ROOT / "docs/claude-one-command-bootstrap.md"
CANONICAL_CACHE_PATH = "~/.claude/baselines/durable-workflow-v1"


class DistributionContractTests(unittest.TestCase):
    def make_git_repo(self) -> Path:
        temp_dir = Path(tempfile.mkdtemp(prefix="workflow-contract-"))
        self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))
        subprocess.run(["git", "init", str(temp_dir)], check=True, capture_output=True, text=True)
        return temp_dir

    def test_init_script_initializes_repo_from_canonical_cache_root(self):
        repo_dir = self.make_git_repo()
        env = os.environ | {"CLAUDE_WORKFLOW_BASELINE_PATH": str(REPO_ROOT)}

        result = subprocess.run(
            [str(INIT_SCRIPT), str(repo_dir)],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

        self.assertIn("Baseline version", result.stdout)
        self.assertTrue((repo_dir / "docs/specs/_template/spec.md").exists())
        self.assertTrue((repo_dir / "docs/workflow/review-protocol.md").exists())
        self.assertTrue((repo_dir / "memory/MEMORY.md").exists())
        self.assertTrue((repo_dir / ".claude/workflow-baseline-version").exists())

    def test_instantiate_feature_creates_feature_from_template(self):
        repo_dir = self.make_git_repo()
        env = os.environ | {"CLAUDE_WORKFLOW_BASELINE_PATH": str(REPO_ROOT)}

        result = subprocess.run(
            [str(NEW_FEATURE_SCRIPT), "user-auth"],
            check=True,
            capture_output=True,
            text=True,
            cwd=repo_dir,
            env=env,
        )

        self.assertIn("FEATURE INSTANCE CREATED", result.stdout)
        spec_file = repo_dir / "docs/specs/user-auth/spec.md"
        tasks_file = repo_dir / "docs/specs/user-auth/tasks/T01-example.md"

        self.assertTrue(spec_file.exists())
        self.assertTrue(tasks_file.exists())
        self.assertIn("user-auth", spec_file.read_text())
        self.assertIn("Example durable task", tasks_file.read_text())

    def test_new_feature_command_uses_slash_command_frontmatter_and_installed_script_path(self):
        content = NEW_FEATURE_COMMAND.read_text()

        self.assertTrue(content.startswith("---\n"))
        self.assertIn("description:", content)
        self.assertIn("argument-hint: <feature-slug>", content)
        self.assertIn("~/.claude/scripts/instantiate-feature.sh", content)
        self.assertNotIn("name: new-feature", content)

    def test_docs_describe_installing_new_feature_command_and_scripts(self):
        readme = README.read_text()
        bootstrap = BOOTSTRAP_DOC.read_text()

        self.assertIn(CANONICAL_CACHE_PATH, readme)
        self.assertIn(CANONICAL_CACHE_PATH, bootstrap)
        self.assertIn("distribution/commands/new-feature.md", readme)
        self.assertIn("distribution/commands/subagent-pipeline-workflow.md", readme)
        self.assertIn("distribution/workflows/subagent-pipeline-dynamic.js", readme)
        self.assertIn("distribution/scripts/*.sh", readme)
        self.assertIn("mkdir -p ~/.claude/scripts", readme)
        self.assertIn("distribution/commands/new-feature.md", bootstrap)
        self.assertIn("distribution/commands/subagent-pipeline-workflow.md", bootstrap)
        self.assertIn("distribution/workflows/subagent-pipeline-dynamic.js", bootstrap)
        self.assertIn("distribution/scripts/*.sh", bootstrap)


class DynamicWorkflowContractTests(unittest.TestCase):
    def test_subagent_pipeline_dynamic_workflow_exists_and_has_meta(self):
        text = SUBAGENT_PIPELINE_DYNAMIC_WORKFLOW.read_text()

        self.assertTrue(text.startswith("export const meta = {"))
        self.assertIn("name: 'subagent-pipeline-dynamic'", text)
        self.assertIn("description: 'Reusable dynamic workflow", text)
        for phase in ["Setup", "Planning", "Execute", "Verify", "Global Review", "Closeout", "Report"]:
            self.assertIn(f"title: '{phase}'", text)

    def test_subagent_pipeline_dynamic_workflow_uses_named_agents_without_model_override(self):
        text = SUBAGENT_PIPELINE_DYNAMIC_WORKFLOW.read_text()

        for agent in [
            "task-planner",
            "plan-reviewer",
            "code-implementer",
            "spec-reviewer",
            "test-engineer",
            "code-reviewer",
        ]:
            self.assertIn(f"'{agent}'", text)
            self.assertIn("agentType: requiredSubagent", text)
        self.assertNotRegex(text, r"\bmodel\s*:")
        self.assertIn("No model override for role agents.", text)
        self.assertIn("Required named subagent selection unavailable", text)

    def test_subagent_pipeline_dynamic_workflow_keeps_dispatch_ledger_and_status_rules(self):
        text = SUBAGENT_PIPELINE_DYNAMIC_WORKFLOW.read_text()

        for needle in [
            "LEDGER_FIELDS",
            "stage",
            "required_subagent",
            "identity_source",
            "tool_status",
            "role_status",
            "evidence_refs",
            "route_decision",
            "RETRY_BUDGET = 3",
            "RESTATEMENT_BUDGET = 1",
            "downgrade-only semantic status mapping",
            "never convert FAIL/BLOCKED to PASS/DONE",
            "never fill missing evidence",
            "never infer verification",
            "never treat ambiguous polarity as PASS",
        ]:
            self.assertIn(needle, text)

    def test_subagent_pipeline_dynamic_workflow_keeps_issue_and_closeout_contract(self):
        text = SUBAGENT_PIPELINE_DYNAMIC_WORKFLOW.read_text()

        for needle in [
            "BASE_SHA",
            "HEAD_SHA",
            "gh issue view",
            "gh issue close",
            "state == \"CLOSED\"",
            "No push before global review PASS",
            "explicit current-session authorization required before commit, push, gh issue close",
            "closeoutAuthorized",
            "phase3: disabled",
            "READY_FOR_CLOSEOUT",
        ]:
            self.assertIn(needle, text)

    def test_subagent_pipeline_workflow_command_describes_reusable_asset(self):
        text = SUBAGENT_PIPELINE_WORKFLOW_COMMAND.read_text()

        self.assertTrue(text.startswith("---\n"))
        self.assertIn("description:", text)
        self.assertIn("allowed-tools:", text)
        self.assertIn("  - Read", text)
        self.assertIn("  - Workflow", text)
        self.assertIn("argument-hint:", text)
        self.assertNotIn("name: subagent-pipeline-workflow", text)
        self.assertIn("distribution/workflows/subagent-pipeline-dynamic.js", text)
        for usage in [
            "/subagent-pipeline-workflow #1",
            "/subagent-pipeline-workflow --parallel #1,#2 #3",
            "/subagent-pipeline-workflow --plan #1",
            "/subagent-pipeline-workflow --no-plan #1",
            "/subagent-pipeline-workflow --no-closeout #1",
        ]:
            self.assertIn(usage, text)
        self.assertIn("source-only and opt-in", text)
        self.assertIn("does not auto-install", text)
        self.assertIn("Do not commit, push, or close GitHub issues without explicit current-session authorization.", text)


class AgentInventoryContractTests(unittest.TestCase):
    AGENTS_ROOT = REPO_ROOT / "distribution" / "agents"
    AGENTS_DIR = AGENTS_ROOT / "claude-code"
    OMP_AGENTS_DIR = AGENTS_ROOT / "oh-my-pi"
    AGENT_SETS = {
        "claude-code": AGENTS_ROOT / "claude-code",
        "oh-my-pi": AGENTS_ROOT / "oh-my-pi",
    }

    def _agent_text(self, md_path: Path) -> str:
        return md_path.read_text()

    def _body(self, md_path: Path) -> str:
        text = md_path.read_text()
        return text.split('---', 2)[2]

    def _handoff_section(self, md_path: Path) -> str:
        body = self._body(md_path)
        marker = "## Artifact and final handoff"
        start = body.index(marker)
        return body[start:]

    def _read_frontmatter(self, md_path: Path) -> dict:
        """Parse YAML frontmatter from a markdown agent file."""
        text = md_path.read_text()
        m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not m:
            self.fail(f"{md_path.name}: no frontmatter found")
        fm = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                fm[key.strip()] = val.strip().strip('"')
        return fm

    def _agent_files(self):
        """Yield all .md agent files excluding README.md."""
        for p in sorted(self.AGENTS_ROOT.glob("*/*.md")):
            if p.name != "README.md":
                yield p

    def test_readme_inventory_matches_actual_frontmatter_name_and_model(self):
        """Verify each README inventory table entries match actual agent frontmatter."""
        mismatches = []
        for agent_set, agent_dir in self.AGENT_SETS.items():
            readme = (agent_dir / "README.md").read_text()
            lines = readme.splitlines()
            sep_idx = next(
                (i for i, l in enumerate(lines) if l.strip().startswith("|---")),
                None,
            )
            if sep_idx is None:
                self.fail(f"{agent_set} README: inventory table separator line not found")

            table_rows = []
            for line in lines[sep_idx + 1:]:
                if not line.strip():
                    break
                if line.startswith("|"):
                    table_rows.append(line)
                else:
                    break

            table_map = {}
            for row in table_rows:
                cells = [c.strip() for c in row.split("|")]
                if len(cells) >= 3:
                    agent = cells[1].strip("`").strip()
                    model = cells[2].strip()
                    if agent:
                        table_map[agent] = model

            for path in sorted(agent_dir.glob("*.md")):
                if path.name == "README.md":
                    continue
                fm = self._read_frontmatter(path)
                name = fm.get("name", "")
                model = fm.get("model", "")
                listed_model = table_map.get(name)
                if listed_model is None:
                    mismatches.append(f"{agent_set}/{name}: not found in README inventory table")
                elif listed_model != model:
                    mismatches.append(
                        f"{agent_set}/{name}: README model='{listed_model}' != frontmatter model='{model}'"
                    )
        self.assertEqual([], mismatches, "Agent inventory model mismatches:\n" + "\n".join(mismatches))

    def test_agent_models_remain_expected(self):
        expected = {
            "task-planner": "opus",
            "code-implementer": "haiku",
            "test-engineer": "haiku",
            "code-reviewer": "sonnet",
            "deployment-operator": "haiku",
            "spec-reviewer": "haiku",
            "mavis": "haiku",
            "plan-reviewer": "sonnet",
        }
        for path in self._agent_files():
            fm = self._read_frontmatter(path)
            self.assertEqual(expected[fm["name"]], fm["model"], path.name)

    def test_agents_use_short_hard_section_order(self):
        required = ["## Role", "## Boundaries", "## Workflow", "## What you produce", "## Artifact and final handoff"]
        for path in self._agent_files():
            body = self._body(path)
            positions = [body.find(section) for section in required]
            self.assertTrue(all(pos >= 0 for pos in positions), path.name)
            self.assertEqual(positions, sorted(positions), path.name)
            last_heading = [line for line in body.splitlines() if line.startswith("## ")][-1]
            self.assertEqual("## Artifact and final handoff", last_heading, path.name)

    def test_agents_include_bookend_handoff_contract(self):
        for path in self._agent_files():
            handoff = self._handoff_section(path)
            fm = self._read_frontmatter(path)
            name = fm["name"]
            expected_status = {
                "task-planner": "STATUS: <DONE|FAIL|BLOCKED>",
                "code-implementer": "STATUS: <DONE|FAIL|BLOCKED>",
                "deployment-operator": "STATUS: <DONE|FAIL|BLOCKED>",
                "code-reviewer": "STATUS: <PASS|FAIL|BLOCKED>",
                "spec-reviewer": "STATUS: <PASS|FAIL|BLOCKED>",
                "test-engineer": "STATUS: <PASS|FAIL|BLOCKED>",
                "mavis": "STATUS: <PASS|FAIL|BLOCKED|PARTIAL>",
                "plan-reviewer": "STATUS: <PASS|FAIL|BLOCKED>",
            }
            self.assertIn(expected_status[name], handoff, path.name)
            self.assertIn(f'<handoff agent="{name}"', handoff, path.name)
            self.assertIn(f'<handoff-end agent="{name}"', handoff, path.name)
            self.assertIn('status="<same>"', handoff, path.name)
            self.assertIn('workspace="<same>"', handoff, path.name)
            self.assertIn('artifact="<same>"', handoff, path.name)
            self.assertIn("No text may follow `<handoff-end ... />`", handoff, path.name)

    def test_handoff_section_stays_short(self):
        max_lines = 22
        for path in self._agent_files():
            handoff = self._handoff_section(path)
            line_count = len(handoff.splitlines())
            self.assertLessEqual(line_count, max_lines, f"{path.name}: {line_count} handoff lines")

    def test_handoff_section_has_no_bulk_rules_block(self):
        for path in self._agent_files():
            handoff = self._handoff_section(path)
            self.assertNotIn("\nRules:\n", handoff, path.name)

    def test_user_artifact_hook_distribution_files_exist(self):
        root = REPO_ROOT / "distribution" / "hooks" / "user" / "validate-agent-artifact-write"
        for rel in ["hook.mjs", "README.md", "scope.md", "manual-test.md", "rollback.md"]:
            self.assertTrue((root / rel).exists(), rel)
        self.assertTrue((REPO_ROOT / "tests" / "validate-agent-artifact-write.test.mjs").exists())

    def test_read_only_artifact_agents_have_write_hook(self):
        for filename, agent in [("code-reviewer.md", "code-reviewer"), ("spec-reviewer.md", "spec-reviewer"), ("task-planner.md", "task-planner"), ("plan-reviewer.md", "plan-reviewer")]:
            path = self.AGENTS_DIR / filename
            text = path.read_text()
            fm = self._read_frontmatter(path)
            self.assertIn("hooks:", text)
            self.assertIn("PreToolUse:", text)
            self.assertIn('matcher: "Write"', text)
            self.assertIn(f"validate-agent-artifact-write/hook.mjs {agent}", text)
            self.assertNotIn("Write", [item.strip() for item in fm.get("disallowedTools", "").split(",")])


class SubagentPipelinePromptContractTests(unittest.TestCase):
    """Prompt text regression tests only; these do not exercise runtime hooks."""

    AGENTS_ROOT = REPO_ROOT / "distribution" / "agents"
    AGENTS_DIR = AGENTS_ROOT / "claude-code"
    OMP_AGENTS_DIR = AGENTS_ROOT / "oh-my-pi"
    SKILL = REPO_ROOT / "distribution" / "skills" / "subagent-pipeline" / "SKILL.md"

    def _agent_files(self):
        for p in sorted(self.AGENTS_ROOT.glob("*/*.md")):
            if p.name != "README.md":
                yield p

    def test_agents_define_role_specific_outputs(self):
        expected = {
            "task-planner.md": [
                "- Executable plan including goal, scope, non-goals, assumptions, tasks, dependencies, acceptance, verification, and risk.",
                "- Open decisions or blockers that prevent safe implementation.",
            ],
            "code-implementer.md": [
                "- Changed files and the behavior each change produces.",
                "- Focused verification commands with exit code and status.",
                "- Deviations, concerns, risks, or blockers.",
            ],
            "test-engineer.md": [
                "- Acceptance criteria mapped to assertions, RED/GREEN evidence, and gaps.",
                "- Commands with exit code, status, failure classification, and coverage gaps.",
            ],
            "code-reviewer.md": [
                "- Criteria applied across correctness, security, maintainability, performance, readability, and complexity.",
                "- Blocking findings with evidence, plus non-blocking concerns and evidence gaps.",
            ],
            "deployment-operator.md": [
                "- Documented command and status evidence.",
                "- Operation state before and after.",
                "- Authorization and rollback evidence for mutating operations.",
            ],
            "spec-reviewer.md": [
                "- Spec items checked against implementation.",
                "- Missing, extra, or misinterpreted requirements with file:line references when available.",
            ],
            "mavis.md": [
                "- Team Plan id, owner/session, task IDs, roles, and status.",
                "- Worker and verifier outputs, failures, raw evidence, and assumptions.",
                "- Final acceptance remains caller-owned.",
            ],
            "plan-reviewer.md": [
                "- Plan criteria checked across goal, scope, acceptance, verification, dependencies, risks, rollback, and architecture fit.",
                "- Blocking plan defects, non-blocking concerns, evidence gaps, and unreviewed scope with file:line references when available.",
            ],
        }
        for path in self._agent_files():
            text = path.read_text()
            for needle in expected[path.name]:
                self.assertIn(needle, text, path.name)

    def test_code_implementer_prompt_guards_scope_and_evidence(self):
        text = (self.AGENTS_DIR / "code-implementer.md").read_text()
        self.assertIn("- Work in existing files by default. New test files, fixtures, or generated artifacts are allowed when the task requires them. New production files are allowed only when the task explicitly requests a new module, public contract, entrypoint, adapter, or similar production artifact. Do not create new production files to broaden scope. If you create one, justify it in <changed_files> and include focused verification.", text)
        self.assertIn("- Completeness: did you implement every requirement in the spec, and does the existing <verification> payload cover each acceptance requirement in substance?", text)
        self.assertIn("If required behavior or evidence is missing, report FAIL; if capability or environment prevents verification, report BLOCKED.", text)

    def test_subagent_pipeline_accident_rules_are_present(self):
        text = self.SKILL.read_text()
        for needle in [
            "### Phase 0.5: Capability Preconditions",
            "Before implementation, note visible repository policy that constrains code discovery or file access. If required source inspection is blocked for the planned reviewer/tester and no allowed alternative is visible, stop as BLOCKED before implementation. Do not start work that cannot be independently reviewed under current tool policy.",
            "If a planned task contains multiple independently verifiable changes, split it before dispatch or send it back to task-planner, then plan-reviewer, for a smaller breakdown. Each slice needs a behavior target and focused verification expectation.",
            "Before any Phase 1 or Phase 2 route on STATUS, treat subagent results as inputs, not completion claims:",
            "- Harness/tool non-success wins over agent prose. If a task is cancelled, timed out, interrupted, reports 0/N succeeded, or required verification errored, do not treat prose like \"Done\" as DONE/PASS.",
            "- A result without a clear role status and usable role-specific handoff is incomplete. If harness/tool status succeeded, ask the same agent once to restate actual status and evidence without changing files. If still incomplete, route implementer results as FAIL and reviewer/tester results as BLOCKED when independent judgment cannot be established. Do not re-ask after cancelled, timed out, interrupted, or 0/N succeeded; route those from the harness/tool status.",
            "- Format alone is not a blocker. Accept malformed formatting only when status, workspace/scope, and evidence are semantically present. Block only on missing capability, unknown workspace/scope, inaccessible source, unavailable verification, or missing semantic evidence needed for the stage.",
            "- If coordinator read-only checks contradict a DONE result, route as FAIL with exact evidence and redispatch code-implementer. Do not patch directly.",
            "- Repair code, tests, or docs directly after any agent FAIL, BLOCKED, incomplete, cancelled, or contradicted result. Diagnose, split scope, add missing context, redispatch the appropriate agent, or stop and report instead.",
        ]:
            self.assertIn(needle, text)

    def test_subagent_pipeline_requires_named_agents_not_impersonation(self):
        text = self.SKILL.read_text()
        for needle in [
            "runtime-recognized named subagents",
            "Prompt impersonation is forbidden.",
            "planning → task-planner",
            "implementation → code-implementer",
            "spec compliance → spec-reviewer",
            "verification/test → test-engineer",
            "plan review/architecture plan review/task breakdown review → plan-reviewer",
            "code review/global review → code-reviewer",
            "generic task/reviewer/agent with assignment text such as \"You are task-planner\"",
            "generic task/reviewer/agent with assignment text such as \"You are code-implementer\"",
            "generic task/reviewer/agent with assignment text such as \"You are spec-reviewer\"",
            "generic task/reviewer/agent with assignment text such as \"You are test-engineer\"",
            "generic task/reviewer/agent with assignment text such as \"You are code-reviewer\"",
            "generic task/reviewer/agent with assignment text such as \"You are plan-reviewer\"",
            "Required named subagent selection unavailable",
        ]:
            self.assertIn(needle, text)

    def test_subagent_pipeline_identity_does_not_require_metadata_only(self):
        text = self.SKILL.read_text()
        for needle in [
            "## Agent Identity Evidence",
            "invocation evidence is required.",
            "metadata is optional.",
            "metadata absence is not BLOCKED.",
            "If invocation used a generic agent and only the prompt or handoff claims the role: BLOCKED.",
        ]:
            self.assertIn(needle, text)

    def test_subagent_pipeline_keeps_mandatory_closeout(self):
        text = self.SKILL.read_text()
        for needle in [
            "### Phase 3: Commit, Push, and Close Completed Issues",
            "Phase 3 is mandatory for completed issues.",
            "Do not remove, skip, or default-disable commit/push/close behavior.",
            "Atomic commit for all changes across all completed issues",
            "Push to GitHub.",
            "gh issue close <number>",
            "gh issue view <number> --json state,url",
            "Require `state == \"CLOSED\"`.",
            "do not claim\n   issue closure or workflow DONE",
            "the issue is already closed",
        ]:
            self.assertIn(needle, text)

    def test_subagent_pipeline_risk_tiers_do_not_skip_gates(self):
        text = self.SKILL.read_text()
        for needle in [
            "Risk tiers do not remove mandatory stages.",
            "task-planner (when required) → plan-reviewer (when task-planner ran) → code-implementer (with self-review) → spec-reviewer → test-engineer → code-reviewer",
            "After all tasks for all issues complete:\n  code-reviewer (global review, full diff)",
            "Risk tiers affect only split decisions, context budget, and plan/review/test prompt focus.",
        ]:
            self.assertIn(needle, text)

    def test_subagent_pipeline_status_mapping_is_downgrade_only(self):
        text = self.SKILL.read_text()
        for needle in [
            "downgrade-only semantic status mapping",
            "Never convert FAIL/BLOCKED to PASS/DONE",
            "never fill missing evidence",
            "never treat ambiguous polarity as PASS",
            "If output says both PASS and blocking issue, route as FAIL/BLOCKED.",
            "Restate at most once per stage result.",
        ]:
            self.assertIn(needle, text)

    def test_subagent_pipeline_planner_trigger_fields_are_defined(self):
        text = self.SKILL.read_text()
        for needle in [
            "A usable structured breakdown exists only when each task has:",
            "behavior target",
            "acceptance criteria",
            "verification expectation",
            "dependencies/blockers",
            "issue has multiple acceptance criteria and lacks task-level slices",
            "public contract/schema/CLI/API ambiguity exists",
            "dispatch named task-planner",
            "dispatch named plan-reviewer",
        ]:
            self.assertIn(needle, text)

    def test_legacy_output_markers_are_absent(self):
        forbidden = ["<acceptance_evidence>", "<output_spec>", "</output_spec>", "## Output Spec"]
        for path in [self.SKILL, *self._agent_files()]:
            text = path.read_text()
            for marker in forbidden:
                self.assertNotIn(marker, text, path.name)

    def test_mavis_keeps_team_plan_rules_before_output_and_acceptance_owned_by_caller(self):
        text = (self.AGENTS_DIR / "mavis.md").read_text()
        self.assertIn("Final acceptance remains caller-owned.", text)
        positions = [
            text.index("## Team Plan rules"),
            text.index("## What you produce"),
            text.index("## Artifact and final handoff"),
        ]
        self.assertEqual(positions, sorted(positions))

    def test_dual_agent_set_consistency(self):
        claude_files = {p.name for p in self.AGENTS_DIR.glob("*.md") if p.name != "README.md"}
        omp_files = {p.name for p in self.OMP_AGENTS_DIR.glob("*.md") if p.name != "README.md"}
        self.assertEqual(claude_files, omp_files)

        for filename in sorted(claude_files):
            claude = (self.AGENTS_DIR / filename).read_text()
            omp = (self.OMP_AGENTS_DIR / filename).read_text()
            claude_name = re.search(r"^name: (.+)$", claude, re.MULTILINE).group(1).strip().strip('"')
            omp_name = re.search(r"^name: (.+)$", omp, re.MULTILINE).group(1).strip().strip('"')
            self.assertEqual(claude_name, omp_name, filename)
            for marker in ["## Role", "## Boundaries", "## Workflow", "## What you produce", "## Artifact and final handoff"]:
                self.assertIn(marker, claude, filename)
                self.assertIn(marker, omp, filename)
            self.assertIn("agent-artifacts", claude, filename)
            self.assertIn("agent-artifacts", omp, filename)
            self.assertNotIn("claude-agent-artifacts", claude, filename)
            self.assertNotIn("omp-agent-artifacts", omp, filename)

    def test_oh_my_pi_frontmatter_uses_allowlist_shape(self):
        forbidden = ["disallowedTools:", "effort:", "permissionMode:", "memory:", "color:", "maxTurns:", "hooks:"]
        for path in self.OMP_AGENTS_DIR.glob("*.md"):
            if path.name == "README.md":
                continue
            text = path.read_text()
            for marker in forbidden:
                self.assertNotIn(marker, text, path.name)

    def test_plan_reviewer_description_is_actionable(self):
        for path in [self.AGENTS_DIR / "plan-reviewer.md", self.OMP_AGENTS_DIR / "plan-reviewer.md"]:
            text = path.read_text()
            description = re.search(r"^description: (.+)$", text, re.MULTILINE).group(1)
            self.assertIn("read-only", description)
            self.assertIn("plan", description)
            self.assertIn("Do not use", description)
            self.assertIn("editing", description)
            self.assertIn("implementation", description)

if __name__ == "__main__":
    unittest.main()
