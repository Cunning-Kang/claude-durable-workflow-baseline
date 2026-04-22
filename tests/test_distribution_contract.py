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
        self.assertIn("distribution/scripts/*.sh", readme)
        self.assertIn("mkdir -p ~/.claude/scripts", readme)
        self.assertIn("distribution/commands/new-feature.md", bootstrap)
        self.assertIn("distribution/scripts/*.sh", bootstrap)


class AgentInventoryContractTests(unittest.TestCase):
    AGENTS_DIR = REPO_ROOT / "distribution" / "agents"

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
        for p in sorted(self.AGENTS_DIR.glob("*.md")):
            if p.name != "README.md":
                yield p

    def test_readme_inventory_matches_actual_frontmatter_name_and_model(self):
        """Verify the README inventory table entries match actual agent frontmatter."""
        readme = (self.AGENTS_DIR / "README.md").read_text()
        mismatches = []
        # Parse the inventory table rows: find the table body between header separator lines
        lines = readme.splitlines()
        # Find the line with the table header separator (|---|---|...)
        sep_idx = next(
            (i for i, l in enumerate(lines) if l.strip().startswith("|---")),
            None,
        )
        if sep_idx is None:
            self.fail("README: inventory table separator line not found")
        # Collect all rows after the separator until an empty line or unrelated content
        in_table = False
        table_rows = []
        for line in lines[sep_idx + 1:]:
            # Stop at blank line or a line that doesn't start with |
            if not line.strip():
                break
            if line.startswith("|"):
                table_rows.append(line)
            else:
                break

        # Build a map from agent name -> listed model from the table
        table_map = {}  # name -> model
        for row in table_rows:
            cells = [c.strip() for c in row.split("|")]
            # cells[0] is empty before first |, cells[1] is Agent, cells[2] is Model
            if len(cells) >= 3:
                agent = cells[1].strip("`").strip()
                model = cells[2].strip()
                if agent:
                    table_map[agent] = model

        # Compare against actual frontmatter
        for path in self._agent_files():
            fm = self._read_frontmatter(path)
            name = fm.get("name", "")
            model = fm.get("model", "")
            listed_model = table_map.get(name)
            if listed_model is None:
                mismatches.append(f"{name}: not found in README inventory table")
            elif listed_model != model:
                mismatches.append(
                    f"{name}: README model='{listed_model}' != frontmatter model='{model}'"
                )
        self.assertEqual([], mismatches, "Agent inventory model mismatches:\n" + "\n".join(mismatches))


if __name__ == "__main__":
    unittest.main()
