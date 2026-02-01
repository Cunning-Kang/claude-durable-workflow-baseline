# Task-Flow + Superpowers Integration Implementation Plan (Executable)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在不依赖外部服务的前提下，把 task-flow（任务持久化/协议）与 superpowers（工作流编排）通过文件系统协议松耦合起来，并实现一个可测试、可演进的 Execution Engine：从计划生成 → 依赖解析 → 分批执行（可替换为真实 subagent）→ 状态持久化 → 错误恢复/合并回收 的闭环。

**Architecture:**
- **Layer 1（持久化/协议边界）**：`docs/tasks/*.md` YAML frontmatter 是系统契约；`TaskManager` 仅负责 CRUD、索引与字段更新。
- **Layer 2（编排）**：superpowers skills 决定“何时做什么”（brainstorming/writing-plans/executing-plans/worktrees），不把业务逻辑塞进 CLI。
- **Layer 3（执行）**：Execution Engine 只做“把 plan 变成执行结果”：`DependencyResolver` 选 ready → `TaskDispatcher` 分派 → `SubagentPool` 执行（当前 stub，未来替换为真实 subagent）→ `StateTracker` 写回 frontmatter。

**Tech Stack:**
- Python 3.10（mise）
- pytest（必须用 `task-flow/pytest.ini`，其中 `pythonpath = src`）
- YAML frontmatter（任务文件协议）
- Git worktree（隔离开发）

---

## 0. 关键事实（执行前必须理解）

### 0.1 单一事实来源（Source of Truth）策略

历史上曾在两个位置直接读写：
- repo：`/Users/cunning/Workspaces/heavy/skills-creation/task-flow/`
- 全局 skills：`/Users/cunning/.claude/skills/task-flow/`

**本计划强制要求：**
1) **开发与测试只在 repo/worktree 内进行**（即 `skills-creation/` 下的 worktree）
2) **全局 skills 只作为“部署目标”**（用 rsync 从 repo 同步过去）

### 0.2 质量入口（唯一可信）

在 repo 根目录运行：
```bash
pytest -q -c task-flow/pytest.ini
```

不要用 `pytest -q`（会遇到 import path/collect 差异）。

---

## 1. 当前代码库现状（截至本计划编写时）

### 1.1 task-flow 核心
- `task-flow/src/task_manager.py`：任务文件 CRUD + frontmatter 字段更新 + 归档
- `task-flow/src/cli.py`：create/list/show/start/update/complete 入口
- `task-flow/src/git_operations.py`：git 操作抽象（worktree/cleanup/push 等）
- `task-flow/src/merge_oracle.py`：冲突风险检测 + smart merge（面向任务文件）
- `task-flow/src/task_state_machine.py`：状态机（To Do/In Progress/Done/Blocked/Cancelled）
- `task-flow/src/error_recovery.py`：重试与统计

### 1.2 Plan Generator
- `task-flow/src/plan_generator/*`：可从 Plan Packet / 项目扫描生成计划产物（现有测试覆盖）

### 1.3 Execution Engine（已存在但需要“闭环接线”）
- `task-flow/src/execution_engine/controller.py`：批处理/检查点逻辑（当前为模拟执行）
- `task-flow/src/execution_engine/dependency_resolver.py`：ready tasks + cycle detection
- `task-flow/src/execution_engine/state_tracker.py`：执行状态写回 frontmatter
- `task-flow/src/execution_engine/engine.py`：当前仅做 ready 选择 + 标记 IN_PROGRESS（需要升级为闭环）

此外：
- `task-flow/src/execution_engine/task_dispatcher.py`：存在（分派并更新 TaskStatus）
- `task-flow/src/execution_engine/subagent_pool/pool.py`：存在（最小可用 stub，执行 callable）

---

## 2. Implementation Plan（严格可执行，按 TDD 拆成“咬一口大小”步骤）

> 执行本计划时：
> - 每个 Task 结束都要 commit
> - 每个 Task 的每一步都能在 2-5 分钟内完成
> - 严格 RED→GREEN→REFACTOR

### Task 1: 基线与环境校验（在 worktree 中开始前）

**Files:**
- Modify: `.gitignore`（必要时）

**Step 1: 确认 worktree 目录存在且被忽略**

Run:
```bash
ls -d .worktrees 2>/dev/null || mkdir -p .worktrees

git check-ignore -v .worktrees/ || true
```
Expected:
- `.worktrees/` 存在
- `git check-ignore -v` 能输出来源规则（例如 `.gitignore:...:.worktrees/`）

**Step 2: 创建/进入开发 worktree（如果尚未建立）**

Run:
```bash
git worktree add ".worktrees/feat-execution-engine-remaining" -b "feat/execution-engine-remaining"
```
Expected: worktree 创建成功。

**Step 3: worktree 基线测试**

Run:
```bash
cd .worktrees/feat-execution-engine-remaining
pytest -q -c task-flow/pytest.ini
```
Expected: PASS。

**Step 4: Commit（仅当 Task 1 有改动）**

Run:
```bash
git add .gitignore
git commit -m "chore: ignore worktree directories"
```

---

### Task 2: ExecutionEngine 执行闭环（把 Dispatcher + Pool + StateTracker 接入 Engine）

**Goal:** 让 `ExecutionEngine.execute_next_batch()` 真正执行 ready tasks：
- 依赖解析（ready selection）
- 分派执行（dispatcher）
- 执行抽象（pool，当前 stub）
- 状态持久化（state_tracker）

**关键设计约束（必须遵守）**
- 当前阶段不调用真实 Claude subagent；只用本地 callable（通过依赖注入/metadata）
- 不修改 CLI 行为（CLI 接入放到后续 Task）
- 最小化对现有测试的破坏：新增测试为主，必要时小范围调整

**Files:**
- Modify: `task-flow/src/execution_engine/engine.py`
- Test (Create): `task-flow/tests/execution_engine/test_engine_execution_loop.py`

#### Step 1: 写 failing test（闭环最小行为）

Create file: `task-flow/tests/execution_engine/test_engine_execution_loop.py`

```python
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
```

> 说明：本测试强制定义“callable 来源”= `Task.metadata["callable"]`。
> 如果未来你决定改成 executor_factory 注入，那么这个测试就是我们必须更新的契约。

#### Step 2: 运行测试确认 RED

Run:
```bash
pytest -q -c task-flow/pytest.ini task-flow/tests/execution_engine/test_engine_execution_loop.py
```
Expected: FAIL（Engine 尚未真正执行任务/写回状态）。

#### Step 3: 最小实现（Engine 执行闭环）

Modify file: `task-flow/src/execution_engine/engine.py`

实现要点（最小可测）：
1) `execute_next_batch()` 选 ready tasks（保持现状的 resolver 同步与筛选）
2) 为 batch 中每个 task：
   - 用 `StateTracker(task_file).start_task(task.id, task.title)` 写 running
   - 取 `callable = task.metadata.get("callable")`
   - 若 callable 不存在：将 task 标记 FAILED（并写回 state）
   - 否则用 `SubagentPool.submit(task.id, callable)` 执行
   - 根据 result.ok 更新 TaskStatus（COMPLETED/FAILED）
   - 对 COMPLETED 调 `complete_task`
   - 对 FAILED 用 `update_execution_state({"status": "failed", "error": ...})`（如果不想扩展 StateTracker API，就直接用 update_execution_state）
3) 返回统计 dict：
   - `tasks_executed` = 实际 dispatch 数
   - `batch_size` = 同上
   - `total_completed` = plan 中 COMPLETED 数

> 切记：不要引入新的抽象层（YAGNI）。先让测试绿。

#### Step 4: 运行测试确认 GREEN

Run:
```bash
pytest -q -c task-flow/pytest.ini task-flow/tests/execution_engine/test_engine_execution_loop.py
```
Expected: PASS。

#### Step 5: 全量回归

Run:
```bash
pytest -q -c task-flow/pytest.ini
```
Expected: PASS。

#### Step 6: Commit

Run:
```bash
git add task-flow/src/execution_engine/engine.py task-flow/tests/execution_engine/test_engine_execution_loop.py

git commit -m "$(cat <<'EOF'
feat(execution-engine): execute ready tasks via pool and persist state

Wire ExecutionEngine to run ready tasks using SubagentPool callables and persist execution_state through StateTracker.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: 导出与接口整理（仅在需要时）

**Goal:** 保持导入方式清晰一致，不破坏既有 `test_exports_and_types.py` 的约束。

**Files:**
- Modify (Optional): `task-flow/src/execution_engine/__init__.py`
- Test (Optional): `task-flow/tests/execution_engine/test_exports_and_types.py`

**Step 1: 如果需要导出新组件（TaskDispatcher/SubagentPool），先写 failing test**

在 `test_exports_and_types.py` 中新增断言（先 FAIL）。

**Step 2: 实现导出**

在 `execution_engine/__init__.py` 中加入 export，并同步更新 test 的 expected __all__。

**Step 3: 全量回归 + Commit**

---

### Task 4（可选里程碑）: CLI 接入 ExecutionEngine 的“执行下一批”命令

> 仅当你决定把 ExecutionEngine 暴露为 CLI 子命令时执行。

**Files:**
- Modify: `task-flow/src/cli.py`
- Test: `task-flow/tests/test_cli.py`

目标：新增一个 `execute-next-batch TASK-XXX` 或 `run TASK-XXX` 命令（具体命名先在 brainstorming 阶段定）。

---

### Task 5: 部署同步（repo → 全局 skills）

**Goal:** 把已验证通过的 repo 版本同步到 `/Users/cunning/.claude/skills/task-flow/` 供 Claude Code 实际调用。

**Step 1: 预览（dry-run）**

Run:
```bash
rsync -avn --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='.git/' --exclude='.DS_Store' \
  "task-flow/" \
  "/Users/cunning/.claude/skills/task-flow/" | sed -n '1,200p'
```
Expected: 只看到预期的新增/覆盖文件。

**Step 2: 同步**

Run:
```bash
rsync -av --exclude='__pycache__/' --exclude='.pytest_cache/' --exclude='.git/' --exclude='.DS_Store' \
  "task-flow/" \
  "/Users/cunning/.claude/skills/task-flow/"
```

**Step 3: 在全局 skills 目录跑一次关键测试（可选）**

Run:
```bash
cd /Users/cunning/.claude/skills/task-flow
pytest -q
```
Expected: PASS（如果环境差异导致失败，必须先回到 repo 查清原因再处理）。

---

## 3. 执行交接（选择一种方式执行本计划）

Plan complete and saved to `docs/plans/2026-02-01-task-flow-superpowers-integration.md`.

Two execution options:

1) **Subagent-Driven（本会话）**
- 使用 `@superpowers:subagent-driven-development`
- 每个 Task 用独立 subagent 实现，主线程 review、确保 TDD 与提交节奏

2) **Parallel Session（新会话）**
- 在 worktree 中开启新会话
- 使用 `@superpowers:executing-plans` 按 Task 批次执行并在 checkpoint 汇报

---

## 4. Execution State 写回规范（默认版）

## 1. 目标与范围
**目标**
定义 `execution_state` 在任务文件 frontmatter 中的语义、字段与写入时机，并澄清 `StateTracker`、`ExecutionEngine`、`ExecutionController` 的职责边界与 `TaskStatus` 的关系。

**非目标**
- 不定义 CLI 行为或命令行接口
- 不扩展新的状态字段或引入新依赖
- 不调整现有代码实现（仅说明现状与约束）

---

## 2. 参与组件与职责
- **StateTracker**：读写任务文件 YAML frontmatter，持久化 `execution_state`。
  参考：`task-flow/src/execution_engine/state_tracker.py:23-198`

- **ExecutionController**：负责批次大小与检查点策略，仅在内存中更新 `Task.status`，不写文件。
  参考：`task-flow/src/execution_engine/controller.py:7-125`

- **ExecutionEngine**：协调依赖解析与批次选择；当前实现只在任务已为 `COMPLETED` 时调用 `StateTracker.complete_task`，不调用 `start_task`。
  参考：`task-flow/src/execution_engine/engine.py:103-157`

- **TaskStatus**：执行计划内任务状态枚举（`pending/in_progress/completed/failed/skipped`）。
  参考：`task-flow/src/plan_generator/types.py:8-15`

---

## 3. `execution_state` 字段语义

> **默认字段范围：完整列出所有已出现/已实现字段。**
> **状态字段只使用 `execution_state.status`，不使用 `execution_status`。**

### 3.1 核心字段
| 字段 | 类型 | 写入者 | 写入时机 | 说明 |
|---|---|---|---|---|
| `status` | string | `StateTracker` 或调用方 | `start_task/complete_task/update_execution_state` | 约定值：`running/completed/failed` |
| `started_at` | ISO 8601 string | `start_task` | 任务开始时 | 由 `datetime.now().isoformat()` 写入 |
| `completed_at` | ISO 8601 string | `complete_task` | 任务完成时 | 若无 `started_at` 也会写入 |
| `duration` | number \| null | `complete_task` | 任务完成时 | 秒数；解析失败时为 `None` |
| `task_id` | string | `start_task` | 任务开始时 | 标识任务 |
| `task_title` | string | `start_task` | 任务开始时 | 任务标题 |

### 3.2 进度与统计字段（默认补全）
由 `get_state` 在读取时补默认值：
`current_step`, `total_steps`, `completed_tasks`, `failed_tasks`
参考：`task-flow/src/execution_engine/state_tracker.py:146-179`

### 3.3 扩展字段
`update_execution_state` 允许写入任意键值（例如 `error`）。
参考：`task-flow/src/execution_engine/state_tracker.py:181-198`

---

## 4. 写入时机与更新规则

### 4.1 `start_task(task_id, title)`
- 写入 `status = "running"`、`started_at`、`task_id`、`task_title`
- 清理 `completed_at` 和 `duration`（用于重启场景）
- 参考：`task-flow/src/execution_engine/state_tracker.py:81-105`

### 4.2 `complete_task(task_id)`
- 写入 `status = "completed"`
- 计算并写入 `completed_at` 与 `duration`
- 若没有 `started_at`，则 `duration = 0`
- 参考：`task-flow/src/execution_engine/state_tracker.py:108-143`

### 4.3 `update_execution_state(state: dict)`
- 合并写入 `execution_state` 任意字段
- 用于进度更新与错误信息
- 参考：`task-flow/src/execution_engine/state_tracker.py:181-198`

### 4.4 文件不存在或 frontmatter 异常
- 任务文件不存在：不写入
- YAML 解析异常或无 frontmatter：不写入
- 参考：`task-flow/src/execution_engine/state_tracker.py:35-79`

---

## 5. `execution_state.status` 与 `TaskStatus` 的关系

- **`TaskStatus`** 是执行计划内的**工作流状态**，驱动依赖解析与批次执行。
  参考：`task-flow/src/plan_generator/types.py:8-15`

- **`execution_state.status`** 是任务文件里持久化的**执行运行状态**（运行态/完成态/失败态）。

- **二者不自动同步**：
  当前 `ExecutionEngine.execute_next_batch` 只会在 `task.status == COMPLETED` 时写回 `execution_state` 完成态。
  参考：`task-flow/src/execution_engine/engine.py:103-157`

**推荐映射（由调用方自行决定）：**
- `running` ↔ `TaskStatus.IN_PROGRESS`
- `completed` ↔ `TaskStatus.COMPLETED`
- `failed` ↔ `TaskStatus.FAILED`

---

## 6. `error` 字段语义（默认）
- `error` 为可选字符串，用于记录失败原因
- 不区分来源（例如 callable 缺失 / 执行异常），由调用方写入
- 写入方式：`update_execution_state({"status": "failed", "error": "..."})`

---

## 7. 示例 frontmatter（默认）

**运行态示例**
```yaml
---
execution_state:
  status: "running"
  started_at: "2026-02-01T12:00:00.000000"
  task_id: "1"
  task_title: "T1"
  current_step: 0
  total_steps: 0
  completed_tasks: []
  failed_tasks: []
---
```

**完成态示例**
```yaml
---
execution_state:
  status: "completed"
  started_at: "2026-02-01T12:00:00.000000"
  completed_at: "2026-02-01T12:05:30.000000"
  duration: 330.0
  task_id: "1"
  task_title: "T1"
  current_step: 3
  total_steps: 3
  completed_tasks: ["1"]
  failed_tasks: []
---
```

---

## 8. 约束与已知行为
- 不会创建新文件；文件缺失时不写入
- 仅支持标准 YAML frontmatter（按 `---` 分隔）
- 解析或保存失败会静默跳过
  参考：`task-flow/src/execution_engine/state_tracker.py:35-79`

---

## 9. 参考实现（源码位置）
- `StateTracker`：`task-flow/src/execution_engine/state_tracker.py:23-198`
- `ExecutionController`：`task-flow/src/execution_engine/controller.py:7-125`
- `ExecutionEngine.execute_next_batch`：`task-flow/src/execution_engine/engine.py:103-157`
- `TaskStatus`：`task-flow/src/plan_generator/types.py:8-15`
