# 2026-03 Baseline Refactor Changelog

## 2026-03-22

### 本轮新增
- 建立 `docs/refactor/2026-03-baseline-refactor/` 作为本次 baseline refactor 的本地执行控制面。
- 新增以下控制面文件：
  - `README.md`
  - `plan.md`
  - `tasks.md`
  - `decisions.md`
  - `risks.md`
  - `changelog.md`
- 将当前最新审计依据链接到：
  - `docs/audits/2026-03-22-production-baseline-audit-and-refactor-plan.md`

### 本轮范围说明
- 本轮只做“建立执行控制面”。
- 本轮没有启动核心 refactor 的具体 phase task。
- 本轮没有修改 runtime 行为、脚本行为或 hooks 行为。

### 本轮明确未做
- 未直接删除 `global/skills/spec-execute/SKILL.md`
- 未新增 hooks 实现
- 未调整 `distribution/scripts` 行为
- 未落任何默认启用的 settings / hooks 配置

### 本轮追加执行（Phase 1）
- 完成 `P1-T03`：新增 `docs/reference/superpowers-boundary.md`，固定仓库定位、Superpowers 主控层边界、禁止竞争性 skills 与 hooks scope 原则。
- 完成 `P1-T01`：收缩 `global/standards/core-standard.md`，移除 `Completion Contract`、`Override Keys and Defaults` 等常驻控制面内容，仅保留长期稳定约束。
- 完成 `P1-T02`：收缩 `global/guides/orchestration-extension.md`，移除重复的 default execution path / routing 细节，仅保留 orchestration decision guidance。
- 完成 `P1-T04`：将 `docs/plan/` 迁移为 `docs/audits/`，并把活动边界/决策引用切换到新 canonical path。
- 完成 `P1-T05`：统一 `README.md`、`docs/claude-one-command-bootstrap.md`、`global/README.md` 的边界表述，明确本仓库是 baseline source / distribution source，Superpowers 是主控层，`global/` 只是薄运行时表面而非平行控制层；并将 `spec-execute` 在 `global/README.md` 中收紧为 historical / transitional reference。
- 本轮未进入 Phase 2/3/4，未修改 runtime 行为、脚本行为或 live hooks wiring。

### 本轮追加执行（Phase 2）
- 完成 `P2-T01`：移除 `global/skills/spec-execute/SKILL.md`，并新增 `global/skills/spec-execute/README.md` 作为迁移说明，明确该 execution lane 由 Superpowers 承接。
- 完成 `P2-T04`：移除 `global/commands/finish-branch.md`，不再从 baseline repo 的 `global/` 分发表面提供平行 finishing 入口。
- 完成 `P2-T02`：重写 `baseline/docs/workflow/execution-contract.md`，将执行约束收敛为 repo-local protocol bridge，明确 authoritative state、verification gates、durable milestone update 与 adjacent protocol docs 的分层边界。
- 完成 `P2-T03`：对齐 `baseline/docs/workflow/review-protocol.md`、`review-checklist.md`、`native-task-translation.md`，明确 review 只承接 review gate 与记录，translation 只承接 durable task 到最小 session task list 的缩译，不再越界承担执行控制语义。
- 完成 `P2-T05`：复核 `global/`、`distribution/`、`docs/` 的活动入口与边界文案，并做明确分类：`global/README.md` = narrowed，`global/skills/spec-execute/README.md` = migrated，`distribution/commands/init-claude-workflow.md` / `distribution/commands/new-feature.md` = narrowed，`docs/claude-one-command-bootstrap.md` / `docs/reference/superpowers-boundary.md` = resolved / authoritative；`docs/audits/*` 明确仅为 historical audit evidence，不作为活动入口。
- 同步更新 `global/README.md`、`README.md`、`docs/claude-one-command-bootstrap.md` 的活动文案与目录清单，明确 `/finish-branch` 由 Superpowers 提供，`global/` 只保留薄运行时表面。
- 更新 `decisions.md` 与 `risks.md`：记录冲突入口退出分发表面的决策，并将 `R-006` 降为后续文案回归风险；`P2-T02` / `P2-T03` 完成后，`R-004` 降为后续 protocol / README 文案越界回归风险；`P2-T05` 完成后，`R-001` 降为后续新增资产时的回归审查风险。

### 本轮追加执行（Phase 3）
- 完成 `P3-T05`：新增 `docs/reference/hooks-scope.md`，固定 user / project / local example only 三层 hooks scope、decision rule、planned distribution surface、why not default global、settings snippets 关系与禁止模式。
- 完成 `P3-T01`：建立 `distribution/hooks/user/README.md`，作为 user scope hooks 的 source-only 目录骨架说明，明确 manual copy、opt-in、非默认启用与不得与 Superpowers 冲突。
- 完成 `P3-T02`：建立 `distribution/hooks/project/README.md`，作为 project scope hooks 的 source-only 目录骨架说明，明确项目级采用边界、非全局默认行为、opt-in 与不得误装为 user-level hooks。
- 完成 `P3-T03`：建立 `distribution/settings-snippets/user/README.md`，作为 user scope settings snippets 的 source-only 目录骨架说明，明确 manual merge、opt-in、why not default enabled、不得分发 live `settings.json`，以及不得与 Superpowers 冲突。
- 完成 `P3-T04`：建立 `distribution/settings-snippets/project/README.md`，作为 project scope settings snippets 的 source-only 目录骨架说明，明确项目级 manual merge、显式 project opt-in、不得误并入 user-level global defaults、why not default global，以及不得与 Superpowers 冲突。
- 完成 `P3-T06`：复核 `distribution/hooks/` 与 `distribution/settings-snippets/` 当前分发表面；确认仅存在 scope README，未落入 live `settings.json` / `settings.local.json`，且 README 均保持 source-only / snippets-only / opt-in 表述。
- 本轮未引入 live hooks wiring，未修改 `distribution/scripts/*` 运行行为。
- 在 review 过程中修正了 `hooks-scope.md`、hooks README 与 settings snippets README 的现实性表述，避免把尚未落地的目录或接线路径写成当前既成事实。

### 后续记录原则
- 只有在实际推进 Phase 1 ~ Phase 4 任务时，才继续在本文件记录核心结构或行为变动。
- 如果只是补充说明、修订任务排序或更新风险/决策，应优先更新对应文件，而不是把所有讨论都堆进 changelog。
