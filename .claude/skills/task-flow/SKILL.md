---
name: task-flow
description: "轻量级任务管理系统，提供持久化任务跟踪、Plan Packet 结构化计划、Git Worktree 自动化集成。支持 Markdown/YAML 计划文件解析和 TodoWrite 兼容层。使用时机：创建任务、启动开发、更新进度、完成任务、执行计划批次。零外部依赖。"
---

# Task Flow

基于文件的轻量级任务管理系统，提供完整的任务生命周期管理。通过 TDD 方法构建，184/185 测试通过（1 skipped，99.5%）。

## Quick Start

```
用户: "创建任务：实现用户认证"
→ Claude: 调用 task-flow 创建 TASK-001，生成 Plan Packet 模板

用户: "启动任务 TASK-001"
→ Claude: 创建 git worktree，更新任务状态

用户: "更新进度：已完成第2步"
→ Claude: 更新任务状态和步骤

用户: "完成任务 TASK-001"
→ Claude: 标记完成，归档任务文件
```

## 工作原理

Task Flow 是**纯 Python + 文件系统**的轻量级方案：

1. **持久化存储** - 任务文件保存在 `docs/tasks/`，_index.json 维护状态
2. **Plan Packet** - 9 个结构化 sections（Goal、Scope、Execution Order 等）
3. **Git 集成** - 自动创建和管理 worktree
4. **CLI 驱动** - 所有操作通过命令行接口
5. **计划执行** - 支持 YAML 和 Markdown 格式的计划文件解析
6. **自动初始化文档** - 自动生成或更新 CLAUDE.md/AGENTS.md
7. **TodoWrite 兼容** - 兼容 TodoWrite 格式输入

## 触发短语

| 用户说 | 触发的命令 |
|--------|-----------|
| "创建任务：实现用户认证" | `create-task "实现用户认证"` |
| "新建任务：添加登录功能" | `create-task "添加登录功能"` |
| "启动任务 TASK-001" | `start-task TASK-001` |
| "列出所有任务" | `list-tasks` |
| "查看任务 TASK-001" | `show-task TASK-001` |
| "更新任务 TASK-001 进度到第3步" | `update-task TASK-001 --step 3` |
| "完成任务 TASK-001" | `complete-task TASK-001` |
| "执行下一批任务" | `execute-next-batch TASK-XXX` |

## 命令详解

### `create-task <title>` - 创建新任务

生成任务 ID，创建包含 Plan Packet 模板的任务文件。

```bash
python -m cli --project-root <project-root> create-task "<title>"
```

**输出示例**：
```
✓ Created task: TASK-001
  File: docs/tasks/TASK-001-implement-feature.md

Next steps:
  1. Edit the task file to fill in the Plan Packet
  2. Run: start-task TASK-001
```

### `start-task <task-id>` - 启动任务

创建或切换到对应的 git worktree，更新任务状态为 In Progress。

```bash
python -m cli --project-root <project-root> start-task TASK-001
```

**输出示例**：
```
✓ Created worktree: .worktrees/implement-feature
✓ Created branch: implement-feature
✓ Task TASK-001 is now In Progress
```

### `update-task <task-id>` - 更新任务

更新任务状态、步骤或添加备注。

```bash
python -m cli --project-root <project-root> update-task TASK-001 [OPTIONS]
```

**选项**：
- `--status <status>` - 更新状态
- `--step <n>` - 更新当前步骤号
- `--note <note>` - 添加备注

### `complete-task <task-id>` - 完成任务

标记任务为 Done，归档任务文件到 `docs/tasks/completed/`。

```bash
python -m cli --project-root <project-root> complete-task TASK-001 [--no-cleanup]
```

### `execute-next-batch <task-id>` - 执行计划批次

执行计划文件的下一批任务。支持 YAML 和 Markdown 格式。

```bash
python -m cli --project-root <project-root> execute-next-batch TASK-100
```

**返回 JSON**：
```json
{"tasks_executed": 1, "total_completed": 1, "errors": [], "skipped": []}
```

### `init` - 初始化项目文档

生成或更新 CLAUDE.md/AGENTS.md，并写入版本标记与 task-flow 章节。

```bash
python -m cli --project-root <project-root> init [--template <minimal|standard|full>] [--force] [--yes] [--no-backup]
```

### `todowrite [--input-file <file>]` - TodoWrite 兼容

处理 TodoWrite 格式输入，创建或更新任务。

```bash
python -m cli --project-root <project-root> todowrite --input-file todos.json
```

## Plan Packet 结构

每个任务文件包含以下 9 个 sections：

1. **Goal / Non-goals** - 明确目标和非目标
2. **Scope** - 按可并行 workstreams 拆分
3. **Interfaces & Constraints** - 接口与约束
4. **Execution Order** - 执行顺序
5. **Acceptance Criteria** - 验收标准
6. **Quality Gates** - 质量检查命令
7. **Risks & Rollback** - 风险与回滚
8. **Backlog 任务映射** - 任务 ID、文件路径、关联分支
9. **Notes** - 备注和上下文

## 计划文件格式

### YAML 格式

```yaml
tasks:
- id: TASK-001
  title: Step 1
  description: First step
- id: TASK-002
  title: Step 2
  description: Second step
  dependencies:
    - TASK-001
```

### Markdown 格式

```markdown
# Example Implementation Plan

### Task 1: First step
**Description:** Do the first thing

### Task 2: Second step
**Description:** Do the second thing
```

## 测试覆盖

```
tests/
├── conftest.py                   # pytest 配置
├── test_ci_detector.py           # CI 检测测试
├── test_cli.py                   # CLI 命令测试
├── test_task_manager.py          # 核心逻辑测试
├── test_start_task.py            # Worktree 集成测试
├── test_update_and_complete.py   # 工作流测试
├── test_todowrite_compat.py      # TodoWrite 兼容测试
└── test_superpowers_integration.py  # 集成测试
```

**测试结果**: 181/182 通过（1 skipped，99.5%）

## 技术架构

**依赖**：
- Python 3.10+
- pytest（仅开发时）
- PyYAML

**项目结构**：
```
~/.claude/skills/task-flow/
├── SKILL.md                      # 本文件
├── src/
│   ├── __init__.py
│   ├── __main__.py              # Python 模块支持
│   ├── cli.py                   # CLI 入口（450+ 行）
│   ├── task_manager.py          # 核心逻辑（350+ 行）
│   ├── ci_detector.py           # CI 命令检测
│   ├── execution_engine.py      # 执行引擎
│   ├── plan_generator/          # 计划类型定义
│   │   └── __init__.py
│   └── todowrite_compat/        # TodoWrite 兼容层
│       ├── __init__.py
│       └── tool.py
├── tests/                        # 测试套件（61 个测试）
├── requirements.txt              # Python 依赖
└── README.md                     # 用户文档
```

## 设计原则

1. **增强而非替换** - 复用 git worktree，不重新实现
2. **文件即事实源** - 任务文件可读可编辑，Git 版本控制
3. **TDD 驱动** - 96.7% 测试通过率
4. **零外部依赖** - 不需要 MCP 服务器

## 常见问题

**Q: 与 Backlog.md 的区别？**
A: Task Flow 使用纯文件系统，不依赖 MCP 服务器，更稳定。

**Q: 如何备份任务？**
A: 所有任务文件都是 markdown，Git 自动版本控制。

**Q: 支持多用户吗？**
A: 当前单用户设计，任务文件可通过 Git 协作。

**Q: 如何使用 execute-next-batch？**
A: 在任务文件中设置 `execution_mode: "executing-plans"` 和 `plan_file` 路径。

## 版本历史

**v2.3** (当前版本)
- ✅ 自动初始化 CLAUDE.md/AGENTS.md
- ✅ 模板渲染与智能合并（version markers）
- ✅ 初始化命令与非交互环境自动初始化
- ✅ 181/182 测试通过（1 skipped，99.5%）

**v2.2**
- ✅ 任务索引与 O(1) 查找
- ✅ frontmatter 单次更新
- ✅ ExecutionEngine 使用 set 状态跟踪
- ✅ start-task 从 frontmatter 读取 branch
- ✅ 145/146 测试通过（1 skipped，99.3%）

**v2.1**
- ✅ Markdown 计划文件解析支持
- ✅ TodoWrite 兼容层
- ✅ CI 命令自动检测
- ✅ execute-next-batch 批量执行
- ✅ 59/61 测试通过（96.7%）

**v2.0**
- ✅ 执行引擎实现
- ✅ 计划类型定义
- ✅ YAML 计划文件支持
