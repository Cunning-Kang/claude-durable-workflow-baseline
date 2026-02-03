# Automation MVP Alignment Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 对齐当前自动化 MVP 实现与计划要求，补齐 Expect 断言、质量门来源、任务状态闭环与入口语义。

**Architecture:** 在既有 task-flow 执行引擎与 CLI 上做最小增量改动，优先通过测试驱动收敛行为差异，确保计划执行的输入、判定与状态更新具备可追溯性与一致性。

**Tech Stack:** Python 3.10+, pytest

---

### Task 1: 让 Expect 参与步骤判定（PASS/FAIL/关键字）

**Files:**
- Modify: `.claude/skills/task-flow/src/execution_engine.py:265-322`
- Test: `.claude/skills/task-flow/tests/test_execution_engine.py`

**Step 1: Write the failing test**

```python
# in tests/test_execution_engine.py

def test_step_runner_fails_when_expect_not_found():
    plan = """
### Step 1: Expect keyword
Run: echo "hello"
Expect: world
"""
    result = execute_plan(plan_text=plan)
    assert result.status == "failed"
    assert "Expect" in result.errors[0]
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_execution_engine.py::test_step_runner_fails_when_expect_not_found -v`
Expected: FAIL with assertion (expect mismatch not enforced)

**Step 3: Write minimal implementation**

```python
# execution_engine.py (inside run_step)
if step.expect:
    if step.expect.upper() == "PASS":
        pass
    elif step.expect.upper() == "FAIL":
        return StepResult(..., status="failed", error="Expect requested FAIL")
    elif step.expect not in completed.stdout:
        return StepResult(..., status="failed", error=f"Expect not found: {step.expect}")
```

**Step 4: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_execution_engine.py::test_step_runner_fails_when_expect_not_found -v`
Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/src/execution_engine.py .claude/skills/task-flow/tests/test_execution_engine.py
git commit -m "feat(task-flow): enforce expect assertions in step runner"
```

---

### Task 2: 质量门来源与计划/任务文件对齐

**Files:**
- Modify: `.claude/skills/task-flow/src/cli.py:275-316`
- Modify: `.claude/skills/task-flow/src/ci_detector.py:7-67`
- Test: `.claude/skills/task-flow/tests/test_ci_detector.py`

**Step 1: Write the failing test**

```python
# in tests/test_ci_detector.py

def test_task_frontmatter_ci_overrides_detection(tmp_path):
    from ci_detector import resolve_quality_gate_command
    cmd = resolve_quality_gate_command(project_root=tmp_path, task_frontmatter={"quality_gate": "pytest -q"})
    assert cmd == "pytest -q"
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_ci_detector.py::test_task_frontmatter_ci_overrides_detection -v`
Expected: FAIL with ImportError or missing function

**Step 3: Write minimal implementation**

```python
# ci_detector.py

def resolve_quality_gate_command(project_root: Path, task_frontmatter: dict | None = None) -> str:
    if task_frontmatter and task_frontmatter.get("quality_gate"):
        return task_frontmatter["quality_gate"]
    return detect_ci_command(project_root)
```

**Step 4: Wire it in CLI**

```python
# cli.py (inside cmd_execute_next_batch)
from ci_detector import resolve_quality_gate_command

quality_gate_cmd = resolve_quality_gate_command(task_file.parent, frontmatter)
```

**Step 5: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_ci_detector.py::test_task_frontmatter_ci_overrides_detection -v`
Expected: PASS

**Step 6: Commit**

```bash
git add .claude/skills/task-flow/src/ci_detector.py .claude/skills/task-flow/src/cli.py .claude/skills/task-flow/tests/test_ci_detector.py
git commit -m "feat(task-flow): prioritize task-defined quality gate"
```

---

### Task 3: 执行状态闭环（开始/失败/完成）

**Files:**
- Modify: `.claude/skills/task-flow/src/execution_engine.py:374-431`
- Modify: `.claude/skills/task-flow/src/cli.py:275-316`
- Modify: `.claude/skills/task-flow/src/task_manager.py:263-362`
- Test: `.claude/skills/task-flow/tests/test_task_manager.py`

**Step 1: Write the failing test**

```python
# in tests/test_task_manager.py

def test_task_status_updates_on_execution_states(task_manager, temp_tasks_dir):
    task_id = task_manager.create_task("Test task")
    task_manager.update_task(task_id, status="In Progress")
    task_file = temp_tasks_dir / f"{task_id}-test-task.md"
    assert "status: In Progress" in task_file.read_text()
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_task_manager.py::test_task_status_updates_on_execution_states -v`
Expected: FAIL if status is not updated

**Step 3: Write minimal implementation**

```python
# cli.py (inside cmd_execute_next_batch)
# set In Progress at start
# set Blocked on failure, Done on success
```

**Step 4: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_task_manager.py::test_task_status_updates_on_execution_states -v`
Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/src/cli.py .claude/skills/task-flow/tests/test_task_manager.py
git commit -m "feat(task-flow): update task status during execution"
```

---

### Task 4: 明确入口语义（“按计划执行 TASK-xxx”）

**Files:**
- Modify: `.claude/skills/task-flow/src/cli.py:384-437`
- Test: `.claude/skills/task-flow/tests/test_cli.py`

**Step 1: Write the failing test**

```python
# in tests/test_cli.py

def test_execute_plan_alias_in_help(cli_env, tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "docs" / "tasks").mkdir(parents=True)

    result = subprocess.run(
        ["python", "-m", "cli", "--help"],
        cwd=project,
        capture_output=True,
        text=True,
        env=cli_env
    )
    assert "execute-plan" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_cli.py::test_execute_plan_alias_in_help -v`
Expected: FAIL (command not present)

**Step 3: Write minimal implementation**

```python
# cli.py
# add subparser "execute-plan" as alias to execute-next-batch
```

**Step 4: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_cli.py::test_execute_plan_alias_in_help -v`
Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/src/cli.py .claude/skills/task-flow/tests/test_cli.py
git commit -m "feat(task-flow): add execute-plan alias"
```

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-02-03-automation-mvp-alignment-fixes-plan.md`. Two execution options:

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration
2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
