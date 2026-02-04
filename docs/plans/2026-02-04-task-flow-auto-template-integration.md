# Task Flow Auto-Template Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 .tmp-superpowers 中的自动模板集成功能以“最小必要变更”迁入 task-flow 技能，并通过完整测试验证。

**Architecture:** 在 task-flow 中新增 config 模块与 templates 目录，通过 CLI 新增 init 命令与初始化检测入口，调用 ConfigManager 完成 CLAUDE.md/AGENTS.md 的模板渲染与智能合并。

**Tech Stack:** Python 3.10+, pytest, PyYAML, packaging.version

---

### Task 1: 审查并选定迁入源文件版本

**Files:**
- Read: `/Users/cunning/Workspaces/heavy/skills-creation/.tmp-superpowers/src/config/*.py`
- Read: `/Users/cunning/Workspaces/heavy/skills-creation/.tmp-superpowers/optimized/*.py`
- Read: `/Users/cunning/Workspaces/heavy/skills-creation/.tmp-superpowers/templates/*.md`

**Step 1: 逐文件对比 src vs optimized 版本**
- 目标：确认是否存在功能差异或仅为风格优化。
- 记录每个文件的差异点与潜在行为差异（例如 ContentMerger 的策略扩展）。

**Step 2: 决定迁入基线版本**
- 推荐优先迁入 optimized 版本，除非与现有 task-flow 逻辑冲突。
- 输出：确定最终将被拷贝到 task-flow 的具体文件列表。

---

### Task 2: 迁入 config 模块与 templates

**Files:**
- Create: `.claude/skills/task-flow/src/config/__init__.py`
- Create: `.claude/skills/task-flow/src/config/manager.py`
- Create: `.claude/skills/task-flow/src/config/template_loader.py`
- Create: `.claude/skills/task-flow/src/config/template_renderer.py`
- Create: `.claude/skills/task-flow/src/config/content_merger.py`
- Create: `.claude/skills/task-flow/src/config/exceptions.py`
- Create: `.claude/skills/task-flow/templates/minimal.md`
- Create: `.claude/skills/task-flow/templates/standard.md`
- Create: `.claude/skills/task-flow/templates/full.md`
- Create: `.claude/skills/task-flow/templates/section_template.md`

**Step 1: 新建目录结构**
- 确保 `src/config` 与 `templates` 目录存在。

**Step 2: 迁入 config 模块**
- 直接复制选定版本文件。
- 在 `__init__.py` 中导出 ConfigManager/TemplateLoader/ContentMerger/TemplateRenderer 与异常类。

**Step 3: 迁入模板文件**
- 将模板文件按标准命名写入 `templates/`。

---

### Task 3: CLI 接入 init 与自动初始化检测

**Files:**
- Modify: `.claude/skills/task-flow/src/cli.py`

**Step 1: 添加模块导入**
```python
from config import ConfigManager
```

**Step 2: 增加 init 命令处理函数**
```python
def cmd_init(args):
    project_root = _get_project_root_from_args(args) or Path.cwd()
    manager = ConfigManager(project_root)
    if manager.is_initialized(project_root) and not args.force:
        existing_version = manager.detect_existing_version()
        print(f"✓ 项目已初始化 (v{existing_version})")
        print("  使用 --force 强制重新初始化")
        return
    result = manager.initialize(
        template_type=args.template or "standard",
        force=args.force,
        interactive=not args.yes,
        backup=not args.no_backup,
    )
    if not result.success:
        sys.exit(1)
```

**Step 3: 注册 init 子命令**
```python
init_parser = subparsers.add_parser("init", help="初始化项目配置")
init_parser.add_argument("--template", "-t", choices=["minimal", "standard", "full"], default="standard")
init_parser.add_argument("--force", "-f", action="store_true")
init_parser.add_argument("--yes", "-y", action="store_true")
init_parser.add_argument("--no-backup", action="store_true")
```

**Step 4: 添加自动初始化检查函数**
```python
def _check_initialization(project_root: Path) -> bool:
    if ConfigManager.is_initialized(project_root):
        return True
    if ConfigManager.is_ci_environment():
        print("⚠️  CI 环境：跳过初始化提示")
        print("   请预先运行: task-flow init")
        return False
    print("╔══════════════════════════════════════════╗")
    print("║  检测到项目尚未初始化 task-flow 工作流   ║")
    print("║                                           ║")
    print("║  [回车] 自动初始化（推荐）               ║")
    print("║  [Ctrl+C] 取消                           ║")
    print("╚══════════════════════════════════════════╝")
    try:
        input()
        manager = ConfigManager(project_root)
        manager.initialize(interactive=False)
        return True
    except KeyboardInterrupt:
        print("\n⚠️  已跳过初始化")
        print("   稍后可运行: task-flow init")
        return False
```

**Step 5: 在命令入口调用初始化检测**
- 在 `cmd_create_task`/`cmd_list_tasks`/`cmd_show_task`/`cmd_start_task`/`cmd_update_task`/`cmd_execute_next_batch`/`cmd_complete_task` 开头调用 `_check_initialization(project_root)`。
- 若返回 False：直接 return 或 exit，避免后续流程。

---

### Task 4: 迁入与调整测试

**Files:**
- Create: `.claude/skills/task-flow/tests/test_config_manager.py`
- Create: `.claude/skills/task-flow/tests/test_template_loader.py`
- Create: `.claude/skills/task-flow/tests/test_content_merger.py`
- Modify: `.claude/skills/task-flow/tests/conftest.py`（如需设置 PYTHONPATH）

**Step 1: 迁入测试文件**
- 从 `.tmp-superpowers/test_*.py` 复制内容。

**Step 2: 统一导入路径**
- 确保测试可通过 `sys.path.insert` 或 conftest 设置读取 `src/`。

**Step 3: 处理空的 test_integration.py**
- 若文件为空则不迁入或删除引用，避免假阳性。

---

### Task 5: 全量测试与修复

**Files:**
- Test: `.claude/skills/task-flow/tests/`

**Step 1: 运行新增测试**
Run: `pytest .claude/skills/task-flow/tests/test_config_manager.py -v`
Expected: PASS

**Step 2: 运行全量测试**
Run: `pytest .claude/skills/task-flow/tests -v`
Expected: PASS (允许已有 1 skipped)

**Step 3: 修复失败项**
- 每次仅修复一个失败用例。
- 修复后重复运行该用例与全量测试。

---

### Task 6: code simplify 深度审查与优化

**Files:**
- Review: `.claude/skills/task-flow/src/config/*.py`
- Review: `.claude/skills/task-flow/src/cli.py`

**Step 1: 调用 code-simplifier 进行审查**
- 聚焦：冗余逻辑、重复校验、命名一致性、无效代码路径。

**Step 2: 仅做等价简化**
- 不改变行为，不引入新功能。

**Step 3: 复测**
Run: `pytest .claude/skills/task-flow/tests -v`
Expected: PASS

---

### Task 7: 验证与交付

**Files:**
- Review: `docs/plans/2026-02-04-task-flow-auto-template-integration.md`

**Step 1: 汇总迁入清单**
- 列出新增文件、修改文件与测试结果。

**Step 2: 关闭任务**
- 准备交付说明与后续建议。