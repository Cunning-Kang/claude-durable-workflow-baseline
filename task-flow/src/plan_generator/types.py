"""Type definitions for task execution."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TaskStatus(Enum):
    """Status of a task in the execution workflow."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """A task to be executed.

    Attributes:
        id: Unique identifier for the task
        title: Brief title describing the task
        description: Detailed description of what the task does
        status: Current status of the task (default: PENDING)
        dependencies: List of task IDs that must complete first (default: empty)
        metadata: Additional metadata about the task (default: empty dict)
    """

    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """A plan for executing tasks.

    Attributes:
        tasks: List of tasks to execute
        metadata: Additional metadata about the plan (default: empty dict)
    """

    tasks: list[Task]
    metadata: dict = field(default_factory=dict)
