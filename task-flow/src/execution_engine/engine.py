"""ExecutionEngine: Orchestrates all Execution Engine components.

This module provides main orchestration layer that integrates:
- ExecutionController: Manages task execution workflow
- DependencyResolver: Determines which tasks are ready to execute
- StateTracker: Tracks execution state for each task
"""

from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

from plan_generator.types import ExecutionPlan, Task, TaskStatus
from .controller import ExecutionController
from .dependency_resolver import DependencyResolver
from .state_tracker import StateTracker
from .subagent_pool.pool import SubagentPool
from .task_dispatcher import TaskDispatcher, TaskExecutor


@dataclass
class ExecutorResult:
    """Result from executor.run() with status attribute for TaskDispatcher."""
    status: TaskStatus


class SubagentPoolExecutor:
    """TaskExecutor adapter that uses SubagentPool to execute tasks.

    This adapter bridges TaskDispatcher's executor interface with SubagentPool:
    - Executor.run(task) returns ExecutorResult with status
    - Uses SubagentPool.submit to execute task.metadata["callable"]
    - Uses callbacks (on_start, on_success, on_fail) to notify about execution state
      instead of directly coupling to StateTracker
    """

    def __init__(
        self,
        subagent_pool: SubagentPool,
        task_metadata_getter: callable,  # callable(task) -> dict
        on_start: callable,              # callable(task_id, task) -> None (required)
        on_success: callable,            # callable(task_id, result) -> None (required)
        on_fail: callable,               # callable(task_id, error) -> None (required)
    ):
        """Initialize executor adapter.

        Args:
            subagent_pool: The SubagentPool for executing callables
            task_metadata_getter: Function to get metadata from a Task
            on_start: Callback when task starts execution (required)
            on_success: Callback when task completes successfully (required)
            on_fail: Callback when task execution fails (required)

        Raises:
            ValueError: If any of the required callbacks is None
        """
        if on_start is None:
            raise ValueError("on_start callback is required")
        if on_success is None:
            raise ValueError("on_success callback is required")
        if on_fail is None:
            raise ValueError("on_fail callback is required")

        self.subagent_pool = subagent_pool
        self.task_metadata_getter = task_metadata_getter
        self.on_start = on_start
        self.on_success = on_success
        self.on_fail = on_fail

    def run(self, task: Task) -> ExecutorResult:
        """Execute a task and return result with status.

        Args:
            task: The Task to execute

        Returns:
            ExecutorResult with TaskStatus.COMPLETED or FAILED
        """
        # Notify that task is starting
        self.on_start(task.id, task)

        # Get callable from task metadata
        metadata = self.task_metadata_getter(task)
        callable = metadata.get("callable")

        if callable is None:
            # No callable - treat as no-op success
            self.on_success(task.id, None)
            return ExecutorResult(status=TaskStatus.COMPLETED)

        # Execute via SubagentPool
        result = self.subagent_pool.submit(task.id, callable)

        if result.ok:
            self.on_success(task.id, result)
            return ExecutorResult(status=TaskStatus.COMPLETED)
        else:
            self.on_fail(task.id, result.error)
            return ExecutorResult(status=TaskStatus.FAILED)


class ExecutionEngine:
    """Orchestrates task execution with dependency resolution and state tracking.

    The ExecutionEngine integrates three core components:
    1. ExecutionController: Manages batch execution workflow
    2. DependencyResolver: Determines which tasks are ready to execute
    3. StateTracker: Tracks and persists execution state

    Attributes:
        plan: The execution plan containing tasks to execute
        task_dir: Directory containing task markdown files
        controller: ExecutionController for managing execution workflow
        resolver: DependencyResolver for determining ready tasks
        state_trackers: Dict mapping task_id to StateTracker instances
    """

    def __init__(self, plan: ExecutionPlan, task_dir: Path):
        """Initialize the ExecutionEngine.

        Args:
            plan: The execution plan containing tasks to execute
            task_dir: Directory containing task markdown files
        """
        self.plan = plan
        self.task_dir = task_dir

        # Initialize controller with the plan
        self.controller = ExecutionController(plan)

        # Initialize resolver with dict representation of tasks
        dict_tasks = self._convert_tasks_to_dicts(plan.tasks)
        self.resolver = DependencyResolver(dict_tasks)

        # Initialize state trackers dict (populated lazily)
        self.state_trackers: Dict[str, StateTracker] = {}

        # Initialize subagent pool for task execution
        self.subagent_pool = SubagentPool()

        # Dispatcher is created lazily and cached
        self._dispatcher: TaskDispatcher = None

    def _convert_tasks_to_dicts(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Convert Task objects to dict format for DependencyResolver.

        Args:
            tasks: List of Task objects

        Returns:
            List of task dictionaries with dependencies in correct format
        """
        dict_tasks = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": self._task_status_to_string(task.status),
                "dependencies": self._convert_dependencies_to_dicts(
                    task.dependencies
                ),
            }
            dict_tasks.append(task_dict)
        return dict_tasks

    def _task_status_to_string(self, status: TaskStatus) -> str:
        """Convert TaskStatus enum to string.

        Args:
            status: TaskStatus enum value

        Returns:
            String representation of status (e.g., "pending", "completed")
        """
        return status.value

    def _convert_dependencies_to_dicts(
        self, dependencies: List[str]
    ) -> List[Dict[str, str]]:
        """Convert dependency IDs to dict format.

        Args:
            dependencies: List of task IDs that this task depends on

        Returns:
            List of dependency dicts with "task_id" and "type" keys
        """
        return [
            {"task_id": dep_id, "type": "blocking"} for dep_id in dependencies
        ]

    def _create_dispatcher(self) -> TaskDispatcher:
        """Create a TaskDispatcher with SubagentPool executor.

        The executor is configured with callbacks that handle state tracking,
        decoupling the executor from StateTracker.

        Returns:
            TaskDispatcher configured to execute tasks via SubagentPool
        """
        executor = SubagentPoolExecutor(
            subagent_pool=self.subagent_pool,
            task_metadata_getter=lambda t: t.metadata,
            # Callbacks for decoupling from StateTracker
            on_start=self._on_task_start,
            on_success=self._on_task_success,
            on_fail=self._on_task_fail,
        )
        return TaskDispatcher(self.plan, self.task_dir, executor)

    def _get_state_tracker(self, task_id: str) -> StateTracker:
        """Get or create StateTracker for a task.

        Args:
            task_id: The task ID

        Returns:
            StateTracker instance for the task
        """
        if task_id not in self.state_trackers:
            task_file = self.task_dir / f"{task_id}.md"
            self.state_trackers[task_id] = StateTracker(task_file)
        return self.state_trackers[task_id]

    def _on_task_start(self, task_id: str, task: Task) -> None:
        """Callback when a task starts execution.

        Args:
            task_id: The task ID
            task: The Task object
        """
        tracker = self._get_state_tracker(task_id)
        # Track in-memory TaskStatus value (e.g., "in_progress")
        tracker.start_task(task_id, task.title, task_status=task.status.value)

    def _on_task_success(self, task_id: str, result) -> None:
        """Callback when a task completes successfully.

        Args:
            task_id: The task ID
            result: The execution result
        """
        tracker = self._get_state_tracker(task_id)
        # Track in-memory TaskStatus value (e.g., "completed")
        tracker.complete_task(task_id, task_status="completed")

    def _on_task_fail(self, task_id: str, error: str) -> None:
        """Callback when a task execution fails.

        Args:
            task_id: The task ID
            error: The error message
        """
        tracker = self._get_state_tracker(task_id)
        # Track in-memory TaskStatus value (e.g., "failed")
        tracker.update_execution_state(
            {"status": "failed", "error": error},
            task_status="failed"
        )

    def execute_next_batch(self) -> dict:
        """Execute the next batch of ready tasks.

        This method:
        1. Updates resolver with latest task states
        2. Gets ready tasks from DependencyResolver
        3. Delegates execution to TaskDispatcher (cached and reused)
        4. Returns execution statistics

        Returns:
            Dictionary containing execution statistics:
            - batch_size: Number of tasks in this batch
            - tasks_executed: Number of tasks dispatched for execution
            - total_completed: Total number of completed tasks in plan
        """
        # Step 1: Update resolver with latest task states
        self._update_resolver_tasks()

        # Step 2: Get ready tasks from DependencyResolver
        ready_ids = self.resolver.get_ready_tasks()

        # Step 3: Get batch size from controller
        batch_size = self.controller.batch_size

        # Step 4: Get or create dispatcher and delegate execution
        # Dispatcher is now cached and reused across batches
        if self._dispatcher is None:
            self._dispatcher = self._create_dispatcher()
        dispatch_stats = self._dispatcher.dispatch_next_batch(batch_size, ready_ids)

        # Step 5: Calculate statistics from plan state
        completed_tasks = [
            task for task in self.plan.tasks if task.status == TaskStatus.COMPLETED
        ]

        return {
            "batch_size": dispatch_stats["tasks_dispatched"],
            "tasks_executed": dispatch_stats["tasks_dispatched"],
            "total_completed": len(completed_tasks),
        }

    def _update_resolver_tasks(self):
        """Update resolver's task list to reflect status changes.

        This should be called after task statuses change to keep the
        DependencyResolver in sync with the current plan state.
        """
        dict_tasks = self._convert_tasks_to_dicts(self.plan.tasks)
        self.resolver.tasks = dict_tasks
