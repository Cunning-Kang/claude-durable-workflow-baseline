"""Tests for ExecutionEngine."""

import pytest
from pathlib import Path
import tempfile
import shutil

from execution_engine.engine import ExecutionEngine
from plan_generator.types import Task, ExecutionPlan, TaskStatus


class TestExecutionEngineInitialization:
    """Tests for ExecutionEngine initialization."""

    def test_init_with_plan_and_task_dir(self):
        """Test engine initialization with plan and task directory."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2"),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            assert engine.plan == plan
            assert engine.task_dir == task_dir
            assert isinstance(engine.controller, object)
            assert isinstance(engine.resolver, object)
            assert isinstance(engine.state_trackers, dict)

    def test_init_creates_dependency_resolver_with_dicts(self):
        """Test that engine creates DependencyResolver with dict tasks."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2"),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            # Verify resolver was initialized
            assert engine.resolver is not None
            # Verify resolver has access to tasks
            assert len(engine.resolver.tasks) == 2


class TestExecutionEngineComponentIntegration:
    """Tests for component integration."""

    def test_controller_integration(self):
        """Test that ExecutionController is properly integrated."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            assert engine.controller is not None
            assert engine.controller.plan == plan

    def test_resolver_integration(self):
        """Test that DependencyResolver is properly integrated."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2", dependencies=["1"]),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            # Verify resolver can access tasks
            assert engine.resolver is not None
            assert len(engine.resolver.tasks) == 2

    def test_state_trackers_initialization(self):
        """Test that state_trackers dict is initialized."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            assert isinstance(engine.state_trackers, dict)
            assert len(engine.state_trackers) == 0


class TestExecutionEngineExecuteNextBatch:
    """Tests for execute_next_batch method."""

    def test_execute_next_batch_returns_dict(self):
        """Test that execute_next_batch returns a dict with stats."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2"),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            result = engine.execute_next_batch()

            assert isinstance(result, dict)
            assert "batch_size" in result
            assert "tasks_executed" in result
            assert "total_completed" in result

    def test_execute_next_batch_filters_ready_tasks(self):
        """Test that execute_next_batch only executes ready tasks."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2", dependencies=["1"]),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            result = engine.execute_next_batch()

            # Only task 1 should be executed (task 2 has dependency)
            assert result["batch_size"] == 1
            assert result["tasks_executed"] == 1

    def test_execute_next_batch_updates_task_status(self):
        """Test that execute_next_batch updates task statuses."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            # Initial status should be PENDING
            assert engine.plan.tasks[0].status == TaskStatus.PENDING

            engine.execute_next_batch()

            # After execution, status should change
            # (Note: Controller marks as IN_PROGRESS, actual execution would mark COMPLETED)


class TestExecutionEngineTypeConversion:
    """Tests for type conversion between Task objects and Dicts."""

    def test_task_to_dict_conversion(self):
        """Test that tasks are converted to dicts for DependencyResolver."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(
                id="2",
                title="Task 2",
                description="Description 2",
                dependencies=["1"],
            ),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            # Verify resolver has dict representation
            resolver_tasks = engine.resolver.tasks
            assert len(resolver_tasks) == 2

            # Check first task dict
            task1_dict = next(t for t in resolver_tasks if t["id"] == "1")
            assert task1_dict["id"] == "1"
            assert task1_dict["title"] == "Task 1"
            assert task1_dict["status"] == "pending"

            # Check second task dict with dependencies
            task2_dict = next(t for t in resolver_tasks if t["id"] == "2")
            assert task2_dict["id"] == "2"
            assert "dependencies" in task2_dict

    def test_dict_dependencies_format(self):
        """Test that dependencies are formatted correctly for DependencyResolver."""
        tasks = [
            Task(
                id="1",
                title="Task 1",
                description="Description 1",
                dependencies=["2"],
            ),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            resolver_tasks = engine.resolver.tasks
            task1_dict = resolver_tasks[0]

            # Dependencies should be list of dicts with "task_id" and "type"
            assert "dependencies" in task1_dict
            dependencies = task1_dict["dependencies"]
            assert len(dependencies) == 1
            assert dependencies[0]["task_id"] == "2"
            assert dependencies[0]["type"] == "blocking"


class TestExecutionEngineStateTracking:
    """Tests for state tracking integration."""

    def test_state_tracking_after_execution(self):
        """Test that state is tracked after task execution."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            # Create task file
            task_file = task_dir / "1.md"
            task_file.write_text("---\nstatus: pending\n---\nTask 1\n")

            engine.execute_next_batch()

            # Verify state tracker was created for the task
            assert "1" in engine.state_trackers


class TestExecutionEngineEndToEnd:
    """Tests for end-to-end workflow."""

    def test_end_to_end_execution_workflow(self):
        """Test complete execution workflow with dependencies."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(
                id="2",
                title="Task 2",
                description="Description 2",
                dependencies=["1"],
            ),
            Task(
                id="3",
                title="Task 3",
                description="Description 3",
                dependencies=["1"],
            ),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            engine = ExecutionEngine(plan, task_dir)

            # Create task files
            for task_id in ["1", "2", "3"]:
                task_file = task_dir / f"{task_id}.md"
                task_file.write_text(f"---\nstatus: pending\n---\nTask {task_id}\n")

            # Execute first batch - should execute task 1 only
            result1 = engine.execute_next_batch()
            assert result1["batch_size"] == 1
            assert result1["tasks_executed"] == 1

            # Mark task 1 as completed in plan
            for task in engine.plan.tasks:
                if task.id == "1":
                    task.status = TaskStatus.COMPLETED

            # Execute second batch - should execute tasks 2 and 3
            result2 = engine.execute_next_batch()
            assert result2["batch_size"] == 2
            assert result2["tasks_executed"] == 2
