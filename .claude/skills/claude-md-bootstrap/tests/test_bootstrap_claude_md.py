from pathlib import Path
import importlib.util
import json

import pytest


def _load_script_module():
    script_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "bootstrap_claude_md.py"
    )
    spec = importlib.util.spec_from_file_location("bootstrap_claude_md", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_render_template_replaces_project_overrides():
    fixtures_dir = Path(__file__).resolve().parent / "fixtures"
    init_snapshot = (fixtures_dir / "init_snapshot.md").read_text(encoding="utf-8")
    thin_template = (fixtures_dir / "thin_template.md").read_text(encoding="utf-8")

    module = _load_script_module()
    rendered = module.render_template(thin_template, init_snapshot)

    assert "{{PROJECT_OVERRIDES}}" not in rendered
    assert "- Use uv for dependency management." in rendered
    assert "- Run tests with `python -m pytest`." in rendered
    assert "## Notes" not in rendered
    assert "- Keep setup reproducible." not in rendered


def test_extract_project_overrides_raises_when_marker_missing():
    module = _load_script_module()

    snapshot_without_marker = """# Init Snapshot\n\n## Runtime\n- Python 3.12\n"""

    with pytest.raises(ValueError, match="Project Overrides"):
        module.extract_project_overrides(snapshot_without_marker)


def test_extract_commands_from_init_snapshot():
    module = _load_script_module()

    init_text = """# Init Snapshot
ENV_SETUP_CMD: uv sync
TEST_CMD = python -m pytest
LINT_CMD: ruff check .
TYPECHECK_CMD = mypy .
BUILD_CMD: python -m build
"""

    commands = module.extract_commands(init_text)

    assert commands == {
        "ENV_SETUP_CMD": "uv sync",
        "TEST_CMD": "python -m pytest",
        "LINT_CMD": "ruff check .",
        "TYPECHECK_CMD": "mypy .",
        "BUILD_CMD": "python -m build",
    }


def test_extract_commands_missing_fields_are_empty():
    module = _load_script_module()

    init_text = """# Init Snapshot
TEST_CMD: python -m pytest
"""

    commands = module.extract_commands(init_text)

    assert commands == {
        "ENV_SETUP_CMD": "",
        "TEST_CMD": "python -m pytest",
        "LINT_CMD": "",
        "TYPECHECK_CMD": "",
        "BUILD_CMD": "",
    }


def test_write_with_backup_creates_bak(tmp_path: Path):
    module = _load_script_module()

    target = tmp_path / "CLAUDE.md"
    target.write_text("old content", encoding="utf-8")

    backup = module.write_with_backup(target, "new content")

    assert backup == tmp_path / "CLAUDE.md.bak"
    assert backup is not None
    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == "old content"
    assert target.read_text(encoding="utf-8") == "new content"


def test_write_with_backup_returns_none_when_target_missing(tmp_path: Path):
    module = _load_script_module()

    target = tmp_path / "CLAUDE.md"

    backup = module.write_with_backup(target, "new content")

    assert backup is None
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "new content"
    assert not (tmp_path / "CLAUDE.md.bak").exists()


def test_write_with_backup_cleans_temp_file_when_replace_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    module = _load_script_module()

    target = tmp_path / "CLAUDE.md"
    target.write_text("old content", encoding="utf-8")

    created_tmp_paths: list[Path] = []
    original_replace = Path.replace

    def failing_replace(self: Path, *args, **kwargs):
        if self.parent == tmp_path and self.name != target.name:
            created_tmp_paths.append(self)
            raise RuntimeError("replace failed")
        return original_replace(self, *args, **kwargs)

    monkeypatch.setattr(Path, "replace", failing_replace)

    with pytest.raises(RuntimeError, match="replace failed"):
        module.write_with_backup(target, "new content")

    assert created_tmp_paths
    assert all(not tmp.exists() for tmp in created_tmp_paths)


def test_main_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    module = _load_script_module()

    template = tmp_path / "template.md"
    init_source = tmp_path / "init.md"
    target = tmp_path / "CLAUDE.md"

    template.write_text(
        "# CLAUDE.md\n\n## Project Overrides\n{{PROJECT_OVERRIDES}}\n",
        encoding="utf-8",
    )
    init_text = """# Init Snapshot

## Project Overrides
ENV_SETUP_CMD: uv sync
TEST_CMD = python -m pytest

## Other
ignored
"""
    init_source.write_text(init_text, encoding="utf-8")
    target.write_text("old content", encoding="utf-8")

    rc = module.main(
        [
            "--project-root",
            str(tmp_path),
            "--template",
            str(template),
            "--init-source",
            str(init_source),
            "--target",
            str(target),
            "--project-name",
            "demo-project",
            "--default-branch",
            "main",
        ]
    )

    assert rc == 0
    assert target.read_text(encoding="utf-8") == (
        "# CLAUDE.md\n\n## Project Overrides\nENV_SETUP_CMD: uv sync\nTEST_CMD = python -m pytest\n"
    )

    backup = tmp_path / "CLAUDE.md.bak"
    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == "old content"

    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload == {
        "target": str(target),
        "backup": str(backup),
        "filled": 2,
        "empty": 3,
    }


def test_main_fails_when_source_missing(tmp_path: Path):
    module = _load_script_module()

    template = tmp_path / "template.md"
    template.write_text("# CLAUDE.md\n{{PROJECT_OVERRIDES}}\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="run /init first or pass --init-source"):
        module.main(
            [
                "--project-root",
                str(tmp_path),
                "--template",
                str(template),
                "--project-name",
                "demo-project",
            ]
        )


def test_main_fails_when_template_missing(tmp_path: Path):
    module = _load_script_module()

    init_source = tmp_path / "init.md"
    init_source.write_text("## Project Overrides\nTEST_CMD: python -m pytest\n", encoding="utf-8")
    missing_template = tmp_path / "missing-template.md"

    with pytest.raises(SystemExit, match="failed to read template"):
        module.main(
            [
                "--project-root",
                str(tmp_path),
                "--template",
                str(missing_template),
                "--init-source",
                str(init_source),
                "--project-name",
                "demo-project",
            ]
        )


def test_main_fails_when_overrides_section_missing(tmp_path: Path):
    module = _load_script_module()

    template = tmp_path / "template.md"
    init_source = tmp_path / "init.md"

    template.write_text("# CLAUDE.md\n\n{{PROJECT_OVERRIDES}}\n", encoding="utf-8")
    init_source.write_text("# Init Snapshot\n\n## Runtime\n- Python 3.12\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="Missing required section: ## Project Overrides"):
        module.main(
            [
                "--project-root",
                str(tmp_path),
                "--template",
                str(template),
                "--init-source",
                str(init_source),
                "--project-name",
                "demo-project",
            ]
        )


def test_skill_frontmatter_and_triggers_exist():
    repo_root = Path(__file__).resolve().parents[4]
    skill_file = repo_root / ".claude" / "skills" / "claude-md-bootstrap" / "SKILL.md"

    assert skill_file.exists()

    content = skill_file.read_text(encoding="utf-8")

    assert content.startswith("---\n")
    assert "\nname:" in content
    assert "\ndescription:" in content
    assert "CLAUDE.md" in content
    assert "Project Overrides" in content
    assert "生成" in content or "刷新" in content
    assert "回填" in content


def test_command_file_exists_and_describes_bootstrap():
    repo_root = Path(__file__).resolve().parents[4]
    command_file = repo_root / ".claude" / "commands" / "claude-md-bootstrap.md"

    assert command_file.exists()

    content = command_file.read_text(encoding="utf-8")

    assert content.startswith("---\n")
    assert "\ndescription:" in content
    assert ".claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py" in content
    assert "--project-root" in content
    assert "--template" in content
    assert "--project-name" in content


def test_template_has_required_anchor_and_placeholder():
    repo_root = Path(__file__).resolve().parents[4]
    template_file = (
        repo_root
        / ".claude"
        / "skills"
        / "claude-md-bootstrap"
        / "templates"
        / "claude-md-thin.md"
    )

    assert template_file.exists()

    content = template_file.read_text(encoding="utf-8")

    assert "@~/.claude/standards/universal-claude.md" in content
    assert "## Project Overrides" in content
    assert "{{PROJECT_OVERRIDES}}" in content
