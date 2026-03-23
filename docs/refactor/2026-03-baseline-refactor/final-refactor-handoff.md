# Final Refactor Handoff — Baseline Repository Closeout

**Date**: 2026-03-23
**Status**: REFACTOR COMPLETED
**Version**: 1.0.0-stable

---

## 1. Final Outcome

### What Was Delivered

本次 refactor 完成了 baseline source repo 的职责收缩与结构重排，在不把本仓库演进成第二主控层的前提下，建立了清晰的知识层边界。

**Completed Phases:**

| Phase | Scope | Status | Key Deliverables |
|-------|-------|--------|------------------|
| **Phase 1** | 结构收缩 | ✅ COMPLETED | 压缩 global core，建立边界文档，迁移 audit 路径 |
| **Phase 2** | 承接层 | ✅ COMPLETED | 移除竞争性 workflow skills，对齐 protocol docs |
| **Phase 3B** | Hooks | ✅ COMPLETED | H-01/H-02/H-03 hook clusters，opt-in 模板 |
| **Phase 4** | Memory | ✅ COMPLETED | Memory boundary authority，protocol 对齐，清理验证 |

### Current Repository State

本仓库现在可以作为 **stable baseline source repo** 长期使用：

- **不是** plugin runtime — 只分发，不执行
- **不是** feature state repository — 不跟踪项目进度
- **不是** project memory repository — 提供 skeleton，不填充内容
- **不是** orchestration engine — 没有行为控制面
- **不是** auto-upgrade system — 升级需要手动 `git pull`

---

## 2. Authoritative Surfaces

### 2.1 Global Runtime Constraints

| Surface | Purpose | Who Should NOT Change | When to Change |
|---------|---------|----------------------|----------------|
| `global/CLAUDE.md` | 极薄入口，指向 core-standard 和 orchestration-extension | 非 host 管理员 | 仅当入口引用变更时 |
| `global/standards/core-standard.md` | Host-wide 跨项目核心原则（证据优先、验证门禁、安全性） | 非 host 管理员 | 仅当发现跨项目稳定约束缺失时 |
| `global/guides/orchestration-extension.md` | 编排决策指导启发式 | 非 host 管理员 | 仅当需要新的编排决策模式时 |

**Key principle**: `global/` 是 **tool governance**，不是 project-specific knowledge。

### 2.2 Protocol Docs

| Surface | Purpose | Who Should NOT Change | When to Change |
|---------|---------|----------------------|----------------|
| `baseline/docs/workflow/memory-protocol.md` | Memory 写入流程（intake/update/removal） | 无特定限制 | 当流程需要优化时 |
| `baseline/docs/workflow/execution-contract.md` | 执行状态、验证、里程碑更新约束 | 无特定限制 | 当执行模型需要调整时 |
| `baseline/docs/workflow/review-protocol.md` | Review required 判定与证据记录 | 无特定限制 | 当 review policy 变更时 |
| `baseline/docs/workflow/review-checklist.md` | Review 轻量辅助清单 | 无特定限制 | 当 review checklist 需要更新时 |
| `baseline/docs/workflow/native-task-translation.md` | Durable task → session task 映射 | 无特定限制 | 当任务翻译模型需要调整时 |

**Key principle**: Protocol docs 定义 **how work is done**，不替代 Superpowers 的 **what to do next**。

### 2.3 Distribution Hooks / Settings Snippets

| Surface | Purpose | Who Should NOT Change | When to Change |
|---------|---------|----------------------|----------------|
| `distribution/hooks/project/*/hook.mjs` | Project-scope 源码模板 | 未理解 hooks-scope.md 时 | 当新增 deterministic gate 类型时 |
| `distribution/settings-snippets/project/*.settings.jsonc` | Project-scope 配置片段模板 | 未理解 hooks-scope.md 时 | 与配对 hook 同步变更 |
| `distribution/hooks/project/README.md` | Hooks 索引与采用路径 | 未理解 opt-in 原则时 | 新增 hook cluster 时 |
| `distribution/settings-snippets/project/README.md` | Snippets 索引与 wiring 说明 | 未理解 opt-in 原则时 | 新增 snippet 时 |

**Key principle**: Hooks/snippets 是 **source-only, opt-in templates**，不是 live default。

### 2.4 Baseline Memory

| Surface | Purpose | Who Should NOT Change | When to Change |
|---------|---------|----------------------|----------------|
| `baseline/memory/MEMORY.md` | 概览级 durable lessons | 无特定限制 | 当满足 D1/D2/D3 的项目规则出现时 |
| `baseline/memory/patterns.md` | 可复用模式（trigger + action） | 无特定限制 | 当满足 D1/D2/D3 的模式被验证时 |
| `baseline/memory/gotchas.md` | 复发性陷阱与规避 | 无特定限制 | 当满足 D1/D2/D3 的陷阱被识别时 |

**Key principle**: Memory 只存储 **durable cross-session lessons**，不是任务日志或一次性笔记。

### 2.5 Reference Docs

| Surface | Purpose | Who Should NOT Change | When to Change |
|---------|---------|----------------------|----------------|
| `docs/reference/superpowers-boundary.md` | 仓库角色与 Superpowers 边界定义 | 未理解 D-001 决策时 | 仅当边界需要重新谈判时 |
| `docs/reference/hooks-scope.md` | Hooks 三层 scope 定义 | 未理解 D-003 决策时 | 仅当 hooks 模型需要扩展时 |
| `docs/reference/memory-boundary.md` | Memory 分类权威标准 | Phase 4 完成后 | 仅当发现新的分类维度时 |

**Key principle**: Reference docs 是 **authoritative boundary anchors**，变更需谨慎。

### 2.6 Refactor Closeout Docs

| Surface | Purpose | Who Should NOT Change | When to Change |
|---------|---------|----------------------|----------------|
| `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementation-closeout.md` | Phase 3B 完成判定与边界复核 | 无特定限制 | 仅当需要对历史审计时 |
| `docs/refactor/2026-03-baseline-refactor/phase-4-memory-closeout.md` | Phase 4 完成判定与一致性验证 | 无特定限制 | 仅当需要对历史审计时 |
| `docs/refactor/2026-03-baseline-refactor/final-refactor-handoff.md` | 本文档 — 最终交付与维护指南 | 无特定限制 | 仅当启动新 refactor 时 |

---

## 3. Layer Responsibilities

### 3.1 `global/CLAUDE.md`

**承接:**
- 极薄入口，指向 `core-standard.md` 和 `orchestration-extension.md`
- Host-wide 运行时表面引用

**不承接:**
- 项目特定规则
- Workflow 脚本
- 执行状态机
- 报告模板

**常见误改方向:**
- ❌ 把项目特定规则写进 global
- ❌ 把 Superpowers 技能内容写进来
- ❌ 让它变厚成第二控制面

### 3.2 `global/standards/core-standard.md`

**承接:**
- 跨项目稳定约束（evidence-first, verification gates）
- 安全性原则
- Git 规则
- 工具失败规则

**不承接:**
- 项目特定 conventions
- Workflow orchestration 逻辑
- Hook 内容
- Memory 内容

**常见误改方向:**
- ❌ 添加项目特定工具命令
- ❌ 把 protocol 内容塞进来
- ❌ 承载大段 completion/reporting schema

### 3.3 `global/guides/orchestration-extension.md`

**承接:**
- 编排决策启发式
- 何时 delegation / parallelism / escalation 的判断标准
- 恢复信号与反模式

**不承接:**
- 具体执行协议
- Agent 定义本身
- 项目特定路由规则
- Task state 管理

**常见误改方向:**
- ❌ 演化成第二控制面
- ❌ 替代 Superpowers 技能
- ❌ 承载具体工作流脚本

### 3.4 `distribution/hooks/**`

**承接:**
- H-01: authoritative state gate（deterministic subset only）
- H-02: verification evidence gate（deterministic subset only）
- H-03: review evidence gate（deterministic subset only）
- 配对的 `scope.md`, `README.md`, `manual-test.md`, `rollback.md`

**不承接:**
- Semantic inference（语义推断）
- Workflow orchestration
- Next-step derivation
- Review policy 推导
- Reviewer assignment / independence 实质证明

**常见误改方向:**
- ❌ 让 hooks 承担 protocol engine 职责
- ❌ 让 hooks 做 judgment 而非 gate
- ❌ 默认启用而非 opt-in
- ❌ 迁移到 user/global scope 而非 project scope

### 3.5 `distribution/settings-snippets/**`

**承接:**
- 与 hooks 配对的配置片段
- Environment variable wiring
- Auth surface 配置

**不承接:**
- Live `settings.json`（必须是 snippet-only）
- Project-specific 非 hook 配置

**常见误改方向:**
- ❌ 写入 live settings 而非 template
- ❌ 把全局配置塞进来
- ❌ 默认启用而非 opt-in merge

### 3.6 `baseline/docs/workflow/**`

**承接:**
- Execution contracts（状态、验证、里程碑更新）
- Review protocols（required 判定、证据记录）
- Memory protocols（intake/update/removal 流程）
- Task translation（durable → session 映射）

**不承接:**
- 具体项目 memory 内容
- Hook 实现细节
- Global CLI rules
- Skill behavior

**常见误改方向:**
- ❌ 把 protocol 内容塞进 memory
- ❌ 让 protocol 变成控制层
- ❌ 与 Superpowers 技能职责重叠

### 3.7 `baseline/memory/**`

**承接:**
- Durable project-specific lessons（满足 D1/D2/D3）
- Reusable patterns（trigger + action）
- Recurring pitfalls（situation → failure → fix）

**不承接:**
- 任务日志
- 一次性会话状态
- Feature progress notes
- Protocol definitions
- Hook installation steps
- Global CLI rules

**常见误改方向:**
- ❌ 把 memory 当任务日志
- ❌ 把 protocol 内容塞进来
- ❌ 把一次性笔记持久化
- ❌ 跨文件重复同一事实

### 3.8 `docs/reference/**`

**承接:**
- 边界定义（superpowers-boundary, hooks-scope, memory-boundary）
- 权威分类标准

**不承接:**
- 具体项目内容
- Audit reports（这些属于 `docs/audits/`）

**常见误改方向:**
- ❌ 把边界文档当配置文件频繁修改
- ❌ 在 reference 里混入具体项目知识

---

## 4. Adoption Path

### 4.1 First Steps for New Adopters

1. **先看什么**
   - `README.md` — 仓库定位与 quick start
   - `docs/reference/superpowers-boundary.md` — 理解这是什么 / 不是什么
   - `docs/reference/hooks-scope.md` — 理解 hooks 为什么不是默认启用
   - `docs/reference/memory-boundary.md` — 理解什么能进 memory

2. **Hooks/templates 从哪里找**
   - `distribution/hooks/project/README.md` — 所有可用 hooks
   - `distribution/settings-snippets/project/README.md` — 配对 snippets

3. **Memory 从哪里看**
   - `baseline/memory/MEMORY.md` — 项目规则概览
   - `baseline/docs/workflow/memory-protocol.md` — 如何写 memory

4. **Protocol 从哪里看**
   - `baseline/docs/workflow/` — 所有协议文档
   - `execution-contract.md` — 执行状态与验证
   - `review-protocol.md` — Review required 判定

### 4.2 What is Opt-In

**Opt-in（需显式采用）:**
- 所有 hooks（需复制到项目目录）
- 所有 settings snippets（需手动 merge 到 `settings.json`）
- Memory 内容填充（需按 protocol 写入）

**NOT opt-in（已是 baseline 的一部分）:**
- `global/` 核心原则
- `baseline/docs/workflow/` 协议定义
- Distribution commands（`/init-claude-workflow`, `/new-feature`）

### 4.3 What is NOT Live Default

**NOT live default（不会自动生效）:**
- Hooks 不会自动安装
- Settings snippets 不会自动写入
- Memory skeleton 不会自动填充
- 仓库不会自动升级

**Live after setup（初始化后即生效）:**
- `global/CLAUDE.md` → `~/.claude/CLAUDE.md`
- `global/standards/` → `~/.claude/standards/`
- `global/guides/` → `~/.claude/guides/`

---

## 5. Maintainer Change-Routing Guide

### 5.1 Decision Tree

```
遇到新问题，首先问：
├─ 这是跨项目稳定约束吗？
│  └─ YES → `global/standards/core-standard.md`
│  └─ NO  → 继续
│
├─ 这是编排决策模式吗？
│  └─ YES → `global/guides/orchestration-extension.md`
│  └─ NO  → 继续
│
├─ 这是 machine-enforced deterministic gate 吗？
│  └─ YES → `distribution/hooks/project/` (新建 cluster)
│  └─ NO  → 继续
│
├─ 这是 workflow 如何执行的协议吗？
│  └─ YES → `baseline/docs/workflow/` (对应协议文档)
│  └─ NO  → 继续
│
├─ 这是 durable cross-session lesson 吗？
│  └─ 满足 D1/D2/D3 → `baseline/memory/` (按文件角色分类)
│  └─ 不满足 → 不持久化（ephemeral）
│
├─ 这是边界定义变更吗？
│  └─ YES → `docs/reference/` (对应边界文档)
│  └─ NO  → 继续
│
└─ 这是一次性笔记 / 临时状态吗？
   └─ YES → 不持久化
   └─ NO  → 重新评估上述路径
```

### 5.2 Example Routes

| Problem Type | Route | Reason |
|--------------|-------|--------|
| Host-level durable rule（跨项目稳定约束） | `global/standards/core-standard.md` | 跨项目 tool governance |
| Machine-enforced deterministic gate（e.g. 检查 task 是否在 tracker 中标记为 done） | `distribution/hooks/project/` (新建 cluster) | Hook scope |
| Reusable workflow pattern（e.g. "如何从 spec 生成 plan"） | `baseline/docs/workflow/` 或 `baseline/memory/patterns.md` | 看是 protocol 还是 lesson |
| Recurring pitfall（e.g. "某个命令在 CI 中总是失败"） | `baseline/memory/gotchas.md` | 满足 D1/D2/D3 后写入 |
| Protocol rule（e.g. "review 什么时候 required"） | `baseline/docs/workflow/review-protocol.md` | Protocol doc |
| One-off note（e.g. "今天遇到一个奇怪的错误"） | **不持久化** | 不满足 D1/D2/D3 |
| Project-specific convention（e.g. "我们团队用 mise run test"） | `baseline/memory/MEMORY.md`（在项目中） | Project memory |
| Hook installation question | `docs/reference/hooks-scope.md` 或 hook 自带 `README.md` | Boundary doc |
| Memory classification question | `docs/reference/memory-boundary.md` | Boundary authority |
| "这是 Superpowers 的职责还是 baseline 的职责？" | `docs/reference/superpowers-boundary.md` | Boundary definition |

---

## 6. Anti-Patterns to Continue Avoiding

### AP-1: 让 global core 再次变厚

**症状:** 把项目特定规则、workflow 脚本、执行状态机塞进 `global/standards/core-standard.md`

**为什么错:** Global core 应该只包含跨项目稳定约束，项目特定内容应该进 protocol 或 memory

**正确做法:**
- 项目规则 → `baseline/memory/MEMORY.md`
- Workflow 协议 → `baseline/docs/workflow/`
- 工具特定命令 → 工具自己的文档

### AP-2: 让 hooks 长成第二主控面

**症状:** Hooks 开始做 semantic inference、next-step derivation、review policy 推导

**为什么错:** Hooks 应该只承接 deterministic gate，不应承担 protocol engine 或 orchestration 职责

**正确做法:**
- Gate（检查一致性） → hooks
- Judgment（语义推断） → Superpowers 或 human
- Orchestration → Superpowers

### AP-3: 把 protocol 内容塞进 memory

**症状:** 把 workflow definitions、phase contracts、review gate descriptions 写进 memory

**为什么错:** Memory 是 durable lessons，不是 protocol 存储位置

**正确做法:**
- Protocol 定义 → `baseline/docs/workflow/`
- 从 protocol 执行中得出的 durable lessons → `baseline/memory/`

### AP-4: 把 one-off notes 写进 memory

**症状:** 把"今天遇到的一个奇怪错误"、"这次会话的特殊配置"写进 memory

**为什么错:** Memory 必须满足 D1/D2/D3，one-off 不满足 recurrence

**正确做法:** One-off 内容不持久化，或仅在 feature spec / issue 中记录

### AP-5: 让 refactor docs 与 actual repo surface 漂移

**症状:** Refactor 文档说"不应该有 X"，但仓库里实际还有 X

**为什么错:** Refactor 文档应该准确描述仓库状态，漂移会导致维护者困惑

**正确做法:** 当仓库结构变更时，同步更新 refactor 文档；或在新 refactor 中更新状态

### AP-6: 跨文件重复同一事实

**症状:** 同一个规则在 `MEMORY.md`、`patterns.md`、`gotchas.md` 都有

**为什么错:** 违反"each durable fact lives once"原则，导致维护成本和更新不同步

**正确做法:** 按 `memory-boundary.md` §5.4 consolidation rules 合并到正确文件

### AP-7: Vague entries

**症状:** Memory 写"be careful with X"、"don't forget Y"，但没有足够 context

**为什么错:** 无法 action，future session 仍需要问人

**正确做法:** 重写为具体、action-triggering 的条目，或删除

---

## 7. Final Completion Judgment

### REFACTOR COMPLETED

**理由:**

1. **所有计划 phase 均已完成**
   - Phase 1: 结构收缩 ✅
   - Phase 2: 承接层 ✅
   - Phase 3B: Hooks ✅
   - Phase 4: Memory ✅

2. **所有验收标准均已满足**
   - Global core 已压缩至稳定约束
   - 边界文档已建立且被引用
   - Hooks/snippets 已按 scope 分类，保持 opt-in
   - Memory 已清理并验证一致性
   - 无与 Superpowers 冲突的 competing workflow skills

3. **仓库状态稳定**
   - Authoritative surfaces 已明确
   - Layer responsibilities 已清晰
   - Anti-patterns 已文档化
   - Adoption path 已可用

4. **无阻塞遗留问题**
   - Phase 3B closeout: 无 enforcement gap（见 `phase-3b-hook-implementation-closeout.md` §E）
   - Phase 4 closeout: 所有 C1-C7 检查通过（见 `phase-4-memory-closeout.md` §C7）
   - Cross-cluster boundary review: H-01/H-02/H-03 边界清晰

### 什么是新工作（不属于本次 refactor 尾项）

以下属于未来新工作，不是本次 refactor 未完成的尾项：

- **Adoption validation** — 在真实 adopting project 中验证这些 opt-in templates 的落地体验
- **New hook clusters** — 新增其他 deterministic gate 类型的 hook clusters
- **New protocol docs** — 新增其他 workflow phase 的协议文档
- **Memory content accumulation** — 随着时间积累新的 patterns/gotchas
- **Baseline version bump** — 当需要重大结构变更时，新版本 baseline 的新 refactor
- **Documentation expansion** — 新增 operator guides、tutorials 等

### 维护者后续关注点

1. **保持边界清晰** — 当需要添加新内容时，先问"这是哪层的职责"
2. **避免 scope creep** — 不让本仓库再次变成第二主控层
3. **遵循 change-routing guide** — 按第 5 节决策树路由变更
4. **持续避免 anti-patterns** — 按第 6 节检查是否有反模式回归

---

## 8. References

### Closeout Documents
- `docs/refactor/2026-03-baseline-refactor/phase-3b-hook-implementation-closeout.md` — Phase 3B 完成判定
- `docs/refactor/2026-03-baseline-refactor/phase-4-memory-closeout.md` — Phase 4 完成判定

### Boundary Authorities
- `docs/reference/superpowers-boundary.md` — 仓库角色与 Superpowers 边界
- `docs/reference/hooks-scope.md` — Hooks 三层 scope 定义
- `docs/reference/memory-boundary.md` — Memory 分类权威标准

### Core Protocols
- `baseline/docs/workflow/execution-contract.md` — 执行状态与验证
- `baseline/docs/workflow/review-protocol.md` — Review required 判定
- `baseline/docs/workflow/memory-protocol.md` — Memory 写入流程

### Global Runtime Surface
- `global/CLAUDE.md` — 入口
- `global/standards/core-standard.md` — 跨项目核心原则
- `global/guides/orchestration-extension.md` — 编排决策指导

---

**END OF HANDOFF**

This document is the single source of truth for:
1. What was delivered in this refactor
2. What each layer is responsible for
3. How to route future changes
4. What anti-patterns to avoid

Maintainers: Keep this document in sync with repository reality. When structure changes, update this handoff or initiate a new refactor.
