"""测试 GoalAnalyzer"""

import pytest
from plan_generator.analyzer import GoalAnalyzer


def test_analyze_goal_extract_requirements():
    """测试从 Goal 提取技术需求"""
    plan_packet = {
        "goal": "实现 JWT 认证系统，支持用户注册、登录、token刷新",
        "context": {
            "tech_stack": ["python", "fastapi"]
        }
    }

    analyzer = GoalAnalyzer()
    requirements = analyzer.extract_requirements(plan_packet)

    assert "jwt" in requirements["libraries"]
    assert "authentication" in requirements["features"]
    assert "user_registration" in requirements["features"]
    assert requirements["language"] == "python"


def test_analyze_goal_detect_language():
    """测试检测编程语言"""
    plan_packet = {
        "goal": "实现用户认证",
        "context": {
            "tech_stack": ["python", "fastapi"]
        }
    }

    analyzer = GoalAnalyzer()
    requirements = analyzer.extract_requirements(plan_packet)

    assert requirements["language"] == "python"


def test_analyze_goal_with_javascript():
    """测试分析 JavaScript 项目"""
    plan_packet = {
        "goal": "实现 React 组件",
        "context": {
            "tech_stack": ["typescript", "react"]
        }
    }

    analyzer = GoalAnalyzer()
    requirements = analyzer.extract_requirements(plan_packet)

    assert requirements["language"] == "javascript"


def test_analyze_goal_extract_features():
    """测试提取功能列表"""
    plan_packet = {
        "goal": "实现 JWT 认证系统，支持用户注册、登录、token刷新和密码重置",
        "context": {"tech_stack": ["python"]}
    }

    analyzer = GoalAnalyzer()
    requirements = analyzer.extract_requirements(plan_packet)

    assert "authentication" in requirements["features"]
    assert "user_registration" in requirements["features"]
    assert "token_refresh" in requirements["features"]
    assert "password_reset" in requirements["features"]


def test_analyze_goal_empty_goal():
    """测试空 Goal"""
    plan_packet = {
        "goal": "",
        "context": {"tech_stack": ["python"]}
    }

    analyzer = GoalAnalyzer()
    with pytest.raises(ValueError, match="Goal cannot be empty"):
        analyzer.extract_requirements(plan_packet)
