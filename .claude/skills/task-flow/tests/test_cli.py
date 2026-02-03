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


class TestProjectRootOverride:
    def test_create_task_respects_project_root_env(self, tmp_path, cli_env):
        project = tmp_path / "project"
        (project / "docs" / "tasks").mkdir(parents=True)
        runner = tmp_path / "runner"
        runner.mkdir()

        env = cli_env.copy()
        env["TASK_FLOW_PROJECT_ROOT"] = str(project)

        result = subprocess.run(
            ["python", "-m", "cli", "create-task", "Test task"],
            cwd=runner,
            capture_output=True,
            text=True,
            env=env
        )

        assert result.returncode == 0
        assert (project / "docs" / "tasks" / "TASK-001-test-task.md").exists()
        assert not (runner / "docs" / "tasks" / "TASK-001-test-task.md").exists()

    def test_create_task_respects_project_root_arg(self, tmp_path, cli_env):
        project = tmp_path / "project"
        (project / "docs" / "tasks").mkdir(parents=True)
        runner = tmp_path / "runner"
        runner.mkdir()

        result = subprocess.run(
            [
                "python",
                "-m",
                "cli",
                "--project-root",
                str(project),
                "create-task",
                "Test task",
            ],
            cwd=runner,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert (project / "docs" / "tasks" / "TASK-001-test-task.md").exists()
        assert not (runner / "docs" / "tasks" / "TASK-001-test-task.md").exists()


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


class TestExecuteNextBatchCommand:
    """测试 execute-next-batch 命令"""

    @pytest.fixture
    def project_dir(self, tmp_path):
        project = tmp_path / "project"
        project.mkdir()
        (project / "docs" / "tasks").mkdir(parents=True)
        (project / "docs" / "plans").mkdir(parents=True)

        plan_file = project / "docs" / "plans" / "execution-plan.yaml"
        plan_file.write_text(
            """tasks:
- id: TASK-001
  title: Step 1
  description: First step
- id: TASK-002
  title: Step 2
  description: Second step
  dependencies:
    - TASK-001
"""
        )

        task_file = project / "docs" / "tasks" / "TASK-001-test-task.md"
        task_file.write_text(
            """---
id: TASK-001
title: "Test Task"
status: "To Do"
created_at: 2026-02-01
updated_at: 2026-02-01
execution_mode: "executing-plans"
plan_file: "docs/plans/execution-plan.yaml"
execution_config:
  batch_size: 1
  auto_continue: false
  checkpoint_interval: 3
execution_state: {}
---
"""
        )

        return project, task_file

    def test_execute_next_batch_command_in_help(self, cli_env, tmp_path):
        project = tmp_path / "project"
        project.mkdir()
        (project / "docs" / "tasks").mkdir(parents=True)

        result = subprocess.run(
            ["python", "-m", "cli", "--help"],
            cwd=project,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        assert "execute-next-batch" in result.stdout

    def test_execute_next_batch_runs_engine(self, cli_env, project_dir):
        project, task_file = project_dir

        result = subprocess.run(
            ["python", "-m", "cli", "execute-next-batch", "TASK-001"],
            cwd=project,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        stats = json.loads(result.stdout)
        assert stats["tasks_executed"] == 1

    @pytest.fixture
    def project_dir_markdown(self, tmp_path):
        project = tmp_path / "markdown-project"
        project.mkdir()
        (project / "docs" / "tasks").mkdir(parents=True)
        (project / "docs" / "plans").mkdir(parents=True)

        plan_file = project / "docs" / "plans" / "execution-plan.md"
        plan_file.write_text(
            """# Example Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Example goal

---

### Task 1: First step
**Description:** Do the first thing

### Task 2: Second step
**Description:** Do the second thing
"""
        )

        task_file = project / "docs" / "tasks" / "TASK-001-test-task.md"
        task_file.write_text(
            """---
id: TASK-001
title: "Test Task"
status: "To Do"
created_at: 2026-02-01
updated_at: 2026-02-01
execution_mode: "executing-plans"
plan_file: "docs/plans/execution-plan.md"
execution_config:
  batch_size: 1
  auto_continue: false
  checkpoint_interval: 3
execution_state: {}
---
"""
        )

        return project

    def test_execute_next_batch_accepts_markdown_plan(self, cli_env, project_dir_markdown):
        project = project_dir_markdown

        result = subprocess.run(
            ["python", "-m", "cli", "execute-next-batch", "TASK-001"],
            cwd=project,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        stats = json.loads(result.stdout)
        assert stats["tasks_executed"] == 1

    def test_execute_next_batch_no_callable_defaults_to_noop(self, cli_env, project_dir):
        project, _task_file = project_dir

        result = subprocess.run(
            ["python", "-m", "cli", "execute-next-batch", "TASK-001"],
            cwd=project,
            capture_output=True,
            text=True,
            env=cli_env
        )

        assert result.returncode == 0
        stats = json.loads(result.stdout)
        assert stats["total_completed"] == 1


class TestExecuteNextBatchStatusChanges:
    """测试 execute-next-batch 命令的状态变更"""

    @pytest.fixture
    def project_dir_with_task(self, tmp_path):
        project = tmp_path / "project"
        project.mkdir()
        (project / "docs" / "tasks").mkdir(parents=True)
        (project / "docs" / "plans").mkdir(parents=True)

        # 创建一个简单的计划文件 - 使用与原测试相同的格式
        plan_file = project / "docs" / "plans" / "simple-plan.yaml"
        plan_file.write_text(
            """tasks:
- id: TASK-001
  title: Step 1
  description: First step
- id: TASK-002
  title: Step 2
  description: Second step
  dependencies:
    - TASK-001
"""
        )

        # 创建任务文件，初始状态为 "To Do"
        task_file = project / "docs" / "tasks" / "TASK-001-test-status-change.md"
        task_file.write_text(
            """---
id: TASK-001
title: "Test Status Change"
status: "To Do"
created_at: 2026-02-01
updated_at: 2026-02-01
execution_mode: "executing-plans"
plan_file: "docs/plans/simple-plan.yaml"
execution_config:
  batch_size: 1
  auto_continue: false
  checkpoint_interval: 3
execution_state: {}
---
# Task: Test Status Change

## Plan Packet
...
"""
        )

        return project, task_file

    def test_execute_next_batch_sets_status_to_done_if_successful(self, cli_env, project_dir_with_task):
        """execute-next-batch 成功时应将状态设置为 'Done'"""
        project, task_file = project_dir_with_task

        # 验证初始状态是 "To Do"
        initial_content = task_file.read_text()
        assert 'status: "To Do"' in initial_content

        # 执行 execute-next-batch 命令
        result = subprocess.run(
            ["python", "-m", "cli", "execute-next-batch", "TASK-001"],
            cwd=project,
            capture_output=True,
            text=True,
            env=cli_env
        )

        # 验证命令正常完成
        assert result.returncode == 0
        json.loads(result.stdout)

        # 验证状态更新为 Done
        updated_content = task_file.read_text()
        assert "status: Done" in updated_content

    def test_execute_next_batch_handles_missing_plan_file(self, tmp_path, cli_env):
        """execute-next-batch 应该正确处理缺少 plan_file 的情况"""
        project = tmp_path / "project"
        project.mkdir()
        (project / "docs" / "tasks").mkdir(parents=True)

        # 创建一个没有 plan_file 的任务
        task_file = project / "docs" / "tasks" / "TASK-001-no-plan.md"
        task_file.write_text(
            """---
id: TASK-001
title: "No Plan Task"
status: "To Do"
created_at: 2026-02-01
updated_at: 2026-02-01
execution_mode: "executing-plans"
plan_file: null
---
# Task: No Plan Task
"""
        )

        # 执行 execute-next-batch 命令 - 这会导致错误
        result = subprocess.run(
            ["python", "-m", "cli", "execute-next-batch", "TASK-001"],
            cwd=project,
            capture_output=True,
            text=True,
            env=cli_env
        )

        # 命令应该返回非 0 并包含错误信息
        assert result.returncode != 0
        assert "plan_file is required" in result.stderr

        # 读取任务文件，验证状态变为 "Blocked" 由于错误
        updated_content = task_file.read_text()
        assert "status: Blocked" in updated_content
