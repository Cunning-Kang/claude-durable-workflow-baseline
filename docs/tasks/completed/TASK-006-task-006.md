---
id: TASK-006
title: 团队邀请与成员管理
status: Done
created_at: 2026-02-04
updated_at: 2026-02-04
execution_mode: executing-plans
plan_file: docs/plans/TASK-006-plan.md
worktree: .worktrees/task-006
branch: task-006
current_step: 3
completion_type: null
pr_url: null
completed_at: 2026-02-04
---

# Task: 团队邀请与成员管理

## Plan Packet

### 1. Goal / Non-goals
**Goal**
- 实现团队邀请与成员管理的全流程能力
- 覆盖邀请、角色分配、成员列表、权限校验与审计记录

**Non-goals**
- 不做计费与订阅变更
- 不做外部 SSO 或 SCIM 集成

### 2. Scope（按可并行 workstreams 拆分）
**Workstream A**
- 交付物：邀请 API、角色管理 API、成员列表 API
- 修改范围：服务端路由、权限中间件、数据访问层
- 风险点：权限边界、数据一致性

**Workstream B**
- 交付物：邀请入口 UI、成员管理页、角色编辑弹窗
- 修改范围：前端路由、状态管理、权限展示逻辑
- 风险点：权限显示与后端规则不一致

### 3. Interfaces & Constraints（接口与约束）
- 代码路径：web/app、api/routes、api/policies
- 外部依赖与版本：无新增依赖
- 统一质量入口：
  - `pytest -q`
- 兼容性要求：现有管理员权限模型保持不变
- 禁止事项：禁止在客户端缓存敏感权限数据

### 4. Execution Order（执行顺序）
1) 定义邀请与角色管理 API
2) 实现权限策略与审计记录
3) 完成前端成员管理 UI 与权限展示
4) 补充测试与文档更新

### 5. Acceptance Criteria（验收标准）
- [ ] 具备邀请成员、分配角色、移除成员能力
- [ ] 权限策略阻止越权操作
- [ ] 审计记录可追踪邀请与角色变更
- [ ] pytest 通过

### 6. Quality Gates（质量检查）
```bash
pytest -q
```

### 7. Risks & Rollback（风险与回滚）
- 潜在风险：权限校验遗漏
- 触发条件：越权访问被发现或审计不完整
- 回滚步骤：回滚到上一版本并禁用邀请入口

### 8. Backlog 任务映射
- 任务 ID：TASK-006
- 任务文件：docs/tasks/TASK-006-task-006.md
- 关联分支：feature/team-invite

### 9. Notes（备注）
- 已完成计划批次执行，记录前端与权限工作流覆盖。
- 该任务用于 task-flow 全流程测试

---
**执行过程中若发现偏离 Plan Packet，在此记录：**
