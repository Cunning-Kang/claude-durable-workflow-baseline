# Task-Flow + Superpowers 全链路 E2E 测试设计

**Goal:** 在临时沙盒项目中用真实 `task-flow` 与 `superpowers` 走完完整工作流（create-task → Plan Packet → 生成 plan_file → execute-next-batch → complete-task → 合并/清理），覆盖 `manual / subagent-driven / executing-plans` 三种执行模式，并固化关键断言为 pytest e2e 测试。

---

## 1. 目标与范围

**范围**
- 沙盒项目：`/tmp/claude/task-flow-e2e`
- 真实调用技能：`task-flow` + `superpowers` 全链路
- 覆盖三种 execution_mode
- 记录可复现证据并转化为自动化 e2e

**成功标准**
- 全流程无错误，关键产物存在（任务文件、plan_file、worktree、合并提交、清理后目录消失）
- 输出可验证（CLI 输出、JSON 统计、git log/worktree list）

---

## 2. 方案选型与取舍

**采用混合策略（推荐）**
1) 真实技能链路跑一遍并记录证据（满足必须真实调用的要求）
2) 把关键断言固化为 pytest e2e（可回归、可追踪）

---

## 3. 架构与组件

- **沙盒项目层**：临时 git 仓库，避免污染主仓
- **task-flow 层**：create-task / update-task / execute-next-batch / complete-task
- **superpowers 层**：using-git-worktrees + writing-plans + subagent-driven-development + executing-plans + finishing-a-development-branch
- **证据层**：命令回显、frontmatter diff、plan_file 内容、git log、worktree list

---

## 4. 数据流与步骤

1) **初始化沙盒仓库**
- 创建 `/tmp/claude/task-flow-e2e`，`git init` + 初始提交
- 设置 `PYTHONPATH=/Users/cunning/.claude/skills/task-flow/src`

2) **TASK-001（manual）**
- `task-flow create-task` → `update-task --step/--note`
- 校验 frontmatter 更新

3) **TASK-002（subagent-driven）**
- 设置 `execution_mode: subagent-driven`
- 调用 `superpowers:subagent-driven-development`
- 记录输出/错误（尤其是对 plan_file 的提示）

4) **TASK-003（executing-plans）**
- 设置 `plan_file` + `execution_config`
- 调用 `superpowers:writing-plans` 生成计划文件
- `task-flow execute-next-batch`，校验 JSON 统计输出

5) **worktree + finishing**
- `superpowers:using-git-worktrees` 创建分支/工作区
- 最小变更提交
- `superpowers:finishing-a-development-branch` 合并与清理
- 验证 `git log` 与 `git worktree list`

---

## 5. 错误处理与诊断策略

- **前置条件失败**：缺失 `plan_file` / `execution_config`
- **计划文件不兼容**：`writing-plans` 产出非 YAML 或缺 `tasks`
- **技能调用失败**：记录 stderr、cwd、git 状态
- **执行统计异常**：`tasks_executed=0` 或 JSON 不可解析
- **worktree/merge 异常**：记录 `git worktree list`、`git status`、`git log`

每类问题都需：最小复现步骤 + 证据输出 + 预期/实际差异

---

## 6. 测试用例设计

### A. 真实技能链路（手工执行）
- TASK-001 manual：create-task → update-task → 验证 frontmatter
- TASK-002 subagent-driven：调用 skill → 记录输出/提示
- TASK-003 executing-plans：writing-plans → execute-next-batch → 验证 JSON 输出
- finishing：merge + cleanup → 验证 git 状态

### B. 自动化 pytest e2e（后续固化）
- plan_file 解析与 ExecutionEngine 执行统计
- 三种 execution_mode 的前置条件与输出提示
- finishing 流程 merge/cleanup 结果

---

## 7. 质量门禁

在全局技能目录运行：
```bash
PYTHONPATH=/Users/cunning/.claude/skills/task-flow/src \
pytest -q -c /Users/cunning/.claude/skills/task-flow/pytest.ini
```
