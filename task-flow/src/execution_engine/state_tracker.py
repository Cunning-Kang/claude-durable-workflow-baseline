"""StateTracker - track execution state and persist to task files

This module provides state tracking capabilities for task execution:
1. Track task status (running, completed, etc.)
2. Record timestamps (started_at, completed_at)
3. Calculate duration
4. Persist state to YAML frontmatter
5. Handle missing fields gracefully

Design principles:
- Simple state tracking with clear API
- Durable persistence to task files
- Graceful error handling
- Integration with TaskStateMachine for validation
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
import yaml


class StateTracker:
    """Track execution state and persist to task files"""

    def __init__(self, task_file: Path):
        """Initialize with task file path

        Args:
            task_file: Path to the task file (.md)
        """
        self.task_file = task_file
        self._cache: Optional[Dict[str, Any]] = None

    def _load_frontmatter(self) -> Dict[str, Any]:
        """Load YAML frontmatter from task file

        Returns:
            Dict containing parsed YAML frontmatter, or empty dict if file doesn't exist
        """
        if not self.task_file.exists():
            return {}

        try:
            content = self.task_file.read_text()
            parts = content.split("---")

            if len(parts) < 3:
                return {}

            yaml_content = parts[1].strip()
            return yaml.safe_load(yaml_content) or {}
        except Exception:
            # Handle malformed YAML or other errors gracefully
            return {}

    def _save_frontmatter(self, data: Dict[str, Any]) -> None:
        """Save YAML frontmatter to task file

        Args:
            data: Dict to save as YAML frontmatter
        """
        if not self.task_file.exists():
            return

        try:
            content = self.task_file.read_text()
            parts = content.split("---")

            if len(parts) < 3:
                return

            # Reconstruct file with updated YAML
            yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{yaml_str}---{parts[2]}"
            self.task_file.write_text(new_content)
        except Exception:
            # Handle errors gracefully
            pass

    def start_task(self, task_id: str, title: str, task_status: str = "in_progress") -> None:
        """Mark task as running

        Args:
            task_id: Task identifier
            title: Task title
            task_status: The TaskStatus value (e.g., "in_progress", "completed", "failed")
        """
        frontmatter = self._load_frontmatter()

        # Initialize execution_state if not present
        if "execution_state" not in frontmatter:
            frontmatter["execution_state"] = {}

        # Update state
        frontmatter["execution_state"]["status"] = "running"
        frontmatter["execution_state"]["started_at"] = datetime.now().isoformat()
        frontmatter["execution_state"]["task_id"] = task_id
        frontmatter["execution_state"]["task_title"] = title
        # Track in-memory TaskStatus enum value
        frontmatter["execution_state"]["task_status"] = task_status

        # Clear completion fields if restarting
        frontmatter["execution_state"].pop("completed_at", None)
        frontmatter["execution_state"].pop("duration", None)

        # Save to file
        self._save_frontmatter(frontmatter)
        self._cache = None  # Clear cache

    def complete_task(self, task_id: str, task_status: str = "completed") -> None:
        """Mark task as completed and calculate duration

        Args:
            task_id: Task identifier
            task_status: The TaskStatus value (e.g., "completed", "failed")
        """
        frontmatter = self._load_frontmatter()

        # Initialize execution_state if not present
        if "execution_state" not in frontmatter:
            frontmatter["execution_state"] = {}

        # Get started_at if available
        started_at_str = frontmatter["execution_state"].get("started_at")
        duration = None

        if started_at_str:
            try:
                started_at = datetime.fromisoformat(started_at_str)
                completed_at = datetime.now()
                duration = (completed_at - started_at).total_seconds()

                frontmatter["execution_state"]["completed_at"] = completed_at.isoformat()
                frontmatter["execution_state"]["duration"] = duration
            except Exception:
                # Handle datetime parsing errors
                frontmatter["execution_state"]["duration"] = None
        else:
            # Task was completed without being started
            frontmatter["execution_state"]["completed_at"] = datetime.now().isoformat()
            frontmatter["execution_state"]["duration"] = 0

        frontmatter["execution_state"]["status"] = "completed"
        # Track in-memory TaskStatus enum value
        frontmatter["execution_state"]["task_status"] = task_status

        # Save to file
        self._save_frontmatter(frontmatter)
        self._cache = None  # Clear cache

    def get_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current execution state for task

        Args:
            task_id: Task identifier

        Returns:
            Dict containing execution state, or None if file doesn't exist
        """
        if not self.task_file.exists():
            return None

        # Use cache if available
        if self._cache is not None:
            return self._cache

        frontmatter = self._load_frontmatter()
        execution_state = frontmatter.get("execution_state", {})

        # Ensure required fields exist
        default_state = {
            "current_step": 0,
            "total_steps": 0,
            "completed_tasks": [],
            "failed_tasks": [],
        }

        # Merge with actual state
        for key, value in default_state.items():
            if key not in execution_state:
                execution_state[key] = value

        self._cache = execution_state
        return execution_state

    def update_execution_state(self, state: Dict[str, Any], task_status: str = None) -> None:
        """Update execution state in YAML frontmatter

        Args:
            state: Dict containing state updates
            task_status: Optional TaskStatus value to track in execution_state.task_status
        """
        frontmatter = self._load_frontmatter()

        # Initialize execution_state if not present
        if "execution_state" not in frontmatter:
            frontmatter["execution_state"] = {}

        # Merge updates
        frontmatter["execution_state"].update(state)

        # Update task_status if provided
        if task_status is not None:
            frontmatter["execution_state"]["task_status"] = task_status

        # Save to file
        self._save_frontmatter(frontmatter)
        self._cache = None  # Clear cache
