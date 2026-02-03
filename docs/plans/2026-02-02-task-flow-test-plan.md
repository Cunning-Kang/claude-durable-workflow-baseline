# task-flow Test Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在真实项目场景中对 `task-flow` 进行全流程验证，定位潜在问题并通过 TDD 补测与修复。

**Architecture:** 以真实仓库为宿主，使用隔离测试项目目录运行 CLI 与 Git 流程，覆盖 create/start/update/complete/execute-next-batch/todowrite 全链路。以 pytest 为主，辅以命令行实测与断言文件系统副作用。

**Tech Stack:** Python 3.10, pytest, git, task-flow CLI

---

## 0. 前置说明

- 代码位置：`/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/`
- 源码路径：`/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/src/`
- 测试路径：`/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/tests/`
- CLI 入口：`python -m cli`（需 `PYTHONPATH=.../src`）
- 关键命令：`create-task` / `list-tasks` / `show-task` / `start-task` / `update-task` / `complete-task` / `execute-next-batch` / `todowrite`

> 注意：当前 `src` 目录中仅存在 `cli.py` 与 `task_manager.py`，但测试与 CLI 引用了一些缺失模块（如 `execution_engine`, `plan_generator`, `ci_detector`, `todowrite_compat`）。本测试计划将把“模块缺失导致的导入错误”作为核心风险点优先验证。

---

## Task 1: 建立真实场景测试基线（不修改代码）

**Files:**
- Verify: `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/src/`
- Verify: `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/tests/`

**Step 1: 设置测试环境变量**

```bash
export TASK_FLOW_ROOT="/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow"
export PYTHONPATH="$TASK_FLOW_ROOT/src"
```

**Step 2: 运行现有测试套件**

Run:
```bash
pytest -q "$TASK_FLOW_ROOT/tests"
```

Expected: 当前应出现导入错误或失败用例（记录具体失败信息作为问题清单）。

**Step 3: 记录失败清单**

- 记录缺失模块名
- 记录对应测试文件与错误堆栈
- 记录 CLI 运行时是否也会触发相同导入错误

---

## Task 2: CLI 核心流程真实场景测试（无修复）

**Files:**
- Source: `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/src/cli.py`
- Source: `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/src/task_manager.py`

**Step 1: 创建隔离临时项目目录**

Run:
```bash
TMP_PROJECT="/tmp/claude/task-flow-e2e-$(date +%s)"
mkdir -p "$TMP_PROJECT"
cd "$TMP_PROJECT"

git init

git config user.email "test@example.com"
git config user.name "Test User"

mkdir -p docs/tasks
```

**Step 2: create-task**

Run:
```bash
python -m cli create-task "Implement feature" \
  --project-root "$TMP_PROJECT"
```

Expected:
- 生成 `docs/tasks/TASK-001-implement-feature.md`
- `_index.json` 自动初始化

**Step 3: list-tasks**

Run:
```bash
python -m cli list-tasks --project-root "$TMP_PROJECT"
```

Expected:
- 输出包含 TASK-001

**Step 4: show-task**

Run:
```bash
python -m cli show-task TASK-001 --project-root "$TMP_PROJECT"
```

Expected:
- 输出包含 TASK-001 与 Plan Packet

**Step 5: start-task（真实 git worktree）**

Run:
```bash
python -m cli start-task TASK-001 --project-root "$TMP_PROJECT"
```

Expected:
- 创建 `.worktrees/implement-feature`
- 任务文件中 `status: In Progress`
- 任务文件中 `worktree: .worktrees/implement-feature`

**Step 6: update-task**

Run:
```bash
python -m cli update-task TASK-001 --step 2 --note "Test note" --project-root "$TMP_PROJECT"
```

Expected:
- YAML frontmatter `current_step: 2`
- Notes section 插入备注

**Step 7: complete-task**

Run:
```bash
python -m cli complete-task TASK-001 --project-root "$TMP_PROJECT"
```

Expected:
- 任务文件移动至 `docs/tasks/completed/`
- `_index.json` 记录 completed_tasks

---

## Task 3: execute-next-batch 流程验证

**Files:**
- Source: `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/src/cli.py`

**Step 1: 准备 YAML 计划文件**

Run:
```bash
mkdir -p "$TMP_PROJECT/docs/plans"
cat > "$TMP_PROJECT/docs/plans/execution-plan.yaml" <<'EOF'
tasks:
- id: TASK-001
  title: Step 1
  description: First step
- id: TASK-002
  title: Step 2
  description: Second step
  dependencies:
    - TASK-001
EOF
```

**Step 2: 创建带 plan_file 的任务文件**

Run:
```bash
cat > "$TMP_PROJECT/docs/tasks/TASK-100-plan-task.md" <<'EOF'
---
id: TASK-100
title: "Plan Task"
status: "To Do"
created_at: 2026-02-02
updated_at: 2026-02-02
execution_mode: "executing-plans"
plan_file: "docs/plans/execution-plan.yaml"
execution_config:
  batch_size: 1
  auto_continue: false
  checkpoint_interval: 3
execution_state: {}
---
EOF
```

**Step 3: 执行 execute-next-batch**

Run:
```bash
python -m cli execute-next-batch TASK-100 --project-root "$TMP_PROJECT"
```

Expected:
- 输出为 JSON
- 至少包含 `tasks_executed` 与 `total_completed`

> 若失败且报 `execution_engine` 或 `plan_generator` 缺失，记录为高优先级缺陷。

---

## Task 4: Markdown 计划文件解析验证

**Files:**
- Source: `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/src/cli.py`

**Step 1: 准备 Markdown 计划文件**

Run:
```bash
cat > "$TMP_PROJECT/docs/plans/execution-plan.md" <<'EOF'
# Example Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Example goal

---

### Task 1: First step
**Description:** Do the first thing

### Task 2: Second step
**Description:** Do the second thing
EOF
```

**Step 2: 更新任务引用 Markdown**

Run:
```bash
cat > "$TMP_PROJECT/docs/tasks/TASK-101-plan-task.md" <<'EOF'
---
id: TASK-101
title: "Plan Task"
status: "To Do"
created_at: 2026-02-02
updated_at: 2026-02-02
execution_mode: "executing-plans"
plan_file: "docs/plans/execution-plan.md"
execution_config:
  batch_size: 1
  auto_continue: false
  checkpoint_interval: 3
execution_state: {}
---
EOF
```

**Step 3: 执行 execute-next-batch**

Run:
```bash
python -m cli execute-next-batch TASK-101 --project-root "$TMP_PROJECT"
```

Expected:
- 输出 JSON 且 `tasks_executed` 为 1

---

## Task 5: todowrite 兼容性验证

**Files:**
- Source: `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/src/cli.py`

**Step 1: 准备 TodoWrite 输入 JSON**

Run:
```bash
cat > "$TMP_PROJECT/todos.json" <<'EOF'
{
  "todos": [
    {"title": "Task A", "description": "Do A"},
    {"title": "Task B", "description": "Do B"}
  ]
}
EOF
```

**Step 2: 执行 todowrite**

Run:
```bash
python -m cli todowrite --input-file "$TMP_PROJECT/todos.json" --project-root "$TMP_PROJECT"
```

Expected:
- 输出 JSON 结果

> 若报 `todowrite_compat` 缺失，记录为高优先级缺陷。

---

## Task 6: 失败路径与边界输入验证

**Files:**
- Source: `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/src/cli.py`
- Source: `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/src/task_manager.py`

**Step 1: show-task 不存在**

Run:
```bash
python -m cli show-task TASK-999 --project-root "$TMP_PROJECT"
```

Expected:
- exit code 非 0
- 错误信息包含 “not found”

**Step 2: start-task 不存在**

Run:
```bash
python -m cli start-task TASK-999 --project-root "$TMP_PROJECT"
```

Expected:
- exit code 非 0
- 错误信息包含 “not found”

**Step 3: execute-next-batch 缺 plan_file**

Run:
```bash
cat > "$TMP_PROJECT/docs/tasks/TASK-102-plan-task.md" <<'EOF'
---
id: TASK-102
title: "Plan Task"
status: "To Do"
created_at: 2026-02-02
updated_at: 2026-02-02
execution_mode: "executing-plans"
plan_file: null
execution_state: {}
---
EOF

python -m cli execute-next-batch TASK-102 --project-root "$TMP_PROJECT"
```

Expected:
- exit code 非 0
- 输出包含 “plan_file is required”

---

## Task 7: 结论与缺陷清单输出格式

**输出格式（建议）**

```
[Summary]
- 基线测试：PASS/FAIL
- CLI 核心流程：PASS/FAIL
- execute-next-batch：PASS/FAIL
- todowrite：PASS/FAIL
- 关键缺陷数：N

[Findings]
1. 缺失模块：execution_engine
   - 触发用例：execute-next-batch
   - 影响：功能不可用
   - 复现步骤：...（引用 Task 3 Step 3）

2. 缺失模块：todowrite_compat
   - 触发用例：todowrite
   - 影响：兼容性命令不可用
   - 复现步骤：...（引用 Task 5 Step 2）
```

---

## Task 8: TDD 修复执行入口（预留）

> 在完成上述测试并输出缺陷清单后，再进入 TDD 修复阶段。每个缺陷单独建测试用例（先失败），再最小实现修复，最后全量回归。执行时严格遵循 superpowers:test-driven-development。
