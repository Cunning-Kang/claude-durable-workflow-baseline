"""Task state machine implementation for task-flow skill.

Defines valid task states and manages state transitions.
"""

from datetime import datetime
from typing import List, Optional


class TransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class TaskState:
    """Represents a valid task state.

    Valid states: To Do, In Progress, Done, Blocked, Cancelled
    """

    VALID_STATES = {"To Do", "In Progress", "Done", "Blocked", "Cancelled"}

    def __init__(self, name: str):
        if name not in self.VALID_STATES:
            raise ValueError(f"Invalid task state: {name}. Valid states are: {sorted(self.VALID_STATES)}")
        self.name = name


class TransitionResult:
    """Result of a state transition attempt."""

    def __init__(
        self,
        is_valid: bool,
        from_state: str,
        to_state: str,
        reason: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.is_valid = is_valid
        self.from_state = from_state
        self.to_state = to_state
        self.reason = reason
        self.timestamp = timestamp or datetime.now()


class TaskStateMachine:
    """Manages task state transitions and history.

    Valid transitions:
    - To Do -> In Progress
    - In Progress -> Done
    - In Progress -> Blocked
    - Blocked -> In Progress
    - Any state -> Cancelled (except Done and Cancelled)
    """

    # Valid state transitions: from_state -> {to_states}
    VALID_TRANSITIONS = {
        "To Do": {"In Progress", "Cancelled"},
        "In Progress": {"Done", "Blocked", "Cancelled"},
        "Blocked": {"In Progress", "Cancelled"},
        "Done": set(),  # Terminal state
        "Cancelled": set(),  # Terminal state
    }

    def __init__(self):
        self._history: List[TransitionResult] = []

    def transition(self, from_state: str, to_state: str, reason: Optional[str] = None) -> TransitionResult:
        """Attempt a state transition.

        Args:
            from_state: Current state name
            to_state: Target state name
            reason: Optional reason for the transition

        Returns:
            TransitionResult with is_valid, from_state, to_state, reason, timestamp

        Raises:
            TransitionError: If the transition is invalid
        """
        # Validate both states exist
        TaskState(from_state)
        TaskState(to_state)

        # Check if transition is valid
        if to_state not in self.VALID_TRANSITIONS.get(from_state, set()):
            raise TransitionError(f"Invalid transition: {from_state} -> {to_state}")

        result = TransitionResult(
            is_valid=True,
            from_state=from_state,
            to_state=to_state,
            reason=reason
        )
        self._history.append(result)
        return result

    def get_history(self) -> List[TransitionResult]:
        """Return all transition history."""
        return self._history
