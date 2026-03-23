# Phase 3B — Rule-to-Hook Migration Plan

> Status: replacement for the discarded candidate-driven Phase 3B draft
> Date: 2026-03-22
> Positioning: map removed/compressed global rules into the correct destination, then isolate the subset that must become deterministic hook enforcement

---

## 背景

Phase 1 与 Phase 2 已经完成两件关键工作：

1. `global/standards/core-standard.md` 与 `global/guides/orchestration-extension.md` 被压缩回“薄而稳定”的 always-on 约束与 decision guidance。
2. 原本挤在 global 层里的执行、评审、翻译与收尾语义，已经分别迁往 repo-local protocol docs、边界文档与 Superpowers 所拥有的主控面。

因此，Phase 3B 当前真正要解决的，不是“先挑几个 hook 事件做模板”，而是：

> **从已被删除、压缩、迁出的全球文字规则中，找出那些仍然需要 deterministic enforcement 的规则簇，并把它们映射为 scoped hooks source/snippets。**

旧版 `phase-3b-hook-implementations-plan.md` 的问题在于：它从 `SessionStart` / `PreToolUse` / `Stop` / `ConfigChange` 等事件位点倒推候选，导致“hook 候选”先于“规则来源”存在。那种做法会把 baseline repo 的 Phase 3B 变成模板挑选题，而不是 rule migration 题。

本版计划将旧 Phase 3B 草案降级为**废弃参考**：只用于说明为什么 event-first / candidate-first 思路不再成立，不再作为当前 Phase 3B 的 authoritative source。

---

## 目标

建立一个可长期复用的 **rule-to-hook migration framework**，用于回答以下问题：

1. 哪些原本存在于 `global/CLAUDE.md`、`global/standards/core-standard.md`、`global/guides/orchestration-extension.md` 的规则，已经被删除、压缩或迁出？
2. 这些规则分别应该留在什么承接层：global core、protocol docs、commands、Superpowers、memory，还是 hooks？
3. 在所有迁出规则中，哪些规则簇必须依靠 hooks 才能形成 deterministic enforcement？
4. 对于进入 hooks migration set 的规则簇，应该如何映射到 event / scope / template artifacts，而不是直接写源码？
5. 只有在规则迁移总表完成后，哪些 hook implementation candidates 才被允许进入下一阶段？

---

## 范围

本阶段只处理以下内容：

- 盘点 `global/CLAUDE.md`、`global/standards/core-standard.md`、`global/guides/orchestration-extension.md` 中被删除、压缩、迁出的规则簇
- 对照当前 refactor 文档：
  - `docs/refactor/2026-03-baseline-refactor/plan.md`
  - `docs/refactor/2026-03-baseline-refactor/tasks.md`
  - `docs/refactor/2026-03-baseline-refactor/decisions.md`
- 对照当前承接层与边界文档：
  - `baseline/docs/workflow/execution-contract.md`
  - `baseline/docs/workflow/review-protocol.md`
  - `baseline/docs/workflow/review-checklist.md`
  - `baseline/docs/workflow/native-task-translation.md`
  - `docs/reference/hooks-scope.md`
  - `docs/reference/superpowers-boundary.md`
- 输出 authoritative 的规则迁移总表
- 输出 hooks migration set 与 hook design mapping
- 在总表完成后，给出**源自规则簇**而不是源自事件倒推的 implementation candidates

---

## 非目标

本阶段明确不做：

- 不实现任何 hook 源码
- 不写或覆盖任何 live `settings.json` / `settings.local.json`
- 不修改 bootstrap、`/init-claude-workflow`、`/new-feature` 或任何 live wiring
- 不从 `SessionStart` / `Stop` / `ConfigChange` / `PreToolUse` 这些事件出发反推首批模板
- 不把 planning / routing / finishing / review orchestration 重新塞进 hooks
- 不把 reminder-only、docs-only、context-injection-only 的内容伪装成 deterministic hook template
- 不把 project-specific policy 偷换成 global default behavior

---

## 规则迁移方法

Phase 3B 必须按以下顺序推进：

### Step 1 — Source delta inventory
先建立 source inventory：
- 哪些规则仍保留在 global 层
- 哪些规则被压缩成更薄的一句话原则
- 哪些规则已迁往 protocol docs / reference docs / Superpowers
- 哪些规则在迁移后仍存在 deterministic enforcement gap

### Step 2 — Rule cluster normalization
不要按句子碎片建表，而要按**规则簇**建表。一个规则簇需要同时描述：
- 原规则来源
- 原规则意图
- 当前状态
- 当前承接层
- 是否仍有 enforcement gap

### Step 3 — Destination classification
对每个规则簇只指定一个**主承接层**：
- global core
- orchestration guide
- protocol docs
- commands / thin bridges
- Superpowers / built-in routing / agent definitions
- memory
- hooks

若 hooks 只是一个辅助 enforcement layer，而主语义仍在 protocol docs / Superpowers，则表中必须显式写清“primary owner”与“hook-enforced subset”。

### Step 4 — Hook admissibility filter
只有同时满足以下条件的规则簇，才可进入 hooks migration set：

1. **源规则确实已被删除、压缩或迁出**，而不是仍应留在 global prose
2. **规则的关键部分可被机器判断**，存在明确的 pass / block / allow / deny 边界
3. **该规则不适合只靠 commands / protocol docs / memory 承接**
4. **该规则不属于 Superpowers 主控面**，不会重建平行的 planning / execution / review control layer
5. **该规则可以 scoped、opt-in、source-only 地分发**，符合 `docs/reference/hooks-scope.md`

### Step 5 — Hook design mapping
只有通过 admissibility filter 的规则簇，才继续映射：
- event family
- scope
- template artifacts
- residual gap

### Step 6 — Candidate derivation after the table
只有当规则迁移总表完整后，才允许提出 implementation candidates；而且候选必须能反向追溯到具体 rule cluster，而不是从事件 affordance 出发命名。

---

## 规则分类标准

| 分类标准 | 判断问题 | 去向 |
|---|---|---|
| Stable always-on principle | 这条规则是否应该长期常驻所有会话，且保持简洁稳定？ | 留在 `global/standards/core-standard.md` 或 `global/CLAUDE.md` |
| On-demand orchestration guidance | 这条规则是否只是在判断是否需要 orchestration，而非执行控制？ | 留在 `global/guides/orchestration-extension.md` |
| Repo-local protocol semantics | 这条规则是否定义执行/评审/翻译/记忆协议，而不是运行时拦截？ | 迁到 `baseline/docs/workflow/*` |
| Primary control-layer behavior | 这条规则是否实际决定 planning / routing / execution / review lane？ | 归 Superpowers、built-in routing、agent definitions |
| Thin entry or bridge | 这条规则是否只是入口、桥接、安装或导航？ | `commands` / README / bootstrap |
| Durable lesson / pattern | 这条规则是否只是长期经验、坑点、例外？ | `memory` |
| Deterministic runtime enforcement | 这条规则是否有明确运行时边界，且仅靠文档会失效？ | `hooks` |

**关键判断**：
- **描述语义**留在文档
- **控制语义**归主控层
- **deterministic enforcement subset** 才归 hooks

---

## 规则迁移总表

| Rule cluster | 原规则来源 | 原规则内容 / 意图 | 当前状态 | 主迁移去向 | 若迁到 hooks：event / scope / template artifacts | 当前 gap |
|---|---|---|---|---|---|---|
| 1. Orchestration consult entry | `global/CLAUDE.md`; old `orchestration-extension.md` role / consult text | 在 orchestration-heavy work 时再查 guide；优先更简单路径；不要因为任务大就升级 | **压缩保留**；仍留在薄入口与 guide 中 | `global/CLAUDE.md` + `global/guides/orchestration-extension.md` | 不迁 hooks | 无 hook gap；这是 decision guidance，不是 enforcement rule |
| 2. Default execution path and agent intent | old `orchestration-extension.md` §2 Default Execution Path + §4 Agent Intent | `execution-implementer` / `mechanical-transformer` / `orchestrator-planner` 的默认路径与语义归属 | **已从 guide 删除 / 压缩** | Superpowers / built-in routing / agent definitions | 不迁 hooks | 若迁 hooks 会重建 routing control surface，违反 Superpowers boundary |
| 3. Task levels and traceability schema | old `core-standard.md` §4 Task Levels + Minimum Traceability | 用 `L0/L1/L2` 与 `Goal/Scope/Acceptance/Assumptions/...` 组织执行与报告 | **从 global core 压缩 / 迁出** | `execution-contract.md`、durable task artifacts、planning surface | 不直接迁 hooks | 这是 schema / protocol，不是单纯运行时拦截；hooks 只会消费其 machine-checkable subset |
| 4. Authoritative state backend and milestone discipline | old `core-standard.md` §4 State Backend + Checkpoint | 一次只保留一个 authoritative task state；阶段切换、高风险前、gate failure 后要显式 checkpoint | **详细规则已迁出 global core**；当前只剩薄原则与 protocol 说明 | `execution-contract.md` 为主；hooks 承接 deterministic subset | **Event family:** task-state transition hooks，首个落点以 `TaskCompleted` 为主； **Scope:** `project`; **Artifacts:** `distribution/hooks/project/<candidate>/hook.mjs` + 对应 snippet / README / scope / manual-test / rollback | 当前没有 deterministic blocker 来阻止“重复 authoritative tracker”或“错误 milestone 关闭”类状态违规；目前主要靠文字约束 |
| 5. Verification gates applicability | old `core-standard.md` §6 Required Gates + Applicability | 完成前必须跑适用的 Environment / Test / Static / Traceability / Review gates，并给出证据 | **从 global core 压缩**，已迁到 `execution-contract.md` 与 verification skill | `execution-contract.md` + Superpowers verification surface；hooks 承接 completion gate subset | **Event family:** `TaskCompleted`; **Scope:** `project`; **Artifacts:** verification-gate template family 的 source/snippet/docs 套件 | 当前仍可在没有新鲜 verification evidence 的情况下宣布任务完成；缺少 deterministic gate |
| 6. Review requirement and independent review evidence | old `core-standard.md` §6 Review Policy + Review Requirements | 何时必须 review；必须独立评审；`PASS/FAIL/BLOCKED` 与 `Reviewer/Reference` 证据要求 | **已迁出 global core**，现由 `review-protocol.md`、`review-checklist.md` 与 Superpowers review surface 承接 | `review-protocol.md` + Superpowers review surface；hooks 承接 evidence-presence subset | **Event family:** `TaskCompleted`; **Scope:** `project`; **Artifacts:** review-evidence-gate template family 的 source/snippet/docs 套件 | 当前缺少 deterministic blocker：需要 review 的任务仍可能在没有 `Reviewer/Reference/outcome` 的情况下被标记完成 |
| 7. Completion contract schema | old `core-standard.md` §9 Completion Contract | completion claim 必须包含 `Scope / Changed / Verification / Gates / Risks / Assumptions / Rollback` 等字段 | **已从 global core 删除** | verification/reporting surface + protocol docs；仅 machine-checkable subset 归 hooks | hooks 不直接承接“整份报告格式”；只承接与 completion gate 相关的 machine-checkable subset | 当前 gap 不是“缺少文案模板”，而是 machine-checkable completion evidence 没有 gate |
| 8. Override keys and defaults | old `core-standard.md` §10 Override Keys and Defaults | 统一 `DEFAULT_BRANCH`、`REVIEW_POLICY` 等 override key 与默认值 | **已从 global core 删除** | runtime defaults / project overrides / config docs | 不迁 hooks | 这是配置约定，不是 Phase 3B 的 deterministic enforcement 主题 |
| 9. Orchestration recovery / anti-pattern heuristics | old `orchestration-extension.md` recovery + anti-pattern sections | context pressure、integration cost、low-confidence 时如何降级；不要把 orchestration 当第二控制面 | **压缩后仍保留在 guide** | `global/guides/orchestration-extension.md` | 不迁 hooks | 这些是 heuristics；若迁 hooks 会把 guide 变成 runtime policy engine |

---

## 哪些规则簇进入 hooks migration set

只有以下规则簇进入 hooks migration set：

### H-01 — Authoritative state and milestone integrity
**来源：** Rule cluster 4

**为什么必须用 hooks 承接：**
- 这类规则在旧 global core 中曾以文字形式存在，但详细 state backend / checkpoint 规则已迁出
- `execution-contract.md` 现在只负责 repo-local protocol 说明，不负责运行时拦截
- “不要同时维护两个 authoritative trackers”与“不要在不满足 milestone 语义时关闭任务”属于**状态转换边界**问题，不能只靠 README / protocol doc
- hooks 可以在 task-state transition 边界做窄而 deterministic 的 block / deny，而不是依赖事后自述

**为什么不能交给别处：**
- 不能交给 memory：memory 只记录 durable lessons
- 不能交给 commands：commands 不是所有状态变化的唯一入口
- 不能交给 Superpowers：这不是新的 planning / routing lane，而是 narrow state guard

### H-02 — Verification-before-completion gate
**来源：** Rule cluster 5 与 cluster 7 的 machine-checkable subset

**为什么必须用 hooks 承接：**
- “完成前必须有新鲜 verification evidence”是典型 deterministic gate
- 现在的 `execution-contract.md` 与 verification skill 解释了应该做什么，但仍属于**控制面上的约束说明**
- 如果没有 hook，任务仍然可以在没有足够 evidence 的情况下被标记完成，导致 completion claim 重新退化成 self-assertion

**为什么不能交给别处：**
- protocol docs 只能定义 gate，不会自动拦截
- Superpowers skill 决定行为流程，但不能替代 opt-in 的 repo-local deterministic enforcement
- reminder 型模板不够，因为问题不在“忘记提醒”，而在“缺少 block”

### H-03 — Independent review evidence gate
**来源：** Rule cluster 6 与 cluster 7 的 review-related subset

**为什么必须用 hooks 承接：**
- 对“需要 review 的任务”，`Reviewer / Reference / Outcome` 是否存在，属于 machine-checkable evidence presence 问题
- review-protocol 负责定义何时需要 review、review 记录长什么样；但缺少 deterministic gate 时，仍可能无证据结案
- hook 的职责不是复写 review policy，而是当 policy 已判定 review required 时，在 done transition 上检查 evidence presence

**为什么不能交给别处：**
- 不能交给 commands：review 记录可能来自多个执行路径
- 不能交给 memory：memory 不负责 gate
- 不能交给 Superpowers：Superpowers 决定 review lane，本计划中的 hooks 只负责 repo-local pass/block 子集

---

## 哪些规则明确不该迁到 hooks

以下规则簇**必须明确留在非-hook 承接层**：

### 保留在 global core / guide
- orchestration consult entry
- orchestration heuristics / anti-patterns
- 高层原则如 correctness / verification / reversibility 排序

### 保留在 protocol docs
- task / traceability schema 的完整人类可读结构
- execution bridge 说明
- review protocol 与 checklist
- native task translation 规则

### 保留在 Superpowers / built-in routing / agent definitions
- default execution path
- subagent routing intent
- planning / execution / finishing / review lane 决策
- “何时进入何种主控流程”这一类控制面判断

### 保留在 commands / bootstrap / README
- thin entrypoints
- 安装/初始化/导航说明

### 保留在 memory
- durable gotchas
- 迁移过程中沉淀的长期经验，而非 enforcement 本身

---

## 与 Superpowers 的边界

本计划的 hooks migration 只允许处理：
- narrow
- scoped
- opt-in
- deterministic
- repo-local
的 enforcement。

它**不允许**处理：
- planning
- routing
- next-step inference
- workflow graph construction
- review orchestration
- finishing lane ownership
- competing skill entry points

换句话说：

- **Superpowers 决定“做什么、何时做、由谁做”。**
- **Protocol docs 解释“规则语义是什么”。**
- **Hooks 只在少数明确边界上执行“满足 / 不满足就拦截”。**

任何会把 hooks 重新扩张成第二主控面的设计，都必须在 Phase 3B 被判定为越界。

---

## Hook design mapping 原则

对进入 hooks migration set 的每个规则簇，下一阶段只能设计到以下粒度：

1. **Rule cluster**
2. **Enforcement objective**
3. **Primary event family**
4. **Scope**
5. **Template artifact set**
6. **Residual gap**

不得越过这一步直接进入：
- hook implementation
- live wiring
- bootstrap integration
- automatic install

标准 template artifact set 统一为：
- `hook.mjs`
- `*.settings.jsonc`
- `README.md`
- `scope.md`
- `manual-test.md`
- `rollback.md`

---

## 只有在总表完成后，才允许提出的 hook implementation candidates

以下 candidates **并不是本计划的输入**，而是由上述规则迁移总表推导出的**下一阶段候选**：

### Candidate C-01 — `taskcompleted-authoritative-state-gate`
- **来源规则簇：** H-01
- **目标：** 在任务完成边界检查 authoritative state / milestone integrity 的 machine-checkable subset
- **说明：** 不负责 reprioritize、不开第二 backlog、不推导 next steps

### Candidate C-02 — `taskcompleted-verification-evidence-gate`
- **来源规则簇：** H-02
- **目标：** 在 done transition 前检查 verification evidence 是否满足最小完成条件
- **说明：** 只 gate evidence presence / freshness，不替代 verification strategy 本身

### Candidate C-03 — `taskcompleted-review-evidence-gate`
- **来源规则簇：** H-03
- **目标：** 当 review required 时，检查 `Reviewer / Reference / Outcome` 等 evidence presence
- **说明：** 不决定 review policy，不评价代码质量本身，只守 evidence gate

### 当前明确排除的旧式候选
以下候选**不进入当前 hooks migration set**，因为它们不是从已迁出规则簇正向推导出来的：
- `sessionstart-boundary-reminder`
- `stop-verification-reminder`
- `pretooluse-context-mode-routing-guard`
- `pretooluse-bash-command-guard`
- `configchange-project-settings-guard`

它们并非一定“永远无价值”，但**不属于本轮 rule-to-hook migration 的 authoritative output**。

---

## 验收标准

新的 Phase 3B 只有在以下条件全部满足时才算成立：

1. 已完成从 `global/CLAUDE.md`、`global/standards/core-standard.md`、`global/guides/orchestration-extension.md` 出发的 rule inventory
2. 规则迁移总表已明确列出：
   - 原规则来源
   - 原规则内容 / 意图
   - 当前状态
   - 迁移去向
   - 若迁到 hooks：对应 event / scope / template artifacts
   - 当前 gap
3. 每个规则簇都被分配到正确承接层，且不会出现 hooks / commands / protocol / memory / Superpowers 夺责
4. hooks migration set 只包含真正需要 deterministic enforcement 的 migrated rule clusters
5. hooks migration set 中的每个 cluster 都有清楚的“为什么必须由 hooks 承接”说明
6. implementation candidates 只在总表之后出现，且都能反向追溯到 hooks migration set
7. 文档明确写出哪些规则**不应**迁到 hooks，而应保留在 commands / protocol docs / memory / Superpowers
8. 当前轮没有任何 hook 源码、live settings、bootstrap wiring 或默认启用变更

---

## 为什么这版比旧的 hook-candidate 驱动计划更符合 baseline repo 的真实目标

这版更符合 baseline repo 目标，因为它：

1. **先找被迁出的规则，再决定 hooks 是否需要存在。**
   旧版先挑事件和模板，再寻找理由；新版先做 source-rule inventory，再做 migration mapping。

2. **把 hooks 从“模板列表问题”改成“承接层问题”。**
   baseline repo 的长期价值不在于先塞几个 event demo，而在于作为 authoritative migration source，说明哪些 deterministic rules 应由 hooks 承接。

3. **显式区分了文档语义、主控语义与 enforcement 子集。**
   很多规则应留在 protocol docs 或 Superpowers；只有 machine-checkable subset 才进入 hooks。

4. **避免把 reminder、routing、repo-private policy 冒充成 canonical hook templates。**
   因此，旧草案里的 event-first 候选不会再自动占用首批模板名额。

5. **为后续实现提供可追溯性。**
   下一阶段若要实现 hook，必须能回答：这个 hook 到底是在承接哪条被迁出的规则，而不是“这个 event 看起来能做点什么”。
