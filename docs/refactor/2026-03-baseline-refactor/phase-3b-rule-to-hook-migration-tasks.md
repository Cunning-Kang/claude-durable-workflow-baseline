# Phase 3B — Rule-to-Hook Migration Tasks

> Date: 2026-03-22
> Scope: rebuild Phase 3B as rule inventory → migration mapping → hook design mapping
> Constraint: this task file does **not** authorize hook implementation in the current round

---

## 执行约束

- 必须先做 rule inventory，再做 migration mapping，再做 hook design mapping
- 当前轮不实现任何 hook 源码
- 当前轮不修改任何 live `settings.json` / `settings.local.json`
- 当前轮不修改 bootstrap / init / default wiring
- 当前轮不得从 hook event 倒推候选
- 只有在 authoritative 规则迁移总表完成后，才允许提出 implementation candidates
- 每个任务都必须明确输入文件、输出文件、完成定义

---

## Stage A — Rule Inventory

### P3B-R01 — 建立全局规则源清单
- **输入文件：**
  - `global/CLAUDE.md`
  - `global/standards/core-standard.md`
  - `global/guides/orchestration-extension.md`
- **输出文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
- **完成定义：**
  - 文档中明确列出本轮 authoritative global rule sources
  - 明确哪些内容仍保留在 global 层，哪些已被删除、压缩或迁出
  - 不出现从 hook 事件位点出发的候选倒推

### P3B-R02 — 盘点被删除 / 压缩 / 迁出的规则簇
- **输入文件：**
  - `global/standards/core-standard.md`
  - `global/guides/orchestration-extension.md`
  - 当前 refactor 说明中的 Phase 1 / Phase 2 记录
- **输出文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
- **完成定义：**
  - 以 rule cluster 而不是零散句子进行盘点
  - 每个 rule cluster 都有“原规则内容 / 意图”与“当前状态”
  - 至少覆盖 task state、verification、review、completion contract、routing/orchestration 等主要迁移簇

### P3B-R03 — 对照当前承接层文档确认迁移落点
- **输入文件：**
  - `baseline/docs/workflow/execution-contract.md`
  - `baseline/docs/workflow/review-protocol.md`
  - `baseline/docs/workflow/review-checklist.md`
  - `baseline/docs/workflow/native-task-translation.md`
  - `docs/reference/hooks-scope.md`
  - `docs/reference/superpowers-boundary.md`
  - `docs/refactor/2026-03-baseline-refactor/decisions.md`
- **输出文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
- **完成定义：**
  - 对每个已迁出规则簇写清 primary destination
  - 明确 protocol docs、Superpowers、hooks、memory、commands 的职责边界
  - 明确哪些规则已经被正确承接，不再需要 hooks

---

## Stage B — Migration Mapping

### P3B-M01 — 编制 authoritative 规则迁移总表
- **输入文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
  - Stage A 的 rule inventory 结果
- **输出文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
- **完成定义：**
  - 规则迁移总表完整包含：
    - 原规则来源
    - 原规则内容 / 意图
    - 当前状态
    - 迁移去向
    - 若迁到 hooks：对应 event / scope / template artifacts
    - 当前 gap
  - 总表成为 Phase 3B 的 authoritative mapping，而不是补充说明

### P3B-M02 — 对每个规则簇做 destination classification
- **输入文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
  - `docs/reference/hooks-scope.md`
  - `docs/reference/superpowers-boundary.md`
- **输出文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
- **完成定义：**
  - 每个 rule cluster 只有一个 primary destination
  - 若 hooks 只是 enforcement subset，必须写清 primary owner 与 hook-enforced subset
  - 明确列出哪些规则不该迁到 hooks，而应保留在 command / protocol / memory / Superpowers

### P3B-M03 — 识别 deterministic enforcement gaps
- **输入文件：**
  - authoritative 规则迁移总表
  - `baseline/docs/workflow/execution-contract.md`
  - `baseline/docs/workflow/review-protocol.md`
  - `docs/reference/hooks-scope.md`
- **输出文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
- **完成定义：**
  - 仅标记那些“文档语义已有承接，但 deterministic enforcement 仍缺失”的规则簇
  - gap 描述具体到可机器判断的 subset
  - 不把 reminder / guidance / routing heuristics 错判为 deterministic gap

### P3B-M04 — 固定 hooks migration set
- **输入文件：**
  - authoritative 规则迁移总表
  - Stage B 的 gap analysis
- **输出文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
- **完成定义：**
  - hooks migration set 只包含真正需要 hooks 的 migrated rule clusters
  - 每个 cluster 都写清“为什么必须由 hooks 承接”
  - 集合中不包含 routing / orchestration ownership / reminder-only 规则

---

## Stage C — Hook Design Mapping

### P3B-H01 — 为 hooks migration set 建立 hook design mapping
- **输入文件：**
  - hooks migration set
  - `docs/reference/hooks-scope.md`
  - `docs/reference/superpowers-boundary.md`
- **输出文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
- **完成定义：**
  - 每个 cluster 只设计到 event family / scope / template artifacts / residual gap
  - 不进入 hook source code 设计
  - 不出现 live settings、自动安装、默认启用方案

### P3B-H02 — 从规则簇而不是事件位点推导 implementation candidates
- **输入文件：**
  - authoritative 规则迁移总表
  - hooks migration set
  - hook design mapping
- **输出文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-tasks.md`
- **完成定义：**
  - 只有在总表完成后才出现 candidates
  - 每个 candidate 都能反向追溯到具体 rule cluster
  - 明确排除旧版 event-first candidates 作为 authoritative 输入

### P3B-H03 — 重写 Phase 3B 任务文件，使后续实现以 migration mapping 为前置条件
- **输入文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
  - 本任务文件
  - 废弃草案：
    - `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementations-plan.md`
    - `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementations-tasks.md`
- **输出文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-tasks.md`
- **完成定义：**
  - 任务文件的先后顺序明确为 inventory → mapping → design mapping
  - 不会让后续执行从一开始就去写 hook 源码
  - 每个任务均含输入文件、输出文件、完成定义

---

## 收口复核

### P3B-C01 — 复核 Phase 3B 不再以 event-first 逻辑驱动
- **输入文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-tasks.md`
  - 废弃旧草案两份文件
- **输出文件：**
  - 同上两份新文件
- **完成定义：**
  - 新 Phase 3B 文案从被迁出的规则簇出发，而不是从 hook events 出发
  - 明确写出旧草案为何被废弃
  - 不再以“首批提醒型模板候选”作为驱动逻辑

### P3B-C02 — 复核边界：不实现 hook、不改 live settings、不动 bootstrap
- **输入文件：**
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`
  - `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-tasks.md`
- **输出文件：**
  - 同上两份新文件
- **完成定义：**
  - 文档明确当前轮只是 migration planning，不是 hook implementation
  - 文档中没有任何 live runtime wiring、默认启用、自动安装或 settings 修改动作
  - 与 `docs/reference/hooks-scope.md`、`docs/reference/superpowers-boundary.md` 无冲突

---

## 完成判定

只有当以下条件全部满足时，新的 Phase 3B 任务层才算完成：

1. Stage A / B / C 的顺序已经固定，且不可跳步
2. authoritative 规则迁移总表已经成为后续 hook 设计的前提输入
3. hooks migration set 只来自 migrated rule clusters
4. implementation candidates 只在总表完成后出现
5. 任务文件未授权当前轮实现任何 hook 源码
6. 文档明确哪些规则应保留在 command / protocol / memory / Superpowers，而不是 hooks
