# CLAUDE.md Bootstrap Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在任意项目中用一条命令自动生成/更新根目录 `CLAUDE.md`，基于内置薄模板并自动回填 `Project Overrides` 命令字段。

**Architecture:** 使用一个可测试的 Python 渲染脚本承载“提取→渲染→备份写入”核心逻辑；Skill 负责流程编排；`/claude-md-bootstrap` 作为统一入口。由于内置 slash command（如 `/init`）不能被自定义命令程序化调用，提取源优先使用当前项目 `CLAUDE.md`（或显式 `--init-source`），缺失时提示先手动执行一次 `/init`。

**Tech Stack:** Claude Code Skills、Custom Slash Commands、Python 3.10、pytest、Markdown 模板。

---

**Required process skills:** `@superpowers:test-driven-development`、`@superpowers:writing-skills`、`@superpowers:verification-before-completion`

## Task 1: 搭建可测试骨架（RED 起步）

**Files:**
- Create: `.claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py`
- Create: `.claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py`
- Create: `.claude/skills/claude-md-bootstrap/tests/fixtures/init_snapshot.md`
- Create: `.claude/skills/claude-md-bootstrap/tests/fixtures/thin_template.md`

**Step 1: 写第一个失败测试（模板渲染）**

```python
# .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py
from pathlib import Path

from bootstrap_claude_md import render_template


def test_render_template_replaces_project_overrides():
    template = Path(__file__).parent / "fixtures" / "thin_template.md"
    rendered = render_template(
        template.read_text(encoding="utf-8"),
        {
            "ENV_SETUP_CMD": "mise install && mise run install",
            "TEST_CMD": "mise run test",
            "LINT_CMD": "mise run lint",
            "TYPECHECK_CMD": "mise run check",
            "BUILD_CMD": "mise run build",
        },
        project_name="skills-creation",
        default_branch="main",
    )
    assert "PROJECT_NAME: skills-creation" in rendered
    assert "TEST_CMD: mise run test" in rendered
```

**Step 2: 运行测试并确认失败**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py::test_render_template_replaces_project_overrides -v`
Expected: FAIL，报 `ModuleNotFoundError` 或 `ImportError`（脚本尚未实现）

**Step 3: 写最小实现使测试通过**

```python
# .claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py
from __future__ import annotations


def render_template(template: str, overrides: dict[str, str], project_name: str, default_branch: str) -> str:
    data = {
        "PROJECT_NAME": project_name,
        "DEFAULT_BRANCH": default_branch,
        "ENV_SETUP_CMD": overrides.get("ENV_SETUP_CMD", ""),
        "TEST_CMD": overrides.get("TEST_CMD", ""),
        "LINT_CMD": overrides.get("LINT_CMD", ""),
        "TYPECHECK_CMD": overrides.get("TYPECHECK_CMD", ""),
        "BUILD_CMD": overrides.get("BUILD_CMD", ""),
        "PRIMARY_LANGUAGE": "",
        "PACKAGE_MANAGER": "",
        "TASK_TRACKING_MODE": "auto",
        "REVIEW_POLICY": "standard",
        "RISK_TOLERANCE": "medium",
        "TASKFLOW_ENTRY": "",
    }
    out = template
    for key, value in data.items():
        out = out.replace(f"{{{{{key}}}}}", value)
    return out
```

**Step 4: 再跑测试确认通过**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py::test_render_template_replaces_project_overrides -v`
Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py .claude/skills/claude-md-bootstrap/tests/fixtures/init_snapshot.md .claude/skills/claude-md-bootstrap/tests/fixtures/thin_template.md
git commit -m "feat: scaffold claude-md bootstrap renderer with first passing test"
```

---

## Task 2: 实现命令提取逻辑（从 init 快照读取）

**Files:**
- Modify: `.claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py`
- Modify: `.claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py`
- Modify: `.claude/skills/claude-md-bootstrap/tests/fixtures/init_snapshot.md`

**Step 1: 写失败测试（提取 5 个命令字段）**

```python
def test_extract_commands_from_init_snapshot():
    from bootstrap_claude_md import extract_commands

    text = (
        "ENV_SETUP_CMD: mise install && mise run install\n"
        "TEST_CMD: mise run test\n"
        "LINT_CMD: mise run lint\n"
        "TYPECHECK_CMD: mise run check\n"
        "BUILD_CMD: mise run build\n"
    )
    result = extract_commands(text)
    assert result["ENV_SETUP_CMD"] == "mise install && mise run install"
    assert result["BUILD_CMD"] == "mise run build"
```

**Step 2: 运行测试并确认失败**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py::test_extract_commands_from_init_snapshot -v`
Expected: FAIL（`extract_commands` 未定义）

**Step 3: 写最小实现**

```python
import re

OVERRIDE_KEYS = [
    "ENV_SETUP_CMD",
    "TEST_CMD",
    "LINT_CMD",
    "TYPECHECK_CMD",
    "BUILD_CMD",
]


def extract_commands(init_text: str) -> dict[str, str]:
    result = {k: "" for k in OVERRIDE_KEYS}
    for key in OVERRIDE_KEYS:
        m = re.search(rf"^{key}\s*[:=]\s*(.+)$", init_text, flags=re.MULTILINE)
        if m:
            result[key] = m.group(1).strip()
    return result
```

**Step 4: 运行测试确认通过，并补一个留空用例**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py -v`
Expected: PASS，且缺失字段返回空字符串

**Step 5: Commit**

```bash
git add .claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py
git commit -m "feat: extract override commands from init snapshot text"
```

---

## Task 3: 实现备份写入与回滚基础

**Files:**
- Modify: `.claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py`
- Modify: `.claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py`

**Step 1: 写失败测试（写入时创建 `.bak`）**

```python
def test_write_with_backup_creates_bak(tmp_path):
    from bootstrap_claude_md import write_with_backup

    target = tmp_path / "CLAUDE.md"
    target.write_text("old", encoding="utf-8")

    backup_path = write_with_backup(target, "new")

    assert target.read_text(encoding="utf-8") == "new"
    assert backup_path is not None
    assert backup_path.read_text(encoding="utf-8") == "old"
```

**Step 2: 运行测试并确认失败**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py::test_write_with_backup_creates_bak -v`
Expected: FAIL（`write_with_backup` 未定义）

**Step 3: 写最小实现**

```python
from pathlib import Path
import shutil


def write_with_backup(target: Path, content: str) -> Path | None:
    backup: Path | None = None
    if target.exists():
        backup = target.with_suffix(target.suffix + ".bak")
        shutil.copy2(target, backup)

    temp = target.with_suffix(target.suffix + ".tmp")
    temp.write_text(content, encoding="utf-8")
    temp.replace(target)
    return backup
```

**Step 4: 运行测试确认通过**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py::test_write_with_backup_creates_bak -v`
Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py
git commit -m "feat: add safe write with CLAUDE.md backup"
```

---

## Task 4: 实现 CLI 主流程与端到端测试

**Files:**
- Modify: `.claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py`
- Modify: `.claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py`

**Step 1: 写失败测试（端到端）**

```python
def test_main_end_to_end(tmp_path):
    from bootstrap_claude_md import main

    source = tmp_path / "init.md"
    source.write_text("TEST_CMD: mise run test\n", encoding="utf-8")

    template = tmp_path / "template.md"
    template.write_text("TEST_CMD: {{TEST_CMD}}\n", encoding="utf-8")

    target = tmp_path / "CLAUDE.md"

    rc = main([
        "--project-root", str(tmp_path),
        "--template", str(template),
        "--init-source", str(source),
        "--target", str(target),
        "--project-name", "demo",
        "--default-branch", "main",
    ])

    assert rc == 0
    assert "mise run test" in target.read_text(encoding="utf-8")
```

**Step 2: 运行测试并确认失败**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py::test_main_end_to_end -v`
Expected: FAIL（`main` 未实现或参数不匹配）

**Step 3: 写最小 CLI 实现**

```python
import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--init-source", required=False)
    parser.add_argument("--target", required=False)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--default-branch", default="main")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root)
    target = Path(args.target) if args.target else project_root / "CLAUDE.md"
    source = Path(args.init_source) if args.init_source else target

    if not source.exists():
        raise SystemExit("init source not found; run /init first or pass --init-source")

    template = Path(args.template).read_text(encoding="utf-8")
    init_text = source.read_text(encoding="utf-8")
    overrides = extract_commands(init_text)
    rendered = render_template(template, overrides, args.project_name, args.default_branch)
    backup = write_with_backup(target, rendered)

    print(json.dumps({
        "target": str(target),
        "backup": str(backup) if backup else None,
        "filled": [k for k, v in overrides.items() if v],
        "empty": [k for k, v in overrides.items() if not v],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Step 4: 运行端到端测试确认通过**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py::test_main_end_to_end -v`
Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py
git commit -m "feat: add claude-md bootstrap CLI flow"
```

---

## Task 5: 写 Skill 与自动命令入口（含可发现性测试）

**Files:**
- Create: `.claude/skills/claude-md-bootstrap/SKILL.md`
- Create: `.claude/skills/claude-md-bootstrap/templates/claude-md-thin.md`
- Create: `.claude/commands/claude-md-bootstrap.md`
- Modify: `.claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py`

**Step 1: 写失败测试（frontmatter 与触发词）**

```python
def test_skill_frontmatter_and_triggers_exist():
    from pathlib import Path

    skill = Path(".claude/skills/claude-md-bootstrap/SKILL.md")
    assert skill.exists(), "SKILL.md must exist"
    text = skill.read_text(encoding="utf-8")
    assert "name:" in text
    assert "description:" in text
    assert "CLAUDE.md" in text
    assert "Project Overrides" in text
```

**Step 2: 运行测试并确认失败**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py::test_skill_frontmatter_and_triggers_exist -v`
Expected: FAIL（文件尚不存在）

**Step 3: 写最小 Skill 与命令文件**

```markdown
---
name: claude-md-bootstrap
description: Use when user wants to generate or refresh project CLAUDE.md with a standard thin template and automatic Project Overrides command filling.
---

# claude-md-bootstrap

## Workflow
1. Read current project `CLAUDE.md` as extraction source (or use user-provided source file).
2. Run Python script to render thin template and write root `CLAUDE.md` with backup.
3. Report filled and empty override fields.
```

```markdown
---
description: Generate project CLAUDE.md from the thin template and auto-fill Project Overrides.
argument-hint: [--init-source <path>]
---

Run the claude-md-bootstrap workflow in this project:
1. Use `.claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py`.
2. Template path: `.claude/skills/claude-md-bootstrap/templates/claude-md-thin.md`.
3. Source path: `$1` if provided, otherwise current `CLAUDE.md`.
4. Target path: project root `CLAUDE.md`.
```

**Step 4: 运行相关测试确认通过**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add .claude/skills/claude-md-bootstrap/SKILL.md .claude/skills/claude-md-bootstrap/templates/claude-md-thin.md .claude/commands/claude-md-bootstrap.md .claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py
git commit -m "feat: add claude-md bootstrap skill and slash command entrypoint"
```

---

## Task 6: 最终验证（证据优先）

**Files:**
- Modify: `CLAUDE.md`（由工具生成）
- Test: `.claude/skills/claude-md-bootstrap/tests/test_bootstrap_claude_md.py`

**Step 1: 跑全量测试**

Run: `python -m pytest .claude/skills/claude-md-bootstrap/tests -v`
Expected: 全部 PASS

**Step 2: 在仓库执行一次真实生成**

Run:
`python .claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py --project-root . --template .claude/skills/claude-md-bootstrap/templates/claude-md-thin.md --project-name skills-creation --default-branch main`

Expected: 输出 JSON，包含 `target`、`filled`、`empty`

**Step 3: 校验生成产物**

Run: `python - <<'PY'
from pathlib import Path
text = Path('CLAUDE.md').read_text(encoding='utf-8')
assert text.startswith('@~/.claude/standards/universal-claude.md')
assert '## Project Overrides' in text
assert 'TEST_CMD:' in text
print('ok')
PY`

Expected: `ok`

**Step 4: 运行 git 检查并人工复核 diff**

Run: `git status && git diff -- CLAUDE.md .claude/skills/claude-md-bootstrap .claude/commands/claude-md-bootstrap.md`
Expected: 仅出现本功能相关变更

**Step 5: Commit**

```bash
git add CLAUDE.md .claude/skills/claude-md-bootstrap .claude/commands/claude-md-bootstrap.md
git commit -m "feat: automate project CLAUDE.md bootstrap workflow"
```

---

## Notes for execution

- 若 `--init-source` 与当前 `CLAUDE.md` 都不存在，脚本必须明确报错并提示先执行 `/init`。
- 严格遵循 TDD：每个新增行为都先看见失败，再写最小实现。
- 不做超范围增强（例如远程模板拉取、自动 git 提交、跨目录写入）。
