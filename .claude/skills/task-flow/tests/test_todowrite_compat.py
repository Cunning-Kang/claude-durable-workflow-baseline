"""
Tests for todo_id ↔ task_id mapping and idempotent creation
"""
import sys
import os
from pathlib import Path

# Add src to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from todowrite_compat.tool import TodoWriteCompat


def test_create_task_from_todo(tmp_path):
    """
    Test creating a task from todo and checking required fields exist
    """
    compat_tool = TodoWriteCompat(project_root=tmp_path)

    # Input: todo with id/content/status format
    todos = [
        {"id": 1, "content": "First task content", "status": "pending"}
    ]

    result = compat_tool.write(todos)

    # Verify the result contains id, content, status and task_id for each item
    assert len(result) == 1
    item = result[0]
    assert "id" in item
    assert "content" in item
    assert "status" in item
    assert "task_id" in item
    # Should have actual task IDs, not hardcoded TASK-000
    assert item["task_id"].startswith("TASK-")


def test_idempotent_create_uses_same_task(tmp_path):
    """
    Test that creating a task with the same todo_id returns the same task_id
    """
    compat_tool = TodoWriteCompat(project_root=tmp_path)

    todos = [
        {"id": 1, "content": "Test task content", "status": "pending"}
    ]

    # First call
    result1 = compat_tool.write(todos)

    # Second call with same todos
    result2 = compat_tool.write(todos)

    # Both results should have the same task_id for the same todo
    assert result1[0]["task_id"] == result2[0]["task_id"]
    assert result1[0]["id"] == result2[0]["id"]
    assert result1[0]["content"] == result2[0]["content"]


def test_status_mapping(tmp_path):
    """
    Test that status values are properly mapped:
    pending -> To Do
    in_progress -> In Progress
    completed -> Done
    """
    compat_tool = TodoWriteCompat(project_root=tmp_path)

    todos = [
        {"id": 1, "content": "Pending task", "status": "pending"},
        {"id": 2, "content": "In progress task", "status": "in_progress"},
        {"id": 3, "content": "Completed task", "status": "completed"}
    ]

    result = compat_tool.write(todos)

    # Verify that the status field in the result reflects the mapped values
    assert result[0]["status"] == "pending"
    assert result[1]["status"] == "in_progress"
    assert result[2]["status"] == "completed"

    # Check that the actual task files have the mapped statuses
    task_manager = compat_tool.task_manager
    for item in result:
        task = task_manager.get_task(item["task_id"])
        if item["status"] == "pending":
            assert task["status"] == "To Do"
        elif item["status"] == "in_progress":
            assert task["status"] == "In Progress"
        elif item["status"] == "completed":
            assert task["status"] == "Done"


def test_content_update_strategy(tmp_path):
    """
    Test content update strategy:
    - Initial creation uses content as title
    - Subsequent content changes are written to Notes
    """
    compat_tool = TodoWriteCompat(project_root=tmp_path)

    # Initial todo creation
    initial_todos = [
        {"id": 1, "content": "Initial task content", "status": "pending"}
    ]

    result1 = compat_tool.write(initial_todos)
    task_id = result1[0]["task_id"]

    # Get the initial task to check title
    task_manager = compat_tool.task_manager
    initial_task = task_manager.get_task(task_id)
    assert initial_task["title"] == "Initial task content"

    # Update with different content
    updated_todos = [
        {"id": 1, "content": "Updated task content", "status": "in_progress"}
    ]

    compat_tool.write(updated_todos)

    # Title should remain the same as the initial content
    updated_task = task_manager.get_task(task_id)
    assert updated_task["title"] == "Initial task content"

    # Updated content should be added as a note
    # Check the file content to verify note was added
    task_file = tmp_path / "docs" / "tasks" / f"{task_id}-initial-task-content.md"
    content = task_file.read_text()

    # The updated content should appear in the Notes section
    assert "Updated task content" in content
    assert "### 9. Notes（备注）" in content
    assert "Updated task content" in content.split("### 9. Notes（备注）")[1]


def test_bootstrap_called_when_in_progress_and_enabled(monkeypatch, tmp_path):
    """
    Test that _run_bootstrap is called when todo status is in_progress and bootstrap='wt'
    """
    # Mock the _run_bootstrap method to record if it was called
    run_bootstrap_called = []

    def mock_run_bootstrap(self, task_id):
        run_bootstrap_called.append(task_id)
        return True

    monkeypatch.setattr('todowrite_compat.tool.TodoWriteCompat._run_bootstrap', mock_run_bootstrap)

    # Create TodoWriteCompat with bootstrap enabled
    compat_tool = TodoWriteCompat(project_root=tmp_path, bootstrap="wt")

    # Create a todo with in_progress status
    todos = [
        {"id": 1, "content": "Test bootstrap task", "status": "in_progress"}
    ]

    # Execute write operation
    result = compat_tool.write(todos)

    # Verify that _run_bootstrap was called
    assert len(run_bootstrap_called) == 1
    assert result[0]["status"] == "in_progress"


def test_bootstrap_failure_does_not_block_status_update(monkeypatch, tmp_path):
    """
    Test that when _run_bootstrap throws exception, status update continues
    and task_manager.add_task_note is used to record failure
    """
    # Mock the _run_bootstrap method to throw an exception
    def mock_run_bootstrap(self, task_id):
        raise Exception("Bootstrap failed")

    monkeypatch.setattr('todowrite_compat.tool.TodoWriteCompat._run_bootstrap', mock_run_bootstrap)

    # Track calls to add_task_note
    add_task_note_calls = []
    original_add_task_note = None

    def mock_add_task_note(task_id, note):
        add_task_note_calls.append((task_id, note))
        return original_add_task_note(task_id, note)

    compat_tool = TodoWriteCompat(project_root=tmp_path, bootstrap="wt")
    original_add_task_note = compat_tool.task_manager.add_task_note
    monkeypatch.setattr(compat_tool.task_manager, 'add_task_note', mock_add_task_note)

    # Create a todo with in_progress status
    todos = [
        {"id": 1, "content": "Test bootstrap failure task", "status": "in_progress"}
    ]

    # Execute write operation - should not raise exception despite bootstrap failure
    result = compat_tool.write(todos)

    # Verify that add_task_note was called with "Bootstrap failed" message
    assert len(add_task_note_calls) >= 1
    note_found = any("Bootstrap failed" in note for _, note in add_task_note_calls)
    assert note_found, f"Expected 'Bootstrap failed' in notes, got: {add_task_note_calls}"

    # Verify that the task status was still updated to "In Progress"
    task_id = result[0]["task_id"]
    task = compat_tool.task_manager.get_task(task_id)
    assert task["status"] == "In Progress"
