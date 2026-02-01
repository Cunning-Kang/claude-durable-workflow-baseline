"""目标分析器 - 从 Plan Packet Goal 提取技术需求"""

from typing import Dict, List, Any


class GoalAnalyzer:
    """分析 Plan Packet 的 Goal 字段，提取技术需求"""

    # 语言映射
    LANGUAGE_MAP = {
        "python": "python",
        "python3": "python",
        "py": "python",
        "javascript": "javascript",
        "typescript": "javascript",
        "ts": "javascript",
        "js": "javascript",
        "java": "java",
        "go": "go",
        "golang": "go",
        "rust": "rust",
        "ruby": "ruby",
        "php": "php",
        "c++": "cpp",
        "cpp": "cpp",
        "c#": "csharp",
        "csharp": "csharp",
    }

    # 常见技术关键词映射
    KEYWORD_PATTERNS = {
        "jwt": ["jwt", "json web token"],
        "authentication": ["认证", "authentication", "auth"],
        "user_registration": ["用户注册", "注册", "registration", "signup"],
        "login": ["登录", "login", "signin"],
        "token_refresh": ["token刷新", "token refresh", "refresh token"],
        "password_reset": ["密码重置", "password reset", "reset password"],
    }

    def extract_requirements(self, plan_packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        从 Plan Packet 提取技术需求

        Args:
            plan_packet: 包含 goal 和 context 的字典

        Returns:
            包含 language, libraries, features 的字典

        Raises:
            ValueError: 当 goal 为空时
        """
        goal = plan_packet.get("goal", "").strip()
        if not goal:
            raise ValueError("Goal cannot be empty")

        context = plan_packet.get("context", {})
        tech_stack = context.get("tech_stack", [])

        # 检测编程语言
        language = self._detect_language(tech_stack)

        # 提取库
        libraries = self._extract_libraries(goal)

        # 提取功能
        features = self._extract_features(goal)

        return {
            "language": language,
            "libraries": libraries,
            "features": features,
        }

    def _detect_language(self, tech_stack: List[str]) -> str:
        """
        从技术栈检测编程语言

        Args:
            tech_stack: 技术栈列表

        Returns:
            编程语言字符串
        """
        for tech in tech_stack:
            tech_lower = tech.lower()
            if tech_lower in self.LANGUAGE_MAP:
                return self.LANGUAGE_MAP[tech_lower]

        # 默认返回 python
        return "python"

    def _extract_libraries(self, goal: str) -> List[str]:
        """
        从 Goal 提取库/框架

        Args:
            goal: 目标字符串

        Returns:
            库名称列表
        """
        goal_lower = goal.lower()
        libraries = []

        # 检查已知关键词
        for keyword, patterns in self.KEYWORD_PATTERNS.items():
            for pattern in patterns:
                if pattern in goal_lower:
                    if keyword not in libraries:
                        libraries.append(keyword)

        return libraries

    def _extract_features(self, goal: str) -> List[str]:
        """
        从 Goal 提取功能列表

        Args:
            goal: 目标字符串

        Returns:
            功能名称列表
        """
        goal_lower = goal.lower()
        features = []

        # 使用关键词模式提取功能
        for feature_name, patterns in self.KEYWORD_PATTERNS.items():
            for pattern in patterns:
                if pattern in goal_lower:
                    # 将关键词转换为功能名（如 jwt -> jwt, authentication -> authentication）
                    if feature_name not in features:
                        features.append(feature_name)

        return features
