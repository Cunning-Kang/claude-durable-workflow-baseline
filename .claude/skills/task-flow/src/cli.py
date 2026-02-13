"""Task-flow CLI"""

import sys
import argparse
import subprocess
import json
import os
import re
import fcntl
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from task_manager import TaskManager
from execution_engine import ExecutionEngine, StateTracker
from plan_generator import ExecutionPlan, Task, TaskStatus
from todowrite_compat.tool import TodoWriteCompat
from ci_detector import resolve_quality_gate_command
from config import ConfigManager


def _resolve_project_root(value: Optional[str]) -> Optional[Path]:
    if not value:
        return None
    root = Path(value)
    return root.resolve()


def find_project_root(override: Optional[Path] = None) -> Path:
    """查找项目根目录（包含 docs/tasks/ 的地方）"""
    if override is not None:
        tasks_dir = override / "docs" / "tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)
        return override

    current = Path.cwd()

    for parent in [current] + list(current.parents):
        if (parent / ConfigManager.INIT_MARKER).exists():
            tasks_dir = parent / "docs" / "tasks"
            tasks_dir.mkdir(parents=True, exist_ok=True)
            return parent

    # 向上查找直到找到 docs/tasks/ 或到达根目录
    for parent in [current] + list(current.parents):
        tasks_dir = parent / "docs" / "tasks"
        if tasks_dir.exists():
            return parent

    # 如果没找到，使用当前目录并创建
    tasks_dir = Path.cwd() / "docs" / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    return Path.cwd()


def get_task_manager(project_root: Optional[Path] = None):
    """获取 TaskManager 实例"""
    resolved_root = find_project_root(project_root)
    tasks_dir = resolved_root / "docs" / "tasks"
    index_file = resolved_root / "docs" / "_index.json"

    return TaskManager(tasks_dir=tasks_dir, index_file=index_file)


def _get_project_root_from_args(args) -> Optional[Path]:
    env_root = os.environ.get("TASK_FLOW_PROJECT_ROOT")
    env_path = _resolve_project_root(env_root)
    arg_path = _resolve_project_root(getattr(args, "project_root", None))
    return arg_path or env_path


def _docs_has_uncommitted_changes(repo_root: Path) -> bool:
    """Check if docs directory has uncommitted changes using git status --porcelain."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "docs"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False


DOCS_ONLY_COMMIT_MESSAGE = "docs: update workflow artifacts"
ALL_CHANGES_COMMIT_MESSAGE = "chore: checkpoint before start-task"
WORKFLOW_CONVENTIONS_BEGIN = "<!-- BEGIN: WORKFLOW_CONVENTIONS -->"
WORKFLOW_CONVENTIONS_END = "<!-- END: WORKFLOW_CONVENTIONS -->"
PLAN_ROUTER_BEGIN = "<!-- BEGIN: TASK_FLOW_PLAN_ROUTER -->"
PLAN_ROUTER_END = "<!-- END: TASK_FLOW_PLAN_ROUTER -->"


def _run_git(repo_root: Path, args: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )


def _normalize_repo_path(path: str) -> str:
    normalized = path.strip().replace("\\", "/")
    if normalized.startswith('"') and normalized.endswith('"'):
        normalized = normalized[1:-1]
    return normalized


def _is_docs_scope_path(path: str) -> bool:
    normalized = _normalize_repo_path(path)
    if not normalized:
        return False
    if normalized.startswith("docs/"):
        return True
    if normalized in {"CLAUDE.md", "AGENTS.md"}:
        return True
    if normalized.startswith(".claude/") and (normalized.endswith(".md") or normalized.endswith(".mdx")):
        return True
    if normalized.endswith(".md") or normalized.endswith(".mdx"):
        return True
    return False


def _collect_git_changes(repo_root: Path) -> Dict[str, Any]:
    result = _run_git(repo_root, ["status", "--porcelain"])
    if result.returncode != 0:
        return {
            "ok": False,
            "error": result.stderr.strip() or result.stdout.strip(),
            "docs_files": [],
            "code_files": [],
            "docs_staged": [],
            "docs_unstaged": [],
            "code_staged": [],
            "code_unstaged": [],
            "all_files": [],
        }

    docs_staged: set[str] = set()
    docs_unstaged: set[str] = set()
    code_staged: set[str] = set()
    code_unstaged: set[str] = set()

    for raw_line in result.stdout.splitlines():
        if len(raw_line) < 3:
            continue
        status = raw_line[:2]
        raw_path = raw_line[3:]
        path = raw_path.split(" -> ", 1)[1] if " -> " in raw_path else raw_path
        path = _normalize_repo_path(path)
        if not path:
            continue

        is_docs = _is_docs_scope_path(path)

        if status == "??":
            if is_docs:
                docs_unstaged.add(path)
            else:
                code_unstaged.add(path)
            continue

        if status[0] != " ":
            if is_docs:
                docs_staged.add(path)
            else:
                code_staged.add(path)

        if status[1] != " ":
            if is_docs:
                docs_unstaged.add(path)
            else:
                code_unstaged.add(path)

    docs_files = sorted(docs_staged | docs_unstaged)
    code_files = sorted(code_staged | code_unstaged)

    return {
        "ok": True,
        "docs_files": docs_files,
        "code_files": code_files,
        "docs_staged": sorted(docs_staged),
        "docs_unstaged": sorted(docs_unstaged),
        "code_staged": sorted(code_staged),
        "code_unstaged": sorted(code_unstaged),
        "all_files": sorted(set(docs_files + code_files)),
    }


def _print_changes(label: str, files: List[str]) -> None:
    if not files:
        return
    print(f"  {label}:")
    for file in files:
        print(f"    - {file}")


def _write_if_changed(file_path: Path, content: str) -> bool:
    if file_path.exists() and file_path.read_text() == content:
        return False
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return True


def _upsert_marked_block(file_path: Path, begin_marker: str, end_marker: str, block_content: str) -> bool:
    block = f"{begin_marker}\n{block_content.rstrip()}\n{end_marker}"
    current = file_path.read_text() if file_path.exists() else ""

    if begin_marker in current and end_marker in current:
        pattern = re.compile(
            re.escape(begin_marker) + r"[\s\S]*?" + re.escape(end_marker),
            re.MULTILINE,
        )
        updated = pattern.sub(block, current, count=1)
    else:
        if current.strip():
            updated = current.rstrip() + "\n\n" + block + "\n"
        else:
            updated = block + "\n"

    return _write_if_changed(file_path, updated)


def _commit_paths(repo_root: Path, files: List[str], message: str, commit_only_paths: Optional[List[str]] = None) -> bool:
    if not files:
        return True

    add_result = _run_git(repo_root, ["add", "--", *files])
    if add_result.returncode != 0:
        print(f"Error: git add 失败: {add_result.stderr.strip()}", file=sys.stderr)
        return False

    commit_args = ["commit", "-m", message]
    if commit_only_paths:
        commit_args.extend(["--", *commit_only_paths])

    commit_result = _run_git(repo_root, commit_args)
    if commit_result.returncode != 0:
        combined = f"{commit_result.stdout}\n{commit_result.stderr}".lower()
        if "nothing to commit" in combined:
            return True
        print(f"Error: git commit 失败: {commit_result.stderr.strip()}", file=sys.stderr)
        return False

    summary = commit_result.stdout.strip().splitlines()
    if summary:
        print(summary[0])
    return True


def _resolve_docs_gate_choice(has_code_changes: bool) -> Optional[str]:
    if os.environ.get("TASK_FLOW_DOCS_GATE_SKIP") == "1":
        return "y" if not has_code_changes else "1"

    env_choice = os.environ.get("TASK_FLOW_DOCS_GATE_CHOICE", "").strip().lower()

    if has_code_changes:
        env_map = {
            "1": "1",
            "docs-only": "1",
            "docs": "1",
            "2": "2",
            "all": "2",
            "3": "3",
            "cancel": "3",
            "n": "3",
            "no": "3",
        }
        if env_choice in env_map:
            return env_map[env_choice]

        if not sys.stdin.isatty():
            return None

        while True:
            choice = input("请选择 [1/2/3] (默认 1): ").strip() or "1"
            if choice in {"1", "2", "3"}:
                return choice
            print("无效输入，请输入 1、2 或 3。")

    env_map = {
        "y": "y",
        "yes": "y",
        "docs-only": "y",
        "docs": "y",
        "n": "n",
        "no": "n",
        "cancel": "n",
    }
    if env_choice in env_map:
        return env_map[env_choice]

    if not sys.stdin.isatty():
        return None

    while True:
        choice = input("继续(Y) / 取消(N): ").strip().lower() or "y"
        if choice in {"y", "yes", "n", "no"}:
            return "y" if choice in {"y", "yes"} else "n"
        print("无效输入，请输入 Y 或 N。")


def _run_docs_gate(repo_root: Path) -> bool:
    if os.environ.get("TASK_FLOW_DOCS_GATE_SKIP") == "1":
        return True

    changes = _collect_git_changes(repo_root)
    if not changes["ok"]:
        print(f"Warning: 无法检查 git 状态，跳过 docs gate: {changes['error']}", file=sys.stderr)
        return True

    docs_files = changes["docs_files"]
    if not docs_files:
        return True

    print("⚠️  检测到 docs 范围存在未提交变更。")
    _print_changes("docs staged", changes["docs_staged"])
    _print_changes("docs unstaged", changes["docs_unstaged"])

    has_code_changes = bool(changes["code_files"])
    if has_code_changes:
        _print_changes("code staged", changes["code_staged"])
        _print_changes("code unstaged", changes["code_unstaged"])
        print("\n检测到 docs 与 code 混改，请选择：")
        print("  [1] 只提交 docs（默认更安全，仍需确认）")
        print("  [2] 全部提交（必须明确确认）")
        print("  [3] 取消并退出")

    choice = _resolve_docs_gate_choice(has_code_changes=has_code_changes)
    if choice is None:
        print(
            "Error: docs gate 需要交互确认。"
            "请在交互终端运行，或设置 TASK_FLOW_DOCS_GATE_CHOICE=docs-only|all|cancel。",
            file=sys.stderr,
        )
        return False

    if not has_code_changes:
        if choice != "y":
            print("已取消 start-task。")
            return False
        print("正在提交 docs 变更...")
        return _commit_paths(
            repo_root,
            files=docs_files,
            message=DOCS_ONLY_COMMIT_MESSAGE,
            commit_only_paths=docs_files,
        )

    if choice == "3":
        print("已取消 start-task。")
        return False

    if choice == "1":
        if sys.stdin.isatty() and not os.environ.get("TASK_FLOW_DOCS_GATE_CHOICE"):
            confirm = input("确认仅提交 docs 变更并继续？[Y/n]: ").strip().lower() or "y"
            if confirm not in {"y", "yes"}:
                print("已取消 start-task。")
                return False
        print("正在提交 docs 变更...")
        return _commit_paths(
            repo_root,
            files=docs_files,
            message=DOCS_ONLY_COMMIT_MESSAGE,
            commit_only_paths=docs_files,
        )

    if sys.stdin.isatty() and not os.environ.get("TASK_FLOW_DOCS_GATE_CHOICE"):
        explicit = input("输入 YES 以确认提交全部变更并继续: ").strip()
        if explicit != "YES":
            print("未确认，已取消 start-task。")
            return False

    print("正在提交全部变更...")
    return _commit_paths(
        repo_root,
        files=changes["all_files"],
        message=ALL_CHANGES_COMMIT_MESSAGE,
        commit_only_paths=None,
    )


def _resolve_task_relative_path(task_file: Path, repo_root: Path) -> str:
    try:
        return str(task_file.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(task_file).replace("\\", "/")


def _resolve_plan_path(frontmatter: Dict[str, Any], repo_root: Path) -> str:
    plan_file_value = frontmatter.get("plan_file")
    if plan_file_value and str(plan_file_value).lower() != "null":
        plan_path = Path(str(plan_file_value))
        if not plan_path.is_absolute():
            plan_path = repo_root / plan_path
        if plan_path.exists():
            try:
                return str(plan_path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
            except ValueError:
                return str(plan_path).replace("\\", "/")

    plans_dir = repo_root / "docs" / "plans"
    if not plans_dir.exists():
        return "NOT GENERATED YET"

    candidates = [
        path for path in plans_dir.glob("*.md")
        if re.match(r"^\d{4}-\d{2}-\d{2}-.+\.md$", path.name)
    ]
    if not candidates:
        return "NOT GENERATED YET"

    latest_plan = max(candidates, key=lambda path: path.stat().st_mtime)
    return str(latest_plan.relative_to(repo_root)).replace("\\", "/")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)


def _load_json_or_default(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return default


def _append_event(
    worktree_root: Path,
    task_id: str,
    event_type: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    task_flow_dir = worktree_root / ".task-flow"
    task_flow_dir.mkdir(parents=True, exist_ok=True)

    events_file = task_flow_dir / "events.jsonl"
    lock_file = task_flow_dir / "events.lock"
    lock_file.touch(exist_ok=True)

    with open(lock_file, "r+", encoding="utf-8") as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        try:
            last_seq = 0
            if events_file.exists():
                lines = [line for line in events_file.read_text(encoding="utf-8").splitlines() if line.strip()]
                if lines:
                    try:
                        last_seq = int(json.loads(lines[-1]).get("seq", 0))
                    except (ValueError, json.JSONDecodeError, TypeError):
                        last_seq = 0

            event = {
                "seq": last_seq + 1,
                "ts": _utc_now_iso(),
                "task_id": task_id,
                "type": event_type,
                "actor": "task-flow",
                "data": data,
            }

            with open(events_file, "a", encoding="utf-8") as events_handle:
                events_handle.write(json.dumps(event, ensure_ascii=False) + "\n")
                events_handle.flush()
                os.fsync(events_handle.fileno())

            return event
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def _upsert_active_registry(
    repo_root: Path,
    task_id: str,
    task_path: str,
    plan_path: str,
    branch_name: str,
    worktree_path: str,
    status: str,
    started_at: str,
    last_event_seq: int,
) -> None:
    active_path = repo_root / "docs" / "tasks" / "_active.json"
    lock_path = repo_root / "docs" / "tasks" / "_active.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.touch(exist_ok=True)

    with open(lock_path, "r+", encoding="utf-8") as lock_handle:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        try:
            active = _load_json_or_default(active_path, {
                "version": 1,
                "updated_at": _utc_now_iso(),
                "tasks": {},
            })

            if not isinstance(active, dict):
                active = {"version": 1, "updated_at": _utc_now_iso(), "tasks": {}}

            tasks = active.get("tasks")
            if not isinstance(tasks, dict):
                tasks = {}
                active["tasks"] = tasks

            existing_started_at = None
            if task_id in tasks and isinstance(tasks[task_id], dict):
                existing_started_at = tasks[task_id].get("started_at")

            tasks[task_id] = {
                "task_file": task_path,
                "plan_file": plan_path,
                "branch": branch_name,
                "worktree": worktree_path,
                "status": status,
                "started_at": existing_started_at or started_at,
                "last_event_seq": last_event_seq,
            }

            active["version"] = 1
            active["updated_at"] = _utc_now_iso()

            _atomic_write_json(active_path, active)
        finally:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def _workflow_conventions_content() -> str:
    return "\n".join([
        "# Workflow Conventions",
        "",
        "## 1) Canonical Source of Truth",
        "- 长期协作事实源仅为 `docs/tasks/` 与 `docs/plans/`。",
        "- `docs/plans/` 使用 `YYYY-MM-DD-*.md` 命名。",
        "- 活跃任务机器状态维护在 `docs/tasks/_active.json`（注册表，不替代 canonical docs）。",
        "- worktree 过程事件写入 `.worktrees/<branch>/.task-flow/events.jsonl`（append-only）。",
        "",
        "## 2) Worktree 目录规则",
        "- 统一使用 `.worktrees/` 存放工作树。",
        "- 必须通过 `git check-ignore -q .worktrees` 校验忽略规则。",
        "- 若不通过：更新 `.gitignore` 增加 `.worktrees/`，并提交该修复后再继续。",
        "",
        "## 3) Docs Gate（启动前守门）",
        "- start-task 前检查 docs 范围 staged/unstaged 变更。",
        "- 若仅 docs 变更：询问继续(Y)/取消(N)，选择继续则自动提交 docs。",
        "- 若 docs + code 混改：提供 [1]仅 docs、[2]全部提交、[3]取消。",
        "- docs-only 提交消息固定：`docs: update workflow artifacts`。",
        "",
        "## 4) Active Registry / Events 规则",
        "- start-task 必须更新 `docs/tasks/_active.json` 中对应任务条目。",
        "- start-task 必须向 `.task-flow/events.jsonl` 追加 `task_started` 事件。",
        "- `_active.json` 使用锁文件与原子替换写入；`events.jsonl` 使用追加锁保证 `seq` 单调递增。",
        "",
        "## 5) PLAN.md 固定入口",
        "- 根目录 `PLAN.md` 维护当前活跃任务路由。",
        "- 至少包含：任务、docs 路径、worktree 路径、`_active.json`、`events.jsonl`。",
        "",
        "## 6) 回滚与清理",
        "- 删除工作树：`git worktree remove .worktrees/<branch>`",
        "- 删除分支：`git branch -D <branch>`",
        "- 清理残留：`git worktree prune`",
        "",
    ])


def _ensure_workflow_conventions(repo_root: Path) -> None:
    conventions_content = _workflow_conventions_content()

    conventions_file = repo_root / "docs" / "workflow" / "CONVENTIONS.md"
    _write_if_changed(conventions_file, conventions_content)

    claude_file = repo_root / "CLAUDE.md"
    agents_file = repo_root / "AGENTS.md"

    if claude_file.exists():
        target_file = claude_file
    elif agents_file.exists():
        target_file = agents_file
    else:
        target_file = claude_file

    block_content = "\n".join([
        "## Workflow Conventions",
        "- Canonical: `docs/tasks/` + `docs/plans/`；机器状态入口为 `docs/tasks/_active.json`。",
        "- worktree 固定目录 `.worktrees/`，并通过 `git check-ignore -q .worktrees` 校验。",
        "- docs gate：检测 docs 未提交变更，按规则确认并提交。",
        "- 事件日志：`.worktrees/<branch>/.task-flow/events.jsonl`（append-only）。",
        "- 固定入口：根目录 `PLAN.md`。",
        "- 详细规范：`docs/workflow/CONVENTIONS.md`。",
    ])

    _upsert_marked_block(
        target_file,
        WORKFLOW_CONVENTIONS_BEGIN,
        WORKFLOW_CONVENTIONS_END,
        block_content,
    )


def _update_plan_router(
    repo_root: Path,
    task_id: str,
    task_title: str,
    task_path: str,
    plan_path: str,
    worktree_path: str,
) -> None:
    plan_file = repo_root / "PLAN.md"
    block_content = "\n".join([
        "## Active Task",
        f"- ID: `{task_id}`",
        f"- Title: `{task_title}`",
        "",
        "## Links",
        f"- Task: `{task_path}`",
        f"- Plan: `{plan_path}`",
        "",
        "## Worktree",
        f"- `{worktree_path}`",
        "",
        "## Machine-readable State",
        "- Active Registry: `docs/tasks/_active.json`",
        f"- Events: `{worktree_path}/.task-flow/events.jsonl`",
    ])

    _upsert_marked_block(
        plan_file,
        PLAN_ROUTER_BEGIN,
        PLAN_ROUTER_END,
        block_content,
    )


def _check_initialization(project_root: Optional[Path]) -> bool:
    if os.environ.get("TASK_FLOW_SKIP_INIT") == "1":
        return True
    if project_root is None:
        project_root = find_project_root()
    if ConfigManager.is_initialized(project_root):
        return True
    if ConfigManager.is_ci_environment():
        print("⚠️  CI 环境：跳过初始化提示")
        print("   请预先运行: task-flow init")
        return False

    manager = ConfigManager(project_root)
    if not sys.stdin.isatty():
        result = manager.initialize(interactive=False)
        if not result.success:
            print(result.message, file=sys.stderr)
            return False
        return True

    print("╔══════════════════════════════════════════╗")
    print("║  检测到项目尚未初始化 task-flow 工作流   ║")
    print("║                                           ║")
    print("║  [回车] 自动初始化（推荐）               ║")
    print("║  [Ctrl+C] 取消                           ║")
    print("╚══════════════════════════════════════════╝")
    try:
        input()
        result = manager.initialize(interactive=False)
        if not result.success:
            print(result.message, file=sys.stderr)
            return False
        return True
    except (KeyboardInterrupt, EOFError):
        print("\n⚠️  已跳过初始化")
        print("   稍后可运行: task-flow init")
        return False


def cmd_init(args):
    """初始化项目配置"""
    project_root = _get_project_root_from_args(args) or Path.cwd()
    manager = ConfigManager(project_root)
    if manager.is_initialized(project_root) and not args.force:
        existing_version = manager.detect_existing_version()
        if existing_version:
            print(f"✓ 项目已初始化 (v{existing_version})")
        else:
            print("✓ 项目已初始化")
        print("  使用 --force 强制重新初始化")
        return
    result = manager.initialize(
        template_type=args.template or "standard",
        force=args.force,
        interactive=not args.yes,
        backup=not args.no_backup,
    )
    if result.success:
        print(result.message)
        return
    print(result.message, file=sys.stderr)
    sys.exit(1)


def cmd_create_task(args):
    """创建新任务"""
    project_root = _get_project_root_from_args(args)
    if not _check_initialization(project_root):
        return
    tm = get_task_manager(project_root)
    task_id = tm.create_task(args.title)
    slug = tm._slugify(args.title)
    if not slug:
        slug = task_id.lower()

    print(f"✓ Created task: {task_id}")
    print(f"  File: docs/tasks/{task_id}-{slug}.md")
    print(f"\nNext steps:")
    print(f"  1. Edit the task file to fill in the Plan Packet")
    print(f"  2. Run: start-task {task_id}")


def cmd_list_tasks(args):
    """列出任务"""
    project_root = _get_project_root_from_args(args)
    if not _check_initialization(project_root):
        return
    tm = get_task_manager(project_root)
    tasks = tm.list_tasks(status=args.status)

    if not tasks:
        print("No tasks found.")
        return

    print(f"Found {len(tasks)} task(s):\n")
    for task in tasks:
        status_icon = {"To Do": "⏳", "In Progress": "🔄", "Done": "✅"}.get(task["status"], "❓")
        print(f"{status_icon} {task['id']}: {task['title']}")
        print(f"   Status: {task['status']}")
        print()


def cmd_show_task(args):
    """显示任务详情"""
    project_root = _get_project_root_from_args(args)
    if not _check_initialization(project_root):
        return
    tm = get_task_manager(project_root)
    task = tm.get_task(args.task_id)

    if not task:
        print(f"Error: Task {args.task_id} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Task: {task['id']}")
    print(f"Title: {task['title']}")
    print(f"Status: {task['status']}")
    print(f"\n{task['content']}")


def cmd_start_task(args):
    """启动任务（创建/切换 worktree）"""
    project_root = _get_project_root_from_args(args)
    if not _check_initialization(project_root):
        return

    resolved_root = project_root or find_project_root()

    tm = get_task_manager(project_root)
    task = tm.get_task(args.task_id)

    if not task:
        print(f"Error: Task {args.task_id} not found", file=sys.stderr)
        sys.exit(1)

    if not _run_docs_gate(resolved_root):
        print("Error: docs gate 未通过，已停止 start-task。", file=sys.stderr)
        sys.exit(1)

    # Load frontmatter to get branch name
    task_file = Path(task["file"])
    frontmatter = tm._load_frontmatter(task_file)

    # Get branch from frontmatter, fallback to slugified title
    branch_name = frontmatter.get("branch")
    if not branch_name or branch_name == "null":
        branch_name = tm._slugify(task['title'])
    if not branch_name:
        branch_name = args.task_id.lower()

    worktree_path = f".worktrees/{branch_name}"
    worktree_full = resolved_root / worktree_path

    # Check if worktree already exists
    if worktree_full.exists():
        print(f"✓ Worktree already exists: {worktree_path}")
        print("  Switching to existing worktree...")
    else:
        # Create worktree
        print(f"Creating worktree: {worktree_path}")
        try:
            subprocess.run(
                ["git", "worktree", "add", worktree_path, "-b", branch_name],
                cwd=resolved_root,
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"✓ Created worktree: {worktree_path}")
            print(f"✓ Created branch: {branch_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating worktree: {e.stderr}", file=sys.stderr)
            sys.exit(1)

    # verify-only: never copy docs into worktree
    worktree_docs = worktree_full / "docs"
    if not worktree_docs.exists():
        print(
            f"Error: worktree 缺少 docs 目录（{worktree_docs}）。"
            "已停止，避免复制 docs 造成双事实源。",
            file=sys.stderr,
        )
        sys.exit(1)

    task_path = _resolve_task_relative_path(task_file, resolved_root)
    plan_path = _resolve_plan_path(frontmatter, resolved_root)

    event = _append_event(
        worktree_root=worktree_full,
        task_id=args.task_id,
        event_type="task_started",
        data={
            "branch": branch_name,
            "worktree": worktree_path,
        },
    )

    _upsert_active_registry(
        repo_root=resolved_root,
        task_id=args.task_id,
        task_path=task_path,
        plan_path=plan_path,
        branch_name=branch_name,
        worktree_path=worktree_path,
        status="In Progress",
        started_at=event["ts"],
        last_event_seq=event["seq"],
    )

    _ensure_workflow_conventions(resolved_root)
    _update_plan_router(
        repo_root=resolved_root,
        task_id=args.task_id,
        task_title=task["title"],
        task_path=task_path,
        plan_path=plan_path,
        worktree_path=worktree_path,
    )

    # Update task status
    tm.update_task(
        args.task_id,
        status="In Progress",
        worktree=worktree_path,
        branch=branch_name,
    )

    print(f"\n✓ Task {args.task_id} is now In Progress")
    print("\nNext steps:")
    print(f"  1. cd {worktree_path}")
    print("  2. 检查 docs/tasks/_active.json 活跃任务注册")
    print(f"  3. 查看 {worktree_path}/.task-flow/events.jsonl 事件流")


def cmd_update_task(args):
    """更新任务"""
    project_root = _get_project_root_from_args(args)
    if not _check_initialization(project_root):
        return
    tm = get_task_manager(project_root)
    task = tm.get_task(args.task_id)

    if not task:
        print(f"Error: Task {args.task_id} not found", file=sys.stderr)
        sys.exit(1)

    # 更新字段
    updates = {}
    if args.status:
        updates["status"] = args.status
    if args.step is not None:
        updates["current_step"] = args.step

    if updates:
        tm.update_task(args.task_id, **updates)
        print(f"✓ Updated task {args.task_id}")

    # 添加备注
    if args.note:
        tm.add_task_note(args.task_id, args.note)
        print(f"✓ Added note to task {args.task_id}")


def _parse_markdown_plan(content: str) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []
    current_task: Dict[str, Any] | None = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if line.startswith("### Task "):
            if current_task:
                if not current_task.get("description"):
                    current_task["description"] = current_task.get("title", "")
                tasks.append(current_task)
            title = line.split(":", 1)[1].strip() if ":" in line else line[len("### Task "):].strip()
            current_task = {
                "id": f"TASK-{len(tasks) + 1:03d}",
                "title": title,
                "description": "",
            }
            continue
        if current_task and line.startswith("**Description:**"):
            current_task["description"] = line.split("**Description:**", 1)[1].strip()

    if current_task:
        if not current_task.get("description"):
            current_task["description"] = current_task.get("title", "")
        tasks.append(current_task)

    return tasks


def _build_execution_plan(plan_data: Dict[str, Any]) -> ExecutionPlan:
    tasks_data = plan_data.get("tasks", [])
    tasks: List[Task] = []
    for task in tasks_data:
        task_status = TaskStatus.PENDING
        if "status" in task:
            try:
                task_status = TaskStatus(task["status"])
            except ValueError:
                task_status = TaskStatus.PENDING
        tasks.append(
            Task(
                id=task["id"],
                title=task.get("title", ""),
                description=task.get("description", ""),
                status=task_status,
                dependencies=task.get("dependencies", []) or [],
                metadata=task.get("metadata", {}) or {},
            )
        )
    return ExecutionPlan(tasks=tasks, metadata=plan_data.get("metadata", {}) or {})


def _load_plan_file(plan_path: Path) -> Dict[str, Any]:
    if not plan_path.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_path}")
    content = plan_path.read_text()
    try:
        data = yaml.safe_load(content) or {}
    except yaml.YAMLError:
        data = {}
    if isinstance(data, dict) and data.get("tasks"):
        return data
    markdown_tasks = _parse_markdown_plan(content)
    if markdown_tasks:
        return {"tasks": markdown_tasks}
    raise ValueError("Unsupported plan format: missing tasks in YAML and Markdown")


def cmd_execute_next_batch(args):
    """执行下一批 ready tasks"""
    project_root = _get_project_root_from_args(args)
    if not _check_initialization(project_root):
        return
    tm = get_task_manager(project_root)
    task = tm.get_task(args.task_id)

    if not task:
        print(f"Error: Task {args.task_id} not found", file=sys.stderr)
        sys.exit(1)

    # Set task status to "In Progress" when execution starts
    tm.update_task(args.task_id, status="In Progress")

    task_file = Path(task["file"])
    frontmatter = tm._load_frontmatter(task_file)
    plan_file_value = frontmatter.get("plan_file")
    if not plan_file_value or str(plan_file_value).lower() == "null":
        print("Error: plan_file is required for execute-next-batch", file=sys.stderr)
        tm.update_task(args.task_id, status="Blocked")
        sys.exit(1)

    plan_path = Path(plan_file_value)
    if not plan_path.is_absolute():
        plan_path = find_project_root() / plan_path

    try:
        plan_data = _load_plan_file(plan_path)
        plan = _build_execution_plan(plan_data)
    except Exception as e:
        tm.update_task(args.task_id, status="Blocked")
        print(f"Error: Failed to load plan: {e}", file=sys.stderr)
        sys.exit(1)

    execution_config = frontmatter.get("execution_config", {}) or {}

    def step_callback(step_number: int):
        tm.update_task_step(args.task_id, step_number)

    engine = ExecutionEngine(plan, task_file.parent, step_callback=step_callback)

    # Apply configuration settings if provided
    for attr_name, value in [
        ('batch_size', execution_config.get('batch_size')),
        ('auto_continue', execution_config.get('auto_continue')),
        ('checkpoint_interval', execution_config.get('checkpoint_interval'))
    ]:
        if value is not None:
            setattr(engine.controller, attr_name, value)

    try:
        stats = engine.execute_next_batch()
    except Exception as e:
        tm.update_task(args.task_id, status="Blocked")
        print(f"Error: Execution failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Resolve quality gate command (used elsewhere, not executed here)
    resolve_quality_gate_command(task_file.parent, frontmatter)

    if stats.get("errors"):
        tm.update_task(args.task_id, status="Blocked")
        print(json.dumps(stats))
        print(f"Error: {stats['errors'][0]}", file=sys.stderr)
        sys.exit(1)
    else:
        tm.update_task(args.task_id, status="Done")

    print(json.dumps(stats))


def cmd_complete_task(args):
    """完成任务"""
    project_root = _get_project_root_from_args(args)
    if not _check_initialization(project_root):
        return
    tm = get_task_manager(project_root)
    task = tm.get_task(args.task_id)

    if not task:
        print(f"Error: Task {args.task_id} not found", file=sys.stderr)
        sys.exit(1)

    # 完成任务（标记为 Done 并归档）
    tm.complete_task(args.task_id)

    print(f"✓ Task {args.task_id} marked as Done")
    print(f"✓ Task file archived to docs/tasks/completed/")

    if not args.no_cleanup:
        print(f"\nNext steps:")
        print(f"  1. Review the work in the worktree")
        print(f"  2. Run tests to verify everything works")
        print(f"  3. Choose merge strategy:")
        print(f"     - Merge locally: git merge <branch>")
        print(f"     - Create PR: gh pr create")
        print(f"  4. Clean up worktree when done:")
        print(f"     git worktree remove .worktrees/<branch>")
    else:
        print(f"\nNote: Worktree cleanup skipped (--no-cleanup flag)")


def cmd_todowrite(args):
    """处理 TodoWrite 兼容性命令"""
    project_root = _get_project_root_from_args(args)

    # If project_root is None, use the current working directory
    if project_root is None:
        project_root = Path.cwd()

    # 初始化 TodoWrite 兼容工具
    bootstrap = os.environ.get("TASK_FLOW_BOOTSTRAP")
    compat_tool = TodoWriteCompat(project_root=project_root, bootstrap=bootstrap)

    # 读取输入 - 优先从文件读取，否则从 stdin 读取
    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)

    # 调用 TodoWrite 兼容工具写入
    result = compat_tool.write(input_data)

    # 输出结果为 JSON 格式
    print(json.dumps(result, ensure_ascii=False))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="task-flow - Task management system")
    parser.add_argument(
        "--project-root",
        help="Explicit project root (overrides TASK_FLOW_PROJECT_ROOT)",
        default=None,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    parser_init = subparsers.add_parser("init", help="Initialize project configuration")
    parser_init.add_argument("--template", "-t", choices=["minimal", "standard", "full"], default="standard")
    parser_init.add_argument("--force", "-f", action="store_true")
    parser_init.add_argument("--yes", "-y", action="store_true")
    parser_init.add_argument("--no-backup", action="store_true")

    # create-task
    parser_create = subparsers.add_parser("create-task", help="Create a new task")
    parser_create.add_argument("title", help="Task title")

    # list-tasks
    parser_list = subparsers.add_parser("list-tasks", help="List all tasks")
    parser_list.add_argument("--status", help="Filter by status")

    # show-task
    parser_show = subparsers.add_parser("show-task", help="Show task details")
    parser_show.add_argument("task_id", help="Task ID (e.g., TASK-001)")

    # start-task
    parser_start = subparsers.add_parser("start-task", help="Start working on a task")
    parser_start.add_argument("task_id", help="Task ID (e.g., TASK-001)")

    # update-task
    parser_update = subparsers.add_parser("update-task", help="Update task status or add notes")
    parser_update.add_argument("task_id", help="Task ID (e.g., TASK-001)")
    parser_update.add_argument("--status", help="Update status (e.g., 'In Progress', 'Done')")
    parser_update.add_argument("--step", type=int, help="Update current step number")
    parser_update.add_argument("--note", help="Add a note to the task")

    # execute-next-batch
    parser_execute = subparsers.add_parser(
        "execute-next-batch",
        aliases=["execute-plan"],  # Add execute-plan as an alias
        help="Execute next batch of ready tasks"
    )
    parser_execute.add_argument("task_id", help="Task ID (e.g., TASK-001)")

    # complete-task
    parser_complete = subparsers.add_parser("complete-task", help="Mark task as complete and archive")
    parser_complete.add_argument("task_id", help="Task ID (e.g., TASK-001)")
    parser_complete.add_argument("--no-cleanup", action="store_true", help="Skip worktree cleanup prompt")

    # todowrite
    parser_todowrite = subparsers.add_parser("todowrite", help="TodoWrite compatibility command")
    parser_todowrite.add_argument("--input-file", help="Input file containing JSON todos (reads from stdin if not provided)")

    args = parser.parse_args()

    # Command dispatch mapping
    command_map = {
        "init": cmd_init,
        "create-task": cmd_create_task,
        "list-tasks": cmd_list_tasks,
        "show-task": cmd_show_task,
        "start-task": cmd_start_task,
        "update-task": cmd_update_task,
        "execute-next-batch": cmd_execute_next_batch,
        "execute-plan": cmd_execute_next_batch,  # Alias for execute-next-batch
        "complete-task": cmd_complete_task,
        "todowrite": cmd_todowrite,
    }

    if args.command in command_map:
        command_map[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
