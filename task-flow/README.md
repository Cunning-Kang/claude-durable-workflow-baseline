# task-flow

基于文件的轻量级任务管理系统，使用 TDD 方法构建。

## 特性

- ✅ **持久化任务管理** - 任务文件保存在 `docs/tasks/`
- ✅ **完整 Plan Packet** - 结构化的计划模板
- ✅ **Git Worktree 集成** - 自动创建隔离的工作环境
- ✅ **TDD 驱动** - 37 个测试，100% 通过率
- ✅ **零依赖 MCP** - 不需要外部 MCP 服务器

## 安装

```bash
# 克隆到你的项目
git clone <repo> /path/to/task-flow

# 添加到 PATH
export PATH="/path/to/task-flow/src:$PATH"
```

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
Creating worktree: .worktrees/implement-user-authentication
✓ Created worktree: .worktrees/implement-user-authentication
✓ Created branch: implement-user-authentication

✓ Task TASK-001 is now In Progress

Next steps:
  1. cd .worktrees/implement-user-authentication
  2. Review the Execution Order in the task file
  3. Start implementing!
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

输出：
```
✓ Task TASK-001 marked as Done
✓ Task file archived to docs/tasks/completed/

Next steps:
  1. Review the work in the worktree
  2. Run tests to verify everything works
  3. Choose merge strategy:
     - Merge locally: git merge <branch>
     - Create PR: gh pr create
  4. Clean up worktree when done
     git worktree remove .worktrees/<branch>
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
```

## 测试

```bash
# 运行所有测试
PYTHONPATH=src python -m pytest tests/ -v

# 查看覆盖率
PYTHONPATH=src python -m pytest tests/ --cov=src --cov-report=html
```

## 项目结构

```
task-flow/
├── src/
│   ├── cli.py              # CLI 入口
│   ├── task_manager.py     # 任务管理核心逻辑
│   └── __main__.py         # Python 模块支持
├── tests/
│   ├── test_cli.py         # CLI 测试
│   ├── test_task_manager.py # 核心逻辑测试
│   ├── test_start_task.py  # Worktree 集成测试
│   └── test_update_and_complete.py  # 工作流测试
└── README.md
```

## 设计原则

### 1. 增强而非替换
- 复用 `finishing-a-development-branch` 的完成逻辑
- 复用 `using-git-worktrees` 的 worktree 创建
- task-flow 只负责任务持久化和状态管理

### 2. 文件即事实源
- 任务文件是唯一的真相源
- YAML frontmatter 存储元数据
- Plan Packet 存储结构化计划

### 3. TDD 驱动
- 37 个测试，100% 通过率
- 红绿重构循环
- 测试覆盖所有核心功能

## 下一步

- [ ] 集成 CI 命令自动检测
- [ ] 创建 Skill 文件使其可安装
- [ ] 添加 resume-task 命令
- [ ] 支持 execution_mode: subagent-driven

## License

MIT
