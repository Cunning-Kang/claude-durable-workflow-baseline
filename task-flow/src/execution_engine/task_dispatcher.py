"""TaskDispatcher: Dispatch ready tasks to an executor.

This is a small coordination layer between:
- an execution plan (Task objects)
- a task executor (callable)

It is intentionally minimal and synchronous for now.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Protocol

from plan_generator.types import ExecutionPlan, Task, TaskStatus


class TaskExecutor(Protocol):
    def run(self, task: Task):  # pragma: no cover
        ...


@dataclass
class DispatchStats:
    tasks_dispatched: int
    tasks_completed: int
    tasks_failed: int

    def as_dict(self) -> Dict[str, int]:
        return {
            "tasks_dispatched": self.tasks_dispatched,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
        }


class TaskDispatcher:
    """Dispatches tasks to an executor and updates TaskStatus."""

    def __init__(self, plan: ExecutionPlan, task_dir: Path, executor: TaskExecutor):
        self.plan = plan
        self.task_dir = task_dir
        self.executor = executor

    def dispatch_next_batch(self, batch_size: int, ready_task_ids: List[str]) -> Dict[str, int]:
        ready_set = set(ready_task_ids)

        candidates: List[Task] = [
            t for t in self.plan.tasks if t.id in ready_set and t.status != TaskStatus.COMPLETED
        ]
        batch = candidates[:batch_size]

        stats = DispatchStats(tasks_dispatched=0, tasks_completed=0, tasks_failed=0)

        for task in batch:
            stats.tasks_dispatched += 1
            task.status = TaskStatus.IN_PROGRESS

            result = self.executor.run(task)
            status = getattr(result, "status", None)

            if status == TaskStatus.COMPLETED:
                task.status = TaskStatus.COMPLETED
                stats.tasks_completed += 1
            elif status == TaskStatus.FAILED:
                task.status = TaskStatus.FAILED
                stats.tasks_failed += 1
            else:
                # Default to failed if executor doesn't provide expected status
                task.status = TaskStatus.FAILED
                stats.tasks_failed += 1

        return stats.as_dict()
