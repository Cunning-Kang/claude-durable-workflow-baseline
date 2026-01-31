## Plan Packet
{version_marker}

### 1. Goal / Non-goals
**Goal**
- <待补充：明确的业务/技术目标>

**Non-goals**
- <待补充：不在本次范围内的事项>

### 2. Scope（按可并行 workstreams 拆分）
**Workstream A**（建议一个独立 worktree/分支）
- 交付物：
- 修改范围：
- 风险点：

### 3. Interfaces & Constraints（接口与约束）
- 代码路径：
- 外部依赖与版本（mise / node / go / python）：
- 统一质量入口（必跑命令）：
  - `{ci_command}`
- 兼容性要求：
- 禁止事项（例如：不改公共 API，不引入新依赖等）：

### 4. Execution Order（执行顺序）
1)
2)
3)

### 5. Acceptance Criteria（验收标准）
> 参见上方的 "Acceptance Criteria" section（backlog.md 原生）
>
> 自动化检查项：
> - [ ] CI 质量门禁通过
> - [ ] format 一致、typecheck 无误
> - [ ] tests 通过（如有）

### 6. Quality Gates（质量检查）
```bash
{ci_command}
```

### 7. Risks & Rollback（风险与回滚）
- 潜在风险：
- 触发条件：
- 回滚步骤：

### 8. Backlog 任务映射
- 任务 ID：{task_id}
- 任务文件：{task_file}
- 关联分支：{branch_name}  <!-- 由 link 命令更新 -->

### 9. Notes（备注）
- <上下文、决策、外部参考链接等>

**重要**：执行过程中若发现偏离 Plan Packet，必须使用以下方式记录：
```bash
# 通过 Backlog MCP 更新任务
task_edit id:{task_id} planAppend:"<描述变更原因和新的执行方向>"
```

{end_marker}
