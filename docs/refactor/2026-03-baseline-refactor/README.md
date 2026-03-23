# 2026-03 Baseline Refactor 执行控制面

## 用途
这组文件是本仓库本次 baseline refactor 的本地执行控制面，用来把审计结论、阶段顺序、任务拆解、关键决策和已知风险固定下来，作为后续逐步执行的工作底稿。

**后续执行应以本目录文件为准，而不是依赖会话临时发挥。**

## 执行边界
- 本目录只负责这次 refactor 的执行控制，不直接承担核心行为实现。
- Phase 必须按顺序推进：**Phase 1 → Phase 2 → Phase 3 → Phase 4**。
- 必须先做**结构收缩**，再做**承接层**，再做 **hooks**，最后做 **memory**。
- 不能跳 phase，不能把 Phase 3 的 hooks 提前落地，更不能默认启用。
- 不能新增与 **Superpowers** 冲突的通用 workflow skills。
- 本轮仅做计划文件落盘与最小链接整理，不直接修改核心行为。

## 当前输入依据
- 最新审计计划（当前实际路径）：[`../../plan/2026-03-22-production-baseline-audit-and-refactor-plan.md`](../../plan/2026-03-22-production-baseline-audit-and-refactor-plan.md)
- 仓库总览：[`../../../README.md`](../../../README.md)
- global 层说明：[`../../../global/README.md`](../../../global/README.md)
- baseline workflow 协议：[`../../../baseline/docs/workflow/`](../../../baseline/docs/workflow/)
- baseline memory skeleton：[`../../../baseline/memory/`](../../../baseline/memory/)

## 文件清单
- [`plan.md`](./plan.md)：Phase 1 ~ Phase 4 的顺序、依赖、验收与 phase gate
- [`tasks.md`](./tasks.md)：按 phase 拆解的细粒度可执行任务清单
- [`decisions.md`](./decisions.md)：当前已经明确的关键架构决策
- [`risks.md`](./risks.md)：当前已知风险、触发信号与缓解方式
- [`changelog.md`](./changelog.md)：本控制面的变更记录

## 使用方式
1. 先读 [`plan.md`](./plan.md)，确认当前允许推进的 phase。
2. 再读 [`tasks.md`](./tasks.md)，一次只挑一个 ready task 执行。
3. 若执行中发现边界变化，先更新 [`decisions.md`](./decisions.md) / [`risks.md`](./risks.md)，再继续实施。
4. 若实际仓库状态与审计结论不一致，先修正文档，再推进代码或结构变更。

## 当前结论
这套文件本身就是这次 refactor 的“本地执行控制面”。它的作用不是替代 Superpowers，而是把**本仓库范围内**的重构顺序、职责边界和交付标准固定下来，避免后续会话随意扩张范围。