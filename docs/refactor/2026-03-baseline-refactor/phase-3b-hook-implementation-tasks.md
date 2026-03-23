# Phase 3B — Hook Implementation Tasks

> Status: future implementation task list derived from `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementation-design.md`
> Authoritative inputs: `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementation-design.md`, `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-plan.md`, `docs/refactor/2026-03-baseline-refactor/phase-3b-rule-to-hook-migration-tasks.md`
> Historical references only: `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementations-plan.md`, `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementations-tasks.md`

## Execution constraints

- This file is for the next implementation phase; the current phase still does **not** implement any hook source.
- Keep all artifacts in `project` scope only.
- Do not modify the authoritative migration plan/tasks files.
- Do not write live settings.
- Do not default-enable any hook.
- Do not expand H-01 / H-02 / H-03 into workflow orchestration.

## Shared artifact convention

Each cluster implementation creates exactly one project-scoped template family:

- `distribution/hooks/project/<candidate>/hook.mjs`
- `distribution/settings-snippets/project/<candidate>.settings.jsonc`
- `distribution/hooks/project/<candidate>/README.md`
- `distribution/hooks/project/<candidate>/scope.md`
- `distribution/hooks/project/<candidate>/manual-test.md`
- `distribution/hooks/project/<candidate>/rollback.md`

---

## H-01 — `taskcompleted-authoritative-state-gate`

### P3B-I01 — 建立 H-01 artifact 骨架
- **输入：** H-01 design mapping
- **输出：**
  - `distribution/hooks/project/taskcompleted-authoritative-state-gate/`
  - `distribution/settings-snippets/project/taskcompleted-authoritative-state-gate.settings.jsonc`
- **完成定义：** candidate 名称、目录和文件命名固定；产物全部位于 `project` scope；没有 live wiring。

### P3B-I02 — 编写 H-01 hook source template
- **输入：** H-01 machine-checkable subset 与 allow/block 条件
- **输出：** `distribution/hooks/project/taskcompleted-authoritative-state-gate/hook.mjs`
- **完成定义：** template 只检查 configured durable tracker 与 target task 的 closure consistency；不会派生 next step、不会创建第二 tracker、不会做 backlog orchestration。

### P3B-I03 — 编写 H-01 settings snippet example
- **输入：** H-01 evidence/state source 设计
- **输出：** `distribution/settings-snippets/project/taskcompleted-authoritative-state-gate.settings.jsonc`
- **完成定义：** snippet 展示 project-level opt-in、durable tracker path/glob 配置与 hook 注册方式；不写 live project settings；不默认启用。

### P3B-I04 — 编写 H-01 README
- **输入：** H-01 enforcement objective、event choice、residual gap
- **输出：** `distribution/hooks/project/taskcompleted-authoritative-state-gate/README.md`
- **完成定义：** README 说明此 hook 只守 completion-time durable state consistency；解释为何选 `TaskCompleted`，以及为何不承担 checkpoint、reprioritization、next-task derivation。

### P3B-I05 — 编写 H-01 scope note
- **输入：** H-01 deliberately-not-implemented boundary
- **输出：** `distribution/hooks/project/taskcompleted-authoritative-state-gate/scope.md`
- **完成定义：** scope 文档明确列出 machine-checkable subset 与故意留给 protocol docs / Superpowers / human judgment 的部分。

### P3B-I06 — 编写 H-01 manual test
- **输入：** H-01 allow/block 条件
- **输出：** `distribution/hooks/project/taskcompleted-authoritative-state-gate/manual-test.md`
- **完成定义：** 手测覆盖至少以下场景：无 tracker 匹配、多个 tracker 冲突、task 无法映射、`Current` 仍指向已完成任务、durable state 自洽时允许完成。

### P3B-I07 — 编写 H-01 rollback note
- **输入：** project-scope adoption model
- **输出：** `distribution/hooks/project/taskcompleted-authoritative-state-gate/rollback.md`
- **完成定义：** rollback 只描述如何撤销 project-level adoption、移除 snippet merge、停用该 hook；不涉及 user/global settings 破坏性操作。

---

## H-02 — `taskcompleted-verification-evidence-gate`

### P3B-I08 — 建立 H-02 artifact 骨架
- **输入：** H-02 design mapping
- **输出：**
  - `distribution/hooks/project/taskcompleted-verification-evidence-gate/`
  - `distribution/settings-snippets/project/taskcompleted-verification-evidence-gate.settings.jsonc`
- **完成定义：** candidate 名称、目录和文件命名固定；全部保持 source/snippet 形态；没有 live wiring。

### P3B-I09 — 编写 H-02 hook source template
- **输入：** H-02 machine-checkable subset 与 allow/block 条件
- **输出：** `distribution/hooks/project/taskcompleted-verification-evidence-gate/hook.mjs`
- **完成定义：** template 只检查 durable verification artifact 是否存在、是否非 placeholder、是否含已填充 evidence fields；不运行测试、不解析原始日志、不决定 verification strategy。

### P3B-I10 — 编写 H-02 settings snippet example
- **输入：** H-02 evidence/state source 设计
- **输出：** `distribution/settings-snippets/project/taskcompleted-verification-evidence-gate.settings.jsonc`
- **完成定义：** snippet 展示 verification artifact path 与字段配置方式；保持 opt-in；不写 live settings；不默认启用。

### P3B-I11 — 编写 H-02 README
- **输入：** H-02 enforcement objective、event choice、residual gap
- **输出：** `distribution/hooks/project/taskcompleted-verification-evidence-gate/README.md`
- **完成定义：** README 说明该 hook 只守 durable verification evidence presence gate；解释为何它优先于 `Stop` reminder，且不替代 verification policy。

### P3B-I12 — 编写 H-02 scope note
- **输入：** H-02 deliberately-not-implemented boundary
- **输出：** `distribution/hooks/project/taskcompleted-verification-evidence-gate/scope.md`
- **完成定义：** scope 文档明确排除 gate applicability 决策、命令选择、日志解释、证据质量判断与广义 freshness 推断。

### P3B-I13 — 编写 H-02 manual test
- **输入：** H-02 allow/block 条件
- **输出：** `distribution/hooks/project/taskcompleted-verification-evidence-gate/manual-test.md`
- **完成定义：** 手测覆盖至少以下场景：verification artifact 缺失、只有模板占位、字段为空、字段已填充并允许完成。

### P3B-I14 — 编写 H-02 rollback note
- **输入：** project-scope adoption model
- **输出：** `distribution/hooks/project/taskcompleted-verification-evidence-gate/rollback.md`
- **完成定义：** rollback 只描述如何撤销 project-level adoption 与 snippet merge；不引入 bootstrap、默认启用或 user/global 层回滚。

---

## H-03 — `taskcompleted-review-evidence-gate`

### P3B-I15 — 建立 H-03 artifact 骨架
- **输入：** H-03 design mapping
- **输出：**
  - `distribution/hooks/project/taskcompleted-review-evidence-gate/`
  - `distribution/settings-snippets/project/taskcompleted-review-evidence-gate.settings.jsonc`
- **完成定义：** candidate 名称、目录和文件命名固定；全部位于 `project` scope；没有 live wiring。

### P3B-I16 — 编写 H-03 hook source template
- **输入：** H-03 machine-checkable subset 与 allow/block 条件
- **输出：** `distribution/hooks/project/taskcompleted-review-evidence-gate/hook.mjs`
- **完成定义：** template 只在 review-required signal 已存在时检查 durable review artifact 与 `Reviewer / Reference / Outcome`；仅允许 `PASS`；不推导 review policy、不分配 reviewer、不评价 review 质量。

### P3B-I17 — 编写 H-03 settings snippet example
- **输入：** H-03 evidence/state source 设计
- **输出：** `distribution/settings-snippets/project/taskcompleted-review-evidence-gate.settings.jsonc`
- **完成定义：** snippet 展示 review-required signal 与 review artifact path 的 project-level 配置方式；不写 live settings；不默认启用。

### P3B-I18 — 编写 H-03 README
- **输入：** H-03 enforcement objective、event choice、residual gap
- **输出：** `distribution/hooks/project/taskcompleted-review-evidence-gate/README.md`
- **完成定义：** README 说明该 hook 只守 review-required evidence presence gate；解释为何它不替代 `review-protocol.md` 或 Superpowers review surface。

### P3B-I19 — 编写 H-03 scope note
- **输入：** H-03 deliberately-not-implemented boundary
- **输出：** `distribution/hooks/project/taskcompleted-review-evidence-gate/scope.md`
- **完成定义：** scope 文档明确排除 review-required policy 推导、真实独立性证明、review 质量判断与 findings 处置编排。

### P3B-I20 — 编写 H-03 manual test
- **输入：** H-03 allow/block 条件
- **输出：** `distribution/hooks/project/taskcompleted-review-evidence-gate/manual-test.md`
- **完成定义：** 手测覆盖至少以下场景：无 review-required signal 时 allow；signal 存在但 review artifact 缺失时 block；`Reviewer/Reference` 缺失时 block；`Outcome=FAIL/BLOCKED` 时 block；`Outcome=PASS` 时 allow。

### P3B-I21 — 编写 H-03 rollback note
- **输入：** project-scope adoption model
- **输出：** `distribution/hooks/project/taskcompleted-review-evidence-gate/rollback.md`
- **完成定义：** rollback 只描述如何停用该 project-level review gate 与撤销 snippet merge；不改 user/global 层默认行为。

---

## Cross-cluster closeout

### P3B-I22 — 更新 project hooks 根 README 的候选索引
- **输入：** 三个 cluster 的最终 candidate 名称与 README 边界
- **输出：** `distribution/hooks/project/README.md`
- **完成定义：** 根 README 能索引这三类 project-level template，并再次强调 source-only、opt-in、非默认启用。

### P3B-I23 — 更新 project settings snippets 根 README 的候选索引
- **输入：** 三个 cluster 的 snippet 名称与 opt-in 说明
- **输出：** `distribution/settings-snippets/project/README.md`
- **完成定义：** 根 README 能索引这三类 project-level settings snippet，并明确它们不是 live settings。

### P3B-I24 — 收口复核 implementation boundary
- **输入：** 所有新建 template artifacts
- **输出：** implementation phase 自检记录（可记入实施时的 review/verify artifact）
- **完成定义：** 复核通过以下边界：不改 authoritative migration inputs、不写 live settings、不默认启用、不引入第二主控面、不把 H-01/H-02/H-03 扩展成广义 workflow orchestration。
