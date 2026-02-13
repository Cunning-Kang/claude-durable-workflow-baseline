# Workflow Conventions

## 1) Canonical Source of Truth
- 长期协作事实源仅为 `docs/tasks/` 与 `docs/plans/`。
- `docs/plans/` 使用 `YYYY-MM-DD-*.md` 命名。
- 活跃任务机器状态维护在 `docs/tasks/_active.json`（注册表，不替代 canonical docs）。
- worktree 过程事件写入 `.worktrees/<branch>/.task-flow/events.jsonl`（append-only）。

## 2) Worktree 目录规则
- 统一使用 `.worktrees/` 存放工作树。
- 必须通过 `git check-ignore -q .worktrees` 校验忽略规则。
- 若不通过：更新 `.gitignore` 增加 `.worktrees/`，并提交该修复后再继续。

## 3) Docs Gate（启动前守门）
- start-task 前检查 docs 范围 staged/unstaged 变更。
- 若仅 docs 变更：询问继续(Y)/取消(N)，选择继续则自动提交 docs。
- 若 docs + code 混改：提供 [1]仅 docs、[2]全部提交、[3]取消。
- docs-only 提交消息固定：`docs: update workflow artifacts`。

## 4) Active Registry / Events 规则
- start-task 必须更新 `docs/tasks/_active.json` 中对应任务条目。
- start-task 必须向 `.task-flow/events.jsonl` 追加 `task_started` 事件。
- `_active.json` 使用锁文件与原子替换写入；`events.jsonl` 使用追加锁保证 `seq` 单调递增。

## 5) PLAN.md 固定入口
- 根目录 `PLAN.md` 维护当前活跃任务路由。
- 至少包含：任务、docs 路径、worktree 路径、`_active.json`、`events.jsonl`。
- 重复更新必须幂等，不得重复追加路由块。

## 6) 回滚与清理
- 删除工作树：`git worktree remove .worktrees/<branch>`
- 删除分支：`git branch -D <branch>`
- 清理残留：`git worktree prune`
