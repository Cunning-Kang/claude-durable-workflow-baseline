# Claude Code 可移植运行方案

> 状态: 正式 | 版本: 1.0.0 | 日期: 2026-03-20

---

## 一、方案组成

```
Superpowers 插件 ────────── 主控层（行为约束）
  │
  ├── TDD / test-driven-development
  ├── verification-before-completion
  ├── requesting-code-review
  ├── writing-plans / executing-plans
  ├── brainstorming
  ├── finish-branch
  └── memory-reflection

增强层 ────────────────────── Repo 本地（知识沉淀）
  │
  ├── docs/specs/_template/  （spec 模板）
  ├── docs/workflow/         （执行协议）
  ├── memory/                （knowledge 沉淀）
  └── baseline/             （初始化 baseline）
```

**Superpowers 是唯一主控层**。增强层不控制行为，只提供 Superpowers 覆盖不到的 durable 知识复利。

---

## 二、新机器初始化（极简路径）

### 必须步骤

1. **安装 Superpowers 插件**
   - 从 Claude Code marketplace 安装 `superpowers` 插件
   - 这是唯一必须的全局安装

2. **安装 source repo 全局资产到 ~/.claude/**
   ```bash
   # 克隆 source repo 到本地 cache
   git clone <source-repo-url> ~/.claude/baselines/durable-workflow/

   # 复制全局 portable 资产到 ~/.claude/
   cp -n ~/.claude/baselines/durable-workflow/global/* ~/.claude/

   # 复制入口命令到 ~/.claude/commands/
   cp ~/.claude/baselines/durable-workflow/distribution/commands/init-claude-workflow.md \
      ~/.claude/commands/init-claude-workflow.md
   ```
   - 仅复制 `global/` 内容：CLAUDE.md, standards/, guides/, commands/
   - **不要复制**：settings.json, hooks, machine-specific 内容

3. **在每个新 repo 执行入口命令**
   ```bash
   cd /path/to/new-repo
   claude
   /init-claude-workflow
   ```
   - 入口命令从 `~/.claude/commands/init-claude-workflow.md` 读取
   - 创建 `docs/specs/_template/`、`docs/workflow/`、`memory/`、`baseline/`

---

## 三、新 Repo 初始化

1. 在目标 repo 中执行 `/init-claude-workflow` 或手动复制 `baseline/` 内容
2. 确认 `docs/specs/_template/`、`docs/workflow/`、`memory/` 存在
3. 以上即为该 repo 的完整 operating model 基础，Superpowers 会自动接管主控

---

## 四、日常使用入口

| 场景 | 入口 |
|------|------|
| 开始任务 | Superpowers `/brainstorming` |
| 写 spec | Superpowers `/writing-plans` |
| 实现中 | Superpowers `/test-driven-development` |
| 验证完成 | Superpowers `/verification-before-completion` |
| 需要 review | Superpowers `/requesting-code-review` |
| 结束会话 | Superpowers `/finish-branch` + `/memory-reflection` |
| 查询增强层 | `docs/specs/_template/`、`docs/workflow/`、`memory/` |

---

## 五、明确不要做的事

1. **不要**在新 repo 中重建主控命令/skills（与 Superpowers 冲突）
2. **不要**将 `docs/workflow/`、`docs/specs/_template/`、`memory/` 作为全局控制层
3. **不要**修改 `~/.claude/settings.json` 的 env 配置
4. **不要**在 Superpowers 已有能力的方向继续造轮子
5. **不要**增加新的全局 automation 控制层

---

## 六、快速检查清单

新 repo 初始化后，确认：

- [ ] `docs/specs/_template/spec.md` 存在
- [ ] `docs/workflow/` 存在（至少含 review-protocol.md）
- [ ] `memory/MEMORY.md` 存在
- [ ] Superpowers 插件已激活
- [ ] `~/.claude/CLAUDE.md` 存在并引用 core-standard

---

## 七、相关文档

| 文档 | 角色 |
|------|------|
| `docs/claude-global-operating-model.md` | 完整方案背景与资产分类 |
| `docs/claude-operating-model-hardening.md` | 强化过程记录 |
| `docs/claude-one-command-bootstrap.md` | **单一入口操作手册**（本方案核心） |
| `~/.claude/standards/core-standard.md` | 全局运行时标准 |

---

> 本文档为可移植化定稿的极简入口。完整操作手册见 `docs/claude-one-command-bootstrap.md`。
