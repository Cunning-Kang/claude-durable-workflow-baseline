# Task Flow Skill - 使用指南

## 🎉 安装成功！

task-flow skill 已成功安装到 `~/.claude/skills/task-flow/`

---

## 📖 在 Claude Code 中的使用方式

### 方式 1：自然语言触发（推荐）

直接对 Claude 说：

```
"创建任务：实现用户认证功能"
```

Claude 会自动：
1. 调用 task-flow 创建任务
2. 生成 TASK-XXX ID
3. 创建包含 Plan Packet 的任务文件
4. 提示下一步操作

### 方式 2：明确指定命令

```
"用 task-flow 创建任务：添加登录页面"
```

### 方式 3：使用 skill 触发器

```
"使用 task-flow skill 列出所有任务"
```

---

## 🔄 完整工作流示例

### 场景：开发新功能

#### 1. 创建任务

**你说**：
```
"创建任务：为博客添加评论系统"
```

**Claude 执行**：
```bash
python ~/.claude/skills/task-flow/src/cli.py create-task "为博客添加评论系统"
```

**输出**：
```
✓ Created task: TASK-001
  File: docs/tasks/TASK-001-添加评论系统.md

Next steps:
  1. Edit the task file to fill in the Plan Packet
  2. Run: start-task TASK-001
```

#### 2. 填写 Plan Packet

**你说**：
```
"帮我填写 TASK-001 的 Plan Packet：
- Goal: 实现基于数据库的评论系统
- 包含评论、回复、点赞功能
- 使用 Django + PostgreSQL"
```

**Claude 会**：
- 读取任务文件
- 更新 Goal、Scope、Interfaces 等字段
- 填充 Execution Order

#### 3. 启动任务

**你说**：
```
"启动任务 TASK-001"
```

**Claude 执行**：
```bash
python ~/.claude/skills/task-flow/src/cli.py start-task TASK-001
```

**输出**：
```
✓ Created worktree: .worktrees/添加评论系统
✓ Created branch: 添加评论系统
✓ Task TASK-001 is now In Progress

Next steps:
  1. cd .worktrees/添加评论系统
  2. Review the Execution Order in the task file
  3. Start implementing!
```

#### 4. 开发中更新

**你说**：
```
"更新 TASK-001 进度：已完成第 2 步，创建了 Comment 模型"
```

**Claude 执行**：
```bash
python ~/.claude/skills/task-flow/src/cli.py update-task TASK-001 --step 2 --note "创建了 Comment 模型，包含用户、内容、时间戳字段"
```

#### 5. 完成任务

**你说**：
```
"完成任务 TASK-001"
```

**Claude 执行**：
```bash
python ~/.claude/skills/task-flow/src/cli.py complete-task TASK-001
```

**输出**：
```
✓ Task TASK-001 marked as Done
✓ Task file archived to docs/tasks/completed/

Next steps:
  1. Review the work in the worktree
  2. Run tests to verify everything works
  3. Choose merge strategy
  4. Clean up worktree when done
```

---

## 🎯 触发短语参考

| 你说 | Claude 执行 |
|------|-----------|
| "创建任务：XXX" | create-task |
| "新建任务：XXX" | create-task |
| "添加任务：XXX" | create-task |
| "列出所有任务" | list-tasks |
| "查看待办任务" | list-tasks --status "To Do" |
| "显示任务 TASK-001" | show-task TASK-001 |
| "启动任务 TASK-001" | start-task TASK-001 |
| "开始任务 TASK-001" | start-task TASK-001 |
| "更新 TASK-001 到第 3 步" | update-task --step 3 |
| "完成任务 TASK-001" | complete-task TASK-001 |
| "归档任务 TASK-001" | complete-task TASK-001 |

---

## 💡 高级用法

### 批量创建任务

**你说**：
```
"创建以下任务：
1. 实现用户注册
2. 实现用户登录
3. 实现密码重置"
```

**Claude 会**：
- 循环创建 3 个任务
- 生成 TASK-001, TASK-002, TASK-003
- 提供任务列表

### 查看任务统计

**你说**：
```
"用 task-flow 显示任务统计"
```

**Claude 会**：
- 列出所有任务
- 按状态分组
- 显示完成进度

### 任务导航

**你说**：
```
"切换到 TASK-002 的 worktree"
```

**Claude 会**：
- 读取任务文件获取 worktree 路径
- 执行 cd 命令
- 显示当前工作目录

---

## 🔧 与其他 Skills 配合

### + brainstorming

**你说**：
```
"用 brainstorming 探索评论系统的设计，
然后用 task-flow 创建任务"
```

### + writing-plans

**你说**：
```
"为 TASK-001 生成详细执行计划"
```

**Claude 会**：
- 读取任务的 Plan Packet
- 生成详细的 Implementation Plan
- 保存到 docs/plans/

### + subagent-driven-development

**你说**：
```
"用 subagent-driven 模式执行 TASK-001"
```

**Claude 会**：
- 更新任务 execution_mode
- 调用 subagent-driven-development skill
- 分配任务给 subagent

---

## 📝 最佳实践

### 1. 任务命名

✅ **好**：
- "实现用户认证"
- "添加评论系统"
- "优化数据库查询"

❌ **差**：
- "做认证"
- "修bug"
- "新功能"

### 2. Plan Packet 填写

每次创建任务后，立即填写：
- ✅ Goal（明确目标）
- ✅ Scope（范围和风险）
- ✅ Execution Order（执行步骤）
- ✅ Acceptance Criteria（验收标准）

### 3. 进度更新

开发过程中及时更新：
- ✅ 每完成一步，更新 --step
- ✅ 重要决策，添加 --note
- ✅ 状态变化，更新 --status

### 4. 任务归档

完成后及时归档：
- ✅ 运行 complete-task
- ✅ 清理 worktree
- ✅ Code Review 后再合并

---

## 🐛 常见问题

### Q: task-flow skill 没有被识别？

**A**: 检查安装：
```bash
ls ~/.claude/skills/task-flow/SKILL.md
```

如果不存在，重新运行：
```bash
cd /path/to/task-flow
bash install.sh
```

### Q: 命令执行失败？

**A**: 检查 Python 环境：
```bash
python3 --version  # 需要 >= 3.7
```

### Q: Git worktree 创建失败？

**A**: 确保在 git 仓库中：
```bash
git status
```

### Q: 如何卸载？

**A**: 删除 skill 目录：
```bash
rm -rf ~/.claude/skills/task-flow
```

---

## 🚀 下一步

### 立即可用

task-flow skill 已经完全可用，开始在你的项目中使用：

1. **创建第一个任务**：
   ```
   "创建任务：熟悉 task-flow 系统"
   ```

2. **填写 Plan Packet**：
   ```
   "帮我填写这个任务的 Plan Packet"
   ```

3. **启动任务**：
   ```
   "启动任务 TASK-001"
   ```

### 后续优化

计划中的功能：
- [ ] CI 命令自动检测
- [ ] Superpowers 深度集成
- [ ] 任务依赖关系
- [ ] Web UI 界面

---

## 📚 相关资源

- **项目位置**: `~/.claude/skills/task-flow/`
- **源码**: `/Users/cunning/Workspaces/heavy/skills-creation/task-flow/`
- **文档**: `~/.claude/skills/task-flow/README.md`
- **测试**: `~/.claude/skills/task-flow/tests/`

---

**开始使用 task-flow，让你的任务管理更高效！** 🎉
