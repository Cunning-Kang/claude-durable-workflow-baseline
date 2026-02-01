"""测试 PlanBuilder - Plan Generator 集成组件"""

import pytest
from pathlib import Path
from plan_generator.plan_builder import PlanBuilder


def test_generate_full_plan_from_plan_packet():
    """测试从完整的 Plan Packet 生成实施计划"""
    plan_packet = {
        "goal": "实现 JWT 认证系统，支持用户注册、登录、token刷新",
        "context": {
            "tech_stack": ["python", "fastapi"],
            "language": "python"
        },
        "scope": ["用户认证", "JWT token管理"],
        "quality_gates": [
            "pytest --cov",
            "black --check"
        ]
    }

    builder = PlanBuilder(project_root=Path("/tmp/test_project"))
    plan = builder.generate(plan_packet)

    # 验证计划结构
    assert isinstance(plan, dict)
    assert "goal" in plan
    assert "architecture" in plan
    assert "tech_stack" in plan
    assert "tasks" in plan
    assert "quality_gates" in plan
    assert "markdown" in plan

    # 验证内容
    assert plan["goal"] == plan_packet["goal"]
    assert isinstance(plan["tasks"], list)
    assert len(plan["tasks"]) > 0
    assert isinstance(plan["markdown"], str)
    assert len(plan["markdown"]) > 0


def test_integrate_with_goal_analyzer():
    """测试与 GoalAnalyzer 的集成 - 需求提取"""
    plan_packet = {
        "goal": "实现 JWT 认证系统，支持用户注册、登录",
        "context": {
            "tech_stack": ["python", "fastapi"]
        }
    }

    builder = PlanBuilder(project_root=Path("/tmp/test_project"))
    plan = builder.generate(plan_packet)

    # 验证 GoalAnalyzer 提取的需求
    assert "jwt" in plan.get("libraries", [])
    assert "authentication" in plan.get("features", [])
    assert "user_registration" in plan.get("features", [])
    assert plan.get("language") == "python"


def test_integrate_with_project_scanner():
    """测试与 ProjectScanner 的集成 - 项目分析"""
    # 创建临时项目结构
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试项目文件
        test_file = Path(tmpdir) / "src" / "main.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# test project")

        plan_packet = {
            "goal": "添加用户认证功能",
            "context": {"tech_stack": ["python"]}
        }

        builder = PlanBuilder(project_root=Path(tmpdir))
        plan = builder.generate(plan_packet)

        # 验证 ProjectScanner 的分析结果
        assert "project_structure" in plan
        assert plan["project_structure"]["root"] == tmpdir
        assert isinstance(plan["project_structure"]["structure"]["directories"], list)


def test_integrate_with_task_breakdown():
    """测试与 TaskBreakdown 的集成 - 任务生成"""
    plan_packet = {
        "goal": "实现用户认证系统",
        "context": {
            "tech_stack": ["python"],
            "language": "python"
        }
    }

    builder = PlanBuilder(project_root=Path("/tmp/test_project"))
    plan = builder.generate(plan_packet)

    # 验证 TaskBreakdown 生成的任务
    assert "tasks" in plan
    assert len(plan["tasks"]) > 0

    # 验证任务结构
    for task in plan["tasks"]:
        assert "title" in task
        assert "description" in task
        assert "estimated_time" in task
        assert isinstance(task["estimated_time"], int)


def test_output_format_writing_plans():
    """测试输出格式符合 writing-plans 规范"""
    plan_packet = {
        "goal": "实现 JWT 认证",
        "context": {"tech_stack": ["python"]},
        "quality_gates": ["pytest --cov"]
    }

    builder = PlanBuilder(project_root=Path("/tmp/test_project"))
    plan = builder.generate(plan_packet)
    markdown = plan["markdown"]

    # 验证 writing-plans 格式要素
    assert "# " in markdown  # 标题
    assert "**Goal:**" in markdown  # 目标
    assert "**Architecture:**" in markdown  # 架构
    assert "**Tech Stack:**" in markdown  # 技术栈
    assert "## Task" in markdown  # 任务标题
    assert "Step 1: Write the failing test" in markdown  # TDD 步骤
    assert "Step 2: Run test to verify it fails" in markdown
    assert "Step 3: Write minimal implementation" in markdown
    assert "Step 4: Run test to verify it passes" in markdown
    assert "Step 5: Commit" in markdown


def test_error_handling_missing_data():
    """测试缺失数据的错误处理"""
    builder = PlanBuilder(project_root=Path("/tmp/test_project"))

    # 测试空 goal
    with pytest.raises(ValueError, match="Goal cannot be empty"):
        builder.generate({"goal": ""})

    # 测试缺失 goal 字段
    with pytest.raises(ValueError, match="Goal cannot be empty"):
        builder.generate({})


def test_build_context_enrichment():
    """测试 _build_context 方法丰富上下文"""
    plan_packet = {
        "goal": "实现 JWT 认证",
        "context": {
            "tech_stack": ["python", "fastapi"],
            "language": "python"
        }
    }

    builder = PlanBuilder(project_root=Path("/tmp/test_project"))
    context = builder._build_context(plan_packet)

    # 验证上下文丰富
    assert "language" in context
    assert "features" in context
    assert "libraries" in context
    assert "project_info" in context

    # 验证从 GoalAnalyzer 提取的数据
    assert context["language"] == "python"
    assert isinstance(context["features"], list)

    # 验证从 ProjectScanner 提取的数据
    assert "root" in context["project_info"]
