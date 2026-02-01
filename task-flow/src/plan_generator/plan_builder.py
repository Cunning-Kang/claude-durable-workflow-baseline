"""PlanBuilder - Plan Generator 集成组件"""

from pathlib import Path
from typing import Dict, List, Any

from .analyzer import GoalAnalyzer
from .project_scanner import ProjectScanner
from .task_breakdown import TaskBreakdown
from .path_inference import PathInference


class PlanBuilder:
    """集成所有 Plan Generator 组件，生成完整的实施计划"""

    def __init__(self, project_root: Path):
        """
        初始化 PlanBuilder

        Args:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.goal_analyzer = GoalAnalyzer()
        self.project_scanner = ProjectScanner(self.project_root)
        self.task_breakdown = TaskBreakdown()
        self.path_inference = PathInference()

    def generate(self, plan_packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成完整的实施计划

        Args:
            plan_packet: 包含 goal, context, scope, quality_gates 的字典

        Returns:
            包含完整实施计划的字典：
            - goal: 目标描述
            - architecture: 架构描述
            - tech_stack: 技术栈列表
            - language: 编程语言
            - libraries: 库列表
            - features: 功能列表
            - tasks: 任务列表
            - quality_gates: 质量检查命令
            - project_structure: 项目结构信息
            - markdown: Markdown 格式的计划

        Raises:
            ValueError: 当 goal 为空时
        """
        # 提取并验证 goal
        goal = plan_packet.get("goal", "").strip()
        if not goal:
            raise ValueError("Goal cannot be empty")

        # 构建丰富的上下文
        context = self._build_context(plan_packet)

        # 提取质量门禁
        quality_gates = plan_packet.get("quality_gates", [])

        # 生成任务
        tasks = self.task_breakdown.breakdown(goal, context)

        # 使用 PathInference 为任务推断文件路径
        tasks = self._add_file_paths_to_tasks(tasks, context)

        # 检测任务依赖关系
        tasks_with_deps = self.task_breakdown.detect_dependencies(tasks)

        # 格式化为 Markdown
        markdown = self._format_plan(
            goal=goal,
            context=context,
            tasks=tasks,
            tasks_with_deps=tasks_with_deps,
            quality_gates=quality_gates
        )

        return {
            "goal": goal,
            "architecture": self._generate_architecture(goal, context),
            "tech_stack": plan_packet.get("context", {}).get("tech_stack", []),
            "language": context.get("language", "python"),
            "libraries": context.get("libraries", []),
            "features": context.get("features", []),
            "tasks": tasks,
            "quality_gates": quality_gates,
            "project_structure": context.get("project_info", {}),
            "markdown": markdown,
        }

    def _build_context(self, plan_packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        丰富上下文信息

        Args:
            plan_packet: 原始 Plan Packet

        Returns:
            包含 language, features, libraries, project_info 的字典
        """
        # 使用 GoalAnalyzer 提取需求
        requirements = self.goal_analyzer.extract_requirements(plan_packet)

        # 使用 ProjectScanner 分析项目
        project_info = {
            "root": str(self.project_root),
            "structure": self.project_scanner.get_project_structure(),
            "entry_points": self.project_scanner.detect_entry_points(),
            "test_framework": self.project_scanner.detect_test_framework(),
        }

        # 合并上下文
        context = plan_packet.get("context", {}).copy()
        context.update({
            "language": requirements["language"],
            "features": requirements.get("features", []),
            "libraries": requirements.get("libraries", []),
            "project_info": project_info,
        })

        return context

    def _add_file_paths_to_tasks(
        self,
        tasks: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        使用 PathInference 为任务推断文件路径

        Args:
            tasks: 任务列表
            context: 上下文信息（包含 language, tech_stack 等）

        Returns:
            包含文件路径的任务列表
        """
        language = context.get("language", "python")
        tech_stack = context.get("tech_stack", [])

        for task in tasks:
            # 从任务标题中提取功能名称
            title = task.get("title", "")

            # 使用 PathInference 推断文件路径
            try:
                file_path = self.path_inference.infer(
                    feature=title,
                    project_type=language,
                    tech_stack=tech_stack
                )

                # 添加文件信息到任务
                task["files"] = [
                    {
                        "action": "Create",
                        "path": file_path
                    }
                ]

                # 如果是测试任务，也推断测试文件路径
                if "测试" in title or "test" in title.lower():
                    test_framework = context.get("project_info", {}).get("test_framework", "pytest")
                    test_path = self.path_inference.infer_test_path(file_path, test_framework)
                    task["files"].append({
                        "action": "Create",
                        "path": test_path
                    })

            except Exception:
                # 如果推断失败，跳过添加文件路径
                pass

        return tasks

    def _format_plan(
        self,
        goal: str,
        context: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        tasks_with_deps: List[Dict[str, Any]],
        quality_gates: List[str]
    ) -> str:
        """
        格式化为 writing-plans 规范的 Markdown

        Args:
            goal: 目标描述
            context: 上下文信息
            tasks: 原始任务列表
            tasks_with_deps: 包含依赖信息的任务列表
            quality_gates: 质量检查命令

        Returns:
            Markdown 格式的计划字符串
        """
        lines = []

        # 标题
        feature_name = self._extract_feature_name(goal)
        lines.append(f"# {feature_name} Implementation Plan\n")

        # Sub-skill 提示
        lines.append("> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans\n")

        # Goal
        lines.append(f"**Goal:** {goal}\n")

        # Architecture
        architecture = self._generate_architecture(goal, context)
        lines.append(f"**Architecture:** {architecture}\n")

        # Tech Stack
        tech_stack = context.get("tech_stack", context.get("libraries", []))
        if tech_stack:
            tech_str = ", ".join(tech_stack) if isinstance(tech_stack, list) else tech_stack
            lines.append(f"**Tech Stack:** {tech_str}\n")

        lines.append("---\n")

        # 任务列表
        for i, dep_info in enumerate(tasks_with_deps, start=1):
            # dep_info 是 {"task": "title string", "depends_on": [...]}
            task_title = dep_info.get("task", "")
            depends_on = dep_info.get("depends_on", [])

            # 从原始 tasks 列表中找到完整的 task 信息
            task = next((t for t in tasks if t.get("title") == task_title), {})

            title = task.get("title", "Unnamed Task")
            description = task.get("description", "")

            lines.append(f"\n## Task {i}: {title}")
            lines.append("")
            lines.append(f"**Description:** {description}")
            lines.append("")

            # 添加依赖信息
            if depends_on:
                lines.append(f"**Dependencies:** {', '.join(depends_on)}")
                lines.append("")

            # 添加文件信息（如果有的话）
            if "files" in task:
                lines.append("**Files:**")
                for file_info in task["files"]:
                    action = file_info.get("action", "Create")
                    path = file_info.get("path", "")
                    lines.append(f"- {action}: `{path}`")
                lines.append("")

            # TDD 步骤
            lines.append("**Step 1: Write the failing test**")
            lines.append("```python")
            lines.append("# TODO: Write test code")
            lines.append("```")
            lines.append("")

            lines.append("**Step 2: Run test to verify it fails**")
            test_framework = context.get("project_info", {}).get("test_framework", "pytest")
            lines.append(f"Run: `{test_framework} ...`")
            lines.append("")

            lines.append("**Step 3: Write minimal implementation**")
            lines.append("```python")
            lines.append("# TODO: Write implementation code")
            lines.append("```")
            lines.append("")

            lines.append("**Step 4: Run test to verify it passes**")
            lines.append(f"Run: `{test_framework} ...`")
            lines.append("")

            lines.append("**Step 5: Commit**")
            lines.append("Run: `git commit -m 'feat: implement ...'`")

        # 添加质量门禁部分
        if quality_gates:
            lines.append("\n---\n")
            lines.append("## Quality Gates")
            lines.append("")
            for gate in quality_gates:
                lines.append(f"- `{gate}`")
            lines.append("")

        return "\n".join(lines)

    def _generate_architecture(self, goal: str, context: Dict[str, Any]) -> str:
        """
        生成架构描述

        Args:
            goal: 目标描述
            context: 上下文信息

        Returns:
            架构描述字符串
        """
        features = context.get("features", [])
        libraries = context.get("libraries", [])

        # 简单的架构生成逻辑
        parts = []

        if "authentication" in features:
            parts.append("基于 JWT 的无状态认证架构")

        if libraries:
            libs_str = "使用 " + ", ".join(libraries[:3])
            parts.append(libs_str)

        if not parts:
            parts.append("模块化架构，遵循 SOLID 原则")

        return "。".join(parts) + "。"

    def _extract_feature_name(self, goal: str) -> str:
        """
        从目标中提取特性名称

        Args:
            goal: 目标描述

        Returns:
            特性名称
        """
        # 简单提取：取前几个关键词
        words = goal.split()[:5]
        return " ".join(words)
