"""Tests for SubagentPool (minimal viable).

TDD: write tests first.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest


@dataclass
class DummyTask:
    id: str
    title: str = ""


class TestSubagentPool:
    def test_submit_runs_callable_and_returns_success_result(self):
        """submit should execute the callable and report success."""
        from execution_engine.subagent_pool.pool import SubagentPool

        pool = SubagentPool(max_workers=2)

        def fn():
            return "ok"

        result = pool.submit(task_id="T1", fn=fn)

        assert result.task_id == "T1"
        assert result.ok is True
        assert result.output == "ok"
        assert result.error is None

    def test_submit_captures_exception_and_marks_failed(self):
        """submit should catch exceptions and return a failed result."""
        from execution_engine.subagent_pool.pool import SubagentPool

        pool = SubagentPool(max_workers=1)

        def fn():
            raise ValueError("boom")

        result = pool.submit(task_id="T2", fn=fn)

        assert result.task_id == "T2"
        assert result.ok is False
        assert result.output is None
        assert "boom" in (result.error or "")

    def test_run_many_executes_all_and_preserves_order(self):
        """run_many should execute all items and preserve input order."""
        from execution_engine.subagent_pool.pool import SubagentPool

        pool = SubagentPool(max_workers=3)

        items = [
            ("1", lambda: 1),
            ("2", lambda: 2),
            ("3", lambda: 3),
        ]

        results = pool.run_many(items)

        assert [r.task_id for r in results] == ["1", "2", "3"]
        assert [r.output for r in results] == [1, 2, 3]

    def test_max_workers_must_be_positive(self):
        """max_workers should be validated."""
        from execution_engine.subagent_pool.pool import SubagentPool

        with pytest.raises(ValueError):
            SubagentPool(max_workers=0)
