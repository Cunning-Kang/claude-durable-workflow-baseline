# Task-flow 依赖与 CLI 兼容修复 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 让 task-flow 在任意项目目录中可稳定运行，依赖缺失时给出可操作提示，并修正 CLI 入口/模块导入导致的启动失败。

**Architecture:** 以“入口统一 + 依赖前置检查 + 测试锁定行为”为核心。CLI 统一通过 skill 内的可执行脚本或绝对路径调用，避免 `python -m` 在未安装包时失败；增加依赖自检与明确安装指引；通过 pytest 固化入口与错误提示行为。

**Tech Stack:** Python 3.10+，pytest，PyYAML，packaging

---

### Task 1: 入口行为与依赖缺失的失败用例

**Files:**
- Modify: `.claude/skills/task-flow/tests/test_cli.py`
- (If needed) Create: `.claude/skills/task-flow/tests/test_entrypoints.py`

**Step 1: 写失败测试（入口可用性）**

在 `test_cli.py` 增加一个子进程测试，验证从任意目录调用 skill 的入口脚本或 `cli.py` 能返回 `--help`。

```python
import os
import subprocess
import sys
from pathlib import Path

def test_task_flow_help_runs_from_any_cwd(tmp_path):
    skill_root = Path(__file__).resolve().parents[1]
    cli = skill_root / "src" / "cli.py"
    result = subprocess.run(
        [sys.executable, str(cli), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "task-flow" in (result.stdout + result.stderr)
```

**Step 2: 运行测试确认失败**

Run: `pytest .claude/skills/task-flow/tests/test_cli.py::test_task_flow_help_runs_from_any_cwd -v`

Expected: FAIL（如果当前入口未稳定或输出不含关键字）

**Step 3: 写失败测试（依赖缺失提示）**

添加一个测试，模拟缺失依赖时输出清晰提示。使用 monkeypatch 临时阻断 import。

```python
import builtins
import importlib
import types


def test_missing_dependency_message(monkeypatch, tmp_path):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name in {"yaml", "packaging"}:
            raise ModuleNotFoundError(name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    skill_root = Path(__file__).resolve().parents[1]
    cli = skill_root / "src" / "cli.py"
    result = subprocess.run(
        [sys.executable, str(cli), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "pip install -r" in (result.stdout + result.stderr)
```

**Step 4: 运行测试确认失败**

Run: `pytest .claude/skills/task-flow/tests/test_cli.py::test_missing_dependency_message -v`

Expected: FAIL（当前未实现友好提示或退出码不一致）

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/tests/test_cli.py

git commit -m "test: lock cli entrypoint and missing-deps behavior"
```

---

### Task 2: 依赖自检与错误提示

**Files:**
- Modify: `.claude/skills/task-flow/src/cli.py`
- Modify: `.claude/skills/task-flow/requirements.txt`

**Step 1: 写最小实现（依赖自检）**

在 `cli.py` 顶部导入依赖前加入显式检查，缺失时打印明确提示并退出：

```python
try:
    import yaml  # noqa: F401
    import packaging  # noqa: F401
except ModuleNotFoundError as exc:
    print(
        "Missing dependency: {}. Install with: "
        "python -m pip install -r <skill_root>/requirements.txt".format(exc.name)
    )
    raise SystemExit(1)
```

**Step 2: 更新 requirements**

在 `requirements.txt` 中明确列出 `PyYAML` 和 `packaging`（如已有，确认版本范围与重复项）。

**Step 3: 运行入口相关测试**

Run: `pytest .claude/skills/task-flow/tests/test_cli.py -v`

Expected: PASS

**Step 4: Commit**

```bash
git add .claude/skills/task-flow/src/cli.py .claude/skills/task-flow/requirements.txt

git commit -m "fix: add dependency preflight and explicit requirements"
```

---

### Task 3: CLI 入口一致性（避免 python -m 失败）

**Files:**
- Modify: `.claude/skills/task-flow/task-flow`
- Modify: `.claude/skills/task-flow/SKILL.md`
- Modify: `.claude/skills/task-flow/README.md`
- (If needed) Modify: `.claude/skills/task-flow/src/__main__.py`

**Step 1: 写失败测试（入口脚本）**

新增测试确保 `task-flow` 脚本从任意 cwd 可运行：

```python

def test_task_flow_script_runs(tmp_path):
    skill_root = Path(__file__).resolve().parents[1]
    script = skill_root / "task-flow"
    result = subprocess.run(
        [str(script), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
```

**Step 2: 运行测试确认失败**

Run: `pytest .claude/skills/task-flow/tests/test_cli.py::test_task_flow_script_runs -v`

Expected: FAIL（若脚本未设置可执行或路径/解释器问题）

**Step 3: 修正脚本与入口文档**

- `task-flow` 脚本使用 `#!/usr/bin/env python3` 并通过绝对路径运行 `src/cli.py`。
- `SKILL.md` 和 `README.md` 统一说明入口为 `task-flow` 脚本或 `python <skill_root>/src/cli.py`，避免 `python -m cli/task_flow`。
- 如必须兼容 `python -m task_flow`，在 `src/__main__.py` 中增加自定位 `src` 路径并转发到 CLI（可选）。

**Step 4: 运行入口测试**

Run: `pytest .claude/skills/task-flow/tests/test_cli.py::test_task_flow_script_runs -v`

Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/task-flow/task-flow .claude/skills/task-flow/SKILL.md .claude/skills/task-flow/README.md .claude/skills/task-flow/src/__main__.py

git commit -m "fix: stabilize task-flow entrypoint and docs"
```

---

### Task 4: 双路径同步与验证

**Files:**
- Modify: `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/**`
- Modify: `/Users/cunning/.claude/skills/task-flow/**`

**Step 1: 同步文件内容**

将 `.claude/skills/task-flow` 下的改动同步复制到 `/Users/cunning/.claude/skills/task-flow`，保证代码、结构、文档一致。

**Step 2: 在两处运行测试**

Run (repo copy): `pytest /Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/task-flow/tests -v`

Run (global copy): `pytest /Users/cunning/.claude/skills/task-flow/tests -v`

Expected: PASS

**Step 3: Commit**

```bash
git add .claude/skills/task-flow

git commit -m "chore: sync task-flow skill to global path"
```

---

Plan complete and saved to `docs/plans/2026-02-04-task-flow-deps-cli-compat-plan.md`. Two execution options:

1. Subagent-Driven (this session) - 我为每个任务派发子代理执行，逐步复核
2. Parallel Session (separate) - 新开会话用 executing-plans 分批执行

Which approach?