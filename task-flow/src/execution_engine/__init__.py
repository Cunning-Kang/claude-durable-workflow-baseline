"""Execution Engine Components

This package contains the execution engine components for task-flow:
- StateTracker: Track execution state and persist to task files
- SubagentPool: Manage subagent pool for parallel execution (future)
- DependencyResolver: Resolve task dependencies (future)
- ExecutionController: Control execution flow (future)
"""

from .state_tracker import StateTracker

__all__ = ["StateTracker"]
