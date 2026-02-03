# 自动化 MVP 执行器 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为自动化 MVP 执行器提供最小闭环能力：计划可执行化 → 逐步执行 → 质量门判定 → 状态同步 → 报告输出。

**Architecture:** 在 task-flow 现有执行引擎与 CLI 之上增加计划校验、步骤执行与结果汇总逻辑，所有输出以任务文件与标准报告为事实源。

**Tech Stack:** Python 3.10+, PyYAML, pytest

---

### Task 0: 实现 ErrorRecovery 模块

**Files:**
- Create: `.claude/skills/task-flow/src/error_recovery.py`
- Test: `.claude/skills/task-flow/tests/test_error_recovery.py`

**Step 1: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_error_recovery.py -v`

Expected: FAIL with "ModuleNotFoundError: error_recovery"

**Step 2: Write minimal implementation**

```python
# error_recovery.py
class RetryableError(Exception):
    pass

class PermanentError(Exception):
    pass

class ErrorRecovery:
    def __init__(self, base_delay: float = 0.1):
        ...

    def retry_with_backoff(self, operation, max_attempts=3, should_retry=None):
        ...

    def generate_recovery_prompt(self, error: Exception, attempts: int, suggestions=None) -> str:
        ...

    def get_statistics(self) -> dict:
        ...
```

**Step 3: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_error_recovery.py -v`

Expected: PASS

**Step 4: Commit**

```bash
git add .claude/skills/task-flow/src/error_recovery.py .claude/skills/task-flow/tests/test_error_recovery.py
git commit -m "feat(task-flow): add error recovery utilities"
```

---

### Task 1: 实现 TaskStateMachine 模块

**Files:**
- Create: `.claude/skills/task-flow/src/task_state_machine.py`
- Test: `.claude/skills/task-flow/tests/test_task_state_machine.py`

**Step 1: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_task_state_machine.py -v`

Expected: FAIL with "ModuleNotFoundError: task_state_machine"

**Step 2: Write minimal implementation**

```python
# task_state_machine.py
class TransitionError(Exception):
    pass

class TaskState:
    ...

class TaskStateMachine:
    def transition(self, from_state, to_state, reason=None):
        ...

    def get_history(self):
        ...
```

**Step 3: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_task_state_machine.py -v`

Expected: PASS

**Step 4: Commit**

```bash
git add .claude/skills/task-flow/src/task_state_machine.py .claude/skills/task-flow/tests/test_task_state_machine.py
git commit -m "feat(task-flow): add task state machine"
```

---

### Task 2: 实现 GitOperations 模块

**Files:**
- Create: `.claude/skills/task-flow/src/git_operations.py`
- Test: `.claude/skills/task-flow/tests/test_git_operations.py`

**Step 1: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_git_operations.py -v`

Expected: FAIL with "ModuleNotFoundError: git_operations"

**Step 2: Write minimal implementation**

```python
# git_operations.py
class GitOperations:
    def has_remote(self):
        ...
    def smart_push(self, branch):
        ...
    def create_worktree(self, branch, worktree_path):
        ...
    def cleanup_branch(self, branch, worktree_path):
        ...
    def detect_potential_conflicts(self, branch):
        ...
```

**Step 3: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_git_operations.py -v`

Expected: PASS

**Step 4: Commit**

```bash
git add .claude/skills/task-flow/src/git_operations.py .claude/skills/task-flow/tests/test_git_operations.py
git commit -m "feat(task-flow): add git operations layer"
```

---

### Task 3: 实现 MergeOracle 模块

**Files:**
- Create: `.claude/skills/task-flow/src/merge_oracle.py`
- Test: `.claude/skills/task-flow/tests/test_merge_oracle.py`

**Step 1: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_merge_oracle.py -v`

Expected: FAIL with "ModuleNotFoundError: merge_oracle"

**Step 2: Write minimal implementation**

```python
# merge_oracle.py
class MergeOracle:
    def detect_potential_conflicts(self, branch):
        ...
    def smart_merge(self, branch, target_branch="main"):
        ...
```

**Step 3: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_merge_oracle.py -v`

Expected: PASS

**Step 4: Commit**

```bash
git add .claude/skills/task-flow/src/merge_oracle.py .claude/skills/task-flow/tests/test_merge_oracle.py
# 依赖 git_operations.py

git commit -m "feat(task-flow): add merge oracle"
```

---

### Task 4: 明确计划步骤规范与解析规则

**Files:**
- Modify: `docs/plans/2026-02-03-automation-mvp.md`
- Modify: `.claude/skills/task-flow/src/plan_generator/__init__.py`
- Test: `.claude/skills/task-flow/tests/`

**Step 1: Write the failing test**

```python
# tests/test_plan_parser.py

def test_plan_step_requires_run_and_expect():
    plan = """
    ### Step 1: Run tests
    Run: pytest -q
    """
    errors = validate_plan_steps(plan)
    assert "Expect" in errors[0]
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_plan_parser.py::test_plan_step_requires_run_and_expect -v`

Expected: FAIL with "validate_plan_steps not implemented"

**Step 3: Write minimal implementation**

```python
# plan_generator/__init__.py

def validate_plan_steps(plan_text: str) -> list[str]:
    errors = []
    # parse blocks, ensure Run/Expect present
    return errors
```

**Step 4: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_plan_parser.py::test_plan_step_requires_run_and_expect -v`

Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/src/plan_generator/__init__.py .claude/skills/task-flow/tests/test_plan_parser.py docs/plans/2026-02-03-automation-mvp.md
git commit -m "feat(task-flow): add plan step validation"
```

---

### Task 2: 计划校验器（Plan Validator）

**Files:**
- Modify: `.claude/skills/task-flow/src/execution_engine.py`
- Test: `.claude/skills/task-flow/tests/test_execution_engine.py`

**Step 1: Write the failing test**

```python
# tests/test_execution_engine.py

def test_execution_fails_on_invalid_plan():
    result = execute_plan(plan_text="### Step 1\nRun: pytest -q\n")
    assert result.status == "failed"
    assert "Expect" in result.errors[0]
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_execution_engine.py::test_execution_fails_on_invalid_plan -v`

Expected: FAIL (execute_plan missing validation)

**Step 3: Write minimal implementation**

```python
# execution_engine.py

def execute_plan(plan_text: str):
    errors = validate_plan_steps(plan_text)
    if errors:
        return ExecutionResult(status="failed", errors=errors)
```

**Step 4: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_execution_engine.py::test_execution_fails_on_invalid_plan -v`

Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/src/execution_engine.py .claude/skills/task-flow/tests/test_execution_engine.py
git commit -m "feat(task-flow): enforce plan validation before execution"
```

---

### Task 3: 步骤执行器（Step Runner）

**Files:**
- Modify: `.claude/skills/task-flow/src/execution_engine.py`
- Test: `.claude/skills/task-flow/tests/test_execution_engine.py`

**Step 1: Write the failing test**

```python
# tests/test_execution_engine.py

def test_step_runner_marks_failed_on_command_error():
    plan = """
    ### Step 1: Bad command
    Run: false
    Expect: PASS
    """
    result = execute_plan(plan_text=plan)
    assert result.status == "failed"
    assert result.steps[0].status == "failed"
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_execution_engine.py::test_step_runner_marks_failed_on_command_error -v`

Expected: FAIL (step runner not implemented)

**Step 3: Write minimal implementation**

```python
# execution_engine.py

def run_step(step):
    completed = subprocess.run(step.run, shell=True)
    if completed.returncode != 0:
        return StepResult(status="failed")
    return StepResult(status="passed")
```

**Step 4: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_execution_engine.py::test_step_runner_marks_failed_on_command_error -v`

Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/src/execution_engine.py .claude/skills/task-flow/tests/test_execution_engine.py
git commit -m "feat(task-flow): add step runner for plan execution"
```

---

### Task 4: 质量门运行与结果记录

**Files:**
- Modify: `.claude/skills/task-flow/src/ci_detector.py`
- Modify: `.claude/skills/task-flow/src/execution_engine.py`
- Test: `.claude/skills/task-flow/tests/test_ci_detector.py`

**Step 1: Write the failing test**

```python
# tests/test_ci_detector.py

def test_quality_gate_command_is_used_in_execution():
    cmd = detect_ci_command(project_root="/tmp/project")
    assert cmd is not None
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_ci_detector.py::test_quality_gate_command_is_used_in_execution -v`

Expected: FAIL if no command is detected

**Step 3: Write minimal implementation**

```python
# execution_engine.py

def run_quality_gate(cmd: str) -> GateResult:
    completed = subprocess.run(cmd, shell=True)
    return GateResult(status="passed" if completed.returncode == 0 else "failed")
```

**Step 4: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_ci_detector.py::test_quality_gate_command_is_used_in_execution -v`

Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/src/ci_detector.py .claude/skills/task-flow/src/execution_engine.py .claude/skills/task-flow/tests/test_ci_detector.py
git commit -m "feat(task-flow): run quality gate after execution"
```

---

### Task 5: 任务状态自动更新

**Files:**
- Modify: `.claude/skills/task-flow/src/task_manager.py`
- Modify: `.claude/skills/task-flow/src/execution_engine.py`
- Test: `.claude/skills/task-flow/tests/test_task_manager.py`

**Step 1: Write the failing test**

```python
# tests/test_task_manager.py

def test_task_updates_step_after_each_execution():
    task = load_task("TASK-001")
    update_task_step(task, 1)
    assert task.current_step == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_task_manager.py::test_task_updates_step_after_each_execution -v`

Expected: FAIL if update not implemented

**Step 3: Write minimal implementation**

```python
# task_manager.py

def update_task_step(task, step: int):
    task.current_step = step
    save_task(task)
```

**Step 4: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_task_manager.py::test_task_updates_step_after_each_execution -v`

Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/src/task_manager.py .claude/skills/task-flow/src/execution_engine.py .claude/skills/task-flow/tests/test_task_manager.py
git commit -m "feat(task-flow): update task step during execution"
```

---

### Task 6: 执行报告输出

**Files:**
- Modify: `.claude/skills/task-flow/src/execution_engine.py`
- Test: `.claude/skills/task-flow/tests/test_execution_engine.py`

**Step 1: Write the failing test**

```python
# tests/test_execution_engine.py

def test_execution_report_contains_steps_and_gate_result():
    report = build_execution_report(result)
    assert "steps" in report
    assert "quality_gate" in report
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_execution_engine.py::test_execution_report_contains_steps_and_gate_result -v`

Expected: FAIL (report builder missing)

**Step 3: Write minimal implementation**

```python
# execution_engine.py

def build_execution_report(result) -> dict:
    return {"steps": result.steps, "quality_gate": result.quality_gate}
```

**Step 4: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_execution_engine.py::test_execution_report_contains_steps_and_gate_result -v`

Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/src/execution_engine.py .claude/skills/task-flow/tests/test_execution_engine.py
git commit -m "feat(task-flow): add execution report output"
```

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-02-03-automation-mvp-implementation-plan.md`. Two execution options:

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration
2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
