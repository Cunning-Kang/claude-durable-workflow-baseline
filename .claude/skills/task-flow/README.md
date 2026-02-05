# task-flow

基于文件的轻量级任务管理系统，使用 TDD 方法构建。提供持久化任务跟踪、Plan Packet 结构化计划、Git Worktree 自动化集成，以及 CLAUDE.md 自动初始化。

## 特性

- ✅ **持久化任务管理** - 任务文件保存在 `docs/tasks/`
- ✅ **索引驱动** - list-tasks 与 todo_id 查询直接走索引
- ✅ **完整 Plan Packet** - 结构化的 9 部分计划模板
- ✅ **Git Worktree 集成** - 自动创建隔离的工作环境
- ✅ **TDD 驱动** - 184/185 测试通过（1 skipped，99.5%）
- ✅ **Markdown/YAML 计划文件** - 支持多种计划格式
- ✅ **TodoWrite 兼容** - 兼容 TodoWrite 格式输入
- ✅ **CI 命令自动检测** - 自动检测项目 CI 配置
- ✅ **自动初始化文档** - 自动生成或更新 CLAUDE.md/AGENTS.md
- ✅ **零依赖 MCP** - 不需要外部 MCP 服务器

## 快速开始

### 初始化检查跳过（可选）

在自动化或批处理环境中可用：

```bash
TASK_FLOW_SKIP_INIT=1 task-flow list-tasks
```

### 1. 创建任务

```bash
cd your-project
task-flow create-task "Implement user authentication"
```

输出：
```
✓ Created task: TASK-001
  File: docs/tasks/TASK-001-implement-user-authentication.md

Next steps:
  1. Edit the task file to fill in the Plan Packet
  2. Run: task-flow start-task TASK-001
```

### 2. 填写 Plan Packet

编辑生成的任务文件：

```markdown
---
id: TASK-001
title: Implement user authentication
status: To Do
---

## Plan Packet

### 1. Goal / Non-goals
**Goal**
- 实现 JWT 认证系统

**Non-goals**
- OAuth 集成
- 多因素认证

### 4. Execution Order
1) 创建 User 模型
2) 实现 JWT 生成和验证
3) 添加认证中间件
4) 编写测试
```

### 3. 启动任务

```bash
task-flow start-task TASK-001
```

输出（示例）：
```
✓ Created worktree: .worktrees/implement-user-authentication
✓ Created branch: implement-user-authentication
✓ Task TASK-001 is now In Progress
```

**关键行为**：
- 若 worktree 缺少 `docs/`，自动从主工作区同步，并输出同步提示
- 若 `docs/` 存在未提交变更，提示但不阻断流程

### 4. 更新进度

```bash
# 更新步骤
task-flow update-task TASK-001 --step 2

# 添加备注
task-flow update-task TASK-001 --note "决定使用 pyjwt 库"
```

### 5. 完成任务

```bash
task-flow complete-task TASK-001
```

## 所有命令

```bash
# 创建任务
task-flow create-task "<title>"

# 列出任务
task-flow list-tasks [--status <status>]

# 显示任务详情
task-flow show-task <TASK-ID>

# 启动任务（创建 worktree）
task-flow start-task <TASK-ID>

# 更新任务
task-flow update-task <TASK-ID> [--status <status>] [--step <n>] [--note <note>]

# 完成任务
task-flow complete-task <TASK-ID> [--no-cleanup]

# 执行计划批次
task-flow execute-next-batch <TASK-ID>

# 初始化项目文档
task-flow init [--template <minimal|standard|full>] [--force] [--yes] [--no-backup]

# TodoWrite 兼容
task-flow todowrite --input-file todos.json
```

### 注：Skill 开发时的直接运行方式

如果你正在开发 task-flow 技能本身，可以直接运行 Python 模块：

```bash
# 从技能目录直接运行（仅用于 skill 开发）
python ~/.claude/skills/task-flow/src/cli.py create-task "<title>"
```

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

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=src --cov-report=html
```

**测试结果**: 184/185 通过（1 skipped，99.5%）

## 项目结构

```
task-flow/
├── task-flow                 # 可执行入口脚本（推荐使用方式）
├── src/
│   ├── __init__.py
│   ├── __main__.py           # Python 模块支持（用于开发）
│   ├── cli.py                # CLI 入口（450+ 行）
│   ├── task_manager.py       # 任务管理核心逻辑（350+ 行）
│   ├── ci_detector.py        # CI 命令检测
│   ├── execution_engine.py   # 执行引擎
│   ├── plan_generator/       # 计划类型定义
│   │   └── __init__.py
│   ├── config/               # 自动初始化配置
│   │   ├── manager.py
│   │   ├── template_loader.py
│   │   ├── template_renderer.py
│   │   ├── content_merger.py
│   │   └── exceptions.py
│   └── todowrite_compat/     # TodoWrite 兼容层
│       ├── __init__.py
│       └── tool.py
├── tests/
│   ├── conftest.py           # pytest 配置
│   ├── test_ci_detector.py   # CI 检测测试
│   ├── test_cli.py           # CLI 测试
│   ├── test_task_manager.py  # 核心逻辑测试
│   ├── test_start_task.py    # Worktree 集成测试
│   ├── test_update_and_complete.py  # 工作流测试
│   ├── test_todowrite_compat.py     # TodoWrite 兼容测试
│   ├── test_superpowers_integration.py  # 集成测试
│   ├── test_config_manager.py        # 配置管理测试
│   ├── test_template_loader.py       # 模板加载测试
│   └── test_content_merger.py        # 内容合并测试
├── requirements.txt          # Python 依赖
├── SKILL.md                  # Skill 定义
└── README.md                 # 本文件
```

## 依赖

- Python 3.10+
- pytest（仅开发时）
- PyYAML

## 设计原则

### 1. 增强而非替换
- 复用 git worktree，不重新实现
- task-flow 只负责任务持久化和状态管理

### 2. 文件即事实源
- 任务文件是唯一的真相源
- YAML frontmatter 存储元数据
- Plan Packet 存储结构化计划

### 3. TDD 驱动
- 96.7% 测试通过率
- 红绿重构循环
- 测试覆盖所有核心功能

## 版本历史

### v2.4 (当前版本)
- ✅ 持久化任务索引与 todo_id 映射
- ✅ list-tasks / get_task_by_todo_id 直走索引
- ✅ frontmatter 轻量解析快速路径
- ✅ execute-next-batch 使用就绪队列避免全量扫描
- ✅ 支持 TASK_FLOW_SKIP_INIT=1 跳过初始化检查

### v2.3
- ✅ 自动初始化 CLAUDE.md/AGENTS.md
- ✅ 模板渲染与智能合并（version markers）
- ✅ 初始化命令与非交互环境自动初始化
- ✅ start-task 在 worktree 缺少 docs 时自动同步
- ✅ docs 未提交变更时提示但不阻断
- ✅ 188/189 测试通过（1 skipped，99.5%）

### v2.2
- ✅ 任务索引与 O(1) 查找
- ✅ frontmatter 单次更新
- ✅ ExecutionEngine 使用 set 状态跟踪
- ✅ start-task 从 frontmatter 读取 branch
- ✅ 145/146 测试通过（1 skipped，99.3%）

### v2.1
- ✅ Markdown 计划文件解析支持
- ✅ TodoWrite 兼容层
- ✅ CI 命令自动检测
- ✅ execute-next-batch 批量执行
- ✅ 59/61 测试通过（96.7%）

### v2.0
- ✅ 执行引擎实现
- ✅ 计划类型定义
- ✅ YAML 计划文件支持

## License

MIT
