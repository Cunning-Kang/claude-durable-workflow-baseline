# 项目工作流指南

> **版本**: 1.0.0 | **更新日期**: {DATE}
> **技术栈**: task-flow v2.2 + superpowers

本项目采用 **task-flow** 作为任务管理系统，结合 **superpowers** 技能体系提供结构化的开发流程。

---

## 快速开始

```bash
# 创建并启动任务
创建任务：实现功能 X
启动任务 TASK-001

# 完成后归档
完成任务 TASK-001
```

---

## 核心命令

### 任务管理

| 用户语句 | 功能 |
|---------|------|
| 创建任务：{标题} | 创建新任务 |
| 启动任务 TASK-XXX | 启动任务（创建 worktree） |
| 更新任务 TASK-XXX 进度到第 N 步 | 更新进度 |
| 完成任务 TASK-XXX | 完成并归档 |
| 查看任务 TASK-XXX | 查看详情 |
| 列出所有任务 | 显示任务列表 |

### 计划执行

| 用户语句 | 功能 |
|---------|------|
| 按计划执行 TASK-XXX | 执行下一批任务 |
| 执行计划 TASK-XXX | 同上（别名） |

### 流程协作

| 用户语句 | 触发技能 |
|---------|---------|
| 开始需求澄清：TASK-XXX | superpowers:brainstorming |
| 为 TASK-XXX 写实施计划 | superpowers:writing-plans |
| 审查 TASK-XXX 的实现 | superpowers:requesting-code-review |

---

## 工作流程

### 标准流程（推荐）

```
创建任务 → 需求澄清 → 实施计划 → 启动任务 → 按计划执行 → 完成任务
```

### 简化流程（小改动）

```
创建任务 → 启动任务 → 直接实现 → 完成任务
```

---

## 项目特定信息

### 技术栈

- **语言**: {LANGUAGE}
- **框架**: {FRAMEWORK}
- **测试**: {TEST_FRAMEWORK}

### 目录结构

```
.
├── docs/
│   ├── tasks/          # 任务文件
│   └── plans/          # 实施计划
├── src/                # 源代码
└── tests/              # 测试文件
```

### 开发规范

- 代码风格：{CODE_STYLE}
- 提交规范：{COMMIT_CONVENTION}
- 分支策略：{BRANCH_STRATEGY}

---

## 相关技能

| 技能 | 用途 |
|------|------|
| task-flow | 任务管理核心 |
| superpowers:brainstorming | 需求澄清 |
| superpowers:writing-plans | 计划编写 |
| superpowers:executing-plans | 计划执行 |
| superpowers:subagent-driven-development | 子代理开发 |

---

## 常见问题

**Q: 如何创建新任务？**

A: 说"创建任务：{标题}"即可

**Q: 如何查看所有任务？**

A: 说"列出所有任务"即可

**Q: 任务完成后会自动归档吗？**

A: 是的，执行"完成任务 TASK-XXX"会自动归档到 `docs/tasks/completed/`
