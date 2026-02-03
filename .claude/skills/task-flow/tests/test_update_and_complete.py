"""Tests for update-task and complete-task commands"""

import pytest
from pathlib import Path
import subprocess
import os
import tempfile
import shutil


@pytest.fixture
def cli_env():
    """设置 CLI 环境变量"""
    env = os.environ.copy()
    task_flow_src = Path(__file__).parent.parent / "src"
    env["PYTHONPATH"] = str(task_flow_src)
    return env


@pytest.fixture
def git_project_with_task(tmp_path, cli_env):
    """创建一个带 git 仓库和任务的测试项目"""
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

    # 创建任务
    subprocess.run(
        ["python", "-m", "cli", "create-task", "Implement feature"],
        cwd=project,
        capture_output=True,
        env=cli_env
    )

    return project


class TestUpdateTask:
    """测试 update-task 命令"""

    def test_update_task_status(self, git_project_with_task, cli_env):
        """update-task 应该更新任务状态"""
        result = subprocess.run(
            ["python", "-m", "cli", "update-task", "TASK-001", "--status", "In Progress"],
            cwd=git_project_with_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert "updated" in result.stdout.lower() or "✓" in result.stdout

        # 验证任务文件被更新
        task_file = git_project_with_task / "docs" / "tasks" / "TASK-001-implement-feature.md"
        content = task_file.read_text()
        assert "status: In Progress" in content

    def test_update_task_current_step(self, git_project_with_task, cli_env):
        """update-task 应该更新当前步骤"""
        result = subprocess.run(
            ["python", "-m", "cli", "update-task", "TASK-001", "--step", "3"],
            cwd=git_project_with_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0

        # 验证任务文件被更新
        task_file = git_project_with_task / "docs" / "tasks" / "TASK-001-implement-feature.md"
        content = task_file.read_text()
        assert "current_step: 3" in content

    def test_update_task_with_note(self, git_project_with_task, cli_env):
        """update-task 应该能添加备注"""
        result = subprocess.run(
            ["python", "-m", "cli", "update-task", "TASK-001", "--note", "Changed approach to use JWT"],
            cwd=git_project_with_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0

        # 验证备注被添加到 Notes section
        task_file = git_project_with_task / "docs" / "tasks" / "TASK-001-implement-feature.md"
        content = task_file.read_text()
        assert "Changed approach to use JWT" in content

    def test_update_nonexistent_task_errors(self, git_project_with_task, cli_env):
        """更新不存在的任务应该报错"""
        result = subprocess.run(
            ["python", "-m", "cli", "update-task", "TASK-999", "--status", "Done"],
            cwd=git_project_with_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode != 0
        assert "not found" in (result.stdout + result.stderr).lower()


class TestCompleteTask:
    """测试 complete-task 命令"""

    def test_complete_task_marks_done(self, git_project_with_task, cli_env):
        """complete-task 应该标记任务为完成"""
        result = subprocess.run(
            ["python", "-m", "cli", "complete-task", "TASK-001", "--no-cleanup"],
            cwd=git_project_with_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert "done" in result.stdout.lower() or "✓" in result.stdout

        # 验证任务状态（文件已被归档到 completed/）
        archived_file = git_project_with_task / "docs" / "tasks" / "completed" / "TASK-001-implement-feature.md"
        content = archived_file.read_text()
        assert "status: Done" in content
        assert "completed_at:" in content

    def test_complete_task_archives_file(self, git_project_with_task, cli_env):
        """complete-task 应该归档任务文件"""
        subprocess.run(
            ["python", "-m", "cli", "complete-task", "TASK-001", "--no-cleanup"],
            cwd=git_project_with_task,
            capture_output=True,
            env=cli_env
        )

        # 验证任务文件被移动到 completed/
        original_file = git_project_with_task / "docs" / "tasks" / "TASK-001-implement-feature.md"
        archived_file = git_project_with_task / "docs" / "tasks" / "completed" / "TASK-001-implement-feature.md"

        assert not original_file.exists()
        assert archived_file.exists()

    def test_complete_task_updates_index(self, git_project_with_task, cli_env):
        """complete-task 应该更新 _index.json"""
        subprocess.run(
            ["python", "-m", "cli", "complete-task", "TASK-001", "--no-cleanup"],
            cwd=git_project_with_task,
            capture_output=True,
            env=cli_env
        )

        # 读取 _index.json
        index_file = git_project_with_task / "docs" / "_index.json"
        import json
        index = json.loads(index_file.read_text())

        # 应该有 completed_tasks 记录
        assert "completed_tasks" in index
        assert "TASK-001" in index["completed_tasks"]

    def test_complete_nonexistent_task_errors(self, git_project_with_task, cli_env):
        """完成不存在的任务应该报错"""
        result = subprocess.run(
            ["python", "-m", "cli", "complete-task", "TASK-999", "--no-cleanup"],
            cwd=git_project_with_task,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode != 0
        assert "not found" in (result.stdout + result.stderr).lower()
