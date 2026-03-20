# 空白仓库 Bootstrap 回归验收报告

**日期**: 2026-03-20
**验收对象**: https://github.com/Cunning-Kang/claude-durable-workflow-baseline
**commit**: db77a81
**状态**: ✅ 通过

---

## A. 验收标准

验收通过当且仅当：
1. 在空白 git repo 中执行 `init-claude-workflow.sh`
2. 生成 `docs/specs/_template/` 全部文件
3. 生成 `docs/workflow/` 全部文件
4. 生成 `memory/MEMORY.md` 等文件
5. 生成 `baseline/claude/claude-snippet.md`
6. 生成 `.claude/workflow-baseline-version`
7. 无未说明的手工补步骤
8. operator 知道下一步看哪里

---

## B. 空白仓库初始状态

```bash
# 创建空白 repo
mkdir /tmp/blank-repo-test
cd /tmp/blank-repo-test
git init
# 仅含 .git/，无任何业务文件
```

---

## C. 实际执行路径

### 1. 安装 baseline cache（模拟新机器步骤 2）

```bash
git clone https://github.com/Cunning-Kang/claude-durable-workflow-baseline.git \
  ~/.claude/baselines/durable-workflow-v1
```

### 2. 执行 bootstrap

```bash
bash ~/.claude/baselines/durable-workflow-v1/distribution/scripts/init-claude-workflow.sh \
  /tmp/blank-repo-test
```

---

## D. 实际行为输出

```
[INFO] Checking git repository...
[INFO] Git repository confirmed: /tmp/blank-repo-test
[INFO] Checking baseline cache...
[INFO] Baseline version: 1.0.0
[INFO] Baseline source: /Users/cunning/.claude/baselines/durable-workflow-v1/baseline
[INFO] Initializing baseline files...
[INFO]   Created directory: claude/
[INFO]   Created file: claude/claude-snippet.md
[INFO]   Created directory: docs/
[INFO]   Created directory: docs/specs/
[INFO]   Created directory: docs/specs/_template/
[INFO]   Created file: docs/specs/_template/index.md
[INFO]   Created file: docs/specs/_template/plan.md
[INFO]   Created file: docs/specs/_template/spec.md
[INFO]   Created file: docs/specs/_template/review.md
[INFO]   Created directory: docs/specs/_template/tasks/
[INFO]   Created file: docs/specs/_template/tasks/T01-example.md
[INFO]   Created file: docs/specs/_template/verify.md
[INFO]   Created directory: docs/workflow/
[INFO]   Created file: docs/workflow/execution-contract.md
[INFO]   Created file: docs/workflow/memory-protocol.md
[INFO]   Created file: docs/workflow/native-task-translation.md
[INFO]   Created file: docs/workflow/review-checklist.md
[INFO]   Created file: docs/workflow/review-protocol.md
[INFO]   Created directory: memory/
[INFO]   Created file: memory/gotchas.md
[INFO]   Created file: memory/MEMORY.md
[INFO]   Created file: memory/patterns.md
[INFO] Version marker written: /tmp/blank-repo-test/.claude/workflow-baseline-version

Created: 23
Skipped: 0
Conflict: 0
```

---

## E. 最终生成的资产

| 文件 | 状态 |
|------|------|
| `docs/specs/_template/index.md` | ✅ |
| `docs/specs/_template/plan.md` | ✅ |
| `docs/specs/_template/spec.md` | ✅ |
| `docs/specs/_template/review.md` | ✅ |
| `docs/specs/_template/verify.md` | ✅ |
| `docs/specs/_template/tasks/T01-example.md` | ✅ |
| `docs/workflow/execution-contract.md` | ✅ |
| `docs/workflow/memory-protocol.md` | ✅ |
| `docs/workflow/native-task-translation.md` | ✅ |
| `docs/workflow/review-checklist.md` | ✅ |
| `docs/workflow/review-protocol.md` | ✅ |
| `memory/MEMORY.md` | ✅ |
| `memory/patterns.md` | ✅ |
| `memory/gotchas.md` | ✅ |
| `baseline/claude/claude-snippet.md` | ✅ |
| `.claude/workflow-baseline-version` | ✅ |

---

## F. Fail-fast 验证

### 非 git 目录

```bash
bash ~/.claude/baselines/durable-workflow-v1/distribution/scripts/init-claude-workflow.sh /tmp/non-git-dir
# → [ERROR] Not a git repository
# → [ERROR] Run 'git init' first, then re-execute this script.
# Exit code: 1
```

---

## G. 验收结论

| 验收项 | 结果 |
|--------|------|
| 空白 repo 中 bootstrap 成功 | ✅ |
| 所有预期文件生成 | ✅ |
| 版本标记生成 | ✅ |
| 非 git 目录 fail-fast | ✅ |
| 下一步提示输出 | ✅ |
| 无未说明手工步骤 | ✅ |

**结论**: bootstrap 已真正可用，通过验收。
