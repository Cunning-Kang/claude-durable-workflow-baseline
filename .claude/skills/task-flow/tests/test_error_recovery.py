"""Tests for ErrorRecovery - retry and recovery mechanisms

These tests follow TDD methodology:
- Write failing test first
- Watch it fail
- Implement minimal code to pass
"""

import pytest
from pathlib import Path
import time
import sys

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from error_recovery import ErrorRecovery, RetryableError, PermanentError


class TestRetryWithBackoff:
    """测试带退避的重试机制"""

    def test_successful_operation_does_not_retry(self):
        """成功的操作不应该重试"""
        recovery = ErrorRecovery()

        call_count = 0

        def successful_operation():
            nonlocal call_count
            call_count += 1
            return "success"

        result = recovery.retry_with_backoff(successful_operation, max_attempts=3)

        assert result == "success"
        assert call_count == 1

    def test_retry_on_transient_failure(self):
        """瞬时失败应该重试并成功"""
        recovery = ErrorRecovery()

        call_count = 0

        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RetryableError("Temporary failure")
            return "success"

        result = recovery.retry_with_backoff(flaky_operation, max_attempts=3)

        assert result == "success"
        assert call_count == 2

    def test_fails_after_max_attempts(self):
        """超过最大重试次数应该失败"""
        recovery = ErrorRecovery()

        def always_failing_operation():
            raise RetryableError("Always fails")

        with pytest.raises(RetryableError):
            recovery.retry_with_backoff(always_failing_operation, max_attempts=3)

    def test_exponential_backoff_between_retries(self):
        """重试之间应该有指数退避"""
        recovery = ErrorRecovery(base_delay=0.01)  # 10ms base delay

        call_times = []

        def failing_operation():
            call_times.append(time.time())
            raise RetryableError("Fail")

        try:
            recovery.retry_with_backoff(failing_operation, max_attempts=3)
        except RetryableError:
            pass

        # 验证有 3 次调用
        assert len(call_times) == 3

        # 验证延迟递增（指数退避）
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        assert delay2 > delay1  # 第二次延迟应该更长

    def test_permanent_error_does_not_retry(self):
        """永久错误不应该重试"""
        recovery = ErrorRecovery()

        call_count = 0

        def permanent_failure():
            nonlocal call_count
            call_count += 1
            raise PermanentError("Permanent failure")

        with pytest.raises(PermanentError):
            recovery.retry_with_backoff(permanent_failure, max_attempts=3)

        # 永久错误应该立即失败，不重试
        assert call_count == 1

    def test_custom_retry_condition(self):
        """应该支持自定义重试条件"""
        recovery = ErrorRecovery()

        call_count = 0

        def operation_with_custom_error():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Network timeout")
            return "success"

        # 自定义条件：ValueError 应该重试
        def should_retry(error):
            return isinstance(error, ValueError)

        result = recovery.retry_with_backoff(
            operation_with_custom_error,
            max_attempts=3,
            should_retry=should_retry
        )

        assert result == "success"
        assert call_count == 2


class TestManualRecoveryPrompt:
    """测试手动恢复提示"""

    def test_generates_recovery_prompt(self):
        """应该生成清晰的恢复提示"""
        recovery = ErrorRecovery()

        error = RetryableError("Git operation failed: connection reset")
        prompt = recovery.generate_recovery_prompt(error, attempts=2)

        assert "Git operation failed" in prompt
        assert "attempts" in prompt.lower() or "尝试" in prompt
        assert len(prompt) > 0

    def test_prompt_includes_suggestions(self):
        """提示应该包含恢复建议"""
        recovery = ErrorRecovery()

        error = RetryableError("Remote repository not found")
        prompt = recovery.generate_recovery_prompt(
            error,
            suggestions=["Check remote URL", "Verify network connection"]
        )

        assert "Check remote URL" in prompt
        assert "Verify network connection" in prompt


class TestRecoveryStatistics:
    """测试恢复统计"""

    def test_tracks_retry_statistics(self):
        """应该跟踪重试统计"""
        recovery = ErrorRecovery()

        call_count = 0

        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RetryableError("Temporary failure")
            return "success"

        recovery.retry_with_backoff(flaky_operation, max_attempts=5)

        stats = recovery.get_statistics()
        assert stats["total_attempts"] == 3
        assert stats["successful_retries"] == 1
        assert stats["total_operations"] == 1

    def test_tracks_failure_rate(self):
        """应该跟踪失败率"""
        recovery = ErrorRecovery()

        # 成功的操作
        def success():
            return "ok"

        recovery.retry_with_backoff(success, max_attempts=3)

        # 失败的操作
        def failure():
            raise RetryableError("Failed")

        try:
            recovery.retry_with_backoff(failure, max_attempts=3)
        except RetryableError:
            pass

        stats = recovery.get_statistics()
        assert stats["total_operations"] == 2
        assert stats["successful_operations"] == 1
        assert stats["failed_operations"] == 1
