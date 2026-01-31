## 工作流：Plan Packet 驱动开发

Plan Packet 是任务文件的结构化计划部分，帮助组织开发思路。

### 使用方式

告诉 Claude：
- "初始化 plan-packet" - 设置工作流
- "添加 Plan Packet 到任务" - 为任务添加结构化计划
- "关联当前分支到任务" - 记录分支关联
- "显示当前任务" - 查看关联的任务和计划

### Plan Packet 结构

1. **Goal / Non-goals** - 明确目标和不做什么
2. **Scope** - 按可并行 workstreams 拆分
3. **Interfaces & Constraints** - 代码路径、依赖、质量入口
4. **Execution Order** - 执行顺序
5. **Acceptance Criteria** - 验收标准
6. **Quality Gates** - 质量检查命令
7. **Risks & Rollback** - 风险和回滚步骤
8. **Backlog 任务映射** - 任务 ID、文件路径、关联分支
9. **Notes** - 上下文、决策、参考链接

### 相关技能

- **plan-packet**: 任务结构化计划
- **wt-workflow**: worktree 工作流管理
- **backlog.md**: 任务管理 (通过 MCP)
