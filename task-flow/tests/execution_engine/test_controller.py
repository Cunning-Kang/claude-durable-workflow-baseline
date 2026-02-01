"""Tests for ExecutionController."""

import pytest
from execution_engine.controller import ExecutionController
from plan_generator.types import Task, ExecutionPlan, TaskStatus


class TestExecutionControllerInitialization:
    """Tests for ExecutionController initialization."""

    def test_init_with_plan(self):
        """Test controller initialization with a valid plan."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2"),
        ]
        plan = ExecutionPlan(tasks=tasks)

        controller = ExecutionController(plan)

        assert controller.plan == plan
        assert controller.batch_size == 3
        assert controller.checkpoint_interval == 3
        assert controller.auto_continue is False
        assert controller.executed_count == 0
        assert controller.last_checkpoint_at == 0

    def test_init_with_custom_batch_size(self):
        """Test controller initialization with custom batch size."""
        tasks = [Task(id="1", title="Task 1", description="Description 1")]
        plan = ExecutionPlan(tasks=tasks)

        controller = ExecutionController(plan, batch_size=5)

        assert controller.batch_size == 5

    def test_init_with_custom_checkpoint_interval(self):
        """Test controller initialization with custom checkpoint interval."""
        tasks = [Task(id="1", title="Task 1", description="Description 1")]
        plan = ExecutionPlan(tasks=tasks)

        controller = ExecutionController(plan, checkpoint_interval=5)

        assert controller.checkpoint_interval == 5

    def test_init_with_auto_continue(self):
        """Test controller initialization with auto_continue mode."""
        tasks = [Task(id="1", title="Task 1", description="Description 1")]
        plan = ExecutionPlan(tasks=tasks)

        controller = ExecutionController(plan, auto_continue=True)

        assert controller.auto_continue is True


class TestBatchExecution:
    """Tests for batch execution functionality."""

    def test_get_next_batch_default_size(self):
        """Test getting next batch with default batch size."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 6)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3)

        batch = controller._get_next_batch(3)

        assert len(batch) == 3
        assert batch[0].id == "1"
        assert batch[1].id == "2"
        assert batch[2].id == "3"
        assert all(task.status == TaskStatus.IN_PROGRESS for task in batch)

    def test_get_next_batch_partial(self):
        """Test getting next batch when remaining tasks < batch size."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 6)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3)

        # Mark first 3 as in_progress
        for task in plan.tasks[:3]:
            task.status = TaskStatus.IN_PROGRESS

        batch = controller._get_next_batch(3)

        assert len(batch) == 2
        assert batch[0].id == "4"
        assert batch[1].id == "5"

    def test_get_next_batch_empty(self):
        """Test getting next batch when all tasks are completed."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 4)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3)

        # Mark all as completed
        for task in plan.tasks:
            task.status = TaskStatus.COMPLETED

        batch = controller._get_next_batch(3)

        assert len(batch) == 0

    def test_execute_batch_returns_stats(self):
        """Test execute_batch returns execution statistics."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2"),
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=2)

        result = controller.execute_batch()

        assert "batch_size" in result
        assert "tasks_executed" in result
        assert "total_completed" in result
        assert result["batch_size"] == 2
        assert result["tasks_executed"] == 2
        assert result["total_completed"] == 2  # Tasks are now executed

    def test_multi_batch_execution(self):
        """Test execution across multiple batches."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 8)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3)

        # First batch
        batch1 = controller._get_next_batch(3)
        assert len(batch1) == 3

        # Mark them as completed
        for task in batch1:
            task.status = TaskStatus.COMPLETED

        # Second batch
        batch2 = controller._get_next_batch(3)
        assert len(batch2) == 3

        # Mark them as completed
        for task in batch2:
            task.status = TaskStatus.COMPLETED

        # Third batch (partial)
        batch3 = controller._get_next_batch(3)
        assert len(batch3) == 1

    def test_single_task_execution(self):
        """Test execution with a single task."""
        tasks = [Task(id="1", title="Task 1", description="Description 1")]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3)

        batch = controller._get_next_batch(3)

        assert len(batch) == 1
        assert batch[0].id == "1"


class TestHumanReviewCheckpoints:
    """Tests for human review checkpoint functionality."""

    def test_requires_human_review_at_checkpoint(self):
        """Test that human review is required at checkpoint intervals."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 10)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, checkpoint_interval=3)

        # Execute 3 tasks
        controller.executed_count = 3
        controller._update_checkpoint_state()

        assert controller.requires_human_review() is True

    def test_requires_human_review_false_before_checkpoint(self):
        """Test that human review is not required before checkpoint."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 10)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, checkpoint_interval=3)

        # Execute only 2 tasks
        controller.executed_count = 2
        controller._update_checkpoint_state()

        assert controller.requires_human_review() is False

    def test_checkpoint_interval_configuration(self):
        """Test custom checkpoint interval."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 20)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, checkpoint_interval=5)

        # Execute 5 tasks
        controller.executed_count = 5
        controller._update_checkpoint_state()

        assert controller.requires_human_review() is True

    def test_auto_continue_skips_human_review(self):
        """Test that auto_continue mode skips human review."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 10)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, checkpoint_interval=3, auto_continue=True)

        # Execute 3 tasks (normally would require review)
        controller.executed_count = 3
        controller._update_checkpoint_state()

        assert controller.requires_human_review() is False


class TestStateTracking:
    """Tests for state tracking updates."""

    def test_update_checkpoint_state(self):
        """Test that checkpoint state is updated correctly."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 10)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, checkpoint_interval=3)

        controller.executed_count = 3
        controller._update_checkpoint_state()

        assert controller.last_checkpoint_at == 3

    def test_state_tracking_update_on_batch_execution(self):
        """Test that state is tracked during batch execution."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 6)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=2, checkpoint_interval=2)

        # Execute first batch
        controller.execute_batch()

        # State is now automatically tracked
        assert controller.executed_count == 2
        assert controller.last_checkpoint_at == 2


class TestExecutionLogic:
    """Tests for actual task execution logic."""

    def test_execute_batch_transitions_task_states(self):
        """Test that execute_batch transitions tasks from IN_PROGRESS to COMPLETED."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2"),
            Task(id="3", title="Task 3", description="Description 3"),
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3)

        result = controller.execute_batch()

        # Verify tasks transitioned to COMPLETED
        assert all(task.status == TaskStatus.COMPLETED for task in tasks)
        assert result["batch_size"] == 3
        assert result["tasks_executed"] == 3
        assert result["total_completed"] == 3

    def test_execute_batch_updates_executed_count(self):
        """Test that execute_batch updates the executed_count tracker."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 4)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3)

        assert controller.executed_count == 0

        controller.execute_batch()

        assert controller.executed_count == 3

    def test_execute_batch_calls_update_checkpoint_state(self):
        """Test that execute_batch calls _update_checkpoint_state."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 4)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3, checkpoint_interval=3)

        controller.execute_batch()

        # Should have updated checkpoint state
        assert controller.last_checkpoint_at == 3
        assert controller._waiting_for_review is True

    def test_execute_batch_multiple_batches(self):
        """Test executing multiple batches sequentially."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 10)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3, checkpoint_interval=3)

        # First batch
        result1 = controller.execute_batch()
        assert result1["batch_size"] == 3
        assert result1["total_completed"] == 3
        assert controller.executed_count == 3
        assert controller.requires_human_review() is True

        # Reset review flag to continue
        controller._waiting_for_review = False

        # Second batch
        result2 = controller.execute_batch()
        assert result2["batch_size"] == 3
        assert result2["total_completed"] == 6
        assert controller.executed_count == 6

    def test_execute_batch_respects_checkpoint_interval(self):
        """Test that checkpoints are triggered at correct intervals."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 10)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=2, checkpoint_interval=4)

        # First batch (2 tasks)
        controller.execute_batch()
        assert controller.requires_human_review() is False

        # Second batch (2 more tasks = 4 total)
        controller.execute_batch()
        assert controller.requires_human_review() is True
        assert controller.last_checkpoint_at == 4

    def test_execute_batch_with_partial_batch(self):
        """Test execution when remaining tasks < batch_size."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 5)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3)

        # First batch (3 tasks)
        result1 = controller.execute_batch()
        assert result1["batch_size"] == 3

        # Second batch (1 task)
        result2 = controller.execute_batch()
        assert result2["batch_size"] == 1
        assert result2["total_completed"] == 4

    def test_execute_batch_idempotent(self):
        """Test that calling execute_batch with no pending tasks is safe."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3)

        # Execute all tasks
        result1 = controller.execute_batch()
        assert result1["batch_size"] == 1

        # Call again with no pending tasks
        result2 = controller.execute_batch()
        assert result2["batch_size"] == 0
        assert result2["tasks_executed"] == 0
        assert result2["total_completed"] == 1

    def test_execute_batch_returns_detailed_stats(self):
        """Test that execute_batch returns detailed execution statistics."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 4)
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=3)

        result = controller.execute_batch()

        # Verify all expected fields
        assert "batch_size" in result
        assert "tasks_executed" in result
        assert "total_completed" in result
        assert result["batch_size"] == 3
        assert result["tasks_executed"] == 3
        assert result["total_completed"] == 3


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_plan_handling(self):
        """Test controller behavior with empty plan."""
        plan = ExecutionPlan(tasks=[])
        controller = ExecutionController(plan)

        batch = controller._get_next_batch(3)

        assert len(batch) == 0

    def test_error_handling_in_batch_execution(self):
        """Test that batch execution handles errors gracefully."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1"),
            Task(id="2", title="Task 2", description="Description 2"),
        ]
        plan = ExecutionPlan(tasks=tasks)
        controller = ExecutionController(plan, batch_size=2)

        # This should not raise an exception even with no actual executor
        result = controller.execute_batch()

        assert result is not None
        assert "batch_size" in result
