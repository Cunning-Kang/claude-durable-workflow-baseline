# 2026-03 Baseline Refactor 风险登记

| 风险编号 | 风险 | 触发信号 | 影响 | 缓解方式 |
| --- | --- | --- | --- | --- |
| R-001 | 与 Superpowers 职责冲突 | 仓库中继续存在 execution / planning / finishing / review 的平行入口或同语义说明 | 产生双主控层、双协议、双入口 | 先更新 `docs/reference/superpowers-boundary.md`，再对冲突点做收窄、桥接或删除 |
| R-002 | hooks 误全局化 | 在 `distribution/` 中直接放 live `settings.json`、默认启用说明或一键全局安装路径 | 把可选 enforcement 误升级为默认行为，破坏用户环境边界 | 只分发 source / snippets；按 `user` / `project` 分层；每个目录写清 opt-in 原则 |
| R-003 | global core 再次膨胀 | `global/standards/core-standard.md` 重新塞入模板、状态机、场景化经验或长流程 | always-on surface 污染，难以维护，继续与 protocol docs 抢职责 | 对 global core 建立“仅长期稳定约束”审查标准；超出边界内容迁往 protocol docs / reference / memory |
| R-004 | protocol docs 变成隐形第二主控层 | `baseline/docs/workflow/*` 开始承担总控编排、跨场景决策或替代 Superpowers 的指挥语气 | 虽然不叫 skill，但实质重新形成第二控制面 | protocol docs 只写 repo-local 协议与边界，不写通用主控工作流；持续做冲突复核 |
| R-005 | 文档迁移后引用失效 | `docs/plan/` 迁到 `docs/audits/` 后，README、bootstrap docs、refactor docs 仍保留旧链接 | 审计依据不可达，执行控制面与仓库实际状态脱节 | 迁移时先做链接清单，再全量修复引用，最后做一次断链复核 |
| R-006 | 冲突入口“收窄不彻底” | `spec-execute`、`finish-branch` 表面改名，但仍保留原有 workflow 语义 | 用户仍会把本仓库当成平行主控层使用 | 对每个入口做“是否仍与 Superpowers 同责”复核，不满足就删除而不是保留灰区 |
| R-007 | memory 再次演变成文档堆 | `baseline/memory/*` 混入任务日志、一次性会话状态、未验证经验 | memory 失去可复用性，变成噪音源 | 只记录 durable patterns / gotchas / conventions，并让 `memory-protocol.md` 明确禁止项 |

## 风险状态更新
- 2026-03-22：`P1-T04` 完成后，`R-005` 已从“迁移待执行”降为“后续需避免重新引入旧 `docs/plan/` 活动引用”。
- 2026-03-22：`P2-T01` 与 `P2-T04` 完成后，`R-006` 已从“冲突入口收窄不彻底”降为“后续需防止 protocol docs 或 README 文案重新引入 execution / finishing 平行入口”。
- 2026-03-22：`P2-T02` 完成后，`R-004` 已从“execution 语义挤在错误承接层”降为“后续需防止 review / translation / README 文案重新长回总控编排语气”。
- 2026-03-22：`P2-T03` 完成后，`R-004` 进一步收敛为“后续仅需防止 protocol docs 与 README 文案重新引入跨文档夺责或总控编排口吻”。
- 2026-03-22：`P2-T05` 完成后，`R-001` 已从“当前存在平行主控入口风险”降为“后续新增或改写资产时，需持续防止重名、同责、同语义入口回归”。
- 2026-03-22：`P3-T05`、`P3-T01`、`P3-T02` 完成后，`R-002` 已从“hooks scope 与 opt-in 规则尚未落文档/骨架，易误写为默认全局行为”降为“后续在 `distribution/hooks/` 与 `distribution/settings-snippets/` 扩展时，需持续防止 live settings、默认启用说明或超前 wiring 表述回归”。
- 2026-03-22：`P3-T03`、`P3-T04`、`P3-T06` 完成后，`R-002` 进一步收敛为“当前 hooks / settings 分发表面已固定为 scope README + source/snippet-only 约束；后续风险主要是新增具体 hook/snippet 样例时重新引入 live config、默认启用说明或 user/project scope 混淆”。
