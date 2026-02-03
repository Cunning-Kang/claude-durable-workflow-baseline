"""Error recovery and retry mechanisms for task-flow.

Provides exception classes and retry logic with exponential backoff.
"""

import time
from typing import Callable, Optional, TypeVar


T = TypeVar("T")


class RetryableError(Exception):
    """An error that can be retried.

    Transient failures like network issues, temporary resource
    unavailability, or rate limits should use this exception.
    """

    pass


class PermanentError(Exception):
    """An error that should not be retried.

    These are typically logical errors, invalid inputs, or
    configuration issues that won't be fixed by retrying.
    """

    pass


class ErrorRecovery:
    """Error recovery and retry mechanisms with exponential backoff."""

    def __init__(
        self,
        base_delay: float = 0.1,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
    ):
        """Initialize error recovery.

        Args:
            base_delay: Initial delay between retries in seconds.
            max_delay: Maximum delay between retries in seconds.
            exponential_base: Base for exponential backoff calculation.
        """
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._exponential_base = exponential_base

        # Statistics tracking
        self._total_operations = 0
        self._total_attempts = 0
        self._successful_retries = 0
        self._successful_operations = 0
        self._failed_operations = 0

    def retry_with_backoff(
        self,
        operation: Callable[[], T],
        max_attempts: int = 3,
        should_retry: Optional[Callable[[Exception], bool]] = None,
    ) -> T:
        """Execute an operation with retry and exponential backoff.

        Args:
            operation: Function to execute (takes no arguments).
            max_attempts: Maximum number of attempts including the first.
            should_retry: Optional function to determine if an error is retryable.
                         If not provided, only RetryableError is retried.

        Returns:
            The result of the operation.

        Raises:
            RetryableError: If the operation fails after all retries.
            PermanentError: If a permanent error occurs (no retry).
            Exception: Any other exception if not caught by should_retry.
        """
        self._total_operations += 1
        last_exception = None

        for attempt in range(max_attempts):
            self._total_attempts += 1

            try:
                result = operation()
                # Track successful operation (after any retries)
                if attempt > 0:
                    self._successful_retries += 1
                self._successful_operations += 1
                return result

            except PermanentError as e:
                # Permanent errors are never retried
                self._failed_operations += 1
                raise

            except Exception as e:
                last_exception = e

                # Determine if this error is retryable
                is_retryable = False
                if should_retry is not None:
                    is_retryable = should_retry(e)
                else:
                    is_retryable = isinstance(e, RetryableError)

                # If not retryable or out of attempts, fail
                if not is_retryable or attempt == max_attempts - 1:
                    self._failed_operations += 1
                    raise

                # Exponential backoff delay
                delay = min(
                    self._base_delay * (self._exponential_base**attempt),
                    self._max_delay,
                )
                time.sleep(delay)

    def generate_recovery_prompt(
        self,
        error: Exception,
        attempts: int = 1,
        suggestions: Optional[list[str]] = None,
    ) -> str:
        """Generate a helpful recovery prompt for manual intervention.

        Args:
            error: The exception that occurred.
            attempts: Number of attempts already made.
            suggestions: Optional list of recovery suggestions.

        Returns:
            A formatted prompt message for the user.
        """
        error_type = type(error).__name__
        error_msg = str(error)

        prompt_parts = [
            f"Error: {error_type}",
            f"Message: {error_msg}",
            f"Attempts: {attempts}",
        ]

        if suggestions:
            prompt_parts.append("\nSuggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                prompt_parts.append(f"  {i}. {suggestion}")

        return "\n".join(prompt_parts)

    def get_statistics(self) -> dict:
        """Get statistics about retry behavior.

        Returns:
            A dictionary containing:
            - total_operations: Total number of operations attempted.
            - total_attempts: Total number of individual attempts.
            - successful_retries: Number of retries that eventually succeeded.
            - successful_operations: Number of operations that succeeded.
            - failed_operations: Number of operations that failed.
        """
        return {
            "total_operations": self._total_operations,
            "total_attempts": self._total_attempts,
            "successful_retries": self._successful_retries,
            "successful_operations": self._successful_operations,
            "failed_operations": self._failed_operations,
        }
