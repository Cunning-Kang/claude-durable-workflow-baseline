"""pytest 配置和共享 fixtures"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime


@pytest.fixture
def temp_project_dir():
    """临时项目目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_plan_packet():
    """示例 Plan Packet"""
    return {
        "goal": "实现 JWT 认证系统",
        "scope": {
            "workstreams": ["A: User model", "B: JWT auth"]
        },
        "execution_order": [
            "1) Create User model",
            "2) Implement JWT generation",
            "3) Implement JWT validation",
            "4) Add auth middleware"
        ],
        "context": {
            "tech_stack": ["python", "fastapi"],
            "test_framework": "pytest",
            "ci_command": "pytest && mypy .",
            "project_type": "web-service"
        }
    }


@pytest.fixture
def sample_task_file(temp_project_dir):
    """示例任务文件"""
    task_file = temp_project_dir / "docs" / "tasks" / "TASK-001.md"
    task_file.parent.mkdir(parents=True, exist_ok=True)

    content = """---
id: TASK-001
title: "Add user authentication"
status: "To Do"
created_at: 2026-02-01
updated_at: 2026-02-01
plan_request: true
plan_file: "docs/plans/2026-02-01-TASK-001-plan.md"
plan_status: "pending"
execution_mode: "subagent-driven"
execution_config:
  batch_size: 3
  auto_continue: false
  checkpoint_interval: 3
dependencies: []
context:
  tech_stack:
    - python
    - fastapi
  test_framework: pytest
  ci_command: pytest && mypy .
execution_state:
  current_step: 0
  total_steps: 0
  completed_tasks: []
  failed_tasks: []
automation_hints:
  can_auto_generate_plan: true
  can_auto_execute: false
---

## Plan Packet

### 1. Goal / Non-goals
**Goal**
- 实现 JWT 认证系统
"""
    task_file.write_text(content)
    return task_file
