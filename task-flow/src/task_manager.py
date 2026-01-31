"""Task Manager for task-flow system"""

from pathlib import Path
import json
from datetime import datetime
import re


class TaskManager:
    """管理任务的生命周期"""

    def __init__(self, tasks_dir: Path, index_file: Path):
        self.tasks_dir = tasks_dir
        self.index_file = index_file
        self._ensure_index()

    def _ensure_index(self):
        """确保 _index.json 存在"""
        if not self.index_file.exists():
            self._write_index({"next_id": 1})

    def _read_index(self) -> dict:
        """读取 _index.json"""
        return json.loads(self.index_file.read_text())

    def _write_index(self, data: dict):
        """写入 _index.json"""
        self.index_file.write_text(json.dumps(data, indent=2))

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
        filename = f"{task_id}-{slug}.md"
        task_file = self.tasks_dir / filename

        content = self._generate_task_content(task_id, title, filename)
        task_file.write_text(content)

        return task_id

    def _slugify(self, title: str) -> str:
        """将标题转换为文件名友好的 slug"""
        # 转小写，空格替换为连字符
        slug = title.lower().replace(" ", "-")
        # 移除非字母数字连字符
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        return slug

    def _generate_task_content(self, task_id: str, title: str, filename: str) -> str:
        """生成任务文件内容"""
        now = datetime.now().strftime("%Y-%m-%d")
        relative_path = f"docs/tasks/{filename}"

        return f"""---
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
completed_at: null
---

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
  - `# 请配置 CI 命令`
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
# 请配置 CI 命令
```

### 7. Risks & Rollback（风险与回滚）
- 潜在风险：
- 触发条件：
- 回滚步骤：

### 8. Backlog 任务映射
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
        tasks = []
        for task_file in self.tasks_dir.glob("TASK-*.md"):
            task = self._parse_task_file(task_file)
            if status is None or task["status"] == status:
                tasks.append(task)
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

    def get_task(self, task_id: str) -> dict:
        """通过 ID 获取任务"""
        for task_file in self.tasks_dir.glob("TASK-*.md"):
            task = self._parse_task_file(task_file)
            if task["id"] == task_id:
                # 读取完整内容
                content = task_file.read_text()
                task["content"] = content
                return task
        return None

    def update_task(self, task_id: str, **kwargs):
        """更新任务字段"""
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task_file = Path(task["file"])
        content = task_file.read_text()

        # 更新 YAML frontmatter 中的字段
        for key, value in kwargs.items():
            # 匹配 "key: value" 格式，value 可能包含空格
            pattern = f"^{key}:\\s*.+$"
            replacement = f"{key}: {value}"
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # 更新 updated_at
        now = datetime.now().strftime("%Y-%m-%d")
        content = re.sub(r"^updated_at:\s*.+$", f"updated_at: {now}", content, flags=re.MULTILINE)

        task_file.write_text(content)
