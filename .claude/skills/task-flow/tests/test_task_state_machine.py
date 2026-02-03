"""Tests for TaskStateMachine - task state transition management

These tests follow TDD methodology:
- Write failing test first
- Watch it fail
- Implement minimal code to pass
"""

import pytest
from pathlib import Path
import sys

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from task_state_machine import TaskStateMachine, TaskState, TransitionError


class TestTaskState:
    """测试任务状态定义"""

    def test_valid_states(self):
        """应该定义所有有效的任务状态"""
        # 定义的状态
        valid_states = ["To Do", "In Progress", "Done", "Blocked", "Cancelled"]

        for state_name in valid_states:
            state = TaskState(state_name)
            assert state.name == state_name

    def test_invalid_state_raises_error(self):
        """无效的状态应该抛出错误"""
        with pytest.raises(ValueError):
            TaskState("Invalid State")


class TestValidTransitions:
    """测试有效的状态转换"""

    def test_to_do_to_in_progress(self):
        """To Do -> In Progress 应该是有效的"""
        machine = TaskStateMachine()
        result = machine.transition("To Do", "In Progress")
        assert result.is_valid is True

    def test_in_progress_to_done(self):
        """In Progress -> Done 应该是有效的"""
        machine = TaskStateMachine()
        result = machine.transition("In Progress", "Done")
        assert result.is_valid is True

    def test_in_progress_to_blocked(self):
        """In Progress -> Blocked 应该是有效的"""
        machine = TaskStateMachine()
        result = machine.transition("In Progress", "Blocked")
        assert result.is_valid is True

    def test_blocked_to_in_progress(self):
        """Blocked -> In Progress 应该是有效的（恢复）"""
        machine = TaskStateMachine()
        result = machine.transition("Blocked", "In Progress")
        assert result.is_valid is True

    def test_any_state_to_cancelled(self):
        """任何状态都可以转为 Cancelled"""
        machine = TaskStateMachine()

        for from_state in ["To Do", "In Progress", "Blocked"]:
            result = machine.transition(from_state, "Cancelled")
            assert result.is_valid is True


class TestInvalidTransitions:
    """测试无效的状态转换"""

    def test_done_to_in_progress_raises_error(self):
        """Done -> In Progress 应该是无效的"""
        machine = TaskStateMachine()

        with pytest.raises(TransitionError):
            machine.transition("Done", "In Progress")

    def test_cancelled_to_in_progress_raises_error(self):
        """Cancelled -> In Progress 应该是无效的"""
        machine = TaskStateMachine()

        with pytest.raises(TransitionError):
            machine.transition("Cancelled", "In Progress")

    def test_to_do_to_blocked_raises_error(self):
        """To Do -> Blocked 应该是无效的"""
        machine = TaskStateMachine()

        with pytest.raises(TransitionError):
            machine.transition("To Do", "Blocked")

    def test_done_to_blocked_raises_error(self):
        """Done -> Blocked 应该是无效的"""
        machine = TaskStateMachine()

        with pytest.raises(TransitionError):
            machine.transition("Done", "Blocked")


class TestTransitionWithMetadata:
    """测试带元数据的状态转换"""

    def test_transition_with_reason(self):
        """状态转换可以记录原因"""
        machine = TaskStateMachine()
        result = machine.transition(
            "In Progress",
            "Blocked",
            reason="Waiting for dependency"
        )

        assert result.is_valid is True
        assert result.reason == "Waiting for dependency"

    def test_transition_includes_timestamp(self):
        """状态转换应该包含时间戳"""
        from datetime import datetime

        machine = TaskStateMachine()
        before = datetime.now()
        result = machine.transition("To Do", "In Progress")
        after = datetime.now()

        assert result.timestamp is not None
        assert before <= result.timestamp <= after


class TestStateMachineHistory:
    """测试状态机历史记录"""

    def test_state_machine_tracks_transitions(self):
        """状态机应该跟踪所有转换历史"""
        machine = TaskStateMachine()

        machine.transition("To Do", "In Progress")
        machine.transition("In Progress", "Blocked")
        machine.transition("Blocked", "In Progress")
        machine.transition("In Progress", "Done")

        history = machine.get_history()
        assert len(history) == 4

        # 验证转换顺序
        assert history[0].from_state == "To Do"
        assert history[0].to_state == "In Progress"
        assert history[1].from_state == "In Progress"
        assert history[1].to_state == "Blocked"
        assert history[2].from_state == "Blocked"
        assert history[2].to_state == "In Progress"
        assert history[3].from_state == "In Progress"
        assert history[3].to_state == "Done"

    def test_history_includes_metadata(self):
        """历史记录应该包含转换元数据"""
        machine = TaskStateMachine()

        machine.transition("In Progress", "Blocked", reason="Dependency issue")
        history = machine.get_history()

        assert history[0].reason == "Dependency issue"
