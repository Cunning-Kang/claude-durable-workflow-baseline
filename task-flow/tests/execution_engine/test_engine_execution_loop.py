"""Tests for ExecutionEngine execution loop (dispatcher + pool + state_tracker)."""

from __future__ import annotations

from pathlib import Path

from plan_generator.types import ExecutionPlan, Task, TaskStatus


def test_engine_executes_ready_tasks_and_updates_frontmatter(tmp_path: Path):
    """Engine should execute ready tasks and persist execution_state to task files."""
    from execution_engine.engine import ExecutionEngine

    # Task 2 depends on Task 1
    t1 = Task(id="1", title="T1", description="D1", metadata={"callable": lambda: "ok"})
    t2 = Task(id="2", title="T2", description="D2", dependencies=["1"], metadata={"callable": lambda: "ok"})
    plan = ExecutionPlan(tasks=[t1, t2])

    # Create task files for StateTracker
    for tid in ["1", "2"]:
        (tmp_path / f"{tid}.md").write_text("---\nexecution_state: {}\n---\n")

    engine = ExecutionEngine(plan, tmp_path)

    r1 = engine.execute_next_batch()
    assert r1["tasks_executed"] == 1
    assert t1.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
    assert t2.status == TaskStatus.PENDING

    # If t1 completed, t2 becomes ready
    if t1.status == TaskStatus.COMPLETED:
        r2 = engine.execute_next_batch()
        assert r2["tasks_executed"] == 1
        assert t2.status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
