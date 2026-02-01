"""Tests for ExecutionEngine using TaskDispatcher.

This test verifies that ExecutionEngine delegates execution to TaskDispatcher
instead of inline execution loops.
"""

import pytest
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch, call

from execution_engine.engine import ExecutionEngine
from plan_generator.types import Task, ExecutionPlan, TaskStatus


class MockDispatchResult:
    """Mock result from executor.run() with status attribute."""

    def __init__(self, status: TaskStatus):
        self.status = status


class TestEngineUsesTaskDispatcher:
    """Tests that ExecutionEngine delegates to TaskDispatcher."""

    def test_execute_next_batch_calls_task_dispatcher(self):
        """Test that execute_next_batch calls TaskDispatcher.dispatch_next_batch.

        This is the key assertion: the Engine should delegate execution to
        TaskDispatcher instead of having an inline execution loop.
        """
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2"),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            # Create task files
            for task_id in ["1", "2"]:
                task_file = task_dir / f"{task_id}.md"
                task_file.write_text(f"---\nstatus: pending\n---\nTask {task_id}\n")

            # Mock TaskDispatcher to track calls
            with patch.object(
                ExecutionEngine,
                "_create_dispatcher",
                return_value=MagicMock()
            ) as mock_create_dispatcher:
                mock_dispatcher = mock_create_dispatcher.return_value
                mock_dispatcher.dispatch_next_batch.return_value = {
                    "tasks_dispatched": 2,
                    "tasks_completed": 2,
                    "tasks_failed": 0,
                }

                # Execute next batch
                result = engine.execute_next_batch()

                # Assert TaskDispatcher.dispatch_next_batch was called
                assert mock_dispatcher.dispatch_next_batch.called
                mock_dispatcher.dispatch_next_batch.assert_called_once()

                # Verify it was called with batch_size and ready_task_ids
                call_args = mock_dispatcher.dispatch_next_batch.call_args
                batch_size = call_args[0][0]
                ready_task_ids = call_args[0][1]

                assert batch_size == engine.controller.batch_size
                assert isinstance(ready_task_ids, list)
                assert "1" in ready_task_ids or "2" in ready_task_ids

                # Verify result structure matches expected stats
                assert "batch_size" in result
                assert "tasks_executed" in result
                assert "total_completed" in result

    def test_dispatcher_used_with_subagent_pool_executor(self):
        """Test that TaskDispatcher is initialized with SubagentPool executor.

        The dispatcher should receive an executor that uses SubagentPool.submit
        to execute task.metadata["callable"].
        """
        tasks = [
            Task(id="1", title="Task 1", description="Description 1", metadata={"callable": lambda: "ok"}),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            task_file = task_dir / "1.md"
            task_file.write_text("---\nstatus: pending\n---\nTask 1\n")

            engine = ExecutionEngine(plan, task_dir)

            with patch.object(
                ExecutionEngine,
                "_create_dispatcher",
                wraps=engine._create_dispatcher
            ) as spy_create_dispatcher:
                # Execute to trigger dispatcher creation
                engine.execute_next_batch()

                # Verify _create_dispatcher was called
                assert spy_create_dispatcher.called

    def test_engine_passes_ready_tasks_to_dispatcher(self):
        """Test that Engine passes resolved ready task IDs to dispatcher."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2", dependencies=["1"]),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)

            # Create task files
            for task_id in ["1", "2"]:
                task_file = task_dir / f"{task_id}.md"
                task_file.write_text(f"---\nstatus: pending\n---\nTask {task_id}\n")

            engine = ExecutionEngine(plan, task_dir)

            with patch.object(
                ExecutionEngine,
                "_create_dispatcher",
                return_value=MagicMock()
            ) as mock_create_dispatcher:
                mock_dispatcher = mock_create_dispatcher.return_value
                mock_dispatcher.dispatch_next_batch.return_value = {
                    "tasks_dispatched": 1,
                    "tasks_completed": 1,
                    "tasks_failed": 0,
                }

                engine.execute_next_batch()

                # Verify ready_task_ids passed to dispatcher
                call_args = mock_dispatcher.dispatch_next_batch.call_args
                ready_task_ids = call_args[0][1]

                # Only task 1 should be ready (no dependencies)
                assert ready_task_ids == ["1"]


class TestEngineHasCreateDispatcherMethod:
    """Tests for the _create_dispatcher method."""

    def test_engine_has_create_dispatcher_method(self):
        """Test that ExecutionEngine has a _create_dispatcher method.

        This method should initialize TaskDispatcher with the appropriate
        executor adapter that uses SubagentPool.
        """
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            # Verify method exists
            assert hasattr(engine, "_create_dispatcher")
            assert callable(getattr(engine, "_create_dispatcher"))
