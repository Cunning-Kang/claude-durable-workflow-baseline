"""Error Recovery - retry and recovery mechanisms

This module provides error recovery capabilities for task-flow:
1. Retry with exponential backoff
2. Distinguish between retryable and permanent errors
3. Track recovery statistics
4. Provide recovery prompts and suggestions

Design principles:
- Simple retry mechanism with exponential backoff
- Fail fast on permanent errors
- Track statistics for monitoring
- Provide helpful recovery guidance
"""

import time
from typing import Callable, Optional, TypeVar, List
from dataclasses import dataclass, field


class RetryableError(Exception):
    """可以重试的错误"""
    pass


class PermanentError(Exception):
    """永久错误，不应该重试"""
    pass


T = TypeVar('T')


@dataclass
class RecoveryStatistics:
    """恢复统计"""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_attempts: int = 0
    successful_retries: int = 0


class ErrorRecovery:
    """错误恢复机制"""

    def __init__(self, base_delay: float = 0.1):
        """
        Args:
            base_delay: 基础延迟时间（秒），用于指数退避
        """
        self.base_delay = base_delay
        self.stats = RecoveryStatistics()

    def retry_with_backoff(
        self,
        operation: Callable[[], T],
        max_attempts: int = 3,
        should_retry: Optional[Callable[[Exception], bool]] = None
    ) -> T:
        """带指数退避的重试机制

        Args:
            operation: 要执行的操作
            max_attempts: 最大尝试次数
            should_retry: 自定义重试条件函数

        Returns:
            操作的结果

        Raises:
            Exception: 操作失败后抛出最后一个异常
        """
        if should_retry is None:
            # 默认重试条件：RetryableError 应该重试
            def should_retry(error: Exception) -> bool:
                return isinstance(error, RetryableError)

        last_error = None
        attempts = 0

        for attempt in range(max_attempts):
            attempts += 1
            self.stats.total_attempts += 1

            try:
                result = operation()
                # 成功：记录统计
                self.stats.total_operations += 1
                self.stats.successful_operations += 1
                if attempt > 0:
                    self.stats.successful_retries += 1
                return result

            except Exception as e:
                last_error = e

                # 检查是否应该重试
                if not should_retry(e):
                    # 永久错误，立即失败
                    self.stats.total_operations += 1
                    self.stats.failed_operations += 1
                    raise

                # 最后一次尝试失败，不再重试
                if attempt == max_attempts - 1:
                    self.stats.total_operations += 1
                    self.stats.failed_operations += 1
                    raise

                # 指数退避
                delay = self.base_delay * (2 ** attempt)
                time.sleep(delay)

        # 不应该到达这里，但为了类型检查
        if last_error:
            raise last_error
        raise RuntimeError("Unexpected state in retry_with_backoff")

    def generate_recovery_prompt(
        self,
        error: Exception,
        attempts: int = 0,
        suggestions: Optional[List[str]] = None
    ) -> str:
        """生成恢复提示

        Args:
            error: 发生的错误
            attempts: 已尝试的次数
            suggestions: 恢复建议列表

        Returns:
            恢复提示字符串
        """
        lines = [
            f"❌ Error: {error}",
            f"   Attempts: {attempts}"
        ]

        if suggestions:
            lines.append("\n💡 Suggestions:")
            for suggestion in suggestions:
                lines.append(f"   - {suggestion}")

        return "\n".join(lines)

    def get_statistics(self) -> dict:
        """获取统计信息"""
        return {
            "total_operations": self.stats.total_operations,
            "successful_operations": self.stats.successful_operations,
            "failed_operations": self.stats.failed_operations,
            "total_attempts": self.stats.total_attempts,
            "successful_retries": self.stats.successful_retries,
        }
