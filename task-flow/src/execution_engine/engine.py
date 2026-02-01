"""ExecutionEngine: Orchestrates all Execution Engine components.

This module provides the main orchestration layer that integrates:
- ExecutionController: Manages task execution workflow
- DependencyResolver: Determines which tasks are ready to execute
- StateTracker: Tracks execution state for each task
"""

from pathlib import Path
from typing import Dict, List, Any

from plan_generator.types import ExecutionPlan, Task, TaskStatus
from .controller import ExecutionController
from .dependency_resolver import DependencyResolver
from .state_tracker import StateTracker


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

    def execute_next_batch(self) -> dict:
        """Execute the next batch of ready tasks.

        This method:
        1. Gets ready tasks from DependencyResolver
        2. Filters plan tasks to only those that are ready
        3. Marks ready tasks as IN_PROGRESS up to batch_size
        4. Tracks state for each executed task

        Returns:
            Dictionary containing execution statistics:
            - batch_size: Number of tasks in this batch
            - tasks_executed: Number of tasks marked for execution
            - total_completed: Total number of completed tasks
        """
        # Keep DependencyResolver in sync with latest plan state
        self._update_resolver_tasks()

        # Step 1: Get ready tasks from DependencyResolver
        ready_ids = self.resolver.get_ready_tasks()

        # Step 2: Filter plan tasks to ready tasks
        ready_tasks = [t for t in self.plan.tasks if t.id in ready_ids]

        # Step 3: Mark tasks as IN_PROGRESS up to batch_size
        batch_size = self.controller.batch_size
        batch_tasks = ready_tasks[:batch_size]

        for task in batch_tasks:
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.IN_PROGRESS

        # Step 4: Track state for each executed task
        for task in batch_tasks:
            # Get or create state tracker for this task
            if task.id not in self.state_trackers:
                task_file = self.task_dir / f"{task.id}.md"
                self.state_trackers[task.id] = StateTracker(task_file)

            # Track completion if task was completed
            if task.status == TaskStatus.COMPLETED:
                tracker = self.state_trackers[task.id]
                tracker.complete_task(task.id)

        # Step 5: Update resolver to reflect status changes
        self._update_resolver_tasks()

        # Calculate statistics
        completed_tasks = [
            task for task in self.plan.tasks if task.status == TaskStatus.COMPLETED
        ]

        return {
            "batch_size": len(batch_tasks),
            "tasks_executed": len(batch_tasks),
            "total_completed": len(completed_tasks),
        }

    def _update_resolver_tasks(self):
        """Update resolver's task list to reflect status changes.

        This should be called after task statuses change to keep the
        DependencyResolver in sync with the current plan state.
        """
        dict_tasks = self._convert_tasks_to_dicts(self.plan.tasks)
        self.resolver.tasks = dict_tasks
