"""TodoWrite compatibility tool for task-flow"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from task_manager import TaskManager


def maybe_run_bootstrap(task_manager: TaskManager, task_id: str, new_status: str):
    """
    Optional bootstrap hook called when transitioning to In Progress.

    This is called by TaskManager.update_task when status changes to In Progress.
    The actual bootstrap behavior depends on TASK_FLOW_BOOTSTRAP env variable.

    Args:
        task_manager: The TaskManager instance
        task_id: The task ID being updated
        new_status: The new status value
    """
    # This function can be called during task status updates
    # It can trigger wt-workflow bootstrap if TASK_FLOW_BOOTSTRAP is set
    bootstrap = os.environ.get("TASK_FLOW_BOOTSTRAP")
    if bootstrap and new_status.lower() in ["in progress", "in_progress"]:
        try:
            # Import and call wt-workflow bootstrap if available
            import subprocess
            result = subprocess.run(
                ["wt", "bootstrap", task_id],
                capture_output=True,
                text=True,
                cwd=task_manager.tasks_dir.parent.parent
            )
            if result.returncode != 0:
                task_manager.add_task_note(task_id, f"Bootstrap failed: {result.stderr}")
        except Exception as e:
            task_manager.add_task_note(task_id, f"Bootstrap failed: {str(e)}")


class TodoWriteCompat:
    """
    Compatibility layer for TodoWrite format.

    Converts TodoWrite todos to task-flow tasks and maintains
    idempotent mapping between todo_id and task_id.
    """

    def __init__(
        self,
        project_root: Path,
        bootstrap: Optional[str] = None,
    ):
        """
        Initialize the TodoWrite compatibility tool.

        Args:
            project_root: Root directory of the project
            bootstrap: Optional bootstrap mode (e.g., 'wt')
        """
        self.project_root = Path(project_root)
        self.bootstrap = bootstrap
        self.tasks_dir = self.project_root / "docs" / "tasks"
        self.index_file = self.project_root / "docs" / "_index.json"
        self.task_manager = TaskManager(
            tasks_dir=self.tasks_dir,
            index_file=self.index_file
        )

        # Track initial content for each todo_id to detect changes
        self._initial_content: Dict[str, str] = {}

    def write(self, todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Write todos as tasks, maintaining idempotent mapping.

        Args:
            todos: List of todo items with format:
                   - id: todo_id (optional)
                   - content: task description
                   - status: pending/in_progress/completed

        Returns:
            List of results with id, content, status, and task_id
        """
        results = []

        for todo in todos:
            todo_id = todo.get("id")
            content = todo.get("content", "")
            status = todo.get("status", "pending")

            # Normalize status for task-flow
            task_flow_status = self._map_status(status)

            # Check if this is an existing todo (for idempotency)
            existing_task = None
            if todo_id is not None:
                existing_task = self.task_manager.get_task_by_todo_id(todo_id)

            if existing_task:
                # Update existing task
                task_id = existing_task["id"]
                self._update_existing_task(
                    task_id,
                    todo_id,
                    content,
                    task_flow_status
                )
            else:
                # Create new task with todo_id
                task_id = self.task_manager.create_task_with_todo_id(
                    title=content,
                    todo_id=str(todo_id) if todo_id is not None else None
                )

                # Set initial content tracking
                if todo_id is not None:
                    self._initial_content[str(todo_id)] = content

                # Set status if not pending
                if task_flow_status != "To Do":
                    self.task_manager.update_task(task_id, status=task_flow_status)

                # Run bootstrap if needed
                if task_flow_status == "In Progress" and self.bootstrap:
                    self._run_bootstrap(task_id)

            results.append({
                "id": todo_id,
                "content": content,
                "status": status,
                "task_id": task_id,
            })

        return results

    def _map_status(self, status: str) -> str:
        """Map TodoWrite status to task-flow status"""
        status_map = {
            "pending": "To Do",
            "in_progress": "In Progress",
            "completed": "Done",
        }
        return status_map.get(status, "To Do")

    def _update_existing_task(
        self,
        task_id: str,
        todo_id: str,
        new_content: str,
        new_status: str
    ):
        """Update an existing task while preserving title"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return

        # Update status
        current_status = task.get("status", "")
        if current_status != new_status:
            self.task_manager.update_task(task_id, status=new_status)

        # Check if content changed
        initial_content = self._initial_content.get(str(todo_id))
        if initial_content and new_content != initial_content:
            # Add content change as a note
            self.task_manager.add_task_note(
                task_id,
                f"Content updated: {new_content}"
            )

        # Run bootstrap if transitioning to In Progress
        if new_status == "In Progress" and current_status != "In Progress" and self.bootstrap:
            self._run_bootstrap(task_id)

    def _run_bootstrap(self, task_id: str) -> bool:
        """
        Run the bootstrap process for a task.

        Returns:
            True if bootstrap succeeded, False otherwise
        """
        if self.bootstrap == "wt":
            try:
                import subprocess
                result = subprocess.run(
                    ["wt", "bootstrap", task_id],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                if result.returncode != 0:
                    self.task_manager.add_task_note(
                        task_id,
                        f"Bootstrap failed: {result.stderr}"
                    )
                    return False
                return True
            except Exception as e:
                self.task_manager.add_task_note(
                    task_id,
                    f"Bootstrap failed: {str(e)}"
                )
                return False
        return True
