 A. Final Judgment

  - 总评：这套结构方向是对的：global/CLAUDE.md 做入口、core-standard.md 做 always-on、orchestration-extension.md 做 on-demand。骨架清楚，但 core 层已开始制度化膨胀。
  - 最关键问题：global/standards/core-standard.md:88-293 把“原则”混入了“流程协议/报告模板/审查状态机/配置字典”，长期会降低遵循率。
  - 推荐方向：中度重构，不是小修。保留核心原则；立即把可程序化/可复用流程拆到 skills/hooks；把经验性偏好留给 memory。

  B. File-by-File Audit

  - global/CLAUDE.md:1-6
  入口层，职责基本清晰。应保留“引 core + 指向 orchestration guide”。第 5-6 行可压缩成一句；不应继续加规则。
  - global/standards/core-standard.md
    - 应保留：0-3, 5, 7, 8（设计契约、核心原则、语言、澄清/反驳、安全、git）——这些是长期稳定 policy。
    - 应拆出：4, 6, 9, 10。其中 Task Levels/Traceability（90-119）和 Completion Contract（246-264）是 reporting protocol；Review Requirements（170-199）是审查状态机；Override
  Keys（266-293）更像 runtime schema。
  - global/guides/orchestration-extension.md
  on-demand expansion 定位正确，整体比 core 健康。
    - 应保留：1-5 的边界、触发条件、升级/降级准则。
    - 应压缩/拆出：6-8 的 checklist/fanout/recovery，很多已接近 routing policy，应交给 subagent routing/hook deterministic enforce。
    - 9 可并入更短的“don’ts”。

  C. Classification Matrix

  - 必须保留：core-standard 的 Design Contract/Core Principles/Language/Security/Git；orchestration-guide 的 role、trigger、default path。
  - 应拆到 skills：Task Levels + Traceability、Completion Contract、Review Requirements。适合 status-reporting、verification-before-completion、request-review。
  - 应拆到 hooks：高风险授权记录、完成前验证 gate、并行 fanout 上限提示、双任务追踪冲突检测。
  - 应迁到 memory：环境差异、哪些 review 流程在本机/本团队最常用、常见 orchestration 误用案例。
  - 应删除：重复表达与“为完整而写”的句子，如 Completion Contract 对 §6 的重复；Override Keys 的长块可移到 machine-readable config doc。

  D. Proposed Target Structure

  - global/CLAUDE.md：只做 2 件事——引入 core；列出少量 on-demand guide 入口。
  - global/standards/core-standard.md：保留 6 章：Design Contract / Principles / Language / Clarification / Security / Git。
  - global/guides/orchestration-extension.md：保留何时查阅、何时委派、何时并行、何时回退；压缩为决策指南，不写协议。
  - 新增 skills：status-reporting、verification-gates、review-gate、risk-acceptance-recorder。
  - 新增 hooks：pre-completion-check、high-risk-confirmation-capture、parallelism-guard、task-tracker-conflict-guard。
  - 迁入 memory/：orchestration-patterns.md、environment-quirks.md、review-preferences.md。

  E. Phased Refactor Plan

  - Phase 1：删减 core 文本，不改行为；风险低；验收=core 明显变短且无流程模板。
  - Phase 2：把 completion/review/traceability 拆成 skills；风险中；验收=同等约束可通过 skill 触发获得。
  - Phase 3：用 hooks 接管 deterministic gate；风险中高；验收=高风险确认、完成前检查不再靠自觉。
  - Phase 4：建立 memory 承接经验；风险低；验收=环境/偏好不再回流到 global。

  F. Highest-Risk Anti-Patterns

  1. 把 状态机 写进 always-on policy。
  2. 把 报告格式 当作核心原则。
  3. 明明可 hook enforce，却只写“应当”。
  4. 入口层继续长胖，变成第二份 standard。
  5. 用 global 承接经验/偏好，导致规则不断沉积。