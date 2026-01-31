## 工作流总则

**任务事实源**：Backlog.md + Plan Packet

**读取任务流程**：优先通过 MCP 资源 `backlog://workflow/overview`

**每次实现必须**：
- 严格按 Plan Packet 执行；发现偏离先回写 Plan Packet
- push/PR 前执行 `./scripts/ci-local.sh`

---

## 具体步骤

### 1) 读取任务
- 读取 Backlog 任务文件（如 `backlog/tasks/task-<id> - <title>.md`）
- 参考 MCP 资源：
  - `backlog://workflow/task-execution` - 执行指南
  - `backlog://workflow/task-finalization` - 完成指南

### 2) 执行与回写
- 按 Plan Packet 完成实现
- 发现偏离时，使用 `task_edit` 的 `planAppend` 字段记录变更
- 更新 Backlog 任务状态

### 3) 验证与发布
- `./scripts/ci-local.sh` 必须通过
- 提交 PR 并链接到任务与 Plan Packet

---

## 使用方式

告诉 Claude：
- "初始化 plan-packet" - 设置工作流
- "添加 Plan Packet 到任务" - 为任务添加结构化计划
- "关联当前分支到任务" - 记录分支关联
- "显示当前任务" - 查看关联的任务和计划
- "更新所有 Plan Packet" - 更新到最新版本

---

## Plan Packet 结构

1. **Goal / Non-goals** - 明确目标和不做什么
2. **Scope** - 按可并行 workstreams 拆分
3. **Interfaces & Constraints** - 代码路径、依赖、质量入口
4. **Execution Order** - 执行顺序
5. **Acceptance Criteria** - 验收标准
6. **Quality Gates** - 质量检查命令
7. **Risks & Rollback** - 风险和回滚步骤
8. **Backlog 任务映射** - 任务 ID、文件路径、关联分支
9. **Notes** - 上下文、决策、参考链接

---

## 相关技能

- **plan-packet**: 任务结构化计划
- **wt-workflow**: worktree 工作流管理
- **backlog.md**: 任务管理 (通过 MCP)

---

## MCP 资源

- `backlog://workflow/overview` - 工作流总览
- `backlog://workflow/task-creation` - 任务创建指南
- `backlog://workflow/task-execution` - 任务执行指南
- `backlog://workflow/task-finalization` - 任务完成指南
