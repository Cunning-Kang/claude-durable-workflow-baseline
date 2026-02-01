"""ExecutionController for orchestrating task execution."""

from typing import Optional
from plan_generator.types import ExecutionPlan, Task, TaskStatus


class ExecutionController:
    """Controls the execution workflow of tasks in batches.

    The ExecutionController manages task execution state, batches tasks for
    execution, and handles human review checkpoints.

    Attributes:
        plan: The execution plan containing tasks to execute
        batch_size: Number of tasks to execute per batch (default: 3)
        checkpoint_interval: Number of tasks between checkpoints (default: 3)
        auto_continue: If True, skip human review between batches (default: False)
        executed_count: Number of tasks executed so far
        last_checkpoint_at: Task count at last checkpoint
    """

    def __init__(
        self,
        plan: ExecutionPlan,
        batch_size: int = 3,
        checkpoint_interval: int = 3,
        auto_continue: bool = False,
    ):
        """Initialize the ExecutionController.

        Args:
            plan: The execution plan containing tasks to execute
            batch_size: Number of tasks to execute per batch (default: 3)
            checkpoint_interval: Number of tasks between checkpoints (default: 3)
            auto_continue: If True, skip human review between batches (default: False)
        """
        self.plan = plan
        self.batch_size = batch_size
        self.checkpoint_interval = checkpoint_interval
        self.auto_continue = auto_continue
        self.executed_count = 0
        self.last_checkpoint_at = 0
        self._waiting_for_review = False

    def execute_batch(self) -> dict:
        """Execute one batch of tasks.

        This method:
        1. Gets the next batch of pending tasks (marks them IN_PROGRESS)
        2. Simulates executing each task (marks them COMPLETED)
        3. Updates execution counters and checkpoint state

        Returns:
            Dictionary containing execution statistics:
            - batch_size: Number of tasks in this batch
            - tasks_executed: Number of tasks executed in this batch
            - total_completed: Total number of completed tasks in plan
        """
        # Get next batch and mark as IN_PROGRESS
        batch = self._get_next_batch(self.batch_size)

        # Execute each task in the batch
        # In a real implementation, this would call an executor
        # For now, we simulate execution by marking COMPLETED
        for task in batch:
            # Simulate task execution
            task.status = TaskStatus.COMPLETED
            self.executed_count += 1

        # Update checkpoint state after execution
        if batch:
            self._update_checkpoint_state()

        # Calculate statistics
        completed_tasks = [
            task for task in self.plan.tasks if task.status == TaskStatus.COMPLETED
        ]

        return {
            "batch_size": len(batch),
            "tasks_executed": len(batch),
            "total_completed": len(completed_tasks),
        }

    def _get_next_batch(self, batch_size: int) -> list[Task]:
        """Get the next batch of pending tasks.

        Args:
            batch_size: Maximum number of tasks to include in the batch

        Returns:
            List of tasks marked as IN_PROGRESS for execution
        """
        batch = []
        for task in self.plan.tasks:
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.IN_PROGRESS
                batch.append(task)
                if len(batch) >= batch_size:
                    break
        return batch

    def requires_human_review(self) -> bool:
        """Check if human review is required at this point.

        Returns:
            True if a checkpoint has been reached and auto_continue is False,
            False otherwise
        """
        if self.auto_continue:
            return False

        return self._waiting_for_review

    def _update_checkpoint_state(self):
        """Update checkpoint state based on executed tasks.

        This should be called after tasks are executed to track when
        the next checkpoint is reached.
        """
        tasks_since_checkpoint = self.executed_count - self.last_checkpoint_at

        if tasks_since_checkpoint >= self.checkpoint_interval:
            self.last_checkpoint_at = self.executed_count
            self._waiting_for_review = True
