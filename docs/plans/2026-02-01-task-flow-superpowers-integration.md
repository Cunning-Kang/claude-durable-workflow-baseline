# Task-Flow + Superpowers Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建完整的 LLM 友好任务自动化系统，实现 task-flow（任务持久化）与 superpowers（工作流编排）的松耦合集成，支持从 Plan Packet → 计划生成 → 分批执行 → 状态持久化 → 回滚/恢复 的闭环。

**Architecture:**
- **Layer 1（持久化）**：task-flow 负责任务 CRUD、Plan Packet 存储、YAML frontmatter 作为协议边界
- **Layer 2（编排）**：superpowers skills 负责任务级别编排（brainstorming / writing-plans / executing-plans / worktrees）
- **Layer 3（执行）**：Execution Engine 负责“把计划执行起来”，通过可测试的抽象（TaskDispatcher / SubagentPool）连接到真实子代理执行（后续阶段）

**Tech Stack:**
- Python 3.10（mise）
- pytest（使用 `task-flow/pytest.ini`，其中 `pythonpath = src`）
- YAML frontmatter（任务文件协议）
- Git worktree（隔离开发）

---

## 当前进度（截至 2026-02-01）

本计划最初版本在 Task 5-65 处为“简化占位”，无法直接被 executing-plans 按步骤执行；且历史实现存在“全局 skills 路径 vs repo 路径”双源写入。现已完成一次基线收敛：

### 已完成（在 repo 中可复现）

**Plan Generator**
- analyzer / project_scanner / task_breakdown / path_inference / plan_builder 已实现，并有对应测试。

**Execution Engine（核心组件）**
- ExecutionController / DependencyResolver / StateTracker / ExecutionEngine 已实现并有测试。

**task-flow（持久化与工具链）**
- cli / task_manager 及 git_operations / merge_oracle / task_state_machine / error_recovery 已实现，并包含 unit + e2e 测试。

### 当前可用的质量入口

- **推荐全量验证命令（在 repo 根目录）**：
  - `pytest -q -c task-flow/pytest.ini`

---

## 本次补全的 Implementation Plan（可执行版本）

> 本段开始，所有任务都按“可执行的最小步骤”编排，满足 executing-plans 所需粒度：
> - 每个 Task 包含：写 failing test → 运行确认 RED → 写最小实现 → 运行确认 GREEN → 必要重构 → 提交

### Task 0: 基线收敛（全局 skills ↔ repo）

**Goal:** 让 `task-flow/` 与 `/Users/cunning/.claude/skills/task-flow/` 在代码与测试层面一致，避免“双源漂移”。

**Files:**
- Modify: `.gitignore`（确保 `.worktrees/` 被忽略）
- Sync: `task-flow/`（从全局 skills 合并补全到 repo）

**Step 1: 预览差异（dry-run）**

Run:
```bash
rsync -avn --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='.git/' --exclude='.DS_Store' \
  "/Users/cunning/.claude/skills/task-flow/" \
  "task-flow/" | sed -n '1,200p'
```
Expected: 输出将新增/覆盖的文件清单（不删除 repo 现有额外文件）。

**Step 2: 执行合并补全同步**

Run:
```bash
rsync -av --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='.git/' --exclude='.DS_Store' \
  "/Users/cunning/.claude/skills/task-flow/" \
  "task-flow/"
```
Expected: 同步完成。

**Step 3: 全量测试验证**

Run:
```bash
pytest -q -c task-flow/pytest.ini
```
Expected: PASS（允许少量 skip，但不得失败）。

**Step 4: 提交基线收敛**

Run:
```bash
git add task-flow/
git commit -m "chore(task-flow): sync repo with global skill implementation"
```

---

### Task 1: 建立 Execution Engine 的“执行闭环”接口（把 Dispatcher/Pool 接入 Engine）

**Goal:** 让 `ExecutionEngine.execute_next_batch()` 不再只做状态标记，而是：
- 通过 `DependencyResolver` 获取 ready tasks
- 通过 `TaskDispatcher` 分派给执行器
- 通过 `SubagentPool`（当前为本地 callable 执行占位）运行任务
- 通过 `StateTracker` 持久化任务执行状态（running/completed/failed + timestamps/duration）

**Design Notes（约束）**
- 当前阶段不做真实 Claude subagent 调用；使用 `SubagentPool.submit()` 执行本地 callable
- 任务执行的“callable”从何而来：先用简单策略（例如 task.metadata["callable"] 或注入 executor_factory），保持可测试
- 不做 CLI 集成（放到后续 Task）

**Files:**
- Create: `task-flow/src/execution_engine/task_dispatcher.py`（若尚未存在）
- Create: `task-flow/src/execution_engine/subagent_pool/pool.py`（若尚未存在）
- Modify: `task-flow/src/execution_engine/engine.py`
- Modify: `task-flow/src/execution_engine/__init__.py`（导出新增组件，按现有测试要求更新/扩展）
- Test: `task-flow/tests/execution_engine/test_engine_execution_loop.py`（新增）

#### Step 1: 写 failing test（ExecutionEngine 闭环）

File: `task-flow/tests/execution_engine/test_engine_execution_loop.py`

```python
import pytest
from pathlib import Path

from plan_generator.types import ExecutionPlan, Task, TaskStatus


def test_engine_executes_ready_tasks_and_updates_state(tmp_path: Path):
    """Engine should dispatch + execute ready tasks and update Task + StateTracker."""
    from execution_engine.engine import ExecutionEngine

    tasks = [
        Task(id="1", title="T1", description="D1"),
        Task(id="2", title="T2", description="D2", dependencies=["1"]),
    ]
    plan = ExecutionPlan(tasks=tasks)

    # Prepare task files for state tracking
    for tid in ["1", "2"]:
        (tmp_path / f"{tid}.md").write_text("---\nexecution_state: {}\n---\n")

    engine = ExecutionEngine(plan, tmp_path)

    # Execute first batch: only task 1 is ready
    r1 = engine.execute_next_batch()
    assert r1["tasks_executed"] == 1
    assert tasks[0].status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
    assert tasks[1].status == TaskStatus.PENDING

    # If task 1 completed, task 2 becomes ready and can run
    if tasks[0].status == TaskStatus.COMPLETED:
        r2 = engine.execute_next_batch()
        assert r2["tasks_executed"] == 1
        assert tasks[1].status in (TaskStatus.COMPLETED, TaskStatus.FAILED)
```

#### Step 2: 运行测试确认 RED

Run:
```bash
pytest -q -c task-flow/pytest.ini task-flow/tests/execution_engine/test_engine_execution_loop.py
```
Expected: FAIL（Engine 目前未接入 dispatcher/pool，不会真的把 task 推到 completed/failed）。

#### Step 3: 最小实现（Engine 接入 dispatcher/pool）

Modify: `task-flow/src/execution_engine/engine.py`

实现要点：
- `ExecutionEngine.__init__` 增加 dispatcher/pool 初始化（可 lazy）
- `execute_next_batch`：
  - sync resolver
  - ready_ids
  - 交给 dispatcher 执行 batch，并根据 executor 结果更新 TaskStatus
  - 对每个任务：start_task/complete_task 或记录 failed

> 注意：先实现“最小可测闭环”，不要提前做真实 subagent。

#### Step 4: 运行测试确认 GREEN

Run:
```bash
pytest -q -c task-flow/pytest.ini task-flow/tests/execution_engine/test_engine_execution_loop.py
```
Expected: PASS

#### Step 5: 全量回归

Run:
```bash
pytest -q -c task-flow/pytest.ini
```
Expected: PASS

#### Step 6: 提交

Run:
```bash
git add task-flow/src/execution_engine/ task-flow/tests/execution_engine/
git commit -m "feat(execution-engine): wire dispatcher and pool into engine"
```

---

### Task 2: 扩展 StateTracker 支持失败状态（可选）

如果闭环测试需要记录失败状态到 frontmatter（status: failed / error），再做此任务。

---

### Task 3: CLI/TaskManager 接入（可选，后续里程碑）

保持为可选：在 Engine 闭环稳定后再引入用户接口。

---

## Worktree 工作流（强制）

- 在 main 完成“基线收敛提交”后，再在 worktree 分支继续开发。
- 每次实现前运行：`pytest -q -c task-flow/pytest.ini` 确认基线干净。

---

## Risks & Rollback

- Risk: 全局 skills 与 repo 双源漂移
  - Rollback: 以本 Task 0 的“基线收敛提交”为锚点；后续所有改动必须先进入 repo，再按部署节奏同步到全局 skills。
- Risk: Engine 闭环引入过度抽象
  - Rollback: 保持 dispatcher/pool 为最小接口；真实 subagent 执行放到后续里程碑。
