#!/usr/bin/env python3
"""
Plan Packet - 核心脚本 v2.2

变更内容：
1. CLAUDE.md 模板重构 - 符合用户要求的工作流总则
2. 深度集成 Backlog MCP 工作流
3. Plan Packet Notes 添加 planAppend 提示

Usage:
    python scripts/plan-packet.py init [--force-agents]
    python scripts/plan-packet.py add [--task TASK_ID]
    python scripts/plan-packet.py link [--branch BRANCH]
    python scripts/plan-packet.py show
    python scripts/plan-packet.py update
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# ============================================================
# 配置
# ============================================================

PLAN_PACKET_VERSION = "2.2"
VERSION_MARKER = f"<!-- PLAN_PACKET:v{PLAN_PACKET_VERSION} -->"
END_MARKER = "<!-- PLAN_PACKET:END -->"

# 工作流片段模板
WORKFLOW_FRAGMENT = """
## 工作流总则

**任务事实源**：Backlog.md + Plan Packet

**读取任务流程**：优先通过 MCP 资源 `backlog://workflow/overview`

**每次实现必须**：
- 严格按 Plan Packet 执行；发现偏离先回写 Plan Packet
- push/PR 前执行 `./scripts/ci-local.sh`

---

## 具体步骤

### 1) 读取任务
- 读取 Backlog 任务文件（如 `backlog/tasks/task-<id> - <title>.md`）
- 参考 MCP 资源：
  - `backlog://workflow/task-execution` - 执行指南
  - `backlog://workflow/task-finalization` - 完成指南

### 2) 执行与回写
- 按 Plan Packet 完成实现
- 发现偏离时，使用 `task_edit` 的 `planAppend` 字段记录变更
- 更新 Backlog 任务状态

### 3) 验证与发布
- `./scripts/ci-local.sh` 必须通过
- 提交 PR 并链接到任务与 Plan Packet

---

## 使用方式

告诉 Claude：
- "初始化 plan-packet" - 设置工作流
- "添加 Plan Packet 到任务" - 为任务添加结构化计划
- "关联当前分支到任务" - 记录分支关联
- "显示当前任务" - 查看关联的任务和计划
- "更新所有 Plan Packet" - 更新到最新版本

---

## Plan Packet 结构

1. **Goal / Non-goals** - 明确目标和不做什么
2. **Scope** - 按可并行 workstreams 拆分
3. **Interfaces & Constraints** - 代码路径、依赖、质量入口
4. **Execution Order** - 执行顺序
5. **Acceptance Criteria** - 验收标准
6. **Quality Gates** - 质量检查命令
7. **Risks & Rollback** - 风险和回滚步骤
8. **Backlog 任务映射** - 任务 ID、文件路径、关联分支
9. **Notes** - 上下文、决策、参考链接

---

## 相关技能

- **plan-packet**: 任务结构化计划
- **wt-workflow**: worktree 工作流管理
- **backlog.md**: 任务管理 (通过 MCP)

---

## MCP 资源

- `backlog://workflow/overview` - 工作流总览
- `backlog://workflow/task-creation` - 任务创建指南
- `backlog://workflow/task-execution` - 任务执行指南
- `backlog://workflow/task-finalization` - 任务完成指南
"""


def get_template(skill_dir: Optional[Path] = None) -> str:
    """
    获取 Plan Packet 模板。

    优先从外部模板文件读取，如果不存在则使用内置模板。
    """
    if skill_dir:
        template_file = skill_dir / "templates" / "plan-packet-template.md"
        if template_file.exists():
            return template_file.read_text()

    # 内置模板（与模板文件保持一致）
    return """
## Plan Packet
{version_marker}

### 1. Goal / Non-goals
**Goal**
- <待补充：明确的业务/技术目标>

**Non-goals**
- <待补充：不在本次范围内的事项>

### 2. Scope（按可并行 workstreams 拆分）
**Workstream A**（建议一个独立 worktree/分支）
- 交付物：
- 修改范围：
- 风险点：

### 3. Interfaces & Constraints（接口与约束）
- 代码路径：
- 外部依赖与版本（mise / node / go / python）：
- 统一质量入口（必跑命令）：
  - `{ci_command}`
- 兼容性要求：
- 禁止事项（例如：不改公共 API，不引入新依赖等）：

### 4. Execution Order（执行顺序）
1)
2)
3)

### 5. Acceptance Criteria（验收标准）
> 参见上方的 "Acceptance Criteria" section（backlog.md 原生）
>
> 自动化检查项：
> - [ ] CI 质量门禁通过
> - [ ] format 一致、typecheck 无误
> - [ ] tests 通过（如有）

### 6. Quality Gates（质量检查）
```bash
{ci_command}
```

### 7. Risks & Rollback（风险与回滚）
- 潜在风险：
- 触发条件：
- 回滚步骤：

### 8. Backlog 任务映射
- 任务 ID：{task_id}
- 任务文件：{task_file}
- 关联分支：{branch_name}  <!-- 由 link 命令更新 -->

### 9. Notes（备注）
- <上下文、决策、外部参考链接等>

**重要**：执行过程中若发现偏离 Plan Packet，必须使用以下方式记录：
```bash
# 通过 Backlog MCP 更新任务
task_edit id:{task_id} planAppend:"<描述变更原因和新的执行方向>"
```

{end_marker}
"""


# ============================================================
# 工具函数
# ============================================================

def find_project_root(cwd: Path = None) -> Optional[Path]:
    """查找项目根目录（包含 backlog/tasks 或 .git）"""
    if cwd is None:
        cwd = Path.cwd()

    dir = cwd
    while dir != dir.parent and dir != Path("/"):
        if (dir / "backlog" / "tasks").exists() or (dir / ".git").exists():
            return dir
        dir = dir.parent

    return None


def find_skill_dir() -> Optional[Path]:
    """查找 plan-packet skill 目录"""
    # 1. 检查相对于脚本的目录
    script_dir = Path(__file__).parent.parent
    if (script_dir / "SKILL.md").exists():
        return script_dir

    # 2. 检查全局技能目录
    global_skill = Path.home() / ".claude" / "skills" / "plan-packet"
    if (global_skill / "SKILL.md").exists():
        return global_skill

    return None


def detect_workflow_file(project_root: Path, force_agents: bool = False) -> tuple[Path, str]:
    """检测项目使用的工作流文件"""
    claude_md = project_root / "CLAUDE.md"
    agents_md = project_root / "AGENTS.md"

    if force_agents:
        return agents_md, "AGENTS.md"

    if claude_md.exists():
        return claude_md, "CLAUDE.md"

    if agents_md.exists():
        return agents_md, "AGENTS.md"

    # 默认创建 CLAUDE.md
    return claude_md, "CLAUDE.md"


def detect_ci_command(project_root: Path) -> str:
    """检测项目可用的 CI 命令"""
    # 1. 检查 wt-workflow
    if (project_root / ".claude" / "skills" / "wt-workflow").exists():
        return "wt ci"

    # 2. 检查 ci-local.sh
    if (project_root / "scripts" / "ci-local.sh").exists():
        return "./scripts/ci-local.sh"

    # 3. 检查 mise.toml
    mise_toml = project_root / "mise.toml"
    if mise_toml.exists():
        content = mise_toml.read_text()
        if 'ci' in content.lower():
            return "mise run ci"

    return "# 请配置 CI 命令"


def extract_frontmatter_field(content: str, field: str) -> Optional[str]:
    """从 frontmatter 提取字段"""
    if not content.startswith("---"):
        return None

    end = content.find("\n---\n")
    if end == -1:
        return None

    frontmatter = content[4:end]
    for line in frontmatter.split("\n"):
        if line.startswith(f"{field}:"):
            return line.split(":", 1)[1].strip().strip('"')

    return None


def has_plan_packet(content: str) -> bool:
    """检查是否已有 Plan Packet"""
    return END_MARKER in content


def get_task_id_from_file(task_file: Path) -> str:
    """从任务文件获取 task_id"""
    content = task_file.read_text()

    # 优先从 frontmatter 获取
    frontmatter_id = extract_frontmatter_field(content, "id")
    if frontmatter_id:
        return frontmatter_id

    # 从文件名解析
    stem = task_file.stem
    if " - " in stem:
        return stem.split(" - ")[0]

    return stem


def get_current_branch() -> Optional[str]:
    """获取当前 git 分支"""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip() or None
    except:
        return None


# ============================================================
# 命令实现
# ============================================================

def cmd_init(project_root: Path, force_agents: bool = False) -> int:
    """初始化工作流文件"""
    target_file, file_type = detect_workflow_file(project_root, force_agents)

    # 检查是否已包含
    if target_file.exists():
        content = target_file.read_text()
        if "工作流：Plan Packet 驱动开发" in content:
            print(f"✓ Plan Packet 工作流已存在于 {file_type}")
            return 0

    # 读取现有内容
    existing = target_file.read_text() if target_file.exists() else ""

    # 合并内容
    if existing:
        merged = existing.rstrip() + WORKFLOW_FRAGMENT
    else:
        merged = WORKFLOW_FRAGMENT.lstrip()

    # 写入
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(merged)

    print(f"✓ Plan Packet 工作流已添加到 {file_type}")
    return 0


def cmd_add(project_root: Path, task_id: Optional[str] = None) -> int:
    """添加 Plan Packet 到任务"""
    tasks_dir = project_root / "backlog" / "tasks"

    if not tasks_dir.exists():
        print(f"❌ 任务目录不存在: {tasks_dir}")
        print("   请先使用 backlog MCP 创建任务")
        print("   示例: '创建一个优化性能的任务'")
        return 1

    # 收集需要处理的任务
    if task_id:
        # 处理单个任务 - 支持多种格式
        task_id_normalized = task_id.upper().lstrip("TASK-")
        task_files = []

        for f in tasks_dir.glob("*.md"):
            content = f.read_text()
            # 检查文件名
            if task_id_normalized in f.name.upper():
                task_files.append(f)
                continue
            # 检查 frontmatter id
            fm_id = extract_frontmatter_field(content, "id")
            if fm_id and fm_id.upper().lstrip("TASK-") == task_id_normalized:
                task_files.append(f)
                continue

        if not task_files:
            print(f"❌ 未找到任务: {task_id}")
            print(f"   可用任务: {[f.stem for f in tasks_dir.glob('*.md')]}")
            return 1
    else:
        # 处理所有任务
        task_files = list(tasks_dir.glob("*.md"))

    if not task_files:
        print(f"ℹ️  任务目录为空: {tasks_dir}")
        print("   请先使用 backlog MCP 创建任务")
        return 0

    # 检测 CI 命令
    ci_command = detect_ci_command(project_root)

    # 获取模板
    skill_dir = find_skill_dir()
    template = get_template(skill_dir)

    # 获取当前分支
    branch_name = get_current_branch() or "<未关联>"

    # 添加 Plan Packet
    count = 0
    skipped = 0

    for task_file in task_files:
        content = task_file.read_text()

        if has_plan_packet(content):
            skipped += 1
            continue

        # 获取任务信息
        tid = get_task_id_from_file(task_file)
        task_file_relative = task_file.relative_to(project_root)

        # 生成 Plan Packet
        plan_packet = template.format(
            version_marker=VERSION_MARKER,
            task_id=tid,
            task_file=task_file_relative,
            ci_command=ci_command,
            branch_name=branch_name,
            end_marker=END_MARKER
        )

        # 追加到文件
        with open(task_file, "a") as f:
            f.write(plan_packet)

        print(f"✓ 已添加 Plan Packet 到 {task_file.name}")
        count += 1

    if count == 0 and skipped > 0:
        print(f"✓ 所有 {skipped} 个任务已有 Plan Packet")
    elif count > 0:
        if skipped > 0:
            print(f"✓ 已添加 {count} 个任务（跳过 {skipped} 个已有 Plan Packet 的任务）")
        else:
            print(f"✓ 共添加 {count} 个任务的 Plan Packet")

    return 0


def cmd_link(project_root: Path, branch: Optional[str] = None) -> int:
    """关联分支到任务"""
    # 获取分支名
    if branch is None:
        branch = get_current_branch()
        if not branch:
            print("❌ 无法获取当前分支")
            return 1

    # 从分支名提取 Task ID
    match = re.search(r'(?:feature/)?task-?(\d+)', branch, re.IGNORECASE)
    if not match:
        print(f"❌ 分支名 '{branch}' 不包含 Task ID")
        print("   推荐格式: feature/task-1-xxx 或 task-1-xxx")
        return 1

    task_id = match.group(1)

    # 查找任务文件
    tasks_dir = project_root / "backlog" / "tasks"
    if not tasks_dir.exists():
        print(f"❌ 任务目录不存在: {tasks_dir}")
        return 1

    task_file = None
    for f in tasks_dir.glob("*.md"):
        if f"task-{task_id}" in f.name.lower():
            task_file = f
            break
        # 检查 frontmatter id
        content = f.read_text()
        if extract_frontmatter_field(content, "id") == f"TASK-{task_id}":
            task_file = f
            break

    if not task_file:
        print(f"❌ 未找到任务 TASK-{task_id}")
        return 1

    # 更新分支关联
    content = task_file.read_text()

    if "- 关联分支：" not in content:
        print(f"❌ 任务没有 Plan Packet section")
        print("   请先运行: python ~/.claude/skills/plan-packet/scripts/plan-packet.py add")
        return 1

    # 替换分支名
    new_content = re.sub(
        r'- 关联分支：.*?(?=<!--|$)',
        f'- 关联分支：{branch}  ',
        content
    )

    task_file.write_text(new_content)
    print(f"✓ 分支 '{branch}' 已关联到任务 TASK-{task_id}")

    return 0


def cmd_show(project_root: Path) -> int:
    """显示当前分支关联的任务"""
    branch = get_current_branch()
    if not branch:
        print("❌ 无法获取当前分支")
        return 1

    # 从分支名提取 Task ID
    match = re.search(r'(?:feature/)?task-?(\d+)', branch, re.IGNORECASE)
    if not match:
        print(f"ℹ️  当前分支 '{branch}' 不包含 Task ID")
        print("   使用以下命名格式可自动关联: feature/task-1-xxx")
        return 0

    task_id = match.group(1)

    # 查找任务文件
    tasks_dir = project_root / "backlog" / "tasks"
    if not tasks_dir.exists():
        return 0

    task_file = None
    for f in tasks_dir.glob("*.md"):
        if f"task-{task_id}" in f.name.lower():
            task_file = f
            break
        content = f.read_text()
        if extract_frontmatter_field(content, "id") == f"TASK-{task_id}":
            task_file = f
            break

    if not task_file:
        print(f"ℹ️  未找到任务 TASK-{task_id}")
        return 0

    # 显示任务信息
    content = task_file.read_text()
    title = extract_frontmatter_field(content, "title")
    status = extract_frontmatter_field(content, "status")

    print(f"\n┌─────────────────────────────────────────────────────────────┐")
    print(f"│  当前分支: {branch:<55}│")
    print(f"│  任务 ID: TASK-{task_id:<53}│")
    if title:
        print(f"│  标题: {title:<56}│")
    if status:
        print(f"│  状态: {status:<55}│")
    print(f"│  文件: {task_file.name:<54}│")

    # 提取关联分支
    branch_match = re.search(r'- 关联分支：([^\s<]+)', content)
    linked_branch = branch_match.group(1).strip() if branch_match else "<未关联>"
    print(f"│  关联分支: {linked_branch:<52}│")

    # 显示 Plan Packet 摘要
    if has_plan_packet(content):
        print(f"│                                                                     │")
        print(f"│  ┌─────────────────────────────────────────────────────────┐   │")
        print(f"│  │ Plan Packet 摘要                                            │   │")

        # 提取 Goal
        goal_match = re.search(r'\*\*Goal\*\*\s*\n(.*?)\*\*Non-goals\*\*', content, re.DOTALL)
        if goal_match:
            goal_text = goal_match.group(1).strip()
            lines = [l.strip() for l in goal_text.split('\n') if l.strip() and l.strip().startswith('-')]
            for line in lines[:3]:
                print(f"│  │ {line[:60]:<60}│   │")

        print(f"│  └─────────────────────────────────────────────────────────┘   │")

    print(f"└─────────────────────────────────────────────────────────────┘\n")

    return 0


def cmd_update(project_root: Path) -> int:
    """更新所有 Plan Packet"""
    tasks_dir = project_root / "backlog" / "tasks"

    if not tasks_dir.exists():
        print(f"❌ 任务目录不存在: {tasks_dir}")
        return 1

    ci_command = detect_ci_command(project_root)

    # 获取模板
    skill_dir = find_skill_dir()
    template = get_template(skill_dir)

    count = 0
    skipped = 0

    for task_file in tasks_dir.glob("*.md"):
        content = task_file.read_text()

        if not has_plan_packet(content):
            skipped += 1
            continue

        # 检查版本
        current_version = re.search(r'<!-- PLAN_PACKET:v([\d.]+) -->', content)
        if current_version and current_version.group(1) == PLAN_PACKET_VERSION:
            skipped += 1
            continue

        # 获取任务信息
        tid = get_task_id_from_file(task_file)
        task_file_relative = task_file.relative_to(project_root)

        # 保留当前分支关联
        branch_match = re.search(r'- 关联分支：([^\s<]+)', content)
        branch_name = branch_match.group(1).strip() if branch_match else "<未关联>"

        # 生成新 Plan Packet
        plan_packet = template.format(
            version_marker=VERSION_MARKER,
            task_id=tid,
            task_file=task_file_relative,
            ci_command=ci_command,
            branch_name=branch_name,
            end_marker=END_MARKER
        )

        # 替换
        start_idx = content.find("## Plan Packet")
        end_idx = content.find(END_MARKER) + len(END_MARKER)

        new_content = content[:start_idx] + plan_packet + "\n" + content[end_idx:]
        task_file.write_text(new_content)

        print(f"✓ 已更新 {task_file.name}")
        count += 1

    if count == 0:
        if skipped > 0:
            print(f"✓ 所有 {skipped} 个 Plan Packet 已是最新版本")
        else:
            print(f"ℹ️  没有找到需要更新的 Plan Packet")
    else:
        if skipped > 0:
            print(f"✓ 共更新 {count} 个任务（{skipped} 个已是最新或无 Plan Packet）")
        else:
            print(f"✓ 共更新 {count} 个任务的 Plan Packet")

    return 0


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Plan Packet - 任务结构化计划工具",
        add_help=False
    )
    parser.add_argument("command", nargs="?", help="命令: init, add, link, show, update")
    parser.add_argument("--task", help="指定任务 ID（用于 add 命令）")
    parser.add_argument("--branch", help="指定分支名（用于 link 命令）")
    parser.add_argument("--force-agents", action="store_true", help="强制使用 AGENTS.md")
    parser.add_argument("--help", "-h", action="store_true", help="显示帮助信息")

    args = parser.parse_args()

    if args.help or not args.command:
        print(f"""
Plan Packet v{PLAN_PACKET_VERSION} - 任务结构化计划工具

用法:
  python scripts/plan-packet.py <command> [options]

命令:
  init           初始化工作流文件（CLAUDE.md 或 AGENTS.md）
  add            添加 Plan Packet 到任务
  link           关联当前分支到任务
  show           显示当前分支关联的任务
  update         更新所有 Plan Packet 到最新版本

选项:
  --task TASK    指定任务 ID（用于 add 命令）
  --branch BRANCH 指定分支名（用于 link 命令）
  --force-agents 强制使用 AGENTS.md 而非 CLAUDE.md
  --help         显示此帮助信息

示例:
  python scripts/plan-packet.py init
  python scripts/plan-packet.py add
  python scripts/plan-packet.py add --task task-1
  python scripts/plan-packet.py link
  python scripts/plan-packet.py show
  python scripts/plan-packet.py update
""")
        return 0 if args.help else 1

    # 查找项目根目录
    project_root = find_project_root()
    if not project_root:
        print("❌ 无法找到项目根目录")
        print("   请在包含 .git 或 backlog/ 目录的项目中运行")
        return 1

    # 执行命令
    commands = {
        "init": lambda: cmd_init(project_root, args.force_agents),
        "add": lambda: cmd_add(project_root, args.task),
        "link": lambda: cmd_link(project_root, args.branch),
        "show": lambda: cmd_show(project_root),
        "update": lambda: cmd_update(project_root),
    }

    if args.command not in commands:
        print(f"❌ 未知命令: {args.command}")
        return 1

    return commands[args.command]()


if __name__ == "__main__":
    sys.exit(main())
