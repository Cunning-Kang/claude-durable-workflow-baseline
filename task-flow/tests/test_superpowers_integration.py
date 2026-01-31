"""Tests for Superpowers skills integration - simplified"""

import pytest
from pathlib import Path
import subprocess
import os


@pytest.fixture
def cli_env():
    env = os.environ.copy()
    task_flow_src = Path(__file__).parent.parent / "src"
    env["PYTHONPATH"] = str(task_flow_src)
    return env


class TestFinishingFlow:
    """测试完成任务流程"""

    def test_complete_task_updates_status(self, cli_env, tmp_path):
        """complete-task 应该标记任务为 Done"""
        project = tmp_path / "project"
        project.mkdir()

        # 初始化 git
        subprocess.run(["git", "init"], cwd=project, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=project, capture_output=True)
        (project / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=project, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=project, capture_output=True)

        # 创建任务
        subprocess.run(
            ["python", "-m", "cli", "create-task", "Test"],
            cwd=project,
            capture_output=True,
            env=cli_env
        )

        # 完成任务
        result = subprocess.run(
            ["python", "-m", "cli", "complete-task", "TASK-001", "--no-cleanup"],
            cwd=project,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert "Done" in result.stdout

        # 检查任务文件被归档
        archived_file = project / "docs" / "tasks" / "completed" / "TASK-001-test.md"
        assert archived_file.exists()

    def test_complete_task_shows_next_steps(self, cli_env, tmp_path):
        """complete-task 应该显示 Superpowers 风格的下一步提示"""
        project = tmp_path / "project"
        project.mkdir()

        # 初始化 git
        subprocess.run(["git", "init"], cwd=project, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=project, capture_output=True)
        (project / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=project, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=project, capture_output=True)

        # 创建并完成任务
        subprocess.run(
            ["python", "-m", "cli", "create-task", "Test"],
            cwd=project,
            capture_output=True,
            env=cli_env
        )

        result = subprocess.run(
            ["python", "-m", "cli", "complete-task", "TASK-001", "--no-cleanup"],
            cwd=project,
            capture_output=True,
            text=True,
            env=cli_env
        )

        # 应该包含完成选项提示
        assert result.returncode == 0
        output = result.stdout.lower()
        # 应该提到测试、合并策略或清理
        assert "test" in output or "merge" in output or "clean" in output or "next" in output


class TestExecutionMode:
    """测试执行模式支持"""

    def test_task_has_execution_mode_field(self, cli_env, tmp_path):
        """任务应该包含 execution_mode 字段"""
        project = tmp_path / "project"
        project.mkdir()

        # 初始化 git
        subprocess.run(["git", "init"], cwd=project, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=project, capture_output=True)
        (project / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=project, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=project, capture_output=True)

        # 创建任务
        subprocess.run(
            ["python", "-m", "cli", "create-task", "Test"],
            cwd=project,
            capture_output=True,
            env=cli_env
        )

        # 读取任务文件
        task_file = project / "docs" / "tasks" / "TASK-001-test.md"
        content = task_file.read_text()

        # 应该包含 execution_mode 字段
        assert "execution_mode:" in content

    def test_default_execution_mode_is_manual(self, cli_env, tmp_path):
        """默认执行模式应该是 manual"""
        project = tmp_path / "project"
        project.mkdir()

        # 初始化 git
        subprocess.run(["git", "init"], cwd=project, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=project, capture_output=True)
        (project / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=project, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=project, capture_output=True)

        # 创建任务
        subprocess.run(
            ["python", "-m", "cli", "create-task", "Test"],
            cwd=project,
            capture_output=True,
            env=cli_env
        )

        # 读取任务文件
        task_file = project / "docs" / "tasks" / "TASK-001-test.md"
        content = task_file.read_text()

        # 应该默认为 manual
        assert "execution_mode: manual" in content
