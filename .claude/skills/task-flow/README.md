# task-flow

基于文件的轻量级任务管理系统，使用 TDD 方法构建。提供持久化任务跟踪、Plan Packet 结构化计划、Git Worktree 自动化集成。

## 特性

- ✅ **持久化任务管理** - 任务文件保存在 `docs/tasks/`
- ✅ **完整 Plan Packet** - 结构化的 9 部分计划模板
- ✅ **Git Worktree 集成** - 自动创建隔离的工作环境
- ✅ **TDD 驱动** - 145/146 测试通过（1 skipped，99.3%）
- ✅ **Markdown/YAML 计划文件** - 支持多种计划格式
- ✅ **TodoWrite 兼容** - 兼容 TodoWrite 格式输入
- ✅ **CI 命令自动检测** - 自动检测项目 CI 配置
- ✅ **零依赖 MCP** - 不需要外部 MCP 服务器

## 快速开始

### 1. 创建任务

```bash
cd your-project
python -m cli create-task "Implement user authentication"
```

输出：
```
✓ Created task: TASK-001
  File: docs/tasks/TASK-001-implement-user-authentication.md

Next steps:
  1. Edit the task file to fill in the Plan Packet
  2. Run: start-task TASK-001
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
python -m cli start-task TASK-001
```

输出：
```
✓ Created worktree: .worktrees/implement-user-authentication
✓ Created branch: implement-user-authentication
✓ Task TASK-001 is now In Progress
```

### 4. 更新进度

```bash
# 更新步骤
python -m cli update-task TASK-001 --step 2

# 添加备注
python -m cli update-task TASK-001 --note "决定使用 pyjwt 库"
```

### 5. 完成任务

```bash
python -m cli complete-task TASK-001
```

## 所有命令

```bash
# 创建任务
python -m cli create-task "<title>"

# 列出任务
python -m cli list-tasks [--status <status>]

# 显示任务详情
python -m cli show-task <TASK-ID>

# 启动任务（创建 worktree）
python -m cli start-task <TASK-ID>

# 更新任务
python -m cli update-task <TASK-ID> [--status <status>] [--step <n>] [--note <note>]

# 完成任务
python -m cli complete-task <TASK-ID> [--no-cleanup]

# 执行计划批次
python -m cli execute-next-batch <TASK-ID>

# TodoWrite 兼容
python -m cli todowrite --input-file todos.json
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

**测试结果**: 59/61 通过（96.7%）

## 项目结构

```
task-flow/
├── src/
│   ├── __init__.py
│   ├── __main__.py           # Python 模块支持
│   ├── cli.py                # CLI 入口（450+ 行）
│   ├── task_manager.py       # 任务管理核心逻辑（350+ 行）
│   ├── ci_detector.py        # CI 命令检测
│   ├── execution_engine.py   # 执行引擎
│   ├── plan_generator/       # 计划类型定义
│   │   └── __init__.py
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
│   └── test_superpowers_integration.py  # 集成测试
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

### v2.1 (当前版本)
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
