# Release Candidate Adoption Validation Plan

> **Date**: 2026-03-23
> **Purpose**: End-to-end adoption surface validation from fresh adopter perspective
> **Scope**: Baseline source repo release-candidate readiness assessment

---

## 1. Goal

从"一个全新的空项目 / 空 repo 采用者"的视角，验证当前仓库是否已经具备作为 baseline source repo 稳定发布/长期复用的质量。

---

## 2. Scope

### In Scope
- Adoption entrypoint clarity
- Installation / adoption path clarity
- Scope clarity (user / project / local)
- Discoverability of assets
- Operational usability
- Maintainer change-routing clarity

### Out of Scope
- 新增 feature / hook / command / memory 内容
- 修改 refactor 计划文件
- 扩展功能或新增能力
- 代码质量审查（已在之前 phase 完成）

---

## 3. Non-Goals

- 不进入新的开发 phase
- 不修改 hook 逻辑或 memory skeleton
- 不把这轮变成 another cleanup round
- 默认先审计和报告，不顺手修（除非高置信 blocking 问题）

---

## 4. 采用者画像

### Primary Adopter: 新空 repo 采用者

**Context:**
- 在一台新机器或新环境上
- 需要为一个新的代码仓库设置 Claude Code workflow
- 想要复用 baseline 的 workflow 协议、spec templates、memory skeleton

**Expectations:**
- 明确知道第一步应该做什么
- 理解什么是自动生效的，什么需要 opt-in
- 能找到 hooks / snippets / protocol / memory / reference docs
- 知道如何验证 adoption 是否成功
- 理解 baseline 与 Superpowers 的边界

**Assumptions:**
- 已安装 Claude Code
- 了解基本的命令行操作
- 可能不了解 Superpowers 或 baseline 设计历史

---

## 5. 验证维度

### A. Entry Clarity
- 一个新采用者第一眼应该看哪里
- README / final handoff / reference docs / distribution / baseline 的入口是否清晰
- 是否存在多个竞争入口导致混乱

### B. Installation / Adoption Path Clarity
- 全局 surface、project surface、opt-in hooks、memory、protocol 各自如何被采用
- 哪些是 source/template only
- 哪些不是 live default
- 采用步骤是否会让新用户误解

### C. Scope Clarity
- user / project / local scope 是否容易理解
- hooks/template 是否会被误解成默认启用
- Superpowers 与 baseline 的边界是否足够清楚

### D. Discoverability
- H-01/H-02/H-03 hooks templates 是否容易发现
- settings snippets 是否容易找到
- protocol / memory / reference docs 是否容易定位

### E. Operational Usability
- adopter 是否能知道：
  - 先读什么
  - 再做什么
  - 哪些不该做
  - 如何 rollback
  - 如何判断自己接入成功

### F. Maintainer Usability
- 后续维护者是否能根据 final handoff 正确判断"问题该改哪一层"
- 是否还存在 change-routing 模糊区

---

## 6. 验证步骤

### Step 1: Entry Point Analysis
- [ ] 识别所有可能的入口点（README, docs/refactor, docs/reference, distribution/, baseline/, global/）
- [ ] 判断是否存在竞争或混乱的入口
- [ ] 评估哪一个是"真正"的第一入口
- [ ] 检查入口之间的引用关系是否清晰

### Step 2: Installation Path Walkthrough
- [ ] 按照 README.md 的 Quick Start 执行安装步骤
- [ ] 检查路径变量是否一致（durable-workflow vs durable-workflow-v1）
- [ ] 验证每一步的输出是否符合预期
- [ ] 识别潜在的误解点

### Step 3: Scope Understanding Check
- [ ] 检查 docs/reference/hooks-scope.md 是否足够清晰
- [ ] 检查 docs/reference/superpowers-boundary.md 是否足够清晰
- [ ] 检查 docs/reference/memory-boundary.md 是否足够清晰
- [ ] 验证 distribution/*/README.md 是否明确说明 opt-in 原则

### Step 4: Asset Discoverability Assessment
- [ ] 检查 hooks 是否容易找到和理解
- [ ] 检查 settings snippets 是否容易找到和理解
- [ ] 检查 protocol docs 是否容易定位
- [ ] 检查 memory skeleton 是否容易理解

### Step 5: Operational Usability Test
- [ ] 验证 /init-claude-workflow 命令是否清晰
- [ ] 验证 /new-feature 命令是否清晰
- [ ] 检查是否有足够的验证清单
- [ ] 检查是否有 rollback 指引

### Step 6: Maintainer Routing Review
- [ ] 检查 final-refactor-handoff.md 的 change-routing guide 是否完整
- [ ] 识别是否存在模糊区域
- [ ] 验证每一层职责是否清晰

---

## 7. 问题分级标准

### Blocking (阻塞发布)
- 高置信会导致采用失败或严重误解的问题
- 无法通过简单文档澄清解决的结构性问题
- 会破坏 baseline source repo 稳定性的问题

### Important but Non-Blocking (重要但不阻塞)
- 会导致困惑但不会阻止采用的问题
- 可以通过澄清文档或小改进解决的问题
- 不影响核心功能但影响体验的问题

### Cosmetic (美观性)
- 文档风格、格式、措辞优化建议
- 不影响理解或使用的微小改进
- 可以作为后续优化项的问题

---

## 8. Release-Candidate 通过标准

### 必须满足：
1. **Entry Clarity**: 存在一个清晰、无竞争的第一入口
2. **Installation Path**: 安装步骤完整、可执行、无矛盾
3. **Scope Clarity**: scope 定义清晰，不会导致误解
4. **Discoverability**: 所有关键资产都可以被找到
5. **Operational Usability**: adopter 可以完成完整的 adoption 流程
6. **Maintainer Usability**: change-routing 足够清晰

### 不要求：
- 文档完美（允许后续改进）
- 所有 cosmetic 问题都解决
- 所有 nice-to-have 的增强都实现

---

## 9. 输出物

1. **Validation Plan** (本文件)
2. **Validation Report** (`release-candidate-adoption-validation-report.md`)
   - 总体结论
   - 按维度的 findings
   - 每条 finding 的严重级别和建议
   - Release-candidate judgment

---

## 10. References

- `README.md` - 仓库主入口
- `docs/claude-one-command-bootstrap.md` - 操作指南
- `docs/refactor/2026-03-baseline-refactor/final-refactor-handoff.md` - Refactor closeout
- `docs/reference/superpowers-boundary.md` - Superpowers 边界
- `docs/reference/hooks-scope.md` - Hooks 三层 scope
- `docs/reference/memory-boundary.md` - Memory 分类
- `distribution/hooks/*/README.md` - Hooks 分发说明
- `distribution/settings-snippets/*/README.md` - Settings snippets 分发说明
- `global/README.md` - Global runtime surface 说明
