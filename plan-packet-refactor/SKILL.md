---
name: plan-packet
description: "在 backlog.md 任务文件中添加结构化 Plan Packet，帮助组织开发思路（Goal、Scope、Interfaces、Execution Order、Quality Gates 等）。使用时机：用户需要为新创建的任务添加详细计划时，或说'初始化 plan-packet'、'添加 Plan Packet'、'关联分支'时。"
---

# Plan Packet

在 backlog.md 任务文件中添加结构化的 Plan Packet，帮助组织开发思路。

## Quick Start

```
用户: "初始化 plan-packet"
→ Claude: 调用脚本初始化工作流文件

用户: "添加 Plan Packet 到任务 TASK-001"
→ Claude: 调用脚本添加结构化计划

用户: "关联当前分支到任务"
→ Claude: 调用脚本记录分支关联
```

## 工作原理

Plan Packet 是**脚本驱动**的工作流，而非手动编辑流程。当用户触发时：

1. **调用脚本** `python ~/.claude/skills/plan-packet/scripts/plan-packet.py <command>`
2. **脚本执行** 检测项目上下文、读取任务、生成模板
3. **返回结果** 显示操作状态和下一步建议

## 与 Backlog MCP 的集成

Plan Packet 与 Backlog.md 深度集成：

- **任务事实源**：Backlog.md 任务文件 + Plan Packet section
- **执行前**：通过 `backlog://workflow/task-execution` 了解执行流程
- **执行中**：发现偏离时使用 `task_edit planAppend` 记录变更
- **执行后**：通过 `backlog://workflow/task-finalization` 完成任务

## 触发短语

| 用户说 | 触发的命令 |
|--------|-----------|
| "初始化 plan-packet" | `init` |
| "添加 Plan Packet" | `add` |
| "添加 Plan Packet 到任务 TASK-001" | `add --task TASK-001` |
| "关联当前分支到任务" | `link` |
| "显示当前任务" | `show` |
| "更新所有 Plan Packet" | `update` |

## 命令详解

### `init` - 初始化工作流文件

在项目根目录创建/更新 `CLAUDE.md`（或 `AGENTS.md`），添加 Plan Packet 工作流说明。

```bash
python ~/.claude/skills/plan-packet/scripts/plan-packet.py init [--force-agents]
```

**检测逻辑**：
- 优先使用现有的 `CLAUDE.md`
- 如果 `AGENTS.md` 存在且 `--force-agents`，则使用 `AGENTS.md`
- 如果都不存在，创建 `CLAUDE.md`

### `add` - 添加 Plan Packet 到任务

为任务文件添加结构化的 Plan Packet section。

```bash
python ~/.claude/skills/plan-packet/scripts/plan-packet.py add [--task TASK_ID]
```

**功能**：
- 自动检测 CI 命令（wt-workflow → ci-local.sh → mise.toml）
- 填充任务 ID、文件路径、当前分支
- 跳过已有 Plan Packet 的任务

### `link` - 关联分支到任务

从当前分支名提取 Task ID，更新任务的"关联分支"字段。

```bash
python ~/.claude/skills/plan-packet/scripts/plan-packet.py link [--branch BRANCH]
```

**分支命名格式**：
- `feature/task-1-xxx` → TASK-1
- `task-1-xxx` → TASK-1
- `feat-TASK-1-desc` → TASK-1

### `show` - 显示当前任务

显示当前分支关联的任务信息摘要。

```bash
python ~/.claude/skills/plan-packet/scripts/plan-packet.py show
```

### `update` - 更新所有 Plan Packet

将所有任务的 Plan Packet 更新到最新模板版本。

```bash
python ~/.claude/skills/plan-packet/scripts/plan-packet.py update
```

## Plan Packet 结构

在每个任务文件末尾添加：

```markdown
## Plan Packet

### 1. Goal / Non-goals
**Goal**
- <明确的业务/技术目标>

**Non-goals**
- <不在本次范围内的事项>

### 2. Scope（按可并行 workstreams 拆分）
**Workstream A**
- 交付物：
- 修改范围：
- 风险点：

### 3. Interfaces & Constraints
- 代码路径：
- 外部依赖：
- 质量检查：
- 兼容性要求：
- 禁止事项：

### 4. Execution Order
1)
2)
3)

### 5. Acceptance Criteria
> 参见上方的 Acceptance Criteria section

### 6. Quality Gates
```bash
# 质量检查命令
```

### 7. Risks & Rollback
- 潜在风险：
- 回滚步骤：

### 8. Backlog 任务映射
- 任务 ID：
- 任务文件：
- 关联分支：

### 9. Notes
- <上下文、决策、参考链接>

**重要**：执行过程中若发现偏离 Plan Packet，必须通过 Backlog MCP 记录：
```bash
task_edit id:TASK-XXX planAppend:"<描述变更原因和新的执行方向>"
```
```

## CI 命令检测顺序

脚本按以下顺序检测 CI 命令：

1. **wt-workflow skill** → `wt ci`
2. **scripts/ci-local.sh** → `./scripts/ci-local.sh`
3. **mise.toml 中的 ci 任务** → `mise run ci`
4. **默认** → `# 请配置 CI 命令`

## 用户交互流程

### 场景 1：新项目初始化

```
用户: "初始化 plan-packet"

Claude 应该：
1. 调用 init 脚本
2. 显示结果
3. 建议下一步："是否需要添加 Plan Packet 到现有任务？"
```

### 场景 2：创建任务后添加计划

```
用户: "我刚创建了任务 TASK-001，添加 Plan Packet"

Claude 应该：
1. 调用 add --task TASK-001 脚本
2. 显示添加结果
3. 读取任务文件，引导用户填写 Goal/Non-goals
```

### 场景 3：开发前关联分支

```
用户: "关联当前分支到任务"

Claude 应该：
1. 调用 link 脚本
2. 显示关联结果
3. 调用 show 显示任务摘要
```

## 集成

- **wt-workflow**: 使用 `wt ci` 作为默认质量检查命令
- **backlog.md MCP**: 任务文件由 `backlog/tasks/` 管理

## 脚本位置

```
~/.claude/skills/plan-packet/
├── SKILL.md
├── scripts/
│   ├── plan-packet.py       # 主脚本
│   └── merge-claude-md.py   # 工作流合并脚本
└── templates/
    ├── claude-md-fragment.md     # CLAUDE.md 片段
    └── plan-packet-template.md   # Plan Packet 模板
```
