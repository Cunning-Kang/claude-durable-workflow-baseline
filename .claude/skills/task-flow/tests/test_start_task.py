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
        capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=project,
        capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=project,
        capture_output=True
    )

    # 创建初始提交
    (project / "README.md").write_text("# Test Project")
    subprocess.run(
        ["git", "add", "."],
        cwd=project,
        capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=project,
        capture_output=True
    )

    # 创建 docs/tasks 目录
    docs = project / "docs" / "tasks"
    docs.mkdir(parents=True)

    return project


@pytest.fixture
def cli_env():
    """设置 CLI 环境变量"""
    env = os.environ.copy()
    task_flow_src = Path(__file__).parent.parent / "src"
    env["PYTHONPATH"] = str(task_flow_src)
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

    def test_start_task_syncs_docs_when_missing(self, git_project, cli_env):
        """start-task 应该在 worktree 缺失 docs 时自动同步"""
        # 创建一个包含 docs 内容的主工作区
        main_docs = git_project / "docs"
        (main_docs / "test.md").write_text("# Test Content")

        # 创建任务
        subprocess.run(
            ["python", "-m", "cli", "create-task", "Sync docs test"],
            cwd=git_project,
            capture_output=True,
            env=cli_env
        )

        # 启动任务（创建 worktree）
        result = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=git_project,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0

        # 验证 worktree 中 docs 目录存在并包含同步的内容
        worktree_docs = git_project / ".worktrees" / "sync-docs-test" / "docs"
        assert worktree_docs.exists()
        assert (worktree_docs / "test.md").exists()
        assert (worktree_docs / "test.md").read_text() == "# Test Content"

    def test_start_task_warns_on_dirty_docs(self, project_with_task, cli_env):
        """当主工作区 docs 有未提交变更时，start-task 应该输出警告"""
        main_docs = project_with_task / "docs"
        (main_docs / "dirty.md").write_text("# Dirty Content")

        # 启动任务（应该显示警告）
        result = subprocess.run(
            ["python", "-m", "cli", "start-task", "TASK-001"],
            cwd=project_with_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        # 验证输出包含警告信息
        assert "docs 有未提交变更" in result.stdout
