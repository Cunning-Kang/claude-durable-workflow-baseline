# 2026-03 Baseline Refactor 任务清单

> 状态枚举：`todo` / `doing` / `done` / `blocked`
>
> 执行规则：
> - 一次只推进一个 ready task
> - 不跨 phase 并行推进
> - 任务完成后立即更新状态与产物链接
> - 如果发现边界变化，先更新 `decisions.md` 或 `risks.md`

## Phase 1 — 结构收缩

- [ ] **P1-T01 — 缩薄 `global/standards/core-standard.md`**
  - 任务描述：移除不应常驻 always-on global core 的 completion/reporting schema、状态机、override 细节，只保留长期稳定约束。
  - 依赖：`P1-T03` 完成后执行，以边界文档作为收缩依据。
  - 预期产物：更新后的 `global/standards/core-standard.md`
  - 验收条件：文件仍保留 core principles / verification / safety 约束，但不再承载大段执行协议模板。
  - 产物链接：`global/standards/core-standard.md`
  - 验证记录：已移除 `Completion Contract`、`Override Keys and Defaults` 等控制面内容，并保留 core principles / verification / safety 约束；独立评审通过。
  - 状态：done

- [ ] **P1-T02 — 缩薄 `global/guides/orchestration-extension.md`**
  - 任务描述：保留 orchestration decision heuristics，删除重复的 default execution path、过细的 trigger/runtime 话术。
  - 依赖：`P1-T01` 完成后执行，避免与 global core 收缩范围冲突。
  - 预期产物：更新后的 `global/guides/orchestration-extension.md`
  - 验收条件：该文件只作为 decision guide，不再像第二控制面一样驱动执行。
  - 产物链接：`global/guides/orchestration-extension.md`
  - 验证记录：已移除重复的 default execution path / agent taxonomy / checklist 式展开，仅保留 consult triggers、delegation / parallelism、escalation、recovery 与 anti-patterns 等 decision guidance。
  - 状态：done

- [ ] **P1-T03 — 新增 `docs/reference/superpowers-boundary.md`**
  - 任务描述：集中写清仓库定位、Superpowers 主控层边界、禁止竞争性 skills、hooks scope 原则。
  - 依赖：无；这是 Phase 1 的边界锚点任务。
  - 预期产物：`docs/reference/superpowers-boundary.md`
  - 验收条件：文档明确回答“本仓库是什么 / 不是什么 / 为什么不能与 Superpowers 竞争”。
  - 产物链接：`docs/reference/superpowers-boundary.md`
  - 验证记录：文档已覆盖仓库定位、Superpowers 主控层边界、禁止竞争性 skills 与 hooks scope 原则；独立评审通过。
  - 状态：done

- [ ] **P1-T04 — 将 `docs/plan/` 迁移为 `docs/audits/`**
  - 任务描述：把审计材料目录更名为 `docs/audits/`，并修复所有仓库内引用。
  - 预期产物：`docs/audits/*` 与修复后的文档链接
  - 验收条件：原审计文档全部迁入新目录，仓库内无失效引用。
  - 产物链接：`docs/audits/`、`docs/reference/superpowers-boundary.md`
  - 验证记录：已将审计材料目录迁移至 `docs/audits/`；边界文档与 refactor 决策/变更记录已切换到新 canonical path。仓库内残留的 `docs/plan/` 仅用于历史任务描述或审计原文，不再作为活动目录引用。
  - 状态：done

- [ ] **P1-T05 — 统一 README / bootstrap / global README 边界表述**
  - 任务描述：校正 `README.md`、`docs/claude-one-command-bootstrap.md`、`global/README.md` 中对 baseline source / distribution source / Superpowers 的表述。
  - 预期产物：更新后的相关 README / docs 文案
  - 验收条件：三处文档对主控层和仓库边界的说法一致，不暗示平行执行层。
  - 产物链接：`README.md`、`docs/claude-one-command-bootstrap.md`、`global/README.md`
  - 验证记录：已统一三处文档对 baseline source repo / distribution source / Superpowers 主控层 / global 薄运行时表面的表述；`global/README.md` 已将 `spec-execute` 收紧为 historical / transitional reference，不再作为推荐分发面；bootstrap 文档已把“唯一入口”收紧为“初始化的唯一 bootstrap 入口”；独立评审通过。
  - 状态：done

## Phase 2 — 承接层

- [ ] **P2-T01 — 冻结并迁移 `global/skills/spec-execute/SKILL.md`**
  - 任务描述：明确该 skill 与 Superpowers execution lane 的职责重叠，改为迁移说明或直接移除准备动作。
  - 依赖：无；这是 Phase 2 的首个冲突消解任务。
  - 预期产物：移除 `global/skills/spec-execute/SKILL.md`，并新增 `global/skills/spec-execute/README.md` 作为迁移说明
  - 验收条件：repo 内不再保留 competing generic workflow skill 语义。
  - 产物链接：`global/skills/spec-execute/README.md`
  - 验证记录：已删除活动 skill 入口 `global/skills/spec-execute/SKILL.md`，并保留目录级迁移说明；`global/README.md` 已同步说明该入口不再分发。
  - 状态：done

- [ ] **P2-T02 — 对齐 `baseline/docs/workflow/execution-contract.md`**
  - 任务描述：把从 global core 迁出的执行约束收敛到 execution contract，不引入新的总控语义。
  - 依赖：`P2-T04` 完成后执行，避免在 `finish-branch` 入口边界未定前固化 execution contract 文案。
  - 预期产物：更新后的 `baseline/docs/workflow/execution-contract.md`
  - 验收条件：执行协议信息完整，但文件职责仍限定为 repo-local protocol doc。
  - 产物链接：`baseline/docs/workflow/execution-contract.md`
  - 验证记录：已将 execution contract 收敛为 repo-local protocol bridge，补入 authoritative state、verification gates、durable milestone update 与 adjacent protocol docs 边界，并明确不承担 planning / routing / finishing / reprioritization 语义。
  - 状态：done

- [ ] **P2-T03 — 对齐 `baseline/docs/workflow/review-protocol.md` 与相关 protocol docs**
  - 任务描述：检查 `review-protocol.md`、`review-checklist.md`、`native-task-translation.md` 的边界是否清晰，补齐缺失说明。
  - 依赖：`P2-T02` 完成后执行，确保 review / translation 文案与 execution contract 同口径。
  - 预期产物：更新后的 protocol docs
  - 验收条件：review / translation / execution 各自职责清楚，不互相覆盖。
  - 产物链接：`baseline/docs/workflow/review-protocol.md`、`baseline/docs/workflow/review-checklist.md`、`baseline/docs/workflow/native-task-translation.md`
  - 验证记录：已对齐 review protocol、review checklist 与 native task translation 的边界口径；明确 review 只负责 gate 与记录、translation 只负责把 durable task 缩译为最小 session task list，并补入与 execution contract 的相邻职责说明。
  - 状态：done

- [ ] **P2-T04 — 收窄或移除 `global/commands/finish-branch.md`**
  - 任务描述：把 `finish-branch` 收窄为薄桥接命令；若无法避免与 Superpowers 冲突，则删除。
  - 依赖：`P2-T01` 完成后执行，按 Phase 2 既定顺序先移除冲突最大的 `spec-execute`。
  - 预期产物：删除 `global/commands/finish-branch.md`，并同步活动文档说明 `/finish-branch` 由 Superpowers 提供
  - 验收条件：命令不再承担完整收尾 workflow，只做薄桥接或退出仓库分发层。
  - 产物链接：`global/README.md`、`README.md`、`docs/claude-one-command-bootstrap.md`
  - 验证记录：已删除 `global/commands/finish-branch.md`；活动 README / bootstrap 文案仍保留 `/finish-branch` 入口，但已明确标注该入口由 Superpowers 提供，而非 baseline repo 分发。
  - 状态：done

- [ ] **P2-T05 — 做一轮 Superpowers 冲突复核**
  - 任务描述：逐项检查 `global/`、`distribution/`、`docs/` 中是否仍有与主控层重名、同责、同语义的入口。
  - 依赖：`P2-T01` ~ `P2-T04` 完成后执行，作为 Phase 2 的收口复核。
  - 预期产物：复核结果记录（可写入 `docs/refactor/.../changelog.md` 或新增审计条目）
  - 验收条件：剩余冲突点被明确标记为“已收窄 / 已迁移 / 待删除”，没有模糊灰区。
  - 产物链接：`docs/refactor/2026-03-baseline-refactor/changelog.md`
  - 验证记录：已复核活动入口与边界文案：`global/README.md` 标记为 narrowed、`global/skills/spec-execute/README.md` 标记为 migrated、`distribution/commands/init-claude-workflow.md` 与 `distribution/commands/new-feature.md` 标记为 narrowed、`docs/claude-one-command-bootstrap.md` 与 `docs/reference/superpowers-boundary.md` 标记为 resolved / authoritative。`docs/audits/*` 保留为 historical audit evidence，不视为活动入口；未发现需要新增“待删除”项的 Phase 2 灰区。
  - 状态：done

## Phase 3 — Hooks

- [ ] **P3-T01 — 建立 `distribution/hooks/user/` 目录骨架**
  - 任务描述：创建 user scope hooks 的目录与 README，说明适用场景、安装方式、为何不是默认启用。
  - 依赖：`P3-T05` 完成后执行，先以 scope reference 固定 user / project / local example only 的判定口径。
  - 预期产物：`distribution/hooks/user/` 及说明文件
  - 验收条件：目录结构清晰，README 明确 scope 与 opt-in 原则。
  - 产物链接：`distribution/hooks/user/README.md`
  - 验证记录：已建立 `distribution/hooks/user/` 骨架与 README；README 明确 user scope、manual copy 到 `~/.claude/hooks/` 的目标安装面、source-only、opt-in、why not default enabled，以及不得与 Superpowers 竞争；独立 spec review 与 code quality review 均通过。
  - 状态：done

- [ ] **P3-T02 — 建立 `distribution/hooks/project/` 目录骨架**
  - 任务描述：创建 project scope hooks 的目录与 README，说明项目级适用边界。
  - 依赖：`P3-T05` 完成后执行，与 `P3-T01` 同口径落 user / project 分层骨架。
  - 预期产物：`distribution/hooks/project/` 及说明文件
  - 验收条件：目录结构清晰，README 明确不能误装成全局默认行为。
  - 产物链接：`distribution/hooks/project/README.md`
  - 验证记录：已建立 `distribution/hooks/project/` 骨架与 README；README 明确 project scope、`<project>/.claude/hooks/` 的目标安装面、显式项目级 opt-in、不得误装为全局默认行为，以及不得与 Superpowers 或 user-level hooks 冲突；独立 spec review 与 code quality review 均通过。
  - 状态：done

- [ ] **P3-T03 — 建立 `distribution/settings-snippets/user/` 目录骨架**
  - 任务描述：创建 user scope settings snippets 的目录与说明文件。
  - 依赖：`P3-T01`、`P3-T02` 完成后执行，先固定 hooks 分层与 README 口径，再补 settings snippets 对应骨架。
  - 预期产物：`distribution/settings-snippets/user/` 及说明文件
  - 验收条件：只提供 snippets/source，不包含 live `settings.json`。
  - 产物链接：`distribution/settings-snippets/user/README.md`
  - 验证记录：已建立 `distribution/settings-snippets/user/` 骨架与 README；README 明确 snippets-only、manual merge 到 `~/.claude/settings.json`、opt-in、why not default enabled、不得分发 live `settings.json`，且不得与 Superpowers 竞争；目录树与 README 关键词检查通过，独立 code review 判定 ready。
  - 状态：done

- [ ] **P3-T04 — 建立 `distribution/settings-snippets/project/` 目录骨架**
  - 任务描述：创建 project scope settings snippets 的目录与说明文件。
  - 依赖：`P3-T01`、`P3-T02` 完成后执行，保持 settings snippets 与 hooks 分层顺序一致。
  - 预期产物：`distribution/settings-snippets/project/` 及说明文件
  - 验收条件：只提供项目级模板，不携带默认启用配置。
  - 产物链接：`distribution/settings-snippets/project/README.md`
  - 验证记录：已建立 `distribution/settings-snippets/project/` 骨架与 README；README 明确 project scope、manual merge 到 `<project>/.claude/settings.json`、显式项目级 opt-in、不得误并入 user-level global defaults、why not default global，以及不得与 Superpowers 竞争；目录树与 README 关键词检查通过，独立 code review 判定 ready。
  - 状态：done

- [ ] **P3-T05 — 新增 `docs/reference/hooks-scope.md`**
  - 任务描述：定义 user / project / local example only 三类 hooks 的范围边界与判定规则。
  - 依赖：无；这是 Phase 3 的边界锚点任务。
  - 预期产物：`docs/reference/hooks-scope.md`
  - 验收条件：能明确回答“哪些 hook 可以全局、哪些只能项目级、哪些只能本地示例”。
  - 产物链接：`docs/reference/hooks-scope.md`
  - 验证记录：已新增 hooks 三层 scope reference，明确 user / project / local example only 的定义、decision rule、planned distribution surface、why not default global、settings snippets 关系与禁止模式；已修正未来态目录/接线表述，避免把未落地骨架写成当前既成事实；独立 spec review 与 code quality review 均通过。
  - 状态：done

- [ ] **P3-T06 — 验证 repo 内不存在默认启用的 live hooks / settings**
  - 任务描述：检查仓库是否错误落入 live `settings.json`、默认 hook 配置或默认启用说明。
  - 依赖：`P3-T01` ~ `P3-T05` 完成后执行，基于最终 hooks / settings snippets 分发表面做一次收口复核。
  - 预期产物：验证记录与必要修正
  - 验收条件：仓库只分发 source / snippets，不默认启用任何 hooks。
  - 验证记录：已复核 `distribution/hooks/` 与 `distribution/settings-snippets/` 当前树；仅存在四个 scope README。`Glob` 未发现 `distribution/hooks/**/*.json` 或 `distribution/settings-snippets/**/*.json`，`ls -R distribution/hooks distribution/settings-snippets` 也确认无 live `settings.json` / `settings.local.json` 落入分发表面；现有 README 均使用 source-only / snippets-only / manual copy / manual merge / opt-in 表述，未发现默认启用说明。
  - 状态：done

## Phase 4 — Memory

- [ ] **P4-T01 — 补 `docs/reference/memory-boundary.md` 或等价说明**
  - 任务描述：明确 memory 只承接 durable lessons，不承接任务日志、临时状态或一次性偏好。
  - 预期产物：memory boundary 文档或等价 reference 说明
  - 验收条件：边界清晰，可直接指导后续 memory 内容筛选。
  - 状态：todo

- [ ] **P4-T02 — 对齐 `baseline/docs/workflow/memory-protocol.md`**
  - 任务描述：校正 memory protocol，使其与最终 memory skeleton 职责一致。
  - 预期产物：更新后的 `baseline/docs/workflow/memory-protocol.md`
  - 验收条件：protocol 只指导 durable memory 的写入与维护，不要求记录会话日志。
  - 状态：todo

- [ ] **P4-T03 — 强化 `baseline/memory/MEMORY.md`**
  - 任务描述：更新 `MEMORY.md` 的用途说明和内容边界，确保其保持极薄。
  - 预期产物：更新后的 `baseline/memory/MEMORY.md`
  - 验收条件：文件只保留稳定、长期、总览型 memory，不夹带执行细节。
  - 状态：todo

- [ ] **P4-T04 — 强化 `baseline/memory/patterns.md`**
  - 任务描述：沉淀可复用模式与 durable conventions，去掉一次性经验。
  - 预期产物：更新后的 `baseline/memory/patterns.md`
  - 验收条件：内容可复用、可跨会话延续，且与 MEMORY.md 不重复。
  - 状态：todo

- [ ] **P4-T05 — 强化 `baseline/memory/gotchas.md`**
  - 任务描述：沉淀稳定的误用案例、边界坑点与环境差异提示。
  - 预期产物：更新后的 `baseline/memory/gotchas.md`
  - 验收条件：内容是 durable gotchas，不是当前任务的临时备注。
  - 状态：todo

- [ ] **P4-T06 — 做一次 memory protocol ↔ skeleton 一致性复核**
  - 任务描述：核对 `memory-protocol.md` 与 `baseline/memory/*` 是否同口径。
  - 预期产物：一致性复核记录与必要修正
  - 验收条件：protocol、MEMORY、patterns、gotchas 的角色边界清楚且互不打架。
  - 状态：todo