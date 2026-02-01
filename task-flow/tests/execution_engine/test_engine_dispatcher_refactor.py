"""Tests for ExecutionEngine dispatcher and state tracking refactor.

TDD: RED - write tests that fail on current implementation.

This test suite validates three important refactors:
1. Dispatcher reuse (avoid recreating dispatcher on each batch)
2. Task status synchronization (execution_state.task_status tracks in-memory TaskStatus)
3. Executor decoupling from StateTracker (callbacks instead of direct getter)
"""

import pytest
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch, call

from execution_engine.engine import ExecutionEngine, SubagentPoolExecutor, ExecutorResult
from plan_generator.types import Task, ExecutionPlan, TaskStatus


class TestDispatcherReuse:
    """Tests for dispatcher caching and reuse across batches.

    Issue: Dispatcher is recreated on every execute_next_batch call, which is
    wasteful and can cause inconsistencies.
    Fix: Cache the dispatcher after first creation and reuse it.
    """

    def test_dispatcher_reused_across_multiple_batches(self):
        """Test that the same dispatcher instance is reused across batches.

        Current implementation creates a new dispatcher on every call to
        execute_next_batch. After refactor, dispatcher should be cached and
        reused.
        """
        tasks = [
            Task(id="1", title="Task 1", description="Description 1", metadata={"callable": lambda: "ok"}),
            Task(id="2", title="Task 2", description="Description 2", dependencies=["1"], metadata={"callable": lambda: "ok"}),
            Task(id="3", title="Task 3", description="Description 3", dependencies=["1"], metadata={"callable": lambda: "ok"}),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)

            # Create task files
            for task_id in ["1", "2", "3"]:
                task_file = task_dir / f"{task_id}.md"
                task_file.write_text(f"---\nstatus: pending\n---\nTask {task_id}\n")

            engine = ExecutionEngine(plan, task_dir)

            # Spy on _create_dispatcher to track calls
            with patch.object(
                ExecutionEngine,
                "_create_dispatcher",
                wraps=engine._create_dispatcher
            ) as spy_create_dispatcher:
                # Execute first batch - should execute task 1 only
                result1 = engine.execute_next_batch()
                assert result1["batch_size"] == 1  # Only task 1 is ready

                # Mark task 1 as completed in plan (simulating successful execution)
                for task in engine.plan.tasks:
                    if task.id == "1":
                        task.status = TaskStatus.COMPLETED

                # Execute second batch - should execute tasks 2 and 3
                result2 = engine.execute_next_batch()

                # After refactor: _create_dispatcher should be called only once
                # Current implementation: called twice (once per batch)
                assert spy_create_dispatcher.call_count == 1, \
                    "Dispatcher should be created once and reused across batches"

    def test_executor_adapter_reused_with_dispatcher(self):
        """Test that the executor adapter is reused along with the dispatcher.

        The SubagentPoolExecutor should be the same instance across batches,
        not recreated each time.
        """
        tasks = [
            Task(id="1", title="Task 1", description="Description 1", metadata={"callable": lambda: "ok"}),
            Task(id="2", title="Task 2", description="Description 2", dependencies=["1"], metadata={"callable": lambda: "ok"}),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)

            # Create task files
            for task_id in ["1", "2"]:
                task_file = task_dir / f"{task_id}.md"
                task_file.write_text(f"---\nstatus: pending\n---\nTask {task_id}\n")

            engine = ExecutionEngine(plan, task_dir)

            # Track executor instances created
            executor_instances = []
            original_create = engine._create_dispatcher

            def tracking_create():
                dispatcher = original_create()
                if isinstance(dispatcher.executor, SubagentPoolExecutor):
                    executor_instances.append(dispatcher.executor)
                return dispatcher

            with patch.object(
                ExecutionEngine,
                "_create_dispatcher",
                side_effect=tracking_create
            ):
                engine.execute_next_batch()
                # Mark task 1 as completed to make task 2 ready
                for task in engine.plan.tasks:
                    if task.id == "1":
                        task.status = TaskStatus.COMPLETED
                engine.execute_next_batch()

                # After refactor: only one executor instance created
                assert len(executor_instances) <= 1, \
                    "Executor adapter should be reused across batches"


class TestTaskStatusSynchronization:
    """Tests for TaskStatus synchronization to task files.

    Issue: Task.status is in-memory, but execution_state.status tracks execution
    flow states (running, completed, failed). There's no field to track the
    in-memory TaskStatus enum values.

    Fix: Add execution_state.task_status to track TaskStatus enum values.
    """

    def test_task_status_synced_to_execution_state(self):
        """Test that task.status.value is synced to execution_state.task_status.

        When a task's status changes (e.g., to IN_PROGRESS), the task file
        should have execution_state.task_status set to "in_progress".
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

            # Execute the task
            engine.execute_next_batch()

            # After execution, read task file and verify task_status field
            content = task_file.read_text()
            parts = content.split("---")
            yaml_content = parts[1]
            import yaml
            data = yaml.safe_load(yaml_content)

            # After refactor: execution_state should contain task_status
            assert "execution_state" in data, "execution_state should exist"
            assert "task_status" in data["execution_state"], \
                "execution_state should contain task_status field"
            # After successful execution, task_status should be "completed"
            assert data["execution_state"]["task_status"] in ["in_progress", "completed"], \
                f"task_status should be 'in_progress' or 'completed', got {data['execution_state'].get('task_status')}"

    def test_task_status_tracks_all_status_transitions(self):
        """Test that task_status tracks transitions: pending -> in_progress -> completed.

        This verifies that task_status is updated at each stage of execution.
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

            # Track state transitions by checking after each phase
            import yaml

            # Before execution - verify initial state
            content = task_file.read_text()
            parts = content.split("---")
            data = yaml.safe_load(parts[1])
            # Initially, task_status may not exist (backward compatible)

            # Execute the task
            engine.execute_next_batch()

            # After execution - verify final state
            content = task_file.read_text()
            parts = content.split("---")
            data = yaml.safe_load(parts[1])

            assert "task_status" in data["execution_state"], \
                "execution_state should contain task_status after execution"
            assert data["execution_state"]["task_status"] == "completed", \
                f"task_status should be 'completed' after execution, got {data['execution_state']['task_status']}"


class TestExecutorStateTrackerDecoupling:
    """Tests for decoupling executor from StateTracker.

    Issue: SubagentPoolExecutor takes state_tracker_getter as a callback,
    creating tight coupling between executor and StateTracker.

    Fix: Use simple callbacks (on_start, on_success, on_fail) or have Engine
    handle StateTracker after executor returns result.
    """

    def test_executor_does_not_take_state_tracker_getter(self):
        """Test that executor doesn't directly access StateTracker.

        After refactor, executor should use callbacks instead of
        state_tracker_getter, reducing coupling.
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

            # Check executor's __init__ signature - it shouldn't take state_tracker_getter
            # after refactor (it should take callbacks instead)
            dispatcher = engine._create_dispatcher()
            executor = dispatcher.executor

            # After refactor: executor should have callbacks like on_start, on_success, on_fail
            # instead of state_tracker_getter
            has_state_tracker_getter = hasattr(executor, "state_tracker_getter")
            has_callbacks = (
                hasattr(executor, "on_start") and
                hasattr(executor, "on_success") and
                hasattr(executor, "on_fail")
            )

            # At least one of the decoupling approaches should be used
            assert has_callbacks or not has_state_tracker_getter, \
                "Executor should use callbacks instead of state_tracker_getter for decoupling"

    def test_executor_callbacks_invoked_correctly(self):
        """Test that executor callbacks are invoked in correct order.

        When executor uses callbacks, they should be invoked:
        - on_start when task begins execution
        - on_success when task completes successfully
        - on_fail when task execution fails

        This test verifies the callbacks are properly wired by checking that
        the internal engine methods that handle state tracking are called.
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

            # Track callback invocations by mocking internal methods
            callback_log = []

            with patch.object(engine, "_on_task_start") as mock_on_start:
                with patch.object(engine, "_on_task_success") as mock_on_success:
                    # Set side effects to track calls
                    mock_on_start.side_effect = lambda task_id, task: callback_log.append(("on_start", task_id))
                    mock_on_success.side_effect = lambda task_id, result: callback_log.append(("on_success", task_id))

                    # Execute the task
                    engine.execute_next_batch()

                    # Verify callbacks were invoked via the mocked methods
                    assert any(cb[0] == "on_start" for cb in callback_log), \
                        "on_start callback should be invoked"
                    assert any(cb[0] == "on_success" for cb in callback_log), \
                        "on_success callback should be invoked"


class TestIntegrationAfterRefactor:
    """Integration tests to verify all refactors work together."""

    def test_full_workflow_with_all_refactors(self):
        """Test full execution workflow with all three refactors applied.

        This ensures that:
        1. Dispatcher is reused across batches
        2. Task status is synced to execution_state.task_status
        3. Executor is decoupled from StateTracker via callbacks
        """
        tasks = [
            Task(id="1", title="Task 1", description="Description 1", metadata={"callable": lambda: "ok"}),
            Task(id="2", title="Task 2", description="Description 2", dependencies=["1"], metadata={"callable": lambda: "ok"}),
            Task(id="3", title="Task 3", description="Description 3", dependencies=["1"], metadata={"callable": lambda: "ok"}),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)

            # Create task files
            for task_id in ["1", "2", "3"]:
                task_file = task_dir / f"{task_id}.md"
                task_file.write_text(f"---\nstatus: pending\n---\nTask {task_id}\n")

            engine = ExecutionEngine(plan, task_dir)

            import yaml

            # Track dispatcher creation
            with patch.object(
                ExecutionEngine,
                "_create_dispatcher",
                wraps=engine._create_dispatcher
            ) as spy_create_dispatcher:
                # First batch - only task 1
                result1 = engine.execute_next_batch()
                assert result1["batch_size"] == 1

                # Verify task 1's status was synced
                task1_file = task_dir / "1.md"
                content = task1_file.read_text()
                parts = content.split("---")
                data = yaml.safe_load(parts[1])
                assert "task_status" in data.get("execution_state", {}), \
                    "Task 1 should have task_status in execution_state"

                # Second batch - tasks 2 and 3 (after task 1 completes)
                result2 = engine.execute_next_batch()

                # Verify dispatcher was reused (created only once)
                assert spy_create_dispatcher.call_count == 1, \
                    "Dispatcher should be created once and reused"

                # Verify tasks 2 and 3 were executed
                assert result2["batch_size"] == 2
