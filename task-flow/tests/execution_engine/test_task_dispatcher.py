"""Tests for TaskDispatcher.

TDD: RED  write tests first.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

import pytest

from plan_generator.types import ExecutionPlan, Task, TaskStatus


@dataclass
class FakeExecutionResult:
    task_id: str
    status: TaskStatus


class FakeExecutor:
    def __init__(self):
        self.executed: List[str] = []
        self.fail_for: set[str] = set()

    def run(self, task: Task) -> FakeExecutionResult:
        self.executed.append(task.id)
        if task.id in self.fail_for:
            return FakeExecutionResult(task_id=task.id, status=TaskStatus.FAILED)
        return FakeExecutionResult(task_id=task.id, status=TaskStatus.COMPLETED)


class TestTaskDispatcher:
    def test_dispatch_ready_tasks_respects_batch_size(self, tmp_path):
        """Should dispatch at most batch_size ready tasks."""
        tasks = [
            Task(id="1", title="t1", description="d1"),
            Task(id="2", title="t2", description="d2"),
            Task(id="3", title="t3", description="d3"),
        ]
        plan = ExecutionPlan(tasks=tasks)
        executor = FakeExecutor()

        from execution_engine.task_dispatcher import TaskDispatcher

        dispatcher = TaskDispatcher(plan=plan, task_dir=tmp_path, executor=executor)
        result = dispatcher.dispatch_next_batch(batch_size=2, ready_task_ids=["1", "2", "3"])

        assert result["tasks_dispatched"] == 2
        assert executor.executed == ["1", "2"]

    def test_dispatch_skips_non_ready_tasks(self, tmp_path):
        """Should only dispatch tasks whose IDs are in ready_task_ids."""
        tasks = [
            Task(id="1", title="t1", description="d1"),
            Task(id="2", title="t2", description="d2"),
        ]
        plan = ExecutionPlan(tasks=tasks)
        executor = FakeExecutor()

        from execution_engine.task_dispatcher import TaskDispatcher

        dispatcher = TaskDispatcher(plan=plan, task_dir=tmp_path, executor=executor)
        dispatcher.dispatch_next_batch(batch_size=3, ready_task_ids=["2"])

        assert executor.executed == ["2"]

    def test_dispatch_updates_task_status_completed(self, tmp_path):
        """When executor returns COMPLETED, task status should become COMPLETED."""
        task = Task(id="1", title="t1", description="d1")
        plan = ExecutionPlan(tasks=[task])
        executor = FakeExecutor()

        from execution_engine.task_dispatcher import TaskDispatcher

        dispatcher = TaskDispatcher(plan=plan, task_dir=tmp_path, executor=executor)
        dispatcher.dispatch_next_batch(batch_size=1, ready_task_ids=["1"])

        assert task.status == TaskStatus.COMPLETED

    def test_dispatch_updates_task_status_failed(self, tmp_path):
        """When executor returns FAILED, task status should become FAILED."""
        task = Task(id="1", title="t1", description="d1")
        plan = ExecutionPlan(tasks=[task])
        executor = FakeExecutor()
        executor.fail_for.add("1")

        from execution_engine.task_dispatcher import TaskDispatcher

        dispatcher = TaskDispatcher(plan=plan, task_dir=tmp_path, executor=executor)
        dispatcher.dispatch_next_batch(batch_size=1, ready_task_ids=["1"])

        assert task.status == TaskStatus.FAILED

    def test_dispatch_returns_stats(self, tmp_path):
        """Should return batch stats including completed/failed counts."""
        tasks = [
            Task(id="1", title="t1", description="d1"),
            Task(id="2", title="t2", description="d2"),
        ]
        plan = ExecutionPlan(tasks=tasks)
        executor = FakeExecutor()
        executor.fail_for.add("2")

        from execution_engine.task_dispatcher import TaskDispatcher

        dispatcher = TaskDispatcher(plan=plan, task_dir=tmp_path, executor=executor)
        result = dispatcher.dispatch_next_batch(batch_size=2, ready_task_ids=["1", "2"])

        assert result == {
            "tasks_dispatched": 2,
            "tasks_completed": 1,
            "tasks_failed": 1,
        }
