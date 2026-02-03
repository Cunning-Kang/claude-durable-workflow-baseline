"""Tests for task-flow task manager"""

import pytest
from pathlib import Path
from task_manager import TaskManager


@pytest.fixture
def temp_tasks_dir(tmp_path):
    """Create a temporary tasks directory"""
    tasks_dir = tmp_path / "docs" / "tasks"
    tasks_dir.mkdir(parents=True)
    return tasks_dir


@pytest.fixture
def task_manager(temp_tasks_dir):
    """Create a TaskManager instance with temp directory"""
    index_file = temp_tasks_dir.parent / "_index.json"
    return TaskManager(tasks_dir=temp_tasks_dir, index_file=index_file)


class TestTaskIDGeneration:
    """测试任务 ID 生成"""

    def test_first_task_gets_TASK_001(self, task_manager):
        """第一个任务应该获得 TASK-001"""
        task_id = task_manager.generate_task_id()

        assert task_id == "TASK-001"

    def test_second_task_gets_TASK_002(self, task_manager):
        """第二个任务应该获得 TASK-002"""
        task_manager.generate_task_id()  # TASK-001
        task_id = task_manager.generate_task_id()

        assert task_id == "TASK-002"

    def test_task_id_persists_in_index(self, task_manager, temp_tasks_dir):
        """任务 ID 应该持久化到 _index.json"""
        task_manager.generate_task_id()  # TASK-001

        # 创建新的 TaskManager 实例，模拟重启
        new_manager = TaskManager(
            tasks_dir=temp_tasks_dir,
            index_file=temp_tasks_dir.parent / "_index.json"
        )
        task_id = new_manager.generate_task_id()

        assert task_id == "TASK-002"


class TestTaskCreation:
    """测试任务创建"""

    def test_create_task_generates_unique_id(self, task_manager):
        """创建任务应该生成唯一 ID"""
        task_id = task_manager.create_task("Implement feature")

        assert task_id == "TASK-001"

    def test_create_task_creates_task_file(self, task_manager, temp_tasks_dir):
        """创建任务应该生成任务文件"""
        task_id = task_manager.create_task("Implement feature")

        task_file = temp_tasks_dir / f"{task_id}-implement-feature.md"
        assert task_file.exists()

    def test_create_task_file_has_plan_packet_template(self, task_manager, temp_tasks_dir):
        """任务文件应该包含完整的 Plan Packet 模板"""
        task_manager.create_task("Implement user authentication")

        task_file = temp_tasks_dir / "TASK-001-implement-user-authentication.md"
        content = task_file.read_text()

        # 检查 Plan Packet 的核心 sections
        assert "## Plan Packet" in content
        assert "### 1. Goal / Non-goals" in content
        assert "### 2. Scope" in content
        assert "### 3. Interfaces & Constraints" in content
        assert "### 4. Execution Order" in content
        assert "### 5. Acceptance Criteria" in content
        assert "### 6. Quality Gates" in content
        assert "### 7. Risks & Rollback" in content
        assert "### 8. Backlog 任务映射" in content
        assert "### 9. Notes" in content

    def test_create_task_file_has_yaml_frontmatter(self, task_manager, temp_tasks_dir):
        """任务文件应该包含 YAML frontmatter"""
        task_manager.create_task("Implement feature")

        task_file = temp_tasks_dir / "TASK-001-implement-feature.md"
        content = task_file.read_text()

        # YAML frontmatter 格式: ---\nYAML\n---
        parts = content.split("---")
        assert content.startswith("---")
        assert "id: TASK-001" in parts[1]  # YAML 在第一和第二个 --- 之间
        assert "title: Implement feature" in parts[1]
        assert "status: To Do" in parts[1]
        assert "created_at:" in parts[1]
        assert parts[1].strip().startswith("id:")  # 验证 YAML 内容
        assert parts[2].strip().startswith("# Task:")  # 验证正文内容

    def test_create_task_auto_fills_plan_packet_fields(self, task_manager, temp_tasks_dir):
        """创建任务应该自动填充 Plan Packet 的任务映射字段"""
        task_id = task_manager.create_task("Implement feature")

        task_file = temp_tasks_dir / f"{task_id}-implement-feature.md"
        content = task_file.read_text()

        # 检查自动填充的字段
        assert f"- 任务 ID：{task_id}" in content
        assert f"- 任务文件：docs/tasks/{task_id}-implement-feature.md" in content
        assert "- 关联分支：" in content


class TestTaskListing:
    """测试任务列表"""

    def test_list_empty_tasks(self, task_manager):
        """空任务列表应该返回空列表"""
        tasks = task_manager.list_tasks()

        assert tasks == []

    def test_list_single_task(self, task_manager):
        """列出单个任务"""
        task_manager.create_task("First task")

        tasks = task_manager.list_tasks()

        assert len(tasks) == 1
        assert tasks[0]["id"] == "TASK-001"
        assert tasks[0]["title"] == "First task"
        assert tasks[0]["status"] == "To Do"

    def test_list_multiple_tasks(self, task_manager):
        """列出多个任务"""
        task_manager.create_task("First task")
        task_manager.create_task("Second task")

        tasks = task_manager.list_tasks()

        assert len(tasks) == 2
        assert tasks[0]["id"] == "TASK-001"
        assert tasks[1]["id"] == "TASK-002"

    def test_list_tasks_filters_by_status(self, task_manager):
        """按状态过滤任务"""
        task_manager.create_task("Todo task")
        in_progress_id = task_manager.create_task("In progress task")

        # 更新任务状态
        task_manager.update_task(in_progress_id, status="In Progress")

        tasks = task_manager.list_tasks(status="In Progress")

        assert len(tasks) == 1
        assert tasks[0]["id"] == in_progress_id


class TestTaskUpdate:
    """测试任务更新"""

    def test_update_task_status(self, task_manager, temp_tasks_dir):
        """更新任务状态"""
        task_id = task_manager.create_task("Test task")

        task_manager.update_task(task_id, status="In Progress")

        task_file = temp_tasks_dir / f"{task_id}-test-task.md"
        content = task_file.read_text()

        assert "status: In Progress" in content

    def test_task_status_updates_on_execution_states(self, task_manager, temp_tasks_dir):
        task_id = task_manager.create_task("Test task")
        task_manager.update_task(task_id, status="In Progress")
        task_file = temp_tasks_dir / f"{task_id}-test-task.md"
        assert "status: In Progress" in task_file.read_text()

    def test_update_task_worktree(self, task_manager, temp_tasks_dir):
        """更新 worktree 路径"""
        task_id = task_manager.create_task("Test task")

        task_manager.update_task(task_id, worktree=".worktrees/feature-branch")

        task_file = temp_tasks_dir / f"{task_id}-test-task.md"
        content = task_file.read_text()

        assert "worktree: .worktrees/feature-branch" in content

    def test_update_task_current_step(self, task_manager, temp_tasks_dir):
        """更新当前步骤"""
        task_id = task_manager.create_task("Test task")

        task_manager.update_task(task_id, current_step=3)

        task_file = temp_tasks_dir / f"{task_id}-test-task.md"
        content = task_file.read_text()

        assert "current_step: 3" in content


class TestTaskRetrieval:
    """测试任务检索"""

    def test_get_task_by_id(self, task_manager):
        """通过 ID 获取任务"""
        task_id = task_manager.create_task("Test task")

        task = task_manager.get_task(task_id)

        assert task["id"] == task_id
        assert task["title"] == "Test task"
        assert task["status"] == "To Do"

    def test_get_nonexistent_task_returns_none(self, task_manager):
        """获取不存在的任务返回 None"""
        task = task_manager.get_task("TASK-999")

        assert task is None


class TestTaskStepUpdates:
    """测试任务步骤更新"""

    def test_task_updates_step_after_each_execution(self, task_manager, temp_tasks_dir):
        """执行步骤后任务应更新 current_step"""
        task_id = task_manager.create_task("Test task")

        # 验证初始 current_step 为 0
        task = task_manager.get_task(task_id)
        content = task["content"]
        assert "current_step: 0" in content

        # 更新步骤到 1
        task_manager.update_task_step(task_id, step=1)

        # 验证步骤已更新
        task_file = temp_tasks_dir / f"{task_id}-test-task.md"
        updated_content = task_file.read_text()
        assert "current_step: 1" in updated_content

        # 更新到其他步骤
        task_manager.update_task_step(task_id, step=3)
        final_content = task_file.read_text()
        assert "current_step: 3" in final_content
