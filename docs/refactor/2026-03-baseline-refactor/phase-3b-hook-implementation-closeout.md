# Phase 3B — Hook Implementation Closeout

> Date: 2026-03-22
> Scope: `P3B-I22` / `P3B-I23` / `P3B-I24`
> Constraint: authoritative migration inputs unchanged; no hook logic expansion; no live wiring

## A. Completed Tasks

- `P3B-I22` — 更新 project hooks 根 README 的候选索引
- `P3B-I23` — 更新 project settings snippets 根 README 的候选索引
- `P3B-I24` — 完成 cross-cluster closeout 与 implementation boundary 收口复核

## B. Files Changed

- `distribution/hooks/project/README.md`
- `distribution/settings-snippets/project/README.md`
- `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementation-closeout.md`

## C. Cross-Cluster Boundary Review

对 H-01 / H-02 / H-03 的统一复核结论如下：

- **machine-checkable subset only**：满足。三者都只承接可 deterministic 判断的 completion-time 子集，没有扩展到语义推断或编排。
- **source-only**：满足。hook artifacts 仅以 `distribution/hooks/project/<candidate>/hook.mjs` 形式分发，没有 live project wiring。
- **snippet-only**：满足。settings 仅以 `distribution/settings-snippets/project/*.settings.jsonc` 分发，没有 live `settings.json`。
- **opt-in**：满足。三者都要求 adopting project 显式 copy hook + 手工 merge snippet。
- **project-scope**：满足。三者都维持在 `project` scope，没有漂移到 user/global default。
- **non-live**：满足。未写入 baseline repo live settings、bootstrap、default wiring。
- **non-competing with Superpowers**：满足。三者都只在 `TaskCompleted` 边界做窄 gate，不承担 planning、routing、batching、review orchestration、next-step inference。

统一边界判断：当前 H-01 / H-02 / H-03 没有偷偷扩张成 protocol engine、review policy engine、workflow orchestrator 或 repo-wide autodiscovery controller。

结构规范复核：三类 cluster 都具备 `hook.mjs`、paired snippet、`README.md`、`scope.md`、`manual-test.md`、`rollback.md` 这一标准 artifact family，目录层级一致，可被同一种 adoption 流程消费。

## D. Rule-to-Hook Coverage Check

### 已承接的 migrated deterministic subsets

- **H-01 / authoritative state gate**
  - 仅承接 completion target 到 configured durable tracker 的映射一致性
  - 仅检查 target entry 存在、open/closed marker 一致、configured authoritative surfaces 不矛盾
- **H-02 / verification evidence gate**
  - 仅承接 durable verification artifact 存在性
  - 仅检查 target identifier、evidence section、configured fields、non-placeholder evidence record
- **H-03 / review evidence gate**
  - 仅承接 repo 已提供 review-required signal 之后的 evidence presence gate
  - 仅检查 matching review entry、`Reviewer`、`Reference`、`Outcome=PASS`（或 configured PASS token）

### 故意未迁到 hooks 的内容

以下内容仍故意保留在 protocol docs / Superpowers / human judgment：

- authoritative backend 选择
- checkpoint / reprioritization / next-task derivation
- verification gate applicability 与 command selection
- test/build/lint 的执行本身
- evidence 质量与 freshness 的语义判断
- review-required policy 推导
- reviewer assignment / independence 实质证明 / review quality judgment
- broad workflow orchestration / routing / repo-wide autodiscovery

### Enforcement gap judgment

- **阻塞性 gap：未发现。**
- 对 authoritative migration plan / design 已批准进入 hooks 的 deterministic subset 而言，H-01 / H-02 / H-03 均已有对应 source + snippet + scope/readme/manual-test/rollback 承接面。
- 当前仍存在的“未覆盖部分”都属于文档中明确故意留在非-hook 承接层的内容，不属于本轮应补实现的 enforcement gap。

## E. Index / Adoption Surface Check

### `distribution/hooks/project/README.md`

已补充三类 candidate 的根索引，明确给出：

- hook 名称
- 事件（均为 `TaskCompleted`）
- 对应 rule cluster（H-01 / H-02 / H-03）
- 作用边界
- paired snippet 路径
- `README / scope / manual-test / rollback` 路径

### `distribution/settings-snippets/project/README.md`

已补充三类 snippet 的根索引，明确给出：

- snippet 文件名
- 事件
- 对应 rule cluster
- wiring purpose 与 boundary
- paired hook source 路径
- supporting docs 路径

### 后续采用者的发现与使用路径

后续采用者现在可以按统一路径发现并采用模板：

1. 从 `distribution/hooks/project/README.md` 选择 candidate
2. 复制对应 `hook.mjs` 到 `<project>/.claude/hooks/...`
3. 从 `distribution/settings-snippets/project/README.md` 找到 paired snippet
4. 手工 merge 到 `<project>/.claude/settings.json`
5. 按 cluster 自带 `manual-test.md` 与 `rollback.md` 完成验证与回退预案

### 为什么不会被误解为 live default wiring

两个根 README 都明确写出：

- project-scope
- source/snippet-only
- opt-in
- non-live
- not global default
- manual copy / manual merge required

因此索引增加了 adoption surface，但没有把模板伪装成 baseline repo 的默认接线。

## F. Phase 3B Completion Judgment

**Completed**

理由：

1. `P3B-I22` / `P3B-I23` 已补全 root adoption indexes。
2. `P3B-I24` 已完成跨 H-01 / H-02 / H-03 的统一边界复核。
3. 本轮未修改任何 authoritative migration inputs。
4. 本轮未新增 live settings、default enablement、bootstrap wiring 或 hook logic expansion。
5. 三个 cluster 仍严格停留在 rule-first / migration-first / deterministic subset / project-scope / opt-in / non-competing with Superpowers 的边界内。
6. 对本阶段计划内应由 hooks 承接的 deterministic subset，未发现阻塞完成判定的 enforcement gap。

建议下一阶段入口：

- 进入 **Phase 4**，或
- 启动后续 **adoption / hardening** 工作流，在真实 adopting project 中验证这些 opt-in template families 的落地体验

## G. Follow-up Items

以下仅作为后续阶段或后续 issue 项，不在本轮修复：

- 复核 H-02 supporting docs 的文案一致性（当前 README/rollback 的元信息与 adoption 表述风格与 H-01/H-03 略有差异）。
- 复核 H-02 rollback note 中对 shell-profile env exports 的表述是否仍是最佳 project-scope 说法。
- 复核 H-03 `manual-test.md` 中 scenario 11 的 `mntmp -d` 命令拼写，必要时在后续文档修订轮更正。
