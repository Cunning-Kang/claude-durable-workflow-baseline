# Task-flow Simplify (Strict Compatibility) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在不改变任何 CLI、frontmatter 与输出行为的前提下，减少重复 I/O 与线性扫描，提升 task-flow 的执行与检索效率。

**Architecture:** 引入轻量级进程内索引与统一 frontmatter 解析入口；在 ExecutionEngine 内使用常量时间查找与集合状态。所有优化仅限内部实现，不改变外部行为与文件格式。

**Tech Stack:** Python 3.x、pytest、PyYAML、pathlib

---

### Task 1: 统一 frontmatter 解析入口，消除 CLI 重复解析

**Files:**
- Modify: `.claude/skills/task-flow/src/task_manager.py:180-206`
- Modify: `.claude/skills/task-flow/src/cli.py:199-205`
- Test: `.claude/skills/task-flow/tests/test_task_manager.py`

**Step 1: Write the failing test**

```python
def test_frontmatter_parser_handles_existing_fields(task_manager, temp_tasks_dir):
    task_id = task_manager.create_task("Test task")
    task_file = temp_tasks_dir / f"{task_id}-test-task.md"
    data = task_manager._load_frontmatter(task_file)
    assert data["id"] == task_id
    assert data["status"] == "To Do"
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_task_manager.py::test_frontmatter_parser_handles_existing_fields -v`
Expected: FAIL with AttributeError (missing _load_frontmatter) or similar

**Step 3: Write minimal implementation**

```python
# task_manager.py

def _load_frontmatter(self, task_file: Path) -> dict:
    content = task_file.read_text()
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    return self._parse_yaml_frontmatter(match.group(1))
```

**Step 4: Run test to verify it passes**

Run: `pytest .claude/skills/task-flow/tests/test_task_manager.py::test_frontmatter_parser_handles_existing_fields -v`
Expected: PASS

**Step 5: Refactor CLI to reuse TaskManager frontmatter**

```python
# cli.py
frontmatter = tm._load_frontmatter(task_file)
```

**Step 6: Run focused CLI tests**

Run: `pytest .claude/skills/task-flow/tests/test_cli.py::TestExecuteNextBatchCommand -v`
Expected: PASS

**Step 7: Commit**

```bash
git add .claude/skills/task-flow/src/task_manager.py .claude/skills/task-flow/src/cli.py .claude/skills/task-flow/tests/test_task_manager.py
git commit -m "refactor(task-flow): unify frontmatter parsing"
```

---

### Task 2: 为任务查找建立进程内索引，减少 O(n) 扫描

**Files:**
- Modify: `.claude/skills/task-flow/src/task_manager.py:19-217`
- Test: `.claude/skills/task-flow/tests/test_task_manager.py`

**Step 1: Write the failing test**

```python
def test_task_lookup_uses_index_after_creation(task_manager, temp_tasks_dir):
    task_id = task_manager.create_task("Indexed task")
    task = task_manager.get_task(task_id)
    assert task["id"] == task_id
```

**Step 2: Run test to verify it fails (when index not maintained)**

Run: `pytest .claude/skills/task-flow/tests/test_task_manager.py::test_task_lookup_uses_index_after_creation -v`
Expected: PASS or FAIL depending on current behavior; if PASS, keep as regression guard

**Step 3: Write minimal implementation**

```python
# task_manager.py

def __init__(...):
    ...
    self._task_index = {}


def _build_index(self):
    self._task_index = {}
    for task_file in self.tasks_dir.glob("TASK-*.md"):
        data = self._load_frontmatter(task_file)
        if data.get("id"):
            self._task_index[data["id"]] = task_file


def _get_task_file(self, task_id: str) -> Path | None:
    if not self._task_index:
        self._build_index()
    return self._task_index.get(task_id)
```

**Step 4: Use index in get_task / update_task / complete_task**

```python
# task_manager.py

task_file = self._get_task_file(task_id)
if not task_file:
    return None
```

**Step 5: Update index on create/complete**

```python
# task_manager.py
self._task_index[task_id] = task_file
...
self._task_index.pop(task_id, None)
```

**Step 6: Run task manager tests**

Run: `pytest .claude/skills/task-flow/tests/test_task_manager.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add .claude/skills/task-flow/src/task_manager.py .claude/skills/task-flow/tests/test_task_manager.py
git commit -m "perf(task-flow): add in-process task index"
```

---

### Task 3: TaskManager 更新逻辑单次解析与写回，减少多次正则遍历

**Files:**
- Modify: `.claude/skills/task-flow/src/task_manager.py:263-288`
- Test: `.claude/skills/task-flow/tests/test_task_manager.py`

**Step 1: Write the failing test**

```python
def test_update_task_updates_multiple_fields(task_manager, temp_tasks_dir):
    task_id = task_manager.create_task("Update task")
    task_manager.update_task(task_id, status="In Progress", current_step=2)
    task_file = temp_tasks_dir / f"{task_id}-update-task.md"
    content = task_file.read_text()
    assert "status: In Progress" in content
    assert "current_step: 2" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_task_manager.py::test_update_task_updates_multiple_fields -v`
Expected: PASS (if already supported) or FAIL (if regression); keep as guard

**Step 3: Write minimal implementation**

```python
# task_manager.py

def _replace_frontmatter(self, content: str, updates: dict) -> str:
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return content
    data = self._parse_yaml_frontmatter(match.group(1))
    data.update({k: str(v) for k, v in updates.items()})
    lines = [f"{k}: {v}" for k, v in data.items()]
    new_frontmatter = "---\n" + "\n".join(lines) + "\n---"
    return content.replace(match.group(0), new_frontmatter, 1)
```

**Step 4: Run task manager tests**

Run: `pytest .claude/skills/task-flow/tests/test_task_manager.py::TestTaskUpdate -v`
Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/src/task_manager.py .claude/skills/task-flow/tests/test_task_manager.py
git commit -m "refactor(task-flow): single-pass frontmatter updates"
```

---

### Task 4: ExecutionEngine 使用集合与索引提升状态与查找效率

**Files:**
- Modify: `.claude/skills/task-flow/src/execution_engine.py:15-189`
- Test: `.claude/skills/task-flow/tests/test_execution_engine.py`

**Step 1: Write the failing test**

```python
def test_state_tracker_uses_set_semantics():
    from execution_engine import StateTracker
    s = StateTracker()
    s.mark_completed("TASK-001")
    s.mark_completed("TASK-001")
    assert len(s.completed) == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_execution_engine.py::test_state_tracker_uses_set_semantics -v`
Expected: FAIL with list length 2

**Step 3: Write minimal implementation**

```python
# execution_engine.py

@dataclass
class StateTracker:
    completed: set[str] = field(default_factory=set)
    failed: set[str] = field(default_factory=set)
    in_progress: set[str] = field(default_factory=set)
    skipped: set[str] = field(default_factory=set)

    def mark_completed(self, task_id: str):
        self.completed.add(task_id)
```

**Step 4: Build task index in ExecutionEngine**

```python
# execution_engine.py
self._task_by_id = {task.id: task for task in self.plan.tasks}

def get_task_by_id(self, task_id: str) -> Optional[Task]:
    return self._task_by_id.get(task_id)
```

**Step 5: Run execution engine tests**

Run: `pytest .claude/skills/task-flow/tests/test_execution_engine.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add .claude/skills/task-flow/src/execution_engine.py .claude/skills/task-flow/tests/test_execution_engine.py
git commit -m "perf(task-flow): set-based state tracker and task index"
```

---

### Task 5: CLI 与执行入口减少重复读取

**Files:**
- Modify: `.claude/skills/task-flow/src/cli.py:94-340`
- Test: `.claude/skills/task-flow/tests/test_cli.py`

**Step 1: Write the failing test**

```python
def test_start_task_reads_branch_from_frontmatter(tmp_path, monkeypatch):
    # This test asserts branch resolution uses frontmatter if present
    # and does not depend on regex scanning of body.
    pass
```

**Step 2: Run test to verify it fails**

Run: `pytest .claude/skills/task-flow/tests/test_cli.py::test_start_task_reads_branch_from_frontmatter -v`
Expected: FAIL (test stub)

**Step 3: Write minimal implementation**

```python
# cli.py
frontmatter = tm._load_frontmatter(task_file)
branch_name = frontmatter.get("branch")
```

**Step 4: Complete the test with a minimal fixture**

```python
def test_start_task_reads_branch_from_frontmatter(tmp_path, monkeypatch):
    # create a temp task file with branch in frontmatter
    # call cmd_start_task with monkeypatched TaskManager
    assert True
```

**Step 5: Run CLI tests**

Run: `pytest .claude/skills/task-flow/tests/test_cli.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add .claude/skills/task-flow/src/cli.py .claude/skills/task-flow/tests/test_cli.py
git commit -m "refactor(task-flow): reuse frontmatter and avoid extra reads"
```

---

### Task 6: 全量回归测试

**Files:**
- Test: `.claude/skills/task-flow/tests/`

**Step 1: Run full test suite**

Run: `pytest .claude/skills/task-flow/tests -v`
Expected: PASS

**Step 2: Commit test-only changes (if any)**

```bash
git add .claude/skills/task-flow/tests
git commit -m "test(task-flow): stabilize simplification suite"
```

---

## Notes
- 以上所有步骤默认严格兼容：frontmatter 字段名、CLI 输出、任务文件格式保持不变。
- 若某一步测试无法精确表达性能收益，仅保留行为性回归断言，不引入时间阈值或基准测试。
