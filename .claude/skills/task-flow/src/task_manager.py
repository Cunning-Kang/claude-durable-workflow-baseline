"""Task Manager for task-flow system"""

from pathlib import Path
import json
from datetime import datetime
import re
import yaml

try:
    from .todowrite_compat.tool import maybe_run_bootstrap
except ImportError:
    # Fallback if todowrite_compat module is not available
    def maybe_run_bootstrap(task_manager, task_id: str, new_status: str):
        pass


class TaskManager:
    """管理任务的生命周期"""

    def __init__(self, tasks_dir: Path, index_file: Path):
        self.tasks_dir = tasks_dir
        self.index_file = index_file
        self._task_index = {}  # In-memory index for task files
        self._task_meta = {}
        self._todo_index = {}
        self._ensure_index()
        self._load_index_cache()

    def _ensure_index(self):
        """确保 _index.json 存在"""
        if not self.index_file.exists():
            self._write_index({"next_id": 1, "tasks": {}, "todos": {}})

    def _load_index_cache(self):
        data = self._read_index()
        tasks = data.get("tasks") or {}
        todos = data.get("todos") or {}
        self._task_meta = tasks
        self._todo_index = todos
        self._task_index = {
            task_id: self.tasks_dir.parent / meta["file"]
            for task_id, meta in tasks.items()
            if meta.get("file")
        }

    def _persist_index_cache(self):
        data = self._read_index()
        data["tasks"] = self._task_meta
        data["todos"] = self._todo_index
        self._write_index(data)

    def _index_task(self, task_id: str, task_file: Path, meta: dict, todo_id: str | None = None, persist: bool = True):
        self._task_index[task_id] = task_file
        self._task_meta[task_id] = meta
        if todo_id is not None:
            self._todo_index[str(todo_id)] = task_id
        if persist:
            self._persist_index_cache()

    def _task_meta_from_frontmatter(self, task_file: Path, frontmatter: dict) -> dict:
        updated_at = frontmatter.get("updated_at")
        if updated_at is not None:
            updated_at = str(updated_at)

        execution_mode = frontmatter.get("execution_mode")
        if execution_mode is not None:
            execution_mode = str(execution_mode)

        plan_file = frontmatter.get("plan_file")
        if plan_file is not None:
            plan_file = str(plan_file)

        return {
            "file": str(task_file.relative_to(self.tasks_dir.parent)),
            "title": frontmatter.get("title"),
            "status": frontmatter.get("status"),
            "updated_at": updated_at,
            "execution_mode": execution_mode,
            "plan_file": plan_file,
        }

    def _remove_task_from_index(self, task_id: str):
        self._task_index.pop(task_id, None)
        self._task_meta.pop(task_id, None)
        for todo_key, mapped in list(self._todo_index.items()):
            if mapped == task_id:
                self._todo_index.pop(todo_key, None)
        self._persist_index_cache()

    def _update_task_index_meta(self, task_id: str, updates: dict):
        meta = self._task_meta.get(task_id) or {}
        meta.update(updates)
        self._task_meta[task_id] = meta
        self._persist_index_cache()

    def _read_index(self) -> dict:
        """读取 _index.json"""
        return json.loads(self.index_file.read_text())

    def _write_index(self, data: dict):
        """写入 _index.json"""
        # Ensure parent directory exists
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        self.index_file.write_text(json.dumps(data, indent=2, default=str))

    def _build_index(self):
        """Build in-memory index of task files by scanning tasks directory"""
        self._task_index = {}
        self._task_meta = {}
        self._todo_index = {}
        for task_file in self.tasks_dir.glob("TASK-*.md"):
            try:
                frontmatter = self._load_frontmatter(task_file)
                task_id = frontmatter.get("id")
                if task_id:
                    relative_path = str(task_file.relative_to(self.tasks_dir.parent))
                    meta = {
                        "file": relative_path,
                        "title": frontmatter.get("title"),
                        "status": frontmatter.get("status"),
                        "updated_at": frontmatter.get("updated_at"),
                    }
                    todo_id = frontmatter.get("todo_id")
                    self._task_index[task_id] = task_file
                    self._task_meta[task_id] = meta
                    if todo_id is not None:
                        self._todo_index[str(todo_id)] = task_id
            except Exception:
                continue
        self._persist_index_cache()

    def _get_task_file(self, task_id: str) -> Path:
        """Get task file path by task ID using in-memory index"""
        if not self._task_index:
            self._load_index_cache()
            if not self._task_index:
                self._build_index()
        return self._task_index.get(task_id)

    def generate_task_id(self) -> str:
        """生成下一个任务 ID"""
        index = self._read_index()
        task_id = f"TASK-{index['next_id']:03d}"
        index['next_id'] += 1
        self._write_index(index)
        return task_id

    def create_task(self, title: str) -> str:
        """创建新任务"""
        task_id = self.generate_task_id()
        slug = self._slugify(title)
        if not slug:
            slug = task_id.lower()
        filename = f"{task_id}-{slug}.md"
        task_file = self.tasks_dir / filename

        # Ensure tasks_dir exists
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        content = self._generate_task_content(task_id, title, filename, todo_id=None)
        task_file.write_text(content)

        relative_path = str(task_file.relative_to(self.tasks_dir.parent))
        meta = {
            "file": relative_path,
            "title": title,
            "status": "To Do",
            "updated_at": datetime.now().strftime("%Y-%m-%d"),
        }
        self._index_task(task_id, task_file, meta)

        return task_id

    def _slugify(self, title: str) -> str:
        """将标题转换为文件名友好的 slug"""
        # 转小写，空格替换为连字符
        slug = title.lower().replace(" ", "-")
        # 移除非字母数字连字符
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        return slug

    def _generate_task_content(self, task_id: str, title: str, filename: str, todo_id: str = None) -> str:
        """生成任务文件内容"""
        now = datetime.now().strftime("%Y-%m-%d")
        relative_path = f"docs/tasks/{filename}"

        # 自动检测 CI 命令
        try:
            # Try direct import first (when running from main directory)
            from ci_detector import detect_ci_command
        except ImportError:
            # If direct import fails, try relative import (when running from src subdirectory)
            try:
                from .ci_detector import detect_ci_command
            except ImportError:
                # Fallback to default command if ci_detector module is not available
                def detect_ci_command(project_root):
                    return "# 请配置 CI 命令"

        project_root = Path.cwd()
        ci_command = detect_ci_command(project_root)

        # 构建 frontmatter，如果提供了 todo_id 则包含它
        frontmatter = f"""---
id: {task_id}
title: {title}
status: To Do
created_at: {now}
updated_at: {now}
execution_mode: manual
plan_file: null
worktree: null
branch: null
current_step: 0
completion_type: null
pr_url: null
completed_at: null"""

        if todo_id is not None:
            frontmatter += f"\ntodo_id: {todo_id}"

        frontmatter += "\n---"

        return f"""{frontmatter}

# Task: {title}

## Plan Packet

### 1. Goal / Non-goals
**Goal**
- <待补充：明确的业务/技术目标>

**Non-goals**
- <待补充：不在本次范围内的事项>

### 2. Scope（按可并行 workstreams 拆分）
**Workstream A**
- 交付物：
- 修改范围：
- 风险点：

### 3. Interfaces & Constraints（接口与约束）
- 代码路径：
- 外部依赖与版本：
- 统一质量入口：
  - `{ci_command}`
- 兼容性要求：
- 禁止事项：

### 4. Execution Order（执行顺序）
1)
2)
3)

### 5. Acceptance Criteria（验收标准）
- [ ] CI 质量门禁通过
- [ ] format 一致、typecheck 无误
- [ ] tests 通过（如有）

### 6. Quality Gates（质量检查）
```bash
{ci_command}
```

### 7. Risks & Rollback（风险与回滚）
- 潜在风险：
- 触发条件：
- 回滚步骤：

### 8. 任务元数据（Task Metadata）
- 任务 ID：{task_id}
- 任务文件：{relative_path}
- 关联分支：

### 9. Notes（备注）
- <上下文、决策、外部参考链接等>

---
**执行过程中若发现偏离 Plan Packet，在此记录：**
"""

    def list_tasks(self, status: str = None) -> list:
        """列出所有任务"""
        if not self._task_meta:
            self._load_index_cache()
            if not self._task_meta:
                self._build_index()

        tasks = []
        for task_id, meta in self._task_meta.items():
            if status is None or meta.get("status") == status:
                tasks.append({
                    "id": task_id,
                    "title": meta.get("title"),
                    "status": meta.get("status"),
                    "file": str(self.tasks_dir.parent / meta.get("file")) if meta.get("file") else None,
                })
        return sorted(tasks, key=lambda t: t["id"])

    def _parse_task_file(self, task_file: Path) -> dict:
        """解析任务文件"""
        content = task_file.read_text()

        # 提取 YAML frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            raise ValueError(f"Invalid task file {task_file}: missing YAML frontmatter")

        frontmatter_text = frontmatter_match.group(1)
        frontmatter = self._parse_yaml_frontmatter(frontmatter_text)

        return {
            "id": frontmatter.get("id"),
            "title": frontmatter.get("title"),
            "status": frontmatter.get("status"),
            "file": str(task_file),
        }

    def _parse_yaml_frontmatter(self, text: str) -> dict:
        """简单的 YAML 解析器（仅支持我们用到的字段）"""
        result = {}
        for line in text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
        return result

    def _load_frontmatter(self, task_file: Path) -> dict:
        """Load YAML frontmatter with a fast path for simple key-value pairs."""

        content = task_file.read_text()

        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return {}

        frontmatter_text = frontmatter_match.group(1)
        lines = frontmatter_text.splitlines()

        def _is_simple_kv(line: str) -> bool:
            if not line or ":" not in line:
                return False
            if line.startswith(" ") or line.startswith("-"):
                return False
            return True

        if lines and all(_is_simple_kv(line) for line in lines if line.strip()):
            parsed = {}
            for line in lines:
                if not line.strip():
                    continue
                key, value = line.split(":", 1)
                parsed[key.strip()] = value.strip()
            return parsed

        return yaml.safe_load(frontmatter_text) or {}

    def get_task(self, task_id: str) -> dict:
        """通过 ID 获取任务"""
        task_file = self._get_task_file(task_id)
        if task_file and task_file.exists():
            task = self._parse_task_file(task_file)
            content = task_file.read_text()
            task["content"] = content

            frontmatter = self._load_frontmatter(task_file)
            meta = self._task_meta_from_frontmatter(task_file, frontmatter)
            todo_id = frontmatter.get("todo_id")
            self._index_task(
                task_id,
                task_file,
                meta,
                todo_id=str(todo_id) if todo_id is not None else None,
                persist=False,
            )

            return task
        return None

    def get_task_by_todo_id(self, todo_id: str) -> dict:
        """通过 todo_id 获取任务"""
        todo_key = str(todo_id)
        if not self._todo_index:
            self._load_index_cache()
            if not self._todo_index:
                self._build_index()

        task_id = self._todo_index.get(todo_key)
        if not task_id:
            return None

        return self.get_task(task_id)

    def create_task_with_todo_id(self, title: str, todo_id: str = None) -> str:
        """创建任务，支持 todo_id 映射和幂等创建"""
        if todo_id is not None:
            existing_task = self.get_task_by_todo_id(todo_id)
            if existing_task:
                return existing_task["id"]

        task_id = self.generate_task_id()
        slug = self._slugify(title)
        if not slug:
            slug = task_id.lower()
        filename = f"{task_id}-{slug}.md"
        task_file = self.tasks_dir / filename

        # Ensure tasks_dir exists
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        content = self._generate_task_content(task_id, title, filename, todo_id=todo_id)
        task_file.write_text(content)

        relative_path = str(task_file.relative_to(self.tasks_dir.parent))
        meta = {
            "file": relative_path,
            "title": title,
            "status": "To Do",
            "updated_at": datetime.now().strftime("%Y-%m-%d"),
        }
        self._index_task(task_id, task_file, meta, todo_id=str(todo_id) if todo_id is not None else None)

        return task_id


    def _replace_frontmatter(self, task_file: Path, updates: dict):
        """Replace the frontmatter in a task file with updated values."""
        content = task_file.read_text()

        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            raise ValueError(f"Invalid task file {task_file}: missing YAML frontmatter")

        frontmatter_text = frontmatter_match.group(1)
        remaining_content = content[frontmatter_match.end():]

        now = datetime.now().strftime("%Y-%m-%d")
        updates_with_timestamp = dict(updates)
        updates_with_timestamp["updated_at"] = now

        updated_lines = []
        for line in frontmatter_text.splitlines():
            stripped = line.lstrip()
            if not stripped or line != stripped or ":" not in line:
                updated_lines.append(line)
                continue
            key, _value = line.split(":", 1)
            key = key.strip()
            if key in updates_with_timestamp:
                updated_lines.append(f"{key}: {updates_with_timestamp[key]}")
            else:
                updated_lines.append(line)

        new_frontmatter = "---\n" + "\n".join(updated_lines) + "\n---"
        new_content = new_frontmatter + remaining_content
        task_file.write_text(new_content)
        return new_content

    def update_task(self, task_id: str, **kwargs):
        """更新任务字段"""
        task_file = self._get_task_file(task_id)
        if not task_file or not task_file.exists():
            raise ValueError(f"Task {task_id} not found")

        if 'status' in kwargs and kwargs['status'].lower() in ["in progress", "in_progress"]:
            maybe_run_bootstrap(self, task_id, kwargs['status'])

        self._replace_frontmatter(task_file, kwargs)

        if kwargs:
            updates = {}
            if "status" in kwargs:
                updates["status"] = kwargs["status"]
            updates["updated_at"] = datetime.now().strftime("%Y-%m-%d")
            self._update_task_index_meta(task_id, updates)

    def add_task_note(self, task_id: str, note: str):
        """在任务的 Notes section 添加备注"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task_file = Path(task["file"])
        content = task_file.read_text()

        # 找到 Notes section 并添加备注
        # 在 "### 9. Notes" 之后的 "- <上下文..." 之前添加
        notes_marker = "### 9. Notes（备注）"
        if notes_marker in content:
            # 在 "- <上下文..." 之前插入
            placeholder = "- <上下文、决策、外部参考链接等>"
            if placeholder in content:
                note_entry = f"- {note}\n{placeholder}"
                content = content.replace(placeholder, note_entry)
            else:
                # 如果没有 placeholder，在 section 后添加
                content = content.replace(
                    notes_marker,
                    f"{notes_marker}\n- {note}"
                )
        else:
            # 如果没有 Notes section，追加到文件末尾
            content += f"\n\n### Notes\n- {note}\n"

        task_file.write_text(content)

    def complete_task(self, task_id: str):
        """完成任务（标记为 Done 并归档）"""
        task_file = self._get_task_file(task_id)
        if not task_file or not task_file.exists():
            raise ValueError(f"Task {task_id} not found")

        filename = task_file.name

        # 更新任务状态
        now = datetime.now().strftime("%Y-%m-%d")
        self.update_task(
            task_id,
            status="Done",
            completed_at=now
        )

        # 创建 completed 目录
        completed_dir = self.tasks_dir / "completed"
        completed_dir.mkdir(exist_ok=True)

        # 移动任务文件到 completed/
        new_path = completed_dir / filename
        task_file.rename(new_path)

        self._remove_task_from_index(task_id)

        # 更新 _index.json
        index = self._read_index()
        if "completed_tasks" not in index:
            index["completed_tasks"] = {}
        index["completed_tasks"][task_id] = {
            "completed_at": now,
            "file": str(new_path.relative_to(self.tasks_dir.parent))
        }
        self._write_index(index)

    def update_task_step(self, task_id: str, step: int):
        """Update the current step of a task.

        Args:
            task_id: The ID of the task to update
            step: The step number to set as current_step
        """
        self.update_task(task_id, current_step=step)
