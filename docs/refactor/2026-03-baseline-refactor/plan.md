# 2026-03 Baseline Refactor Plan

## 总目标
在不把本仓库演进成第二主控层的前提下，完成 baseline source repo 的职责收缩与结构重排：**Superpowers 继续作为全局主控层**；本仓库只保留 baseline source、distribution source、protocol docs、hooks source/snippets、memory skeleton 等边界内能力。

## 本计划适用范围
- `global/`
- `distribution/`
- `baseline/`
- `docs/`
- 与上述目录直接相关的 README / reference / audit 文档

## 全局约束
- 不跳 phase，不并行跨 phase 推进。
- 不先做 hooks 默认启用，只允许在 Phase 3 处理 hooks source / settings snippets。
- 不新增与 Superpowers 冲突的通用 workflow skills。
- `global/standards/core-standard.md` 只保留长期稳定约束，不再承载执行协议、报告模板或场景化经验。
- `protocol docs / commands / hooks / memory` 必须分层承接，不相互夺责。
- 当前审计源文件实际位于 `docs/plan/2026-03-22-production-baseline-audit-and-refactor-plan.md`；是否迁往 `docs/audits/` 由 Phase 1 执行。

## 非目标
- 本轮不直接实现 hooks。
- 本轮不直接调整 `distribution/scripts` 的运行行为。
- 本轮不直接把本仓库扩展为新的 workflow runtime。
- 本轮不新增泛化控制层能力来替代或复制 Superpowers。

---

## Phase 1 — 结构收缩

### 目标
先锁定 repo boundary，收缩膨胀的 global 控制面，明确“这是什么 / 不是什么”，让后续承接层有稳定边界可依。

### 范围
- 压缩 `global/standards/core-standard.md`
- 压缩 `global/guides/orchestration-extension.md`
- 新增 `docs/reference/superpowers-boundary.md`
- 将 `docs/plan/` 迁为 `docs/audits/` 并修复引用
- 校正 README / bootstrap / global README 中的边界表述

### 依赖关系
- 依赖当前审计文档与现有 README / global / baseline 结构
- 不依赖 hooks、memory 或 distribution/scripts 行为改动

### 先后顺序
1. 固定边界文案：先写 `docs/reference/superpowers-boundary.md`
2. 缩薄 `core-standard.md`，只保留长期稳定约束
3. 缩薄 `orchestration-extension.md`，只保留 decision guidance
4. 迁移 `docs/plan/` → `docs/audits/`
5. 全面修复 README / docs 链接并做一次边界复核

### 验收标准
- `global/CLAUDE.md` 仍保持极薄入口
- `core-standard.md` 不再常驻大段 completion/reporting schema 或执行状态机
- `orchestration-extension.md` 不再扮演第二控制面
- 仓库文档对 “Superpowers 是主控层” 的表述一致
- 审计材料路径与 README 引用一致，不留失效链接

---

## Phase 2 — 承接层

### 目标
把原本挤在 global core 或竞争性入口中的执行/评审/收尾语义，迁到正确的承接层：**protocol docs、薄命令桥接、reference docs**，而不是继续长成第二主控层。

### 范围
- 冻结并移除或替换 `global/skills/spec-execute/SKILL.md`
- 评估并压缩 `global/commands/finish-branch.md`
- 对齐 `baseline/docs/workflow/*` 中 execution / review / task translation / memory 协议
- 让 README / bootstrap 文档只描述 baseline / distribution / protocol 的职责，不再暗示并行执行层
- 做一轮 Superpowers 冲突复核

### 依赖关系
- 必须在 Phase 1 边界和结构收缩完成后开始
- Phase 2 完成前，不得进入 hooks 或 memory 扩张

### 先后顺序
1. 先冻结冲突最大的 `spec-execute` 能力，并补迁移说明
2. 再决定 `finish-branch` 是收窄为薄桥接命令还是删除
3. 对齐 `baseline/docs/workflow/*` 的 protocol docs 边界
4. 更新 README / bootstrap / reference 文案
5. 完成一次 “与 Superpowers 是否重名、同责、同语义” 的复核

### 验收标准
- repo 内不再存在 competing generic workflow skills
- 命令入口若保留，只是薄桥接，不承担完整 workflow orchestration
- execution / review / task translation 的语义都落在 protocol docs，而不是 global core
- README / bootstrap 文案不再暗示本仓库有独立主控执行层

---

## Phase 3 — Hooks

### 目标
把真正适合 deterministic enforcement 的内容迁到 **scoped hooks source / settings snippets**，但保持 opt-in，不把模板直接升级成默认全局行为。

### 范围
- 新增 `distribution/hooks/{user,project}/`
- 新增 `distribution/settings-snippets/{user,project}/`
- 新增 `docs/reference/hooks-scope.md`
- 为每类 hook 和 snippet 标清 scope、安装方式、为何不是默认启用

### 依赖关系
- 必须在 Phase 2 承接层稳定后开始
- 不能在 Phase 3 之前落 live `settings.json`
- 不能把 hooks 直接塞入 baseline 默认产物

### 先后顺序
1. 先写 `docs/reference/hooks-scope.md`，定义 scope 规则
2. 建立 `distribution/hooks/` 目录骨架
3. 建立 `distribution/settings-snippets/` 目录骨架
4. 为每类模板补 README / usage note
5. 验证 repo 内没有 live hooks / live settings 被默认启用

### 验收标准
- hooks 全部按 scope 分类
- settings snippets 全部按 scope 分类
- 仓库内不落 live `settings.json`
- 每个 hook / snippet 都明确写出“为什么不是默认全局启用”
- hooks 只是 source / template，不是默认 runtime behavior

---

## Phase 4 — Memory

### 目标
把经验、误用案例、环境差异从 global core 和临时控制面里清出去，沉淀到 `baseline/memory/*` 与对应 protocol 中，但只保留 durable lessons。

### 范围
- 对齐 `baseline/docs/workflow/memory-protocol.md`
- 强化 `baseline/memory/MEMORY.md`
- 强化 `baseline/memory/patterns.md`
- 强化 `baseline/memory/gotchas.md`
- 补充 memory boundary 说明，明确什么能进 memory，什么不能进

### 依赖关系
- 必须在 hooks phase 完成后开始
- 只有当前三 phase 边界稳定后，才能安全沉淀 durable knowledge

### 先后顺序
1. 先定义 memory boundary
2. 对齐 `memory-protocol.md`
3. 更新 `MEMORY.md`
4. 更新 `patterns.md`
5. 更新 `gotchas.md`
6. 做一次 protocol ↔ skeleton 一致性复核

### 验收标准
- global core 中不再夹带经验性/环境性知识
- memory 只承接 durable patterns / gotchas / conventions
- memory 不写任务日志、不写一次性会话状态
- baseline 的 memory 协议与 skeleton 一致，不相互打架

---

## Phase Gate
- 只有上一 phase 验收通过，下一 phase 才能开始。
- 如在任一 phase 发现与 Superpowers 冲突，优先更新边界文档与决策记录，再决定是收窄、迁移还是删除。
- 未通过验收前，不得宣称该 phase 完成。
- `tasks.md` 是具体执行入口；执行时以 phase gate + task readiness 双重约束推进。