# Plan Packet Skill - 优化版 v2.2

这是 plan-packet skill 的深度优化版本，修复了原版的所有已知问题并深度集成 Backlog MCP 工作流。

## 问题修复清单

| # | 问题 | 状态 |
|---|------|------|
| 1 | SKILL.md 描述手动流程，未引导调用脚本 | ✅ 已修复 |
| 2 | 脚本中的模板与 `templates/` 目录不一致 | ✅ 已修复 |
| 3 | `add` 命令在空任务目录时显示错误提示 | ✅ 已修复 |
| 4 | `merge-claude-md.py` 查找 `skill.md` 而非 `SKILL.md` | ✅ 已修复 |
| 5 | **CLAUDE.md 模板不符合用户要求** | ✅ v2.2 修复 |
| 6 | **缺少与 Backlog MCP 工作流的深度集成** | ✅ v2.2 新增 |

## v2.2 核心变更

### 1. CLAUDE.md 模板重构

**原版问题**：模板过于简化，缺少核心原则和 MCP 资源引用

**v2.2 优化**：
```markdown
## 工作流总则

**任务事实源**：Backlog.md + Plan Packet

**读取任务流程**：优先通过 MCP 资源 `backlog://workflow/overview`

**每次实现必须**：
- 严格按 Plan Packet 执行；发现偏离先回写 Plan Packet
- push/PR 前执行 `./scripts/ci-local.sh`

---

## 具体步骤

### 1) 读取任务
- 读取 Backlog 任务文件
- 参考 MCP 资源：task-execution、task-finalization

### 2) 执行与回写
- 按 Plan Packet 完成实现
- 发现偏离时，使用 `task_edit` 的 `planAppend` 字段记录变更

### 3) 验证与发布
- `./scripts/ci-local.sh` 必须通过
- 提交 PR 并链接到任务

---

## MCP 资源

- `backlog://workflow/overview` - 工作流总览
- `backlog://workflow/task-execution` - 任务执行指南
- `backlog://workflow/task-finalization` - 任务完成指南
```

### 2. Plan Packet 模板增强

在 Notes 部分添加了 MCP planAppend 提示：

```markdown
### 9. Notes（备注）
- <上下文、决策、外部参考链接等>

**重要**：执行过程中若发现偏离 Plan Packet，必须使用以下方式记录：
```bash
# 通过 Backlog MCP 更新任务
task_edit id:{task_id} planAppend:"<描述变更原因和新的执行方向>"
```
```

### 3. SKILL.md 文档更新

新增「与 Backlog MCP 的集成」章节，明确：
- 任务事实源为 Backlog.md + Plan Packet
- 执行前/中/后的 MCP 资源使用流程
- planAppend 的偏离记录机制

## 目录结构

```
plan-packet/
├── SKILL.md                      # 主文档（脚本驱动 + MCP 集成）
├── scripts/
│   ├── plan-packet.py           # v2.2 核心脚本
│   └── merge-claude-md.py        # 工作流合并脚本
└── templates/
    ├── claude-md-fragment.md     # CLAUDE.md 片段（v2.2 更新）
    └── plan-packet-template.md   # Plan Packet 模板（v2.2 更新）
```

## 安装方法

### 方式一：一键安装

```bash
#!/bin/bash
# 迁移 plan-packet 到优化版 v2.2

SKILL_DIR="$HOME/.claude/skills/plan-packet"
REFACTOR_DIR="/Users/cunning/Workspaces/heavy/skills-creation/plan-packet-refactor"

# 备份现有版本
if [ -d "$SKILL_DIR" ]; then
    mv "$SKILL_DIR" "$SKILL_DIR.backup.$(date +%Y%m%d%H%M%S)"
fi

# 创建新目录
mkdir -p "$SKILL_DIR"

# 复制文件
cp "$REFACTOR_DIR/SKILL.md" "$SKILL_DIR/"
mkdir -p "$SKILL_DIR/scripts"
cp "$REFACTOR_DIR/scripts/plan-packet.py" "$SKILL_DIR/scripts/"
cp "$REFACTOR_DIR/scripts/merge-claude-md.py" "$SKILL_DIR/scripts/"
mkdir -p "$SKILL_DIR/templates"
cp "$REFACTOR_DIR/templates/"*.md "$SKILL_DIR/templates/"

echo "✓ 安装完成！"
ls -la "$SKILL_DIR"
```

### 方式二：手动安装

```bash
# 1. 备份现有版本
mv ~/.claude/skills/plan-packet ~/.claude/skills/plan-packet.backup

# 2. 复制优化版文件
cp /path/to/plan-packet-refactor/SKILL.md ~/.claude/skills/plan-packet/
mkdir -p ~/.claude/skills/plan-packet/scripts
cp /path/to/plan-packet-refactor/scripts/*.py ~/.claude/skills/plan-packet/scripts/
mkdir -p ~/.claude/skills/plan-packet/templates
cp /path/to/plan-packet-refactor/templates/*.md ~/.claude/skills/plan-packet/templates/
```

## 验证安装

```bash
# 1. 检查文件结构
ls -la ~/.claude/skills/plan-packet/

# 2. 测试脚本
python ~/.claude/skills/plan-packet/scripts/plan-packet.py --help

# 3. 在项目中测试
cd /path/to/project
python ~/.claude/skills/plan-packet/scripts/plan-packet.py init
```

## 使用示例

### 场景 1：新项目初始化

```
用户: "初始化 plan-packet"

Claude 应该：
1. 调用 init 脚本
2. 显示结果
3. 建议下一步："是否需要添加 Plan Packet 到现有任务？"
```

### 场景 2：创建任务后添加计划

```
用户: "我刚创建了任务 TASK-001，添加 Plan Packet"

Claude 应该：
1. 调用 add --task TASK-001 脚本
2. 显示添加结果
3. 读取任务文件，引导用户填写 Goal/Non-goals
```

### 场景 3：执行时偏离处理

```
执行过程中发现原计划不可行：

Claude 应该：
1. 使用 task_edit 记录偏离原因
2. 提出新的执行方向
3. 等待用户确认
4. 继续执行新计划
```

## 与原版兼容性

优化版 v2.2 完全兼容：
- 原有 Plan Packet 格式
- 原有分支命名规则
- backlog MCP 创建的任务

版本标记升级到 v2.2，`update` 命令可自动升级所有任务的 Plan Packet。

## Backlog MCP 工作流对齐

v2.2 完全对齐 Backlog MCP 的工作流程：

| 阶段 | Backlog MCP | Plan Packet v2.2 |
|------|-------------|------------------|
| 规划 | 先计划，后实现 | Plan Packet 作为实现计划 |
| 执行 | 更新计划用 planAppend | Notes 中明确要求记录偏离 |
| 完成 | 检查验收标准 | Acceptance Criteria 引用 backlog 原生 |
