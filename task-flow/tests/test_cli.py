"""Tests for task-flow CLI"""

import pytest
from pathlib import Path
import subprocess
import json
import tempfile
import shutil
import os


@pytest.fixture
def cli_env():
    """设置 CLI 环境变量"""
    env = os.environ.copy()
    # 获取 task-flow/src 的绝对路径
    task_flow_src = Path(__file__).parent.parent / "src"
    env["PYTHONPATH"] = str(task_flow_src)
    return env


class TestCreateTaskCommand:
    """测试 create-task 命令"""

    @pytest.fixture
    def project_dir(self, tmp_path):
        """创建临时项目目录"""
        project = tmp_path / "test-project"
        project.mkdir()
        docs = project / "docs" / "tasks"
        docs.mkdir(parents=True)
        return project

    def test_create_task_generates_id(self, project_dir, cli_env):
        """create-task 应该生成任务 ID"""
        result = subprocess.run(
            ["python", "-m", "cli", "create-task", "Implement feature"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert "TASK-001" in result.stdout

    def test_create_task_creates_file(self, project_dir, cli_env):
        """create-task 应该创建任务文件"""
        subprocess.run(
            ["python", "-m", "cli", "create-task", "Test task"],
            cwd=project_dir,
            capture_output=True,
            env=cli_env
        )

        task_file = project_dir / "docs" / "tasks" / "TASK-001-test-task.md"
        assert task_file.exists()

    def test_create_task_second_gets_new_id(self, project_dir, cli_env):
        """第二个任务应该获得 TASK-002"""
        subprocess.run(
            ["python", "-m", "cli", "create-task", "First task"],
            cwd=project_dir,
            capture_output=True,
            env=cli_env
        )

        result = subprocess.run(
            ["python", "-m", "cli", "create-task", "Second task"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert "TASK-002" in result.stdout


class TestListTasksCommand:
    """测试 list-tasks 命令"""

    @pytest.fixture
    def project_dir(self, tmp_path, cli_env):
        """创建临时项目目录并添加任务"""
        project = tmp_path / "test-project"
        project.mkdir()
        docs = project / "docs" / "tasks"
        docs.mkdir(parents=True)

        # 创建一个测试任务
        index_file = project / "docs" / "_index.json"
        index_file.write_text('{"next_id": 1}')

        subprocess.run(
            ["python", "-m", "cli", "create-task", "Test task"],
            cwd=project,
            capture_output=True,
            env=cli_env
        )

        return project

    def test_list_tasks_shows_tasks(self, project_dir, cli_env):
        """list-tasks 应该显示任务列表"""
        result = subprocess.run(
            ["python", "-m", "cli", "list-tasks"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert "TASK-001" in result.stdout
        assert "Test task" in result.stdout

    def test_list_tasks_empty(self, tmp_path, cli_env):
        """空任务列表应该显示空信息"""
        project = tmp_path / "empty-project"
        project.mkdir()
        docs = project / "docs" / "tasks"
        docs.mkdir(parents=True)

        result = subprocess.run(
            ["python", "-m", "cli", "list-tasks"],
            cwd=project,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert "No tasks" in result.stdout


class TestShowTaskCommand:
    """测试 show-task 命令"""

    @pytest.fixture
    def project_dir(self, tmp_path, cli_env):
        """创建临时项目目录并添加任务"""
        project = tmp_path / "test-project"
        project.mkdir()
        docs = project / "docs" / "tasks"
        docs.mkdir(parents=True)

        subprocess.run(
            ["python", "-m", "cli", "create-task", "Test task"],
            cwd=project,
            capture_output=True,
            env=cli_env
        )

        return project

    def test_show_task_displays_details(self, project_dir, cli_env):
        """show-task 应该显示任务详情"""
        result = subprocess.run(
            ["python", "-m", "cli", "show-task", "TASK-001"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert "TASK-001" in result.stdout
        assert "Test task" in result.stdout
        assert "Plan Packet" in result.stdout

    def test_show_nonexistent_task_errors(self, project_dir, cli_env):
        """显示不存在的任务应该报错"""
        result = subprocess.run(
            ["python", "-m", "cli", "show-task", "TASK-999"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode != 0
        assert "not found" in (result.stdout + result.stderr).lower()
