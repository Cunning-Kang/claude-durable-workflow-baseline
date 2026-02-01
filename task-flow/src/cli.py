"""Task-flow CLI"""

import sys
import argparse
import subprocess
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from task_manager import TaskManager
from execution_engine import ExecutionEngine, StateTracker
from plan_generator.types import ExecutionPlan, Task, TaskStatus


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


def cmd_create_task(args):
    """创建新任务"""
    project_root = _get_project_root_from_args(args)
    tm = get_task_manager(project_root)
    task_id = tm.create_task(args.title)

    print(f"✓ Created task: {task_id}")
    print(f"  File: docs/tasks/{task_id}-{tm._slugify(args.title)}.md")
    print(f"\nNext steps:")
    print(f"  1. Edit the task file to fill in the Plan Packet")
    print(f"  2. Run: start-task {task_id}")


def cmd_list_tasks(args):
    """列出任务"""
    project_root = _get_project_root_from_args(args)
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
    tm = get_task_manager(project_root)
    task = tm.get_task(args.task_id)

    if not task:
        print(f"Error: Task {args.task_id} not found", file=sys.stderr)
        sys.exit(1)

    # 从任务文件中提取分支名，如果没有则从标题生成
    import re
    branch_match = re.search(r'branch:\s*(\S+)', task['content'])
    if branch_match:
        branch_name = branch_match.group(1)
        if branch_name == 'null':
            branch_name = None
    else:
        branch_name = None

    if not branch_name:
        # 从标题生成分支名
        branch_name = tm._slugify(task['title'])

    worktree_path = f".worktrees/{branch_name}"

    # 检查 worktree 是否已存在
    worktree_full = Path(worktree_path)
    if worktree_full.exists():
        print(f"✓ Worktree already exists: {worktree_path}")
        print(f"  Switching to existing worktree...")
    else:
        # 创建 worktree
        print(f"Creating worktree: {worktree_path}")
        try:
            result = subprocess.run(
                ["git", "worktree", "add", worktree_path, "-b", branch_name],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✓ Created worktree: {worktree_path}")
            print(f"✓ Created branch: {branch_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error creating worktree: {e.stderr}", file=sys.stderr)
            sys.exit(1)

    # 更新任务状态
    tm.update_task(
        args.task_id,
        status="In Progress",
        worktree=worktree_path,
        branch=branch_name
    )

    print(f"\n✓ Task {args.task_id} is now In Progress")
    print(f"\nNext steps:")
    print(f"  1. cd {worktree_path}")
    print(f"  2. Review the Execution Order in the task file")
    print(f"  3. Start implementing!")


def cmd_update_task(args):
    """更新任务"""
    project_root = _get_project_root_from_args(args)
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


def _load_frontmatter(task_file: Path) -> Dict[str, Any]:
    content = task_file.read_text()
    parts = content.split("---")
    if len(parts) < 3:
        return {}
    yaml_content = parts[1].strip()
    return yaml.safe_load(yaml_content) or {}


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
    tm = get_task_manager(project_root)
    task = tm.get_task(args.task_id)

    if not task:
        print(f"Error: Task {args.task_id} not found", file=sys.stderr)
        sys.exit(1)

    task_file = Path(task["file"])
    frontmatter = _load_frontmatter(task_file)
    plan_file_value = frontmatter.get("plan_file")
    if not plan_file_value:
        print("Error: plan_file is required for execute-next-batch", file=sys.stderr)
        sys.exit(1)

    plan_path = Path(plan_file_value)
    if not plan_path.is_absolute():
        plan_path = find_project_root() / plan_path

    plan_data = _load_plan_file(plan_path)
    plan = _build_execution_plan(plan_data)

    execution_config = frontmatter.get("execution_config", {}) or {}
    batch_size = execution_config.get("batch_size")
    auto_continue = execution_config.get("auto_continue")
    checkpoint_interval = execution_config.get("checkpoint_interval")

    engine = ExecutionEngine(plan, task_file.parent)
    if batch_size is not None:
        engine.controller.batch_size = batch_size
    if auto_continue is not None:
        engine.controller.auto_continue = auto_continue
    if checkpoint_interval is not None:
        engine.controller.checkpoint_interval = checkpoint_interval

    stats = engine.execute_next_batch()
    print(json.dumps(stats))


def cmd_complete_task(args):
    """完成任务"""
    project_root = _get_project_root_from_args(args)
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



def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="task-flow - Task management system")
    parser.add_argument(
        "--project-root",
        help="Explicit project root (overrides TASK_FLOW_PROJECT_ROOT)",
        default=None,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

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
        help="Execute next batch of ready tasks"
    )
    parser_execute.add_argument("task_id", help="Task ID (e.g., TASK-001)")

    # complete-task
    parser_complete = subparsers.add_parser("complete-task", help="Mark task as complete and archive")
    parser_complete.add_argument("task_id", help="Task ID (e.g., TASK-001)")
    parser_complete.add_argument("--no-cleanup", action="store_true", help="Skip worktree cleanup prompt")

    args = parser.parse_args()

    if args.command == "create-task":
        cmd_create_task(args)
    elif args.command == "list-tasks":
        cmd_list_tasks(args)
    elif args.command == "show-task":
        cmd_show_task(args)
    elif args.command == "start-task":
        cmd_start_task(args)
    elif args.command == "update-task":
        cmd_update_task(args)
    elif args.command == "execute-next-batch":
        cmd_execute_next_batch(args)
    elif args.command == "complete-task":
        cmd_complete_task(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
