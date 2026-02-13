"""Tests for start-task command (git worktree integration)"""

import pytest
from pathlib import Path
import subprocess
import os
import tempfile
import shutil


@pytest.fixture
def git_project(tmp_path):
    """创建一个带 git 仓库的测试项目"""
    project = tmp_path / "test-project"
    project.mkdir()

    # 初始化 git 仓库
    subprocess.run(
        ["git", "init"],
        cwd=project,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=project,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=project,
        capture_output=True,
        check=True,
    )

    (project / "README.md").write_text("# Test Project")

    # 先创建 docs/tasks 与初始化标记，再做初始提交
    docs = project / "docs" / "tasks"
    docs.mkdir(parents=True)
    # 跟踪一个占位文件，确保 worktree 中 docs 与 docs/tasks 目录都存在
    (docs / ".gitkeep").write_text("")
    (project / ".task-flow-initialized").write_text("initialized")

    subprocess.run(
        ["git", "add", "."],
        cwd=project,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=project,
        capture_output=True,
        check=True,
    )

    return project


@pytest.fixture
def cli_env():
    """设置 CLI 环境变量"""
    env = os.environ.copy()
    task_flow_src = Path(__file__).parent.parent / "src"
    env["PYTHONPATH"] = str(task_flow_src)
    env["TASK_FLOW_SKIP_INIT"] = "1"
    env["TASK_FLOW_DOCS_GATE_SKIP"] = "1"
    return env


@pytest.fixture
def project_with_task(git_project, cli_env):
    """创建一个带任务的 git 项目"""
    subprocess.run(
        ["python", "-m", "cli", "create-task", "Implement feature"],
        cwd=git_project,
        capture_output=True,
        env=cli_env
    )
    return git_project


@pytest.fixture
def project_with_non_latin_task(git_project, cli_env):
    """创建一个带中文标题任务的 git 项目"""
    subprocess.run(
        ["python", "-m", "cli", "create-task", "团队邀请与成员管理"],
        cwd=git_project,
        capture_output=True,
        env=cli_env
    )
    return git_project


class TestStartTask:
    """测试 start-task 命令"""

    def test_start_task_creates_worktree(self, project_with_task, cli_env):
        """start-task 应该创建 git worktree"""
        result = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert "worktree" in result.stdout.lower() or "created" in result.stdout.lower()

        # 验证 worktree 存在
        worktree_path = project_with_task / ".worktrees" / "implement-feature"
        assert worktree_path.exists()

    def test_start_task_with_non_latin_title_creates_valid_worktree(self, project_with_non_latin_task, cli_env):
        """中文标题应创建有效 worktree 路径"""
        result = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_non_latin_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        worktree_path = project_with_non_latin_task / ".worktrees" / "task-001"
        assert worktree_path.exists()

    def test_start_task_updates_task_status(self, project_with_task, cli_env):
        """start-task 应该更新任务状态为 In Progress"""
        subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_task,
            capture_output=True,
            env=cli_env
        )

        # 读取任务文件
        task_file = project_with_task / "docs" / "tasks" / "TASK-001-implement-feature.md"
        content = task_file.read_text()

        assert "status: In Progress" in content

    def test_start_task_updates_worktree_field(self, project_with_task, cli_env):
        """start-task 应该更新任务的 worktree 字段"""
        subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_task,
            capture_output=True,
            env=cli_env
        )

        # 读取任务文件
        task_file = project_with_task / "docs" / "tasks" / "TASK-001-implement-feature.md"
        content = task_file.read_text()

        assert "worktree: .worktrees/implement-feature" in content

    def test_start_existing_worktree_reuses(self, project_with_task, cli_env):
        """如果 worktree 已存在，应该复用而不是报错"""
        # 第一次启动
        subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_task,
            capture_output=True,
            env=cli_env
        )

        # 第二次启动（应该复用）
        result = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert "existing" in result.stdout.lower() or "reusing" in result.stdout.lower()

    def test_start_nonexistent_task_errors(self, project_with_task, cli_env):
        """启动不存在的任务应该报错"""
        result = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-999"],
            cwd=project_with_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode != 0
        assert "not found" in (result.stdout + result.stderr).lower()

    def test_start_task_uses_verify_only_docs_mode(self, git_project, cli_env):
        """start-task 采用 verify-only，不复制 docs 内容"""
        main_docs = git_project / "docs"
        (main_docs / "test.md").write_text("# Test Content")

        subprocess.run(
            ["python", "-m", "cli", "create-task", "Verify docs mode"],
            cwd=git_project,
            capture_output=True,
            env=cli_env,
            check=True,
        )

        result = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=git_project,
            capture_output=True,
            text=True,
            env=cli_env,
        )

        assert result.returncode == 0
        assert "Syncing docs from main working area" not in result.stdout

        worktree_docs = git_project / ".worktrees" / "verify-docs-mode" / "docs"
        assert worktree_docs.exists()
        assert not (worktree_docs / "test.md").exists()

    def test_start_task_creates_active_registry_events_and_plan_router(self, project_with_task, cli_env):
        """start-task 应写入 active registry / events 并更新 PLAN.md"""
        result = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_task,
            capture_output=True,
            text=True,
            env=cli_env,
        )

        assert result.returncode == 0

        worktree_root = project_with_task / ".worktrees" / "implement-feature"
        assert worktree_root.exists()

        assert not (worktree_root / "task_plan.md").exists()
        assert not (worktree_root / "findings.md").exists()
        assert not (worktree_root / "progress.md").exists()

        active_file = project_with_task / "docs" / "tasks" / "_active.json"
        assert active_file.exists()
        active_data = __import__("json").loads(active_file.read_text())

        assert active_data["version"] == 1
        assert "updated_at" in active_data
        assert "TASK-001" in active_data["tasks"]

        entry = active_data["tasks"]["TASK-001"]
        assert entry["task_file"] == "docs/tasks/TASK-001-implement-feature.md"
        assert entry["branch"] == "implement-feature"
        assert entry["worktree"] == ".worktrees/implement-feature"
        assert entry["status"] == "In Progress"
        assert entry["last_event_seq"] == 1

        events_file = worktree_root / ".task-flow" / "events.jsonl"
        assert events_file.exists()
        lines = [line for line in events_file.read_text().splitlines() if line.strip()]
        assert len(lines) == 1

        first_event = __import__("json").loads(lines[0])
        assert first_event["seq"] == 1
        assert first_event["task_id"] == "TASK-001"
        assert first_event["type"] == "task_started"
        assert "ts" in first_event

        plan_router = (project_with_task / "PLAN.md").read_text()
        assert "<!-- BEGIN: TASK_FLOW_PLAN_ROUTER -->" in plan_router
        assert "- ID: `TASK-001`" in plan_router
        assert "- Task: `docs/tasks/TASK-001-implement-feature.md`" in plan_router
        assert "- Plan: `NOT GENERATED YET`" in plan_router
        assert "- Active Registry: `docs/tasks/_active.json`" in plan_router
        assert "- Events: `.worktrees/implement-feature/.task-flow/events.jsonl`" in plan_router

    def test_start_task_writes_workflow_conventions(self, project_with_task, cli_env):
        """start-task 应生成 conventions 文件并注入 CLAUDE.md 块"""
        result = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_task,
            capture_output=True,
            text=True,
            env=cli_env,
        )

        assert result.returncode == 0

        conventions_file = project_with_task / "docs" / "workflow" / "CONVENTIONS.md"
        assert conventions_file.exists()
        conventions_content = conventions_file.read_text()
        assert "Canonical Source of Truth" in conventions_content
        assert "docs: update workflow artifacts" in conventions_content
        assert "_active.json" in conventions_content
        assert "events.jsonl" in conventions_content
        assert "task_plan.md" not in conventions_content
        assert "task_plan.md" not in conventions_content

        claude_file = project_with_task / "CLAUDE.md"
        assert claude_file.exists()
        claude_content = claude_file.read_text()
        assert "<!-- BEGIN: WORKFLOW_CONVENTIONS -->" in claude_content
        assert "<!-- END: WORKFLOW_CONVENTIONS -->" in claude_content
        assert "_active.json" in claude_content
        assert "events.jsonl" in claude_content
        assert "task_plan.md" not in claude_content
        assert "task_plan.md" not in claude_content

    def test_start_task_appends_event_when_restarting_existing_worktree(self, project_with_task, cli_env):
        """重复 start-task 应在 events.jsonl 追加事件并更新 active last_event_seq"""
        first_run = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_task,
            capture_output=True,
            text=True,
            env=cli_env,
        )
        assert first_run.returncode == 0

        second_run = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_task,
            capture_output=True,
            text=True,
            env=cli_env,
        )
        assert second_run.returncode == 0

        worktree_root = project_with_task / ".worktrees" / "implement-feature"
        events_file = worktree_root / ".task-flow" / "events.jsonl"
        lines = [line for line in events_file.read_text().splitlines() if line.strip()]
        assert len(lines) == 2

        first_event = __import__("json").loads(lines[0])
        second_event = __import__("json").loads(lines[1])
        assert first_event["seq"] == 1
        assert second_event["seq"] == 2
        assert second_event["type"] == "task_started"

        active_file = project_with_task / "docs" / "tasks" / "_active.json"
        active_data = __import__("json").loads(active_file.read_text())
        assert active_data["tasks"]["TASK-001"]["last_event_seq"] == 2
