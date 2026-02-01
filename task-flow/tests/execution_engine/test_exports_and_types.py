"""Tests for execution engine exports and type conversion (Task 12)."""

import pytest
from plan_generator.types import Task, ExecutionPlan, TaskStatus
from execution_engine import (
    StateTracker,
    ExecutionController,
    DependencyResolver,
    TaskDispatcher,
    TaskExecutor,
    SubagentPool,
    SubagentResult,
    ExecutionEngine,
    ExecutorResult
)


class TestModuleExports:
    """Test that all components are properly exported."""

    def test_state_tracker_is_exported(self):
        """Test StateTracker can be imported from execution_engine."""
        from execution_engine import StateTracker as ImportedStateTracker
        assert ImportedStateTracker is StateTracker

    def test_execution_controller_is_exported(self):
        """Test ExecutionController can be imported from execution_engine."""
        from execution_engine import (
            ExecutionController as ImportedExecutionController
        )
        assert ImportedExecutionController is ExecutionController

    def test_dependency_resolver_is_exported(self):
        """Test DependencyResolver can be imported from execution_engine."""
        from execution_engine import (
            DependencyResolver as ImportedDependencyResolver
        )
        assert ImportedDependencyResolver is DependencyResolver

    def test_task_dispatcher_is_exported(self):
        """Test TaskDispatcher can be imported from execution_engine."""
        from execution_engine import TaskDispatcher as ImportedTaskDispatcher
        assert ImportedTaskDispatcher is TaskDispatcher

    def test_subagent_pool_is_exported(self):
        """Test SubagentPool can be imported from execution_engine."""
        from execution_engine import SubagentPool as ImportedSubagentPool
        assert ImportedSubagentPool is SubagentPool

    def test_execution_engine_is_exported(self):
        """Test ExecutionEngine can be imported from execution_engine."""
        from execution_engine import ExecutionEngine as ImportedExecutionEngine
        assert ImportedExecutionEngine is ExecutionEngine

    def test_task_executor_is_exported(self):
        """Test TaskExecutor can be imported from execution_engine."""
        from execution_engine import TaskExecutor as ImportedTaskExecutor
        assert ImportedTaskExecutor is TaskExecutor

    def test_subagent_result_is_exported(self):
        """Test SubagentResult can be imported from execution_engine."""
        from execution_engine import SubagentResult as ImportedSubagentResult
        assert ImportedSubagentResult is SubagentResult

    def test_executor_result_is_exported(self):
        """Test ExecutorResult can be imported from execution_engine."""
        from execution_engine import ExecutorResult as ImportedExecutorResult
        assert ImportedExecutorResult is ExecutorResult

    def test_all_exports_in___all__(self):
        """Test all exported components are listed in __all__."""
        import execution_engine
        expected_exports = [
            "StateTracker",
            "ExecutionController",
            "DependencyResolver",
            "TaskDispatcher",
            "TaskExecutor",
            "SubagentPool",
            "SubagentResult",
            "ExecutionEngine",
            "ExecutorResult"
        ]
        assert set(execution_engine.__all__) == set(expected_exports)

    def test_can_import_all_components_simultaneously(self):
        """Test all components can be imported together without conflicts."""
        from execution_engine import (
            StateTracker,
            ExecutionController,
            DependencyResolver,
            TaskDispatcher,
            TaskExecutor,
            SubagentPool,
            SubagentResult,
            ExecutionEngine,
            ExecutorResult
        )
        # If we get here without ImportError, the test passes
        assert StateTracker is not None
        assert ExecutionController is not None
        assert DependencyResolver is not None
        assert TaskDispatcher is not None
        assert TaskExecutor is not None
        assert SubagentPool is not None
        assert SubagentResult is not None
        assert ExecutionEngine is not None
        assert ExecutorResult is not None


class TestTaskToDictConversion:
    """Test task_to_dict conversion method."""

    def test_task_to_dict_basic_conversion(self):
        """Test converting a basic task to dict format."""
        task = Task(
            id="TASK-001",
            title="Test Task",
            description="A test task"
        )

        result = DependencyResolver.task_to_dict(task)

        assert result["id"] == "TASK-001"
        assert result["title"] == "Test Task"
        assert result["status"] == "pending"
        assert result["dependencies"] == []

    def test_task_to_dict_with_custom_status(self):
        """Test converting task with custom status."""
        task = Task(
            id="TASK-001",
            title="Test Task",
            description="A test task",
            status=TaskStatus.IN_PROGRESS
        )

        result = DependencyResolver.task_to_dict(task)

        assert result["status"] == "in_progress"

    def test_task_to_dict_with_dependencies(self):
        """Test converting task with dependencies."""
        task = Task(
            id="TASK-003",
            title="Dependent Task",
            description="Task with dependencies",
            dependencies=["TASK-001", "TASK-002"]
        )

        result = DependencyResolver.task_to_dict(task)

        assert len(result["dependencies"]) == 2
        assert result["dependencies"][0] == {"task_id": "TASK-001", "type": "blocking"}
        assert result["dependencies"][1] == {"task_id": "TASK-002", "type": "blocking"}

    def test_task_to_dict_with_metadata(self):
        """Test that metadata field is preserved (optional field)."""
        task = Task(
            id="TASK-001",
            title="Test Task",
            description="A test task",
            metadata={"key": "value"}
        )

        result = DependencyResolver.task_to_dict(task)

        # Metadata is not part of DependencyResolver's expected format
        # so it should not be in the result
        assert "metadata" not in result

    def test_task_to_dict_all_status_types(self):
        """Test converting tasks with all possible status types."""
        statuses = [
            TaskStatus.PENDING,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.SKIPPED
        ]

        expected_values = [
            "pending",
            "in_progress",
            "completed",
            "failed",
            "skipped"
        ]

        for status, expected in zip(statuses, expected_values):
            task = Task(
                id="TASK-001",
                title="Test Task",
                description="A test task",
                status=status
            )

            result = DependencyResolver.task_to_dict(task)
            assert result["status"] == expected


class TestDependencyResolverWithTaskObjects:
    """Test DependencyResolver can work with converted Task objects."""

    def test_resolver_with_converted_tasks(self):
        """Test DependencyResolver initialization with converted tasks."""
        tasks = [
            Task(
                id="TASK-001",
                title="Task A",
                description="First task",
                status=TaskStatus.PENDING
            ),
            Task(
                id="TASK-002",
                title="Task B",
                description="Second task",
                status=TaskStatus.PENDING,
                dependencies=["TASK-001"]
            )
        ]

        # Convert tasks to dicts
        task_dicts = [DependencyResolver.task_to_dict(t) for t in tasks]

        # Initialize resolver
        resolver = DependencyResolver(task_dicts)

        # Verify resolver works correctly
        ready = resolver.get_ready_tasks()
        assert "TASK-001" in ready
        assert "TASK-002" not in ready

    def test_resolver_dependencies_satisfied_after_conversion(self):
        """Test dependencies_satisfied works with converted tasks."""
        tasks = [
            Task(
                id="TASK-001",
                title="Task A",
                description="First task",
                status=TaskStatus.COMPLETED
            ),
            Task(
                id="TASK-002",
                title="Task B",
                description="Second task",
                status=TaskStatus.PENDING,
                dependencies=["TASK-001"]
            )
        ]

        task_dicts = [DependencyResolver.task_to_dict(t) for t in tasks]
        resolver = DependencyResolver(task_dicts)

        assert resolver.dependencies_satisfied("TASK-002") is True

    def test_resolver_complex_dependency_chain(self):
        """Test resolver with complex dependency chain from Task objects."""
        tasks = [
            Task(
                id="TASK-001",
                title="Foundation",
                description="Base task",
                status=TaskStatus.COMPLETED
            ),
            Task(
                id="TASK-002",
                title="Middle A",
                description="Middle task A",
                status=TaskStatus.PENDING,
                dependencies=["TASK-001"]
            ),
            Task(
                id="TASK-003",
                title="Middle B",
                description="Middle task B",
                status=TaskStatus.PENDING,
                dependencies=["TASK-001"]
            ),
            Task(
                id="TASK-004",
                title="Final",
                description="Final task",
                status=TaskStatus.PENDING,
                dependencies=["TASK-002", "TASK-003"]
            )
        ]

        task_dicts = [DependencyResolver.task_to_dict(t) for t in tasks]
        resolver = DependencyResolver(task_dicts)

        ready = resolver.get_ready_tasks()
        assert "TASK-002" in ready
        assert "TASK-003" in ready
        assert "TASK-004" not in ready


class TestExecutionControllerIntegration:
    """Test ExecutionController works with the type system."""

    def test_controller_with_task_objects(self):
        """Test ExecutionController can work with Task objects directly."""
        tasks = [
            Task(id=str(i), title=f"Task {i}", description=f"Description {i}")
            for i in range(1, 6)
        ]
        plan = ExecutionPlan(tasks=tasks)

        controller = ExecutionController(plan, batch_size=3)

        batch = controller._get_next_batch(3)
        assert len(batch) == 3

    def test_controller_and_resolver_compatibility(self):
        """Test ExecutionController and DependencyResolver can share task data."""
        tasks = [
            Task(
                id="TASK-001",
                title="Task A",
                description="First task"
            ),
            Task(
                id="TASK-002",
                title="Task B",
                description="Second task",
                dependencies=["TASK-001"]
            )
        ]
        plan = ExecutionPlan(tasks=tasks)

        # Controller uses Task objects directly
        controller = ExecutionController(plan)
        assert len(controller.plan.tasks) == 2

        # Resolver uses dict format (converted)
        task_dicts = [DependencyResolver.task_to_dict(t) for t in tasks]
        resolver = DependencyResolver(task_dicts)
        assert len(resolver.tasks) == 2

        # Both should work with the same data
        ready = resolver.get_ready_tasks()
        assert "TASK-001" in ready
        assert "TASK-002" not in ready


class TestTypeSystemUnification:
    """Test that the type system is unified across components."""

    def test_task_id_consistency(self):
        """Test Task IDs are preserved through conversion."""
        task = Task(id="CUSTOM-ID-123", title="Test", description="Test")
        task_dict = DependencyResolver.task_to_dict(task)

        assert task_dict["id"] == task.id
        assert task.id == "CUSTOM-ID-123"

    def test_status_value_consistency(self):
        """Test status values are consistent across components."""
        task = Task(
            id="TASK-001",
            title="Test",
            description="Test",
            status=TaskStatus.COMPLETED
        )

        task_dict = DependencyResolver.task_to_dict(task)

        # Status should be string value in dict
        assert task_dict["status"] == "completed"

        # But enum in original task
        assert task.status == TaskStatus.COMPLETED

    def test_dependencies_format_consistency(self):
        """Test dependencies format is consistent across components."""
        task = Task(
            id="TASK-003",
            title="Test",
            description="Test",
            dependencies=["TASK-001", "TASK-002"]
        )

        task_dict = DependencyResolver.task_to_dict(task)

        # Dependencies should be in dict format
        assert all(isinstance(dep, dict) for dep in task_dict["dependencies"])
        assert all("task_id" in dep and "type" in dep for dep in task_dict["dependencies"])

    def test_roundtrip_consistency(self):
        """Test data is consistent through Task -> dict -> resolver workflow."""
        original_tasks = [
            Task(
                id="TASK-001",
                title="Original A",
                description="Description A",
                status=TaskStatus.PENDING
            ),
            Task(
                id="TASK-002",
                title="Original B",
                description="Description B",
                status=TaskStatus.PENDING,
                dependencies=["TASK-001"]
            )
        ]

        # Convert to dicts
        task_dicts = [DependencyResolver.task_to_dict(t) for t in original_tasks]

        # Create resolver
        resolver = DependencyResolver(task_dicts)

        # Verify data integrity
        assert resolver.tasks[0]["id"] == original_tasks[0].id
        assert resolver.tasks[0]["title"] == original_tasks[0].title
        assert resolver.tasks[1]["dependencies"][0]["task_id"] == "TASK-001"


class TestBackwardCompatibility:
    """Test that existing tests still work with new exports."""

    def test_existing_import_patterns_still_work(self):
        """Test existing import patterns from tests still work."""
        # These import patterns are used in existing tests
        from execution_engine.controller import ExecutionController
        from execution_engine.dependency_resolver import DependencyResolver
        from execution_engine.state_tracker import StateTracker

        assert ExecutionController is not None
        assert DependencyResolver is not None
        assert StateTracker is not None

    def test_direct_dict_initialization_still_works(self):
        """Test DependencyResolver can still be initialized with dicts directly."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending", "dependencies": []}
        ]

        resolver = DependencyResolver(tasks)

        assert len(resolver.tasks) == 2
        assert resolver.tasks[0]["id"] == "TASK-001"
