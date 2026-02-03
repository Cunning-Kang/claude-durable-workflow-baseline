# Task Flow × Superpowers 工作流蓝图

**用途**：为个人使用提供稳定、可复用、可自动化的任务执行闭环。该蓝图以 task-flow 作为“任务事实源”，以 superpowers 作为“流程纪律与执行能力”的核心。

---

## 1. 核心原则

1. **事实源唯一**：所有任务与状态仅存在于 `docs/tasks/` 任务文件中。
2. **计划归档唯一**：所有实施计划仅存在于 `docs/plans/`。
3. **入口语句固定**：所有流程仅由标准入口语句触发，避免语义漂移。
4. **执行纪律固定**：复杂任务必须经过 brainstorming → plan → execute。
5. **强可追溯**：任务、计划、实现均可追踪到 TASK-xxx。

---

## 2. 标准入口语句库（建议写入 CLAUDE.md）

```
创建任务：<标题>
开始需求澄清：TASK-xxx
为 TASK-xxx 写实施计划
启动任务 TASK-xxx
按计划执行 TASK-xxx
更新任务 TASK-xxx 进度到第 N 步
完成任务 TASK-xxx
```

---

## 3. 最佳执行顺序（推荐主流程）

**目标**：确保“可执行性、可验证性、可回溯性”。

1. `创建任务：<标题>`
   - 触发：task-flow `create-task`
   - 产出：`docs/tasks/TASK-xxx-*.md`

2. `开始需求澄清：TASK-xxx`
   - 触发：superpowers:brainstorming
   - 产出：明确目标、约束、成功标准

3. `为 TASK-xxx 写实施计划`
   - 触发：superpowers:writing-plans
   - 产出：`docs/plans/YYYY-MM-DD-<topic>.md`

4. `启动任务 TASK-xxx`
   - 触发：task-flow `start-task`
   - 产出：worktree + 分支 + 任务状态 In Progress

5. `按计划执行 TASK-xxx`
   - 触发：superpowers:executing-plans 或 superpowers:subagent-driven-development
   - 产出：按 TDD 步骤完成实现

6. `更新任务 TASK-xxx 进度到第 N 步`
   - 触发：task-flow `update-task --step N`
   - 产出：任务状态同步

7. `完成任务 TASK-xxx`
   - 触发：task-flow `complete-task`
   - 产出：任务归档

---

## 4. 分支流程（按复杂度选择）

### A. 小改动（低复杂）

1. `创建任务：<标题>`
2. `启动任务 TASK-xxx`
3. 直接实现（可简化 TDD）
4. `完成任务 TASK-xxx`

### B. 复杂需求（高不确定）

1. `创建任务：<标题>`
2. `开始需求澄清：TASK-xxx`
3. `为 TASK-xxx 写实施计划`
4. `启动任务 TASK-xxx`
5. `按计划执行 TASK-xxx`
6. `完成任务 TASK-xxx`

---

## 5. 角色分工（最小语义冲突）

- **task-flow**：任务事实源 + 任务生命周期
- **superpowers:brainstorming**：需求澄清、范围界定
- **superpowers:writing-plans**：可执行计划
- **superpowers:executing-plans**：计划执行

**原则**：任何“任务状态”仅由 task-flow 更新；任何“执行计划”仅由 superpowers 输出到 docs/plans。

---

## 6. 任务状态与文件结构

```
./docs/
  tasks/
    TASK-001-xxx.md
    TASK-002-yyy.md
    completed/
  plans/
    2026-02-03-xxx.md
```

---

## 7. 质量门与验证

- 执行计划必须包含 Quality Gates
- 每个执行阶段需明确验证命令
- 任务完成前必须通过关键测试

---

## 8. 操作清单（一次性记忆）

**我要开始一个任务时**：
1. 创建任务
2. 需求澄清
3. 计划
4. 启动
5. 执行
6. 完成

**我要快速修一个小问题时**：
1. 创建任务
2. 启动
3. 实现
4. 完成
