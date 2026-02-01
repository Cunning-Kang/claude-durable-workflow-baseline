"""
DependencyResolver: Handles task dependency resolution and cycle detection.
"""

from typing import Dict, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from plan_generator.types import Task


class DependencyResolver:
    """
    Resolves task dependencies and determines which tasks are ready to execute.

    Attributes:
        tasks: List of task dictionaries with dependencies
    """

    def __init__(self, tasks: List[Dict[str, Any]]):
        """
        Initialize resolver with task list.

        Args:
            tasks: List of task dictionaries. Each task should have:
                - id: Unique task identifier
                - title: Task title
                - status: Task status (e.g., "pending", "completed")
                - dependencies: List of dependency dicts with "task_id" and "type"
        """
        self.tasks = tasks

    @staticmethod
    def task_to_dict(task: 'Task') -> Dict[str, Any]:
        """Convert Task object to dict format for DependencyResolver.

        Args:
            task: Task object from plan_generator.types

        Returns:
            Dictionary representation compatible with DependencyResolver format:
                - id: Task ID
                - title: Task title
                - status: Task status as string value
                - dependencies: List of dependency dicts with task_id and type
        """
        from plan_generator.types import Task

        # Convert dependencies list to dependency dict format
        deps = [
            {"task_id": dep_id, "type": "blocking"}
            for dep_id in task.dependencies
        ]

        # Handle status - convert enum to string if needed
        status_value = task.status.value if hasattr(task.status, 'value') else task.status

        return {
            "id": task.id,
            "title": task.title,
            "status": status_value,
            "dependencies": deps
        }

    def get_ready_tasks(self) -> List[str]:
        """
        Get list of task IDs whose dependencies are satisfied.

        A task is ready if:
        - It has no dependencies, OR
        - All its blocking dependencies are completed

        Returns:
            List of task IDs that are ready to execute
        """
        ready_tasks = []

        for task in self.tasks:
            # Skip completed tasks
            if task.get("status") == "completed":
                continue

            # Check if dependencies are satisfied
            if self.dependencies_satisfied(task["id"]):
                ready_tasks.append(task["id"])

        return ready_tasks

    def _build_graph(self) -> Dict[str, List[str]]:
        """
        Build dependency graph from tasks.

        Creates a graph representation where:
        - Keys are task IDs
        - Values are lists of task IDs they depend on (blocking only)

        Returns:
            Dictionary mapping task_id to list of dependency IDs
        """
        graph = {}

        for task in self.tasks:
            task_id = task["id"]
            dependencies = task.get("dependencies", [])

            # Only include blocking dependencies in the graph
            blocking_deps = [
                dep["task_id"]
                for dep in dependencies
                if dep.get("type") == "blocking"
            ]

            graph[task_id] = blocking_deps

        return graph

    def _has_cycle(self, graph: Dict[str, List[str]]) -> bool:
        """
        Detect if dependency graph contains a cycle using DFS.

        Args:
            graph: Dependency graph from _build_graph()

        Returns:
            True if cycle detected, False otherwise
        """
        # Track visited nodes and nodes in current recursion stack
        visited = set()
        rec_stack = set()

        def dfs(node: str) -> bool:
            """
            Depth-First Search to detect cycles.

            Args:
                node: Current node being visited

            Returns:
                True if cycle found, False otherwise
            """
            # Mark current node as visited and add to recursion stack
            visited.add(node)
            rec_stack.add(node)

            # Recur for all neighbors
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # If neighbor is in recursion stack, we found a cycle
                    return True

            # Remove node from recursion stack before returning
            rec_stack.remove(node)
            return False

        # Check all nodes in the graph
        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True

        return False

    def dependencies_satisfied(self, task_id: str) -> bool:
        """
        Check if all blocking dependencies for a task are satisfied.

        A dependency is satisfied if the dependent task has status "completed".

        Args:
            task_id: ID of the task to check

        Returns:
            True if all blocking dependencies are satisfied, False otherwise
        """
        # Find the task
        task = None
        for t in self.tasks:
            if t["id"] == task_id:
                task = t
                break

        if task is None:
            return False

        # Get dependencies
        dependencies = task.get("dependencies", [])

        # If no dependencies, they're satisfied
        if not dependencies:
            return True

        # Check only blocking dependencies
        for dep in dependencies:
            if dep.get("type") == "blocking":
                dep_task_id = dep["task_id"]

                # Find the dependency task
                dep_task = None
                for t in self.tasks:
                    if t["id"] == dep_task_id:
                        dep_task = t
                        break

                # If dependency task not found or not completed, not satisfied
                if dep_task is None or dep_task.get("status") != "completed":
                    return False

        return True
