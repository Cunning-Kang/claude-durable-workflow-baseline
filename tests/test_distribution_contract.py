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
INIT_COMMAND = REPO_ROOT / "distribution/commands/init-claude-workflow.md"
NEW_FEATURE_COMMAND = REPO_ROOT / "distribution/commands/new-feature.md"
README = REPO_ROOT / "README.md"
BOOTSTRAP_DOC = REPO_ROOT / "docs/claude-one-command-bootstrap.md"
GLOBAL_README = REPO_ROOT / "global/README.md"
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

    def test_init_script_copies_memory_skeleton_to_expected_locations(self):
        """Memory skeleton files land in expected locations after init."""
        repo_dir = self.make_git_repo()
        env = os.environ | {"CLAUDE_WORKFLOW_BASELINE_PATH": str(REPO_ROOT)}

        subprocess.run(
            [str(INIT_SCRIPT), str(repo_dir)],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

        # All three memory skeleton files must be present
        self.assertTrue((repo_dir / "memory/MEMORY.md").exists(),
            "memory/MEMORY.md must be created by init script")
        self.assertTrue((repo_dir / "memory/patterns.md").exists(),
            "memory/patterns.md must be created by init script")
        self.assertTrue((repo_dir / "memory/gotchas.md").exists(),
            "memory/gotchas.md must be created by init script")

    def test_memory_docs_do_not_reference_source_only_baseline_paths(self):
        """Distributed memory docs must not contain baseline/... source-only paths."""
        memory_files = [
            REPO_ROOT / "baseline/memory/MEMORY.md",
            REPO_ROOT / "baseline/memory/patterns.md",
            REPO_ROOT / "baseline/memory/gotchas.md",
        ]

        broken_links = []
        for mem_file in memory_files:
            if not mem_file.exists():
                continue
            content = mem_file.read_text()
            # Check for source-repo-only baseline/ paths that would break after install
            if re.search(r'baseline/', content):
                broken_links.append(mem_file.name)

        self.assertEqual([], broken_links,
            f"These memory docs contain 'baseline/' path references that will break "
            f"after installation: {broken_links}. Use relative paths or project-root "
            f"references that remain valid in the target repo.")

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
        self.assertIn("distribution/scripts/*.sh", readme)
        self.assertIn("mkdir -p ~/.claude/scripts", readme)
        self.assertIn("distribution/commands/new-feature.md", bootstrap)
        self.assertIn("distribution/scripts/*.sh", bootstrap)

    def test_global_install_uses_recursive_no_clobber_copy(self):
        """All three docs describe the same recursive no-clobber copy semantics."""
        readme = README.read_text()
        bootstrap = BOOTSTRAP_DOC.read_text()
        global_readme = GLOBAL_README.read_text()

        # The canonical command pattern: cp -rn .../global/* ~/.claude/
        recursive_copy_pattern = re.compile(r'cp\s+-rn\s+.*?/global/\*\s+~\/.claude/')

        self.assertRegex(readme, recursive_copy_pattern,
            "README.md must use recursive no-clobber copy for global/*")
        self.assertRegex(bootstrap, recursive_copy_pattern,
            "bootstrap doc must use recursive no-clobber copy for global/*")
        self.assertRegex(global_readme, recursive_copy_pattern,
            "global/README.md must use recursive no-clobber copy for global/*")

    def test_init_command_does_not_advertise_unsupported_flags(self):
        """init-claude-workflow.md argument-hint must not list flags not in the script."""
        content = INIT_COMMAND.read_text()

        # argument-hint must be --help only (reflecting what the script actually supports)
        self.assertRegex(content, r'argument-hint:\s*\[--help\]',
            "init-claude-workflow.md must not advertise unsupported flags "
            "(current: --dry-run, --print-patch, --force-template)")

        # Must not advertise patch-generation behavior
        self.assertNotIn("--print-patch", content,
            "init-claude-workflow.md must not advertise --print-patch flag")
        self.assertNotIn("patch", content.lower(),
            "init-claude-workflow.md must not reference patch-generation semantics")

    def test_init_command_script_behavior_matches_documentation(self):
        """The init script does not produce patches; docs must not say it does."""
        # Verify script has no patch-generation logic
        script_content = INIT_SCRIPT.read_text()

        self.assertNotIn("patch", script_content.lower(),
            "init-claude-workflow.sh must not implement patch generation")
        self.assertNotIn("--print-patch", script_content,
            "init-claude-workflow.sh must not support --print-patch flag")
        self.assertNotIn("--dry-run", script_content,
            "init-claude-workflow.sh must not support --dry-run flag")
        self.assertNotIn("--force-template", script_content,
            "init-claude-workflow.sh must not support --force-template flag")

    def test_all_three_docs_describe_same_installation_chain(self):
        """README, bootstrap, and global/README describe consistent installation semantics."""
        readme = README.read_text()
        bootstrap = BOOTSTRAP_DOC.read_text()
        global_readme = GLOBAL_README.read_text()

        # All three must mention copying global/* to ~/.claude/
        for doc_name, doc_content in [
            ("README.md", readme),
            ("bootstrap doc", bootstrap),
            ("global/README.md", global_readme),
        ]:
            self.assertIn("global/*", doc_content,
                f"{doc_name} must reference global/* for installation")
            self.assertIn("~/.claude/", doc_content,
                f"{doc_name} must reference ~/.claude/ as the install target")

        # All three must use cp -rn (recursive, no clobber)
        copy_pattern = re.compile(r'cp\s+-rn\s+')

        self.assertRegex(readme, copy_pattern,
            "README.md must use cp -rn for global/* copy")
        self.assertRegex(bootstrap, copy_pattern,
            "bootstrap doc must use cp -rn for global/* copy")
        self.assertRegex(global_readme, copy_pattern,
            "global/README.md must use cp -rn for global/* copy")

    def test_command_docs_reference_correct_installed_script_paths(self):
        """Command docs must reference the correct runtime script paths."""
        init_cmd = INIT_COMMAND.read_text()
        new_feature_cmd = NEW_FEATURE_COMMAND.read_text()

        # Both command docs must reference the correct script paths
        self.assertIn("~/.claude/scripts/init-claude-workflow.sh", init_cmd,
            "init command must reference correct script path")
        self.assertIn("~/.claude/scripts/instantiate-feature.sh", new_feature_cmd,
            "new-feature command must reference correct script path")

        # Verify scripts actually exist at those paths in the repo
        self.assertTrue(INIT_SCRIPT.exists(),
            "init-claude-workflow.sh must exist at expected path")
        self.assertTrue(NEW_FEATURE_SCRIPT.exists(),
            "instantiate-feature.sh must exist at expected path")

    def test_global_is_thin_runtime_surface_not_behavior_control_layer(self):
        """global/README.md must describe itself as a thin runtime surface."""
        content = GLOBAL_README.read_text()

        self.assertIn("thin portable user-level runtime surface", content,
            "global/README.md must self-describe as thin runtime surface")
        # Must not describe itself AS (positively) a behavior control layer
        self.assertNotIn("is a behavior control layer", content.lower(),
            "global/ must not describe itself as a behavior control layer")
        self.assertNotIn("as a behavior control layer", content.lower(),
            "global/ must not describe itself as a behavior control layer")


class VersionAndSurfaceConsistencyTests(unittest.TestCase):
    """Unit 6: VERSION, release notes, bootstrap docs must not drift from repo surface."""

    def test_version_has_parseable_baseline_version_field(self):
        """VERSION must have a baseline-version field with valid semver."""
        version_content = (REPO_ROOT / "VERSION").read_text()
        match = re.search(r'^baseline-version:\s*(\S+)', version_content, re.MULTILINE)
        self.assertIsNotNone(match, "VERSION must contain baseline-version field")
        baseline_version = match.group(1)
        # Validate semver format (major.minor.patch)
        semver_pattern = re.compile(r'^\d+\.\d+\.\d+$')
        self.assertRegex(baseline_version, semver_pattern,
            f"baseline-version '{baseline_version}' must be valid semver (major.minor.patch)")

    def test_bootstrap_doc_version_matches_version_file(self):
        """Bootstrap doc header version and date must match VERSION."""
        version_content = (REPO_ROOT / "VERSION").read_text()
        version_match = re.search(r'^baseline-version:\s*(\S+)', version_content, re.MULTILINE)
        date_match = re.search(r'^release-date:\s*(\S+)', version_content, re.MULTILINE)
        self.assertIsNotNone(version_match, "VERSION must have baseline-version")
        self.assertIsNotNone(date_match, "VERSION must have release-date")

        expected_version = version_match.group(1)
        expected_date = date_match.group(1)

        bootstrap = BOOTSTRAP_DOC.read_text()
        bootstrap_version_match = re.search(r'版本:\s*(\S+)', bootstrap)
        bootstrap_date_match = re.search(r'日期:\s*(\S+)', bootstrap)

        self.assertIsNotNone(bootstrap_version_match,
            "Bootstrap doc must contain version in header")
        self.assertIsNotNone(bootstrap_date_match,
            "Bootstrap doc must contain date in header")

        self.assertEqual(expected_version, bootstrap_version_match.group(1),
            f"Bootstrap doc version must match VERSION (expected {expected_version})")
        self.assertEqual(expected_date, bootstrap_date_match.group(1),
            f"Bootstrap doc date must match VERSION (expected {expected_date})")

    def test_docs_do_not_reference_nonexistent_audits_directory(self):
        """Release notes must not reference docs/audits/ which does not exist."""
        audits_dir = REPO_ROOT / "docs/audits"
        self.assertFalse(audits_dir.exists(),
            "docs/audits/ must not exist in repo (precondition)")

        docs_to_check = [
            REPO_ROOT / "docs/releases/v1.0.0-release-note.md",
            REPO_ROOT / "docs/releases/v1.0.0-maintainer-note.md",
            REPO_ROOT / "docs/reference/superpowers-boundary.md",
        ]

        failures = []
        for doc_path in docs_to_check:
            if doc_path.exists():
                content = doc_path.read_text()
                if re.search(r'docs/audits/', content):
                    failures.append(doc_path.name)

        self.assertEqual([], failures,
            "These docs reference non-existent docs/audits/: " + str(failures))

    def test_reference_docs_date_is_current_or_aligned_with_version(self):
        """Reference docs with Status: Current must have current dates."""
        ref_doc = REPO_ROOT / "docs/reference/superpowers-boundary.md"
        content = ref_doc.read_text()

        status_match = re.search(r'Status:\s*(\w+)', content)
        date_match = re.search(r'Date:\s*(\S+)', content)

        self.assertIsNotNone(status_match, "superpowers-boundary.md must have Status field")
        self.assertIsNotNone(date_match, "superpowers-boundary.md must have Date field")

        # Status is Current, so date should be near the version release date
        version_content = (REPO_ROOT / "VERSION").read_text()
        version_date_match = re.search(r'^release-date:\s*(\S+)', version_content, re.MULTILINE)
        self.assertIsNotNone(version_date_match, "VERSION must have release-date")

        # Just verify the date in the doc is not the stale 2026-03-20 value
        self.assertNotEqual("2026-03-20", date_match.group(1),
            "superpowers-boundary.md date is stale (2026-03-20); should be updated to current")


class AgentInventoryContractTests(unittest.TestCase):
    """Verify agent inventory in distribution/agents/README.md matches actual frontmatter."""

    def test_agent_inventory_matches_frontmatter(self):
        """Each agent listed in README inventory has matching name/model in its frontmatter."""
        readme_path = REPO_ROOT / "distribution/agents/README.md"
        readme_content = readme_path.read_text()

        # Extract the inventory table rows (skip header and separator)
        inventory_section = re.search(
            r'## Agent Inventory\s*\|[^\n]+\|[^\n]+\|[^\n]+\|[^\n]+\|[^\n]+\n\|[-| ]+\|', readme_content
        )
        self.assertIsNotNone(inventory_section, "Agent Inventory table not found in README")

        # Find all agent names from the inventory table
        table_part = readme_content[inventory_section.end():]
        rows = re.findall(r'^\| (`?[\w-]+`?) \| (\w+) \|', table_part, re.MULTILINE)

        failures = []
        for agent_name, table_model in rows:
            # Strip backticks if present
            agent_name = agent_name.strip('`')
            agent_md_path = REPO_ROOT / f"distribution/agents/{agent_name}.md"

            if not agent_md_path.exists():
                failures.append(f"Agent '{agent_name}' listed in README but no file exists")
                continue

            agent_content = agent_md_path.read_text()

            # Extract frontmatter name and model
            fm_match = re.search(r'^name:\s*([^\s\n]+)', agent_content, re.MULTILINE)
            model_match = re.search(r'^model:\s*([^\s\n]+)', agent_content, re.MULTILINE)

            if not fm_match:
                failures.append(f"Agent '{agent_name}': no frontmatter name found")
            if not model_match:
                failures.append(f"Agent '{agent_name}': no frontmatter model found")
            if fm_match and model_match:
                fm_name = fm_match.group(1)
                fm_model = model_match.group(1)
                if fm_name != agent_name:
                    failures.append(
                        f"Agent '{agent_name}': README lists '{agent_name}' but frontmatter name is '{fm_name}'"
                    )
                if fm_model != table_model:
                    failures.append(
                        f"Agent '{agent_name}': README lists model='{table_model}' "
                        f"but frontmatter model='{fm_model}'"
                    )

        self.assertEqual([], failures, "Agent inventory drift detected")


if __name__ == "__main__":
    unittest.main()