# source repo 真相核对与最小闭环验收报告

**审计日期**: 2026-03-21
**审计范围**: 本地 source repo、远端 GitHub main、空白仓库 bootstrap 回归
**审计结论**: 部分通过，存在 1 个阻塞性 bug

---

## A. 最终判断

| 问题 | 结论 |
|------|------|
| 本地 source repo 与远端 GitHub main 是否一致？ | **不一致** — 存在 2 个未提交变更 |
| 远端 main 是否真的具备完整能力？ | **基本具备**，但 bootstrap 脚本存在 1 个阻塞性 bug |
| 空白测试仓库能否基于远端真相源成功 bootstrap？ | **部分失败** — 产生错误的 `Users/` 目录结构 |
| 当前是否还存在阻塞性缺口？ | **是** — bootstrap 脚本路径处理 bug |

---

## B. 一致性核对清单

### 本地 vs 远端

| 项目 | 值 |
|------|-----|
| 本地 HEAD | `1688829c84a2e0c76454452407540cb56ad9972f` |
| 远端 origin/main | `1688829c84a2e0c76454452407540cb56ad9972f` |
| commit 是否一致 | **是** |
| 是否有未 push 差异 | **否** |
| 未提交变更 | `distribution/scripts/init-claude-workflow.sh` (modified), `CLAUDE.md` (untracked) |

### 关键文件树核对（远端 HEAD）

```
baseline/claude/claude-snippet.md
baseline/docs/specs/_template/index.md
baseline/docs/specs/_template/plan.md
baseline/docs/specs/_template/review.md
baseline/docs/specs/_template/spec.md
baseline/docs/specs/_template/tasks/T01-example.md
baseline/docs/specs/_template/verify.md
baseline/docs/workflow/execution-contract.md
baseline/docs/workflow/memory-protocol.md
baseline/docs/workflow/native-task-translation.md
baseline/docs/workflow/review-checklist.md
baseline/docs/workflow/review-protocol.md
baseline/memory/MEMORY.md
baseline/memory/gotchas.md
baseline/memory/patterns.md
distribution/commands/init-claude-workflow.md
distribution/scripts/init-claude-workflow.sh
docs/claude-one-command-bootstrap.md
docs/blank-repo-bootstrap-regression-report.md
docs/source-repo-bootstrap-fix-report.md
docs/migration-notes.md
global/CLAUDE.md
global/README.md
global/commands/finish-branch.md
global/guides/orchestration-extension.md
global/skills/spec-execute/SKILL.md
global/standards/core-standard.md
.gitignore
README.md
VERSION
```

**结论**: 关键文件全部存在，结构完整。

---

## C. 远端能力核验清单

### 目录结构

| 目录/文件 | 状态 |
|----------|------|
| `baseline/` | ✅ 存在 |
| `distribution/` | ✅ 存在 |
| `global/` | ✅ 存在 |
| `docs/` | ✅ 存在 |
| `README.md` | ✅ 存在 |
| `VERSION` | ✅ 存在 |

### 关键文件逐项

| 文件 | 行数 | 状态 |
|------|------|------|
| `distribution/commands/init-claude-workflow.md` | 28 | ✅ |
| `distribution/scripts/init-claude-workflow.sh` | 192 | ✅ |
| `docs/claude-one-command-bootstrap.md` | 159 | ✅ |
| `global/CLAUDE.md` | 5 | ✅ (引用全局标准) |
| `global/standards/core-standard.md` | 296 | ✅ |
| `global/guides/orchestration-extension.md` | 174 | ✅ |
| `global/commands/finish-branch.md` | 58 | ✅ |
| `global/skills/spec-execute/SKILL.md` | 388 | ✅ |

### README 能力清单

| 能力 | 状态 |
|------|------|
| Quick Start | ✅ |
| Superpowers 角色说明 | ✅ |
| `/init-claude-workflow` 职责与边界 | ✅ |
| baseline cache 路径约定 (`~/.claude/baselines/durable-workflow-v1`) | ✅ |
| operator guide 链接 | ✅ (`docs/claude-one-command-bootstrap.md`) |

**远端能力结论**: 完整，无 stub/缺失/误导描述。

---

## D. 空白仓库回归结果

### 测试执行

- **测试仓库**: `/tmp/blank-test-repo` (新建空 git repo)
- **bootstrap 脚本**: `distribution/scripts/init-claude-workflow.sh`
- **源缓存**: `~/.claude/baselines/durable-workflow-v1/baseline`

### 实际生成结果

**正确生成的文件**:
- `claude/claude-snippet.md` ✅
- `docs/specs/_template/` 全套模板 (index, plan, review, spec, verify, tasks/T01-example.md) ✅
- `docs/workflow/` (execution-contract, memory-protocol, native-task-translation, review-checklist, review-protocol) ✅
- `memory/` (MEMORY.md, gotchas.md, patterns.md) ✅
- `.claude/workflow-baseline-version` ✅

**错误生成的内容**:
- `Users/cunning/.claude/baselines/durable-workflow-v1/baseline/` — **空目录，错误的绝对路径结构**

### 根因分析

当 `find $BASELINE_DIR` 返回根 baseline 目录自身作为第一个 item 时，脚本执行:

```bash
cp -r "$src" "$dst"
```

其中 `src = /Users/cunning/.claude/baselines/durable-workflow-v1/baseline`，`dst = /tmp/blank-test-repo/`。

`cp -r` 在复制目录时，保留了完整路径层级，导致在 repo 根下创建了 `Users/cunning/.claude/baselines/durable-workflow-v1/baseline/` 嵌套空目录。

### 验收结论

**FAIL** — bootstrap 产生了错误路径结构，必须修复后才能作为稳定入口。

---

## E. 不应进入 source repo 的内容

以下内容**不应**进入 source repo 的 Git 提交历史：

### 1. context-mode 相关内容
- 根目录 `CLAUDE.md` (当前为 untracked，含有 context-mode MCP 规则)
- **理由**: `CLAUDE.md` 是主项目会话级配置文件，scope 限定在主项目 repo，不属于 durable baseline 分发资产

### 2. 主项目私有内容
- 主项目 repo 中的历史分析文档、fix report 等
- **理由**: 这些是主项目迭代过程的中间产物，source repo 应保持"干净的分发源"状态

### 3. 缓存目录内容
- `~/.claude/baselines/durable-workflow-v1/` 不应被 git track
- **理由**: 这是运行时缓存，应通过 `git clone` + `cp` 机制分发，不是源码的一部分

---

## F. 最小正确修正

### 阻塞性 bug: bootstrap 脚本路径处理

**文件**: `distribution/scripts/init-claude-workflow.sh`

**问题**: `find $BASELINE_DIR -type f -o -type d` 会返回 `$BASELINE_DIR` 自身，导致 `cp -r` 在 repo 根下创建错误的嵌套路径。

**最小修正方案**: 在 `find` 管道中排除 `$BASELINE_DIR` 自身：

```bash
# 当前（有 bug）:
find "$BASELINE_DIR" -type f -o -type d | sort

# 修正为:
find "$BASELINE_DIR" \( -type f -o -type d \) | grep -v "^$BASELINE_DIR$" | sort
```

或者更优方案：用 `find "$BASELINE_DIR" -mindepth 1 ...` 排除根目录自身。

### 本地未提交变更

| 文件 | 当前状态 | 建议处理 |
|------|----------|----------|
| `distribution/scripts/init-claude-workflow.sh` | modified (改进了错误消息) | **应提交** — 改进有意义 |
| `CLAUDE.md` (untracked) | 含 context-mode 内容 | **删除** — 不应进入 source repo |

---

## G. durable 文档入口

| 文档 | 路径 | 用途 |
|------|------|------|
| 真相核对报告 | `docs/source-repo-truth-audit.md` | 本次审计结论，后续复查基准 |
| Operator Guide | `docs/claude-one-command-bootstrap.md` | 新机器/新 repo bootstrap 操作手册 |
| Bootstrap 修复报告 | `docs/source-repo-bootstrap-fix-report.md` | 之前修复的历史记录 |

### 后续微调先看哪个文件

1. **先看**: `docs/source-repo-truth-audit.md` (本报告)
2. **再看**: `distribution/scripts/init-claude-workflow.sh` (需修复的 bug)
3. **再看**: `README.md` (验证分发入口描述)

---

## H. 最终行动清单

### 现在立刻做

1. **删除**根目录 untracked `CLAUDE.md` (context-mode 内容不应进入 source repo)
2. **提交** `distribution/scripts/init-claude-workflow.sh` 的改进 (更好的错误消息)
3. **修复** bootstrap 脚本的路径处理 bug (排除 `$BASELINE_DIR` 自身)

### 本轮已完成

- ✅ 确认本地 HEAD 与远端 origin/main commit 一致 (1688829c)
- ✅ 确认远端 main 具备完整文件结构和能力清单
- ✅ 执行空白仓库 bootstrap 回归验收，发现路径 bug
- ✅ 识别不应进入 source repo 的 context-mode 内容

### 本轮还必须补

- ❌ bootstrap 脚本 bug 尚未实际修复
- ❌ 未提交变更尚未 push 到远端
- ❌ 修复后需重新执行空白仓库回归验收

### 暂时不要做

- 不要把 context-mode 相关内容推进 source repo
- 不要修改 `settings.json` 的 env
- 不要在 source repo 中做新架构设计

### 明确不要做

- 不要依赖主项目历史分析作为事实来源
- 不要把主项目的 CLAUDE.md 内容回灌到 source repo

---

## I. 当前是否已形成真正闭环

**否**。存在 1 个阻塞性 bug：

1. **bootstrap 脚本产生错误路径结构** — 空白仓库验收失败
2. **本地未提交变更未 push** — 真相源与工作树不同步

修复以上 2 项后，闭环才能成立。
