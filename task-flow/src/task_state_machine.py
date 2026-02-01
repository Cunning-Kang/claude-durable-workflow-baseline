"""Task State Machine - manage task state transitions

This module provides state machine capabilities for task-flow:
1. Define valid task states
2. Validate state transitions
3. Track transition history
4. Provide metadata for transitions

Design principles:
- Simple state machine with explicit transitions
- Fail fast on invalid transitions
- Track all state changes for auditability
"""

from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional


class TaskState:
    """任务状态"""

    VALID_STATES = {
        "To Do", "In Progress", "Done", "Blocked", "Cancelled"
    }

    def __init__(self, name: str):
        if name not in self.VALID_STATES:
            raise ValueError(f"Invalid state: {name}. Valid states: {self.VALID_STATES}")
        self.name = name


class TransitionError(Exception):
    """无效的状态转换"""
    pass


@dataclass
class TransitionResult:
    """状态转换结果"""
    is_valid: bool
    from_state: str
    to_state: str
    timestamp: datetime
    reason: Optional[str] = None


class TaskStateMachine:
    """任务状态机"""

    # 定义有效的状态转换
    VALID_TRANSITIONS = {
        "To Do": {"In Progress", "Cancelled"},
        "In Progress": {"Done", "Blocked", "Cancelled"},
        "Blocked": {"In Progress", "Cancelled"},
        "Done": set(),  # Done 是终态,不能转换
        "Cancelled": set(),  # Cancelled 是终态,不能转换
    }

    def __init__(self):
        self.history: List[TransitionResult] = []

    def transition(self, from_state: str, to_state: str, reason: Optional[str] = None) -> TransitionResult:
        """执行状态转换

        Args:
            from_state: 当前状态
            to_state: 目标状态
            reason: 转换原因（可选）

        Returns:
            TransitionResult: 转换结果

        Raises:
            TransitionError: 如果转换无效
        """
        # 验证状态是否有效
        if from_state not in TaskState.VALID_STATES:
            raise ValueError(f"Invalid from_state: {from_state}")
        if to_state not in TaskState.VALID_STATES:
            raise ValueError(f"Invalid to_state: {to_state}")

        # 验证转换是否有效
        valid_targets = self.VALID_TRANSITIONS.get(from_state, set())
        if to_state not in valid_targets:
            raise TransitionError(
                f"Invalid transition: {from_state} -> {to_state}. "
                f"Valid transitions from {from_state}: {valid_targets}"
            )

        # 记录转换
        result = TransitionResult(
            is_valid=True,
            from_state=from_state,
            to_state=to_state,
            timestamp=datetime.now(),
            reason=reason
        )
        self.history.append(result)

        return result

    def get_history(self) -> List[TransitionResult]:
        """获取转换历史"""
        return self.history.copy()
