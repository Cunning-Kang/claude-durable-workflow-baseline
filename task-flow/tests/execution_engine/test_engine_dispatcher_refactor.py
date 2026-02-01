"""Tests for ExecutionEngine dispatcher refactor - TDD RED phase.

This test suite validates three important refactors:
A) execution_state.execution_status as canonical (vs status) - tracks execution flow states
B) Replace private method mocks with frontmatter verification
C) Explicit validation for required callbacks (no silent no-op defaults)
"""

import pytest
from pathlib import Path
import tempfile
import yaml
from unittest.mock import patch

from execution_engine.engine import ExecutionEngine, SubagentPoolExecutor
from plan_generator.types import Task, ExecutionPlan, TaskStatus


class TestExecutionStatusCanonical:
    """Tests for A) execution_state.execution_status as canonical field.

    execution_state.execution_status should track execution flow states:
    - "running" when task is executing
    - "completed" when task completes successfully
    - "failed" when task execution fails

    execution_state.status is kept as compatibility alias, always in sync.
    execution_state.task_status tracks in-memory TaskStatus enum values.
    """

    def test_execution_status_field_exists_and_synced(self):
        """Test that execution_status is the canonical field for execution flow.

        After task execution, frontmatter should have:
        - execution_state.execution_status = canonical execution flow state
        - execution_state.status = compatibility alias (same value)
        - execution_state.task_status = in-memory TaskStatus enum value
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
            engine.execute_next_batch()

            # Read frontmatter
            content = task_file.read_text()
            parts = content.split("---")
            data = yaml.safe_load(parts[1])

            # After refactor: execution_status should exist
            assert "execution_state" in data, "execution_state should exist"
            execution_state = data["execution_state"]
            assert "execution_status" in execution_state, \
                "execution_state.execution_status should exist (canonical field)"

            # After refactor: status should exist as compatibility alias
            assert "status" in execution_state, \
                "execution_state.status should exist as compatibility alias"

            # After refactor: status and execution_status should be synced
            assert execution_state["execution_status"] == execution_state["status"], \
                f"execution_status and status should be synced: execution_status={execution_state['execution_status']}, status={execution_state['status']}"

            # After refactor: task_status should also exist
            assert "task_status" in execution_state, \
                "execution_state.task_status should exist"

    def test_execution_status_running_on_task_start(self):
        """Test that execution_status is 'running' when task starts."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1", metadata={"callable": lambda: "ok"}),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            task_file = task_dir / "1.md"
            task_file.write_text("---\nstatus: pending\n---\nTask 1\n")

            engine = ExecutionEngine(plan, task_dir)

            # Mock SubagentPool to delay execution so we can check "running" state
            from execution_engine.subagent_pool.pool import SubagentPool

            call_log = []

            def delayed_submit(self, task_id, fn):
                call_log.append(("submit", task_id))
                # Check state immediately after on_start callback but before return
                content = task_file.read_text()
                parts = content.split("---")
                data = yaml.safe_load(parts[1])
                execution_state = data.get("execution_state", {})
                call_log.append(("state_during_start", execution_state.get("execution_status")))
                # Call original submit with correct signature
                from unittest.mock import MagicMock
                mock_result = MagicMock()
                mock_result.ok = True
                return mock_result

            with patch.object(SubagentPool, "submit", delayed_submit):
                engine.execute_next_batch()

            # Verify execution_status was set to "running" during execution
            state_entries = [log for log in call_log if log[0] == "state_during_start"]
            assert any(entry[1] == "running" for entry in state_entries), \
                "execution_status should be 'running' when task starts"

    def test_execution_status_completed_on_success(self):
        """Test that execution_status is 'completed' on successful task."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1", metadata={"callable": lambda: "ok"}),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            task_file = task_dir / "1.md"
            task_file.write_text("---\nstatus: pending\n---\nTask 1\n")

            engine = ExecutionEngine(plan, task_dir)
            engine.execute_next_batch()

            # Read frontmatter
            content = task_file.read_text()
            parts = content.split("---")
            data = yaml.safe_load(parts[1])
            execution_state = data["execution_state"]

            # After refactor: execution_status should be "completed"
            assert execution_state["execution_status"] == "completed", \
                f"execution_status should be 'completed' on success, got {execution_state['execution_status']}"

            # Verify status alias is also "completed"
            assert execution_state["status"] == "completed", \
                "status alias should also be 'completed'"

    def test_execution_status_failed_on_failure(self):
        """Test that execution_status is 'failed' when task fails."""
        tasks = [
            Task(id="1", title="Task 1", description="Description 1", metadata={"callable": lambda: (_ for _ in ()).throw(Exception("Simulated failure"))}),
        ]
        plan = ExecutionPlan(tasks=tasks)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_dir = Path(tmpdir)
            task_file = task_dir / "1.md"
            task_file.write_text("---\nstatus: pending\n---\nTask 1\n")

            engine = ExecutionEngine(plan, task_dir)
            engine.execute_next_batch()

            # Read frontmatter
            content = task_file.read_text()
            parts = content.split("---")
            data = yaml.safe_load(parts[1])
            execution_state = data["execution_state"]

            # After refactor: execution_status should be "failed"
            assert execution_state["execution_status"] == "failed", \
                f"execution_status should be 'failed' on failure, got {execution_state['execution_status']}"

            # Verify status alias is also "failed"
            assert execution_state["status"] == "failed", \
                "status alias should also be 'failed'"

            # Verify error was recorded
            assert "error" in execution_state, \
                "error should be recorded in execution_state"


class TestFrontmatterVerification:
    """Tests for B) Verify observable behavior (frontmatter) instead of mocking private methods.

    Tests should verify frontmatter content directly rather than patching
    private methods like _create_dispatcher, _on_task_start, etc.
    """

    def test_verify_dispatcher_reuse_via_frontmatter(self):
        """Test dispatcher reuse by checking frontmatter state (not private method patches).

        Instead of patching _create_dispatcher, verify that:
        - Tasks execute correctly
        - State persists correctly
        - Frontmatter is updated appropriately
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

            # Execute first batch
            result1 = engine.execute_next_batch()
            assert result1["batch_size"] == 1

            # Verify task 1 state via frontmatter (not mocking)
            task1_file = task_dir / "1.md"
            content = task1_file.read_text()
            parts = content.split("---")
            data = yaml.safe_load(parts[1])
            execution_state = data.get("execution_state", {})
            assert "execution_status" in execution_state, \
                "Task 1 should have execution_status in frontmatter"

            # Mark task 1 as completed (simulate successful execution)
            for task in engine.plan.tasks:
                if task.id == "1":
                    task.status = TaskStatus.COMPLETED

            # Execute second batch
            result2 = engine.execute_next_batch()
            assert result2["batch_size"] == 2

            # Verify tasks 2 and 3 have execution_status in frontmatter
            for task_id in ["2", "3"]:
                task_file = task_dir / f"{task_id}.md"
                content = task_file.read_text()
                parts = content.split("---")
                data = yaml.safe_load(parts[1])
                execution_state = data.get("execution_state", {})
                # Tasks should have been executed
                assert "execution_status" in execution_state, \
                    f"Task {task_id} should have execution_status in frontmatter"

    def test_verify_callbacks_via_frontmatter(self):
        """Test callbacks work correctly by checking frontmatter changes.

        Instead of mocking _on_task_start, _on_task_success, _on_task_fail,
        verify that frontmatter reflects the expected state after callbacks.
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

            # Verify callbacks worked by checking frontmatter state
            content = task_file.read_text()
            parts = content.split("---")
            data = yaml.safe_load(parts[1])
            execution_state = data.get("execution_state", {})

            # on_start callback should have set these fields
            assert "started_at" in execution_state, \
                "on_start callback should have set started_at"
            assert "task_id" in execution_state, \
                "on_start callback should have set task_id"
            assert "task_title" in execution_state, \
                "on_start callback should have set task_title"

            # on_success callback should have set these fields
            assert "execution_status" in execution_state, \
                "on_success callback should have set execution_status"
            assert execution_state["execution_status"] in ["running", "completed"], \
                f"execution_status should be 'running' or 'completed', got {execution_state.get('execution_status')}"


class TestRequiredCallbacks:
    """Tests for C) Explicit validation for required callbacks.

    SubagentPoolExecutor should require callbacks and error if missing.
    No silent no-op defaults.
    """

    def test_subagent_pool_executor_requires_on_start_callback(self):
        """Test that SubagentPoolExecutor raises error if on_start is None.

        After refactor: callbacks should be required, no no-op defaults.
        """
        from execution_engine.subagent_pool.pool import SubagentPool

        subagent_pool = SubagentPool()

        # After refactor: should raise error when on_start is None
        with pytest.raises(ValueError, match="on_start.*required"):
            executor = SubagentPoolExecutor(
                subagent_pool=subagent_pool,
                task_metadata_getter=lambda t: t.metadata,
                on_start=None,  # Should error
                on_success=lambda task_id, result: None,
                on_fail=lambda task_id, error: None,
            )

    def test_subagent_pool_executor_requires_on_success_callback(self):
        """Test that SubagentPoolExecutor raises error if on_success is None."""
        from execution_engine.subagent_pool.pool import SubagentPool

        subagent_pool = SubagentPool()

        # After refactor: should raise error when on_success is None
        with pytest.raises(ValueError, match="on_success.*required"):
            executor = SubagentPoolExecutor(
                subagent_pool=subagent_pool,
                task_metadata_getter=lambda t: t.metadata,
                on_start=lambda task_id, task: None,
                on_success=None,  # Should error
                on_fail=lambda task_id, error: None,
            )

    def test_subagent_pool_executor_requires_on_fail_callback(self):
        """Test that SubagentPoolExecutor raises error if on_fail is None."""
        from execution_engine.subagent_pool.pool import SubagentPool

        subagent_pool = SubagentPool()

        # After refactor: should raise error when on_fail is None
        with pytest.raises(ValueError, match="on_fail.*required"):
            executor = SubagentPoolExecutor(
                subagent_pool=subagent_pool,
                task_metadata_getter=lambda t: t.metadata,
                on_start=lambda task_id, task: None,
                on_success=lambda task_id, result: None,
                on_fail=None,  # Should error
            )

    def test_subagent_pool_executor_accepts_all_required_callbacks(self):
        """Test that SubagentPoolExecutor works when all callbacks are provided."""
        from execution_engine.subagent_pool.pool import SubagentPool

        subagent_pool = SubagentPool()

        # Should work when all callbacks are provided
        executor = SubagentPoolExecutor(
            subagent_pool=subagent_pool,
            task_metadata_getter=lambda t: t.metadata,
            on_start=lambda task_id, task: None,
            on_success=lambda task_id, result: None,
            on_fail=lambda task_id, error: None,
        )

        assert executor is not None
        assert callable(executor.on_start)
        assert callable(executor.on_success)
        assert callable(executor.on_fail)
