# A. Final Judgment

- **当前结构总评**
  - 这个仓库的**定位大体是对的**，已经明显更接近“durable workflow baseline source repo”，而不是普通应用仓。证据在 `README.md:5-15`、`README.md:52-67`、`global/README.md:35-39`、`docs/claude-one-command-bootstrap.md:110-133`：它反复把自己定义为 baseline source / distribution source，并明确把 Superpowers 放在主控层。
  - 但当前结构里仍有**两处明显漂移风险**：
    1. `global/standards/core-standard.md:88-284` 仍然过厚，混入了状态机、报告模板、review 状态、override schema 等“流程控制面”内容。
    2. `global/skills/spec-execute/SKILL.md` 明显越界，语义上直接落在“已有 spec/plan/task 后的执行层”，与已安装的 Superpowers execution lane 高度重叠。

- **最关键问题**
  1. `core-standard.md` 还没有收敛成“极薄 always-on global core”；它现在仍然承担了一部分 workflow runtime 职责。
  2. 仓库当前缺少一套**按 scope 分层的 hooks source / settings snippets / boundary docs**；文档里已经说“不要把 hooks 一刀切全局化”，但仓库结构尚未把这个设计落地。
  3. `global/skills/spec-execute/SKILL.md` 与仓库在 `docs/claude-one-command-bootstrap.md:127-133` 自己声明的“不要重建主控命令/skills”形成内在冲突。

- **推荐方向**
  - 明确收敛为：
    - **global/**：只放极薄 global core + on-demand guide + 少量非竞争性入口；
    - **distribution/**：只放分发命令、脚本、hooks source、settings snippets；
    - **baseline/**：只放 repo-local durable artifacts；
    - **docs/**：只放边界、安装、审计、reference。
  - **删除/迁出会与 Superpowers 竞争的执行层能力**，尤其是 `global/skills/spec-execute/SKILL.md`。
  - 把从 core-standard / orchestration-extension 拆出的流程性内容，优先承接到：
    - `baseline/docs/workflow/*`
    - `docs/reference/*`
    - `distribution/hooks/*`
    - `distribution/settings-snippets/*`
    - baseline memory skeleton，而不是新的通用 skills。

# B. File-by-File Audit

## `global/CLAUDE.md`

### 当前职责
- `global/CLAUDE.md:1-6` 只做两件事：
  1. 引入 `@~/.claude/standards/core-standard.md`
  2. 提示 orchestration-heavy work 时再看 `@~/.claude/guides/orchestration-extension.md`
- 它已经满足“极薄入口”的要求。

### 判断
- **保留**。
- 这是当前三文件里边界最干净的一个，没有第二份 standard、没有状态机、没有流程模板。

### 建议
- 只做极小修整即可：保留现状，最多把第二条说明再压缩一行。
- 不建议继续往这里加任何 workflow protocol、reporting format、review states。

---

## `global/standards/core-standard.md`

### 当前职责
- `global/standards/core-standard.md:1-42`：元定义与核心原则。
- `global/standards/core-standard.md:55-84`：语言契约、pushback/clarification。
- `global/standards/core-standard.md:88-121`：Task Framing / Traceability / State Backend。
- `global/standards/core-standard.md:132-200`：Verification / Review / Completion 规则。
- `global/standards/core-standard.md:203-242`：Security / Tool Failure / Git Rules。
- `global/standards/core-standard.md:246-295`：Completion Contract + Override Keys。

### 逐规则簇判断

#### §0 Design Contract (`core-standard.md:9-40`)
- **保留**。
- 这是 global core 最该保留的内容之一：定义“什么该进 core、什么不该进 core”，能持续约束膨胀。

#### §1 Core Principles (`core-standard.md:42-53`)
- **保留**。
- 这 7 条是长期稳定、高杠杆、低争议约束，完全符合 global core 定位。

#### §2 Language Contract (`core-standard.md:55-63`)
- **保留**。
- 属于稳定元规则，遗漏成本高。

#### §3 Pushback and Clarification (`core-standard.md:65-86`)
- **保留，但压缩**。
- 核心思想应保留；“pushback format”与“clarification rules”可以更短，不必像半模板。

#### §4 Task Framing and State (`core-standard.md:88-121`)
- **拆分处理**。
- `### Task Levels` (`90-95`)：**保留**。L0/L1/L2 作为任务风险分层是稳定抽象。
- `### Minimum Traceability` (`96-108`)：**压缩保留一层原则，细项迁出**。`Goal/Scope/Acceptance/Assumptions` 对 L1/L2 仍然有价值，但不应写成总是常驻的详细执行模板。
- `### State Backend` + checkpoint (`110-121`)：**迁出**。`Prefer project task tools` / `fall back to inline` / checkpoint 触发条件，更像执行协议，应迁往 `baseline/docs/workflow/execution-contract.md` 或 hooks docs。

#### §5 Capability Handling (`123-130`)
- **保留**。
- 这是“能力降级时如何诚实地继续工作”的核心约束，适合 always-on。

#### §6 Verification and Definition of Done (`132-200`)
- **大幅压缩；绝大部分迁出**。
- 这里是当前最厚、最像第二控制面的部分。
- 应保留的只有：
  - “未经适用验证不要宣称完成”
  - “需要独立 review 的情形必须满足 review evidence”
- 应迁出的内容：
  - `Required Gates` 的五栏分类与解释
  - `Applicability` 的详细规则
  - `Review Policy` 的完整矩阵
  - `Review Requirements` 的 `PASS / FAIL / BLOCKED` 状态机
  - `Completion Rule` 的执行语义
- 这些更适合放在：
  - `baseline/docs/workflow/execution-contract.md`
  - `baseline/docs/workflow/review-protocol.md`
  - `docs/reference/*`
  - 以及未来的 scoped hook templates
- **理由**：这些不是“高杠杆 global core”，而是“执行协议 + 证据格式 + 状态机”。在 Superpowers 已承担主控层的前提下，继续把这整块常驻 global core，会让这个仓库继续像第二主控层。

#### §7 Security and Safety (`203-233`)
- **保留，但压缩模板化段落**。
- 高风险授权要求、tool failure rule 应保留。
- `Risk Acceptance` 那段字段模板可迁到 `docs/reference/high-risk-operations.md` 或 hooks scope doc，global core 只保留原则即可。

#### §8 Git Rules (`235-242`)
- **保留硬边界，删除偏好项**。
- 应保留：
  - no destructive git actions without explicit request
  - never force-push protected default branch
  - do not amend without explicit request
  - do not mix unrelated changes in one commit
- 应删除/迁出：
  - `Prefer small, reviewable commits`
  - `Prefer explicit staging`
- 原因：前者是偏好，不是 always-on 约束。

#### §9 Completion Contract (`246-264`)
- **迁出**。
- 这一整块是“完成报告模板 / 状态报告协议”，不应继续常驻 global core。
- 迁移落点：
  - `baseline/docs/workflow/execution-contract.md`
  - 若需要样例，再放 `docs/reference/completion-report-examples.md`

#### §10 Override Keys and Defaults (`266-295`)
- **迁出**。
- 这是 runtime/config schema，不是 core policy。
- 迁移落点：`docs/reference/runtime-override-keys.md`。

### 总结
- **保留**：§0、§1、§2、§5、§7 的原则层；§4 的任务分层；§6 的最小验证原则。
- **压缩**：§3、§4、§6、§7、§8。
- **迁出**：§4 backend/checkpoint、§6 详细 gates/review state、§9、§10。
- **删除**：Git 偏好项、与 §6/§9 重复的模板化表述。

---

## `global/guides/orchestration-extension.md`

### 当前职责
- 文件从标题开始就在强调自己是 **Global on-demand extension for orchestration-heavy work**（`orchestration-extension.md:1-15`）。
- 它也明确写了：
  - 仅在 orchestration justified 时查阅（`13-15`）
  - 不覆盖 built-in routing 或更合适的 subagent（`30-31`）
  - 不替代 runtime precedence（`50-56`）
- 这说明它的**方向是对的**，当前不是最大问题源。

### 逐节判断

#### §1 Role of This Guide (`9-19`)
- **保留**。
- 这节是文件存在的正当性：on-demand decision guide，而不是第二控制面。

#### §2 Default Execution Path (`21-33`)
- **压缩或迁出**。
- 核心意思“默认走最简单路径，有明确理由才升级 orchestration”已经被 `core-standard.md:42-53` 的核心原则覆盖。
- 这一节可以压成 2-3 行，或者并入 §1。

#### §3 Consult Triggers (`35-46`)
- **压缩**。
- 保留“什么时候才值得打开这个 guide”的判断标准，但不必写成小型 routing checklist。

#### §4 Agent Intent (`48-58`)
- **压缩**。
- 它当前的边界是对的：强调 agent 定义在 `~/.claude/agents/`，本 guide 只是补充。
- 但这节可以更短，避免看起来像在重复定义运行时 agent taxonomy。

#### §5 Escalation and Downgrade Rules (`60-79`)
- **保留**。
- 这是 on-demand guide 最有价值的部分之一，属于决策指南，不是执行协议。

#### §6 Delegation Checklist (`80-102`)
- **保留，但压缩为 decision heuristics**。
- 保留“独立、可恢复、边界稳定时才委派”的原则；去掉过多 checklist 味道。

#### §7 Parallelism and Fanout (`104-128`)
- **保留**。
- 这节与“不要乱并行”高度相关，且不会与 Superpowers 冲突，只要保持为 advice，不写成强制状态机。

#### §8 Recovery and Failure Handling (`130-160`)
- **保留，但压缩**。
- “tool/agent failure / low-confidence output / integration failure / context pressure” 这类 on-demand 恢复建议是有用的，但不宜越来越像完整 SOP。

#### §9 Common Anti-Patterns (`162-169`)
- **保留**。
- 保持为少量反例即可。

### 总结
- 这个文件**不是当前主要越界源**；它已经把自己定位为 supplement，而非 controller。
- 但仍建议做一次压缩，目标是：
  - 更像“decision guide”
  - 更少像“隐式 routing control surface”

# C. Classification Matrix

## 必须保留

- `global/CLAUDE.md:1-6`
  - 极薄入口；职责清晰。
- `global/standards/core-standard.md`
  - §0 Design Contract
  - §1 Core Principles
  - §2 Language Contract
  - §3 Pushback/Clarification（压缩版）
  - §4 的 L0/L1/L2 分层
  - §5 Capability Handling
  - §6 的最小验证原则
  - §7 Security / Tool Failure 原则
  - §8 的硬边界 Git 规则
- `global/guides/orchestration-extension.md`
  - 保留为 on-demand decision guide
- `distribution/commands/init-claude-workflow.md`
- `distribution/commands/new-feature.md`
- `distribution/scripts/init-claude-workflow.sh`
- `distribution/scripts/instantiate-feature.sh`
- `baseline/docs/specs/_template/*`
- `baseline/docs/workflow/*`
- `baseline/memory/*`
- `docs/claude-one-command-bootstrap.md`
- `docs/source-repo-truth-audit.md`

## 应拆到 commands / protocol docs

- `core-standard.md` 中详细的 verification gate 说明
  - → `baseline/docs/workflow/execution-contract.md`
- `core-standard.md` 中 review applicability / review state / review evidence 细则
  - → `baseline/docs/workflow/review-protocol.md`
- `core-standard.md` 中 Completion Contract 报告模板
  - → `baseline/docs/workflow/execution-contract.md`
  - 示例可另放 `docs/reference/completion-report-examples.md`
- `core-standard.md` 中 Override Keys schema
  - → `docs/reference/runtime-override-keys.md`
- `global/commands/finish-branch.md`
  - **应压缩为薄命令，或改成 reference doc + 对 Superpowers finishing 能力的桥接说明**；不能继续长成一个通用 finish workflow。

## 应拆到 hooks

- **user scope hooks**
  - 高风险 git guard（force-push / reset / branch delete 等）
  - 用户级危险操作确认 capture
- **project scope hooks**
  - durable task/review/verify 一致性提醒
  - baseline repo 特有的 repo hygiene 检查
- **只能作为 local examples / templates**
  - fanout/parallelism guard
  - 双 authoritative tracker 冲突告警
  - 任何依赖本地工具链、团队偏好、shell 环境的 hook
- 承接落点：
  - `distribution/hooks/user/*`
  - `distribution/hooks/project/*`
  - `distribution/settings-snippets/user/*.jsonc`
  - `distribution/settings-snippets/project/*.jsonc`
  - `docs/reference/hooks-scope.md`

## 应迁到 memory

- 环境 quirks
- review evidence 示例与常见误判
- delegation / fanout 经验模式
- baseline 命令误用案例
- 只有在多次复现后才成立的 workflow 经验
- 迁移落点：baseline memory skeleton（供消费 repo 使用），而不是继续塞回 global core

## 应删除

- `global/skills/spec-execute/SKILL.md`
  - 它与 Superpowers 已有执行层能力发生直接职责重叠。
  - 该文件自己还写了 `Do not introduce a second planning layer...`，但它本身就是第二执行入口，边界不再成立。
- `core-standard.md` 中 `§9 Completion Contract` 的完整模板块
- `core-standard.md` 中 `§10 Override Keys and Defaults` 的完整 schema 块
- `core-standard.md` 中纯偏好型 git 规则（如 explicit staging / small reviewable commits）
- 若 `finish-branch` 最终无法压缩成“薄桥接命令”，则应删除而不是继续保留一个与 Superpowers 收尾能力平行的入口

# D. Proposed Target Structure

## 目标结构草案

```text
.
├── global/
│   ├── CLAUDE.md
│   ├── standards/
│   │   └── core-standard.md              # 极薄 always-on global core
│   ├── guides/
│   │   └── orchestration-extension.md    # on-demand decision guide only
│   └── commands/
│       └── finish-branch.md              # 仅在压缩后保留；否则移除
│
├── distribution/
│   ├── commands/
│   │   ├── init-claude-workflow.md
│   │   └── new-feature.md
│   ├── scripts/
│   │   ├── init-claude-workflow.sh
│   │   └── instantiate-feature.sh
│   ├── hooks/
│   │   ├── user/
│   │   ├── project/
│   │   └── README.md
│   └── settings-snippets/
│       ├── user/
│       ├── project/
│       └── README.md
│
├── baseline/
│   ├── claude/
│   │   └── claude-snippet.md
│   ├── docs/
│   │   ├── specs/_template/
│   │   └── workflow/
│   └── memory/
│
└── docs/
    ├── reference/
    │   ├── superpowers-boundary.md
    │   ├── hooks-scope.md
    │   ├── runtime-override-keys.md
    │   └── completion-report-examples.md
    ├── audits/
    │   ├── audit_by_GPT.md
    │   ├── audit_by_MMX.md
    │   └── 2026-03-22-production-baseline-audit-and-refactor-plan.md
    ├── claude-one-command-bootstrap.md
    └── source-repo-truth-audit.md
```

## 目录职责说明

- **`global/` 保留职责**
  - 只保留极薄 global core、on-demand guide、少量不与 Superpowers 竞争的薄入口。
  - **不再保留 `skills/`**。

- **`distribution/` 保留并扩展职责**
  - 保留 commands/scripts。
  - 新增 **hooks source** 与 **settings snippets**，但只作为 source / template，不作为 live runtime config。

- **`baseline/` 保留职责**
  - 继续承接 repo-local durable artifacts：spec skeleton、workflow protocols、memory skeleton。
  - 不要把 hooks 直接落进 baseline 默认产物；否则容易把“可选 deterministic control”误升级成默认项目行为。

- **`docs/` 需要新增的结构**
  - 建议新增 `docs/reference/`。
  - 建议把当前 `docs/plan/` 改名为 `docs/audits/`，因为里面存放的不是计划执行工单，而是审计材料。

## 是否需要新增 `reference/`
- **不建议新增顶层 `reference/`**。
- **建议新增 `docs/reference/`**。
- 原因：这些内容是说明性、边界性、schema 性文档，不是分发资产，也不是 baseline runtime 文件；放在 `docs/reference/` 更清晰。

## 是否需要新增 hooks source / settings snippets
- **需要。**
- 但必须放在 `distribution/` 下，以“可分发模板”身份存在，而不是默认 live config。

## 是否需要新增 `superpowers-boundary.md` 或等价文档
- **需要。**
- 当前 README 与 bootstrap 文档已经表达了边界，但还不够集中；应该有一份单独的边界文档，明确：
  - Superpowers 是主控层
  - 本仓库是 baseline source repo
  - 本仓库不提供 competing generic workflow skills
  - hooks 只提供 source/snippets，不默认全局化

# E. Phased Refactor Plan

## Phase 1: 只做结构审计与删减，不改行为
- **目标**
  - 锁定 repo boundary，先把“这是什么 / 不是什么”说清楚，并收敛文档膨胀。
- **改动范围**
  - 压缩 `global/standards/core-standard.md`
  - 压缩 `global/guides/orchestration-extension.md`
  - 新增 `docs/reference/superpowers-boundary.md`
  - 将 `docs/plan/` 迁为 `docs/audits/` 并更新 README/doc links
- **风险**
  - 主要是文档引用路径变化；不涉及脚本和命令行为。
- **验收标准**
  - `global/CLAUDE.md` 仍保持极薄
  - `core-standard.md` 明显缩薄，不再包含大段报告模板/状态机/schema
  - `orchestration-extension.md` 仍是 decision guide，而非控制面
  - 仓库文档中对 Superpowers 主控层边界表述一致

## Phase 2: 拆出 commands / protocol docs，避免与 Superpowers 冲突
- **目标**
  - 移除所有会被理解为“第二执行层/第二主控层”的资产。
- **改动范围**
  - 删除 `global/skills/spec-execute/SKILL.md`
  - 将 `core-standard.md` 中详细 verification/review/completion 内容迁入：
    - `baseline/docs/workflow/execution-contract.md`
    - `baseline/docs/workflow/review-protocol.md`
    - `docs/reference/runtime-override-keys.md`
  - 评估 `global/commands/finish-branch.md`：压缩为薄桥接命令；若仍与 Superpowers 冲突则移除
- **风险**
  - 历史用户若依赖 `spec-execute` 会感到入口变化；需要清晰迁移说明。
- **验收标准**
  - 仓库不再分发 generic global workflow skill
  - 所有迁出的流程性内容都有明确新落点
  - README / bootstrap docs 不再暗示本仓库提供并行于 Superpowers 的执行层

## Phase 3: 引入 hooks 做确定性控制
- **目标**
  - 把真正适合 deterministic enforcement 的内容从文字规则迁移到 scoped hook source/snippets。
- **改动范围**
  - 新增 `distribution/hooks/{user,project}/`
  - 新增 `distribution/settings-snippets/{user,project}/`
  - 新增 `docs/reference/hooks-scope.md`
  - 明确哪些 hook 属于 user scope、project scope、local example only
- **风险**
  - 最容易犯的错误是“模板一出就默认全局化”；必须用 README 和路径设计防止误装。
- **验收标准**
  - hooks 全部按 scope 分类
  - 仓库内不落 live `settings.json`
  - 每个 hook 都有“为什么不是默认全局启用”的说明

## Phase 4: 建立 memory 承接经验性知识
- **目标**
  - 把经验、误用案例、环境差异从 global core 中排出，沉淀到 memory。
- **改动范围**
  - 强化 `baseline/memory/{MEMORY.md,patterns.md,gotchas.md}` 的用途说明
  - 为 docs/reference 增加 memory boundary 说明
  - 只把经过复用验证的经验写进 memory skeleton 示例，不写任务日志
- **风险**
  - memory 很容易再次膨胀成“第二文档堆”；必须限制为 stable lessons。
- **验收标准**
  - global core 中不再夹带经验性/环境性知识
  - memory 只承接 durable patterns / gotchas / conventions
  - baseline 的 memory 协议与 skeleton 一致，不相互打架

# F. Highest-Risk Anti-Patterns

1. **把本仓库继续做成与 Superpowers 并行的通用 workflow runtime**
   - 最危险。
   - 一旦同时存在两套 planning/execution/review 入口，用户会在同一主机上得到冲突语义、冲突路径和重复维护成本。

2. **把状态机、报告模板、schema 长期塞在 always-on global core**
   - 这会让 core-standard 从“约束层”变成“操作手册 + 运行时协议”。
   - 结果是遵循率下降、维护成本上升、边界不断膨胀。

3. **把 hooks 一刀切全局化**
   - hooks 天然依赖用户环境、团队风险偏好、项目边界。
   - 如果全部落到全局，会把 repo-specific 习惯误升级成 host-wide policy。

4. **把 baseline repo 演进成 orchestration engine / auto-sync system**
   - `README.md:10-15` 已明确它不是 orchestration engine / auto-upgrade system。
   - 一旦越界，source repo 会从“稳定真源”变成“高维护运行时系统”。

5. **把经验性知识继续写回 global core，而不是 memory**
   - 经验、偏好、误用案例变化快，放进 global core 会污染 always-on surface。
   - 正确承接位置应是 memory 或 reference docs。

# Appendix: Immediate Next Actions

1. **优先冻结并准备移除 `global/skills/spec-execute/SKILL.md`**，同时写迁移说明，明确由 Superpowers execution lane 承接。
2. **新增 `docs/reference/superpowers-boundary.md`**，把仓库定位、Superpowers 边界、禁止竞争性 skills、hooks scope 原则集中写清楚。
3. **压缩 `global/standards/core-standard.md`**：先删 `§9 Completion Contract`、`§10 Override Keys`，再缩 `§6`。
4. **压缩 `global/guides/orchestration-extension.md`**：保留 decision heuristics，移除重复的 default path / trigger 细节。
5. **评估 `global/commands/finish-branch.md`**：要么收窄成 repo-hygiene readiness check，要么删除，避免与 Superpowers 收尾能力重叠。
6. **建立 `distribution/hooks/` 与 `distribution/settings-snippets/` 目录骨架**，按 `user/`、`project/`、`README.md` 三层组织。
7. **新增 `docs/reference/hooks-scope.md`**，明确哪些 hook 可全局、哪些只能项目级、哪些只能作为 local example。
8. **把 `docs/plan/` 迁为 `docs/audits/`**，并更新 README 的目录结构，避免“审计材料看起来像执行计划目录”。
9. **把 `core-standard` 迁出的流程细节回填到 `baseline/docs/workflow/*`**，确保删减后不丢信息，但承接位置正确。
10. **做一轮“Superpowers 冲突复核”**：逐项检查 global/distribution/docs 中是否还有与主控层重名、同责、同语义的入口。