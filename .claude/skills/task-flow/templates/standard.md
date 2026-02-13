<!-- TASK-FLOW-TEMPLATE:STANDARD -->

## Task Flow 工作流

本项目采用 **task-flow v{VERSION}** 作为任务管理系统。

### 快速开始

```bash
# 1. 创建任务
创建任务：实现功能 X

# 2. 启动任务
启动任务 TASK-001

# 3. 完成任务
完成任务 TASK-001
```

### 核心命令

#### 任务管理

| 用户语句 | 功能 |
|---------|------|
| 创建任务：{标题} | 创建新任务 |
| 启动任务 TASK-XXX | 启动任务（docs gate + active registry + events + PLAN 路由） |
| 更新任务 TASK-XXX 进度到第 N 步 | 更新进度 |
| 完成任务 TASK-XXX | 完成并归档 |
| 查看任务 TASK-XXX | 查看详情 |
| 列出所有任务 | 显示任务列表 |

#### 计划执行

| 用户语句 | 功能 |
|---------|------|
| 按计划执行 TASK-XXX | 执行下一批任务 |
| 执行计划 TASK-XXX | 同上（别名） |

#### 流程协作

| 用户语句 | 触发技能 |
|---------|---------|
| 开始需求澄清：TASK-XXX | superpowers:brainstorming |
| 为 TASK-XXX 写实施计划 | superpowers:writing-plans |
| 审查 TASK-XXX 的实现 | superpowers:requesting-code-review |

### 工作流程

**标准流程**（推荐用于复杂功能）：

```
创建任务 → 需求澄清 → 实施计划 → 启动任务 → 按计划执行 → 完成任务
```

**简化流程**（用于小改动）：

```
创建任务 → 启动任务 → 直接实现 → 完成任务
```

### 相关技能

- **task-flow**: 任务管理核心
- **superpowers:brainstorming**: 需求澄清
- **superpowers:writing-plans**: 计划编写
- **superpowers:executing-plans**: 计划执行
- **machine-readable state**: `docs/tasks/_active.json` + `worktree/.task-flow/events.jsonl`

> 由 task-flow v{VERSION} 自动生成 | {DATE}
