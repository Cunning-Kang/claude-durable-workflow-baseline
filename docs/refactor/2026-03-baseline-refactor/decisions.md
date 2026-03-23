# 2026-03 Baseline Refactor 关键决策

## D-001 — Superpowers 是主控层
- **决策**：Superpowers 继续承担全局主控职责；本仓库不能重建一个平行的通用 workflow control layer。
- **原因**：当前仓库已经被定位为 baseline source repo / distribution source，而不是新的总控 runtime。
- **影响**：凡是与 planning / execution / finishing / review lane 同责的能力，都必须收窄、桥接、迁移或删除。

## D-002 — baseline repo 不提供 competing generic workflow skills
- **决策**：本仓库不再新增，也不长期保留，与 Superpowers execution/planning/review 主线冲突的通用 workflow skills。
- **原因**：重复提供同语义能力会制造双入口、双协议和职责冲突。
- **影响**：`global/skills/spec-execute/SKILL.md` 需要冻结并迁移；其他类似入口也要复核。

## D-003 — hooks 必须按 scope 分层
- **决策**：hooks 只能按 `user` / `project` / `local example only` 分层提供，并以 source / snippets 形式分发。
- **原因**：hooks 天然依赖用户环境、团队风险偏好和项目边界，不能被一刀切全局化。
- **影响**：未来 hooks 产物应进入 `distribution/hooks/` 与 `distribution/settings-snippets/`，且必须显式说明 opt-in。

## D-004 — global core 只保留长期稳定约束
- **决策**：`global/standards/core-standard.md` 只保留长期稳定、低争议、高杠杆约束，不再承接报告模板、执行状态机、经验性样例。
- **原因**：always-on global core 一旦膨胀，会污染所有会话，并与协议文档/主控层发生职责重叠。
- **影响**：执行协议、review protocol、memory guidance 需要迁往更合适的 repo-local 文档层。

## D-005 — protocol docs / commands / hooks / memory 必须职责分离
- **决策**：
  - `protocol docs` 负责 repo-local 的执行/评审/记忆协议说明；
  - `commands` 只保留薄入口或桥接，不做总控编排；
  - `hooks` 负责可选 deterministic enforcement source/snippets；
  - `memory` 负责 durable lessons / patterns / gotchas。
- **原因**：只有分层，才能避免“文档、命令、hook、memory 全都在重复讲同一套控制逻辑”。
- **影响**：后续 Phase 2 ~ Phase 4 必须按承接层 → hooks → memory 的顺序推进。

## D-006 — 说明性边界文档放在 `docs/reference/`
- **决策**：边界说明、scope 说明、reference/schema 类文档应放在 `docs/reference/`，而不是顶层 `reference/` 或 global core。
- **原因**：这类内容是说明性资产，不是 baseline runtime 文件，也不是全局 always-on 规则。
- **影响**：`superpowers-boundary.md`、`hooks-scope.md`、`memory-boundary.md` 等均应收敛到 `docs/reference/`。

## D-007 — 当前审计源文件先按实际路径引用
- **决策**：在 Phase 1 正式迁移前，继续把最新审计文档视为 `docs/plan/2026-03-22-production-baseline-audit-and-refactor-plan.md`。
- **原因**：当前仓库真实状态如此，控制面应基于实际结构，而不是假设结构。
- **影响**：本轮新文件全部按当前真实路径建立引用；目录迁移在后续 task 中处理。

## D-008 — 审计材料 canonical path 切换到 `docs/audits/`
- **决策**：自 `P1-T04` 完成起，审计材料 canonical path 统一切换为 `docs/audits/2026-03-22-production-baseline-audit-and-refactor-plan.md`；`docs/plan/` 不再作为活动目录。
- **原因**：Phase 1 目录迁移已完成，需要消除活动审计路径的歧义，并让目录语义与内容类型一致。
- **影响**：后续边界文档、决策记录与变更记录统一引用 `docs/audits/*`；`docs/plan/` 仅允许出现在历史任务描述或审计原文中。

## D-009 — Phase 2 冲突入口直接退出 global distribution surface
- **决策**：`global/skills/spec-execute/SKILL.md` 直接移除，并以 `global/skills/spec-execute/README.md` 提供迁移说明；`global/commands/finish-branch.md` 直接退出本仓库分发表面，不再作为 baseline source repo 的活动入口。
- **原因**：两者都落在 Superpowers 已拥有的 execution / finishing lane 上；继续以 skill 或 command 形式分发，只会保留平行主控层灰区。
- **影响**：Phase 2 后续 protocol docs 只能承接 repo-local 协议，不得重新长回 generic execution / finishing 入口；活动 README / bootstrap 文案也必须同步到“由 Superpowers 提供”。
