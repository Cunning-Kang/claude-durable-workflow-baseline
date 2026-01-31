"""Task-flow CLI"""

import sys
import argparse
import subprocess
from pathlib import Path
from task_manager import TaskManager


def find_project_root() -> Path:
    """查找项目根目录（包含 docs/tasks/ 的地方）"""
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


def get_task_manager():
    """获取 TaskManager 实例"""
    project_root = find_project_root()
    tasks_dir = project_root / "docs" / "tasks"
    index_file = project_root / "docs" / "_index.json"

    return TaskManager(tasks_dir=tasks_dir, index_file=index_file)


def cmd_create_task(args):
    """创建新任务"""
    tm = get_task_manager()
    task_id = tm.create_task(args.title)

    print(f"✓ Created task: {task_id}")
    print(f"  File: docs/tasks/{task_id}-{tm._slugify(args.title)}.md")
    print(f"\nNext steps:")
    print(f"  1. Edit the task file to fill in the Plan Packet")
    print(f"  2. Run: start-task {task_id}")


def cmd_list_tasks(args):
    """列出任务"""
    tm = get_task_manager()
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
    tm = get_task_manager()
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
    tm = get_task_manager()
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



def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="task-flow - Task management system")
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

    args = parser.parse_args()

    if args.command == "create-task":
        cmd_create_task(args)
    elif args.command == "list-tasks":
        cmd_list_tasks(args)
    elif args.command == "show-task":
        cmd_show_task(args)
    elif args.command == "start-task":
        cmd_start_task(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
