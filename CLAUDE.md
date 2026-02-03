## 官方工作流：Task Flow × Superpowers

本项目以 **task-flow** 作为任务事实源，以 **superpowers** 作为流程纪律与执行能力核心。所有任务、状态、计划必须可追溯到 TASK-xxx。

### 核心原则

1. **事实源唯一**：任务与状态仅存在于 `docs/tasks/`。
2. **计划归档唯一**：实施计划仅存在于 `docs/plans/`。
3. **入口语句固定**：仅使用标准入口语句触发流程。
4. **复杂任务强流程**：brainstorm → plan → execute。
5. **强可追溯**：任务、计划、实现必须相互映射。

### 标准入口语句

```
创建任务：<标题>
开始需求澄清：TASK-xxx
为 TASK-xxx 写实施计划
启动任务 TASK-xxx
按计划执行 TASK-xxx
更新任务 TASK-xxx 进度到第 N 步
完成任务 TASK-xxx
```

### 推荐执行顺序（主流程）

1. **创建任务** → task-flow `create-task`
2. **需求澄清** → superpowers:brainstorming
3. **实施计划** → superpowers:writing-plans
4. **启动任务** → task-flow `start-task`
5. **执行计划** → superpowers:executing-plans / superpowers:subagent-driven-development
6. **更新进度** → task-flow `update-task`
7. **完成任务** → task-flow `complete-task`

### 分支流程

**小改动**
1. 创建任务
2. 启动任务
3. 直接实现
4. 完成任务

**复杂需求**
1. 创建任务
2. 需求澄清
3. 实施计划
4. 启动任务
5. 执行计划
6. 完成任务

### 相关技能

- **task-flow**: 任务管理与执行入口
- **superpowers:brainstorming**: 需求澄清
- **superpowers:writing-plans**: 可执行计划
- **superpowers:executing-plans**: 计划执行
- **superpowers:subagent-driven-development**: 子代理分步执行
