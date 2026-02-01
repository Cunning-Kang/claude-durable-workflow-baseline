"""
Tests for DependencyResolver class.
Following TDD: RED → GREEN → REFACTOR
"""

import pytest
from execution_engine.dependency_resolver import DependencyResolver


class TestDependencyResolverInitialization:
    """Test resolver initialization with various task configurations."""

    def test_initialization_with_empty_list(self):
        """Test resolver initializes with empty task list."""
        resolver = DependencyResolver([])
        assert resolver.tasks == []

    def test_initialization_with_tasks(self):
        """Test resolver initializes with task list."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending", "dependencies": []}
        ]
        resolver = DependencyResolver(tasks)
        assert len(resolver.tasks) == 2
        assert resolver.tasks[0]["id"] == "TASK-001"


class TestGetReadyTasks:
    """Test getting ready tasks (dependencies satisfied)."""

    def test_get_ready_tasks_with_no_dependencies(self):
        """Test tasks with no dependencies are ready."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending", "dependencies": []}
        ]
        resolver = DependencyResolver(tasks)
        ready = resolver.get_ready_tasks()
        assert len(ready) == 2
        assert "TASK-001" in ready
        assert "TASK-002" in ready

    def test_get_ready_tasks_with_satisfied_dependencies(self):
        """Test tasks are ready when dependencies are completed."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "completed", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending",
             "dependencies": [{"task_id": "TASK-001", "type": "blocking"}]}
        ]
        resolver = DependencyResolver(tasks)
        ready = resolver.get_ready_tasks()
        assert len(ready) == 1
        assert "TASK-002" in ready

    def test_get_ready_tasks_with_unsatisfied_dependencies(self):
        """Test tasks are not ready when dependencies are pending."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending",
             "dependencies": [{"task_id": "TASK-001", "type": "blocking"}]}
        ]
        resolver = DependencyResolver(tasks)
        ready = resolver.get_ready_tasks()
        assert len(ready) == 1
        assert "TASK-001" in ready
        assert "TASK-002" not in ready


class TestBuildDependencyGraph:
    """Test building dependency graph structure."""

    def test_build_graph_simple_chain(self):
        """Test graph builds simple chain A→B→C."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending",
             "dependencies": [{"task_id": "TASK-001", "type": "blocking"}]},
            {"id": "TASK-003", "title": "Task C", "status": "pending",
             "dependencies": [{"task_id": "TASK-002", "type": "blocking"}]}
        ]
        resolver = DependencyResolver(tasks)
        graph = resolver._build_graph()
        assert graph == {
            "TASK-001": [],
            "TASK-002": ["TASK-001"],
            "TASK-003": ["TASK-002"]
        }

    def test_build_graph_complex_web(self):
        """Test graph builds complex dependency web."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending",
             "dependencies": [{"task_id": "TASK-001", "type": "blocking"}]},
            {"id": "TASK-003", "title": "Task C", "status": "pending",
             "dependencies": [{"task_id": "TASK-001", "type": "blocking"}]},
            {"id": "TASK-004", "title": "Task D", "status": "pending",
             "dependencies": [
                 {"task_id": "TASK-002", "type": "blocking"},
                 {"task_id": "TASK-003", "type": "blocking"}
             ]}
        ]
        resolver = DependencyResolver(tasks)
        graph = resolver._build_graph()
        assert graph == {
            "TASK-001": [],
            "TASK-002": ["TASK-001"],
            "TASK-003": ["TASK-001"],
            "TASK-004": ["TASK-002", "TASK-003"]
        }


class TestCycleDetection:
    """Test circular dependency detection."""

    def test_has_cycle_with_direct_cycle(self):
        """Test detection of direct cycle A→A."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending",
             "dependencies": [{"task_id": "TASK-001", "type": "blocking"}]}
        ]
        resolver = DependencyResolver(tasks)
        graph = resolver._build_graph()
        assert resolver._has_cycle(graph) is True

    def test_has_cycle_with_indirect_cycle(self):
        """Test detection of indirect cycle A→B→C→A."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending",
             "dependencies": [{"task_id": "TASK-002", "type": "blocking"}]},
            {"id": "TASK-002", "title": "Task B", "status": "pending",
             "dependencies": [{"task_id": "TASK-003", "type": "blocking"}]},
            {"id": "TASK-003", "title": "Task C", "status": "pending",
             "dependencies": [{"task_id": "TASK-001", "type": "blocking"}]}
        ]
        resolver = DependencyResolver(tasks)
        graph = resolver._build_graph()
        assert resolver._has_cycle(graph) is True

    def test_has_cycle_with_no_cycle(self):
        """Test no cycle detected in valid dependency chain."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending",
             "dependencies": [{"task_id": "TASK-001", "type": "blocking"}]},
            {"id": "TASK-003", "title": "Task C", "status": "pending",
             "dependencies": [{"task_id": "TASK-002", "type": "blocking"}]}
        ]
        resolver = DependencyResolver(tasks)
        graph = resolver._build_graph()
        assert resolver._has_cycle(graph) is False


class TestDependenciesSatisfied:
    """Test checking if dependencies are satisfied."""

    def test_dependencies_satisfied_all_completed(self):
        """Test returns True when all dependencies are completed."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "completed", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "completed", "dependencies": []},
            {"id": "TASK-003", "title": "Task C", "status": "pending",
             "dependencies": [
                 {"task_id": "TASK-001", "type": "blocking"},
                 {"task_id": "TASK-002", "type": "blocking"}
             ]}
        ]
        resolver = DependencyResolver(tasks)
        assert resolver.dependencies_satisfied("TASK-003") is True

    def test_dependencies_satisfied_some_pending(self):
        """Test returns False when some dependencies are pending."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "completed", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending", "dependencies": []},
            {"id": "TASK-003", "title": "Task C", "status": "pending",
             "dependencies": [
                 {"task_id": "TASK-001", "type": "blocking"},
                 {"task_id": "TASK-002", "type": "blocking"}
             ]}
        ]
        resolver = DependencyResolver(tasks)
        assert resolver.dependencies_satisfied("TASK-003") is False

    def test_dependencies_satisfied_no_dependencies(self):
        """Test returns True when task has no dependencies."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending", "dependencies": []}
        ]
        resolver = DependencyResolver(tasks)
        assert resolver.dependencies_satisfied("TASK-001") is True


class TestBlockingVsNonBlocking:
    """Test blocking vs non-blocking dependencies."""

    def test_blocking_dependencies_required(self):
        """Test blocking dependencies prevent task execution."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending",
             "dependencies": [{"task_id": "TASK-001", "type": "blocking"}]}
        ]
        resolver = DependencyResolver(tasks)
        ready = resolver.get_ready_tasks()
        assert "TASK-002" not in ready

    def test_non_blocking_dependencies_optional(self):
        """Test non-blocking dependencies don't prevent execution."""
        tasks = [
            {"id": "TASK-001", "title": "Task A", "status": "pending", "dependencies": []},
            {"id": "TASK-002", "title": "Task B", "status": "pending",
             "dependencies": [{"task_id": "TASK-001", "type": "non-blocking"}]}
        ]
        resolver = DependencyResolver(tasks)
        ready = resolver.get_ready_tasks()
        assert "TASK-002" in ready
