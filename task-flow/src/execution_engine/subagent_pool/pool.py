"""SubagentPool: Minimal execution pool abstraction.

This is a minimal, local implementation that can run callables and capture
results. It does NOT invoke real subagents.

The goal is to provide a stable interface that higher-level orchestration can
depend on while we iterate on actual agent execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, List, Optional, Tuple


@dataclass
class SubagentResult:
    task_id: str
    ok: bool
    output: Any = None
    error: Optional[str] = None


class SubagentPool:
    def __init__(self, max_workers: int = 1):
        if max_workers <= 0:
            raise ValueError("max_workers must be positive")
        self.max_workers = max_workers

    def submit(self, task_id: str, fn: Callable[[], Any]) -> SubagentResult:
        try:
            out = fn()
            return SubagentResult(task_id=task_id, ok=True, output=out, error=None)
        except Exception as e:  # noqa: BLE001
            return SubagentResult(task_id=task_id, ok=False, output=None, error=str(e))

    def run_many(self, items: List[Tuple[str, Callable[[], Any]]]) -> List[SubagentResult]:
        # Minimal synchronous implementation; preserves input order.
        return [self.submit(task_id, fn) for task_id, fn in items]
