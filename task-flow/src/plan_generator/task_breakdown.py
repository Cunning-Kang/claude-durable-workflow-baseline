"""任务分解器 - 将目标分解为可执行的小任务"""

from typing import Dict, List, Any


class TaskBreakdown:
    """将 Plan Packet Goal 分解为 bite-sized 任务"""

    # 复杂度关键词
    COMPLEXITY_KEYWORDS = {
        "low": [
            "简单", "simple", "basic", "基础",
            "添加", "add", "创建", "create",
            "配置", "config", "设置", "setup",
            "编写", "write", "实现", "implement"
        ],
        "medium": [
            "设计", "design", "重构", "refactor",
            "优化", "optimize", "集成", "integrate",
            "测试", "test", "文档", "document",
            "数据库", "database", "schema", "model",
            "接口", "api", "endpoint", "路由"
        ],
        "high": [
            "架构", "architecture", "微服务", "microservice",
            "分布式", "distributed", "性能", "performance",
            "安全", "security", "加密", "encryption",
            "完整", "complete", "系统", "system",
            "平台", "platform", "框架", "framework"
        ]
    }

    # Python 任务模板
    PYTHON_TASK_TEMPLATES = {
        "authentication": [
            {"title": "设计用户数据模型", "description": "创建 User 模型，包含必要字段"},
            {"title": "实现密码哈希", "description": "使用 bcrypt 或 argon2 进行密码加密"},
            {"title": "创建注册接口", "description": "实现 POST /api/register 端点"},
            {"title": "创建登录接口", "description": "实现 POST /api/login 端点"},
            {"title": "实现 JWT 生成", "description": "创建 token 生成逻辑"},
            {"title": "实现 token 验证", "description": "创建认证中间件或装饰器"},
            {"title": "编写单元测试", "description": "测试认证流程"},
        ],
        "user_registration": [
            {"title": "设计用户注册表单", "description": "定义注册所需字段"},
            {"title": "实现输入验证", "description": "验证邮箱、密码格式等"},
            {"title": "创建用户注册逻辑", "description": "处理用户创建流程"},
            {"title": "发送欢迎邮件", "description": "可选：实现邮件通知"},
        ],
        "default": [
            {"title": "需求分析", "description": "明确功能需求和技术方案"},
            {"title": "设计数据结构", "description": "设计数据库表结构或数据模型"},
            {"title": "实现核心逻辑", "description": "编写主要业务逻辑"},
            {"title": "编写单元测试", "description": "测试核心功能"},
            {"title": "编写文档", "description": "更新 API 文档和使用说明"},
        ]
    }

    def breakdown(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        将目标分解为任务列表

        Args:
            goal: 目标字符串
            context: 上下文信息（包含 language, features 等）

        Returns:
            任务字典列表，每个包含 title, description, estimated_time
        """
        # 生成任务
        tasks = self._generate_tasks(goal, context)

        # 验证任务
        validated_tasks = self._validate_tasks(tasks)

        return validated_tasks

    def detect_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检测任务之间的依赖关系

        Args:
            tasks: 任务列表

        Returns:
            包含依赖信息的任务列表
        """
        dependencies = []

        for i, task in enumerate(tasks):
            task_with_deps = {
                "task": task.get("title", ""),
                "depends_on": []
            }

            # 简单的依赖检测规则
            # 如果任务标题包含某些关键词，可能依赖于之前的任务
            title = task.get("title", "").lower()

            # 接口任务通常依赖于模型任务
            if any(keyword in title for keyword in ["接口", "api", "endpoint", "路由"]):
                # 查找模型任务
                for j in range(i):
                    prev_title = tasks[j].get("title", "").lower()
                    if any(keyword in prev_title for keyword in ["模型", "model", "schema", "数据结构"]):
                        task_with_deps["depends_on"].append(tasks[j].get("title", ""))

            # 测试任务依赖于实现任务
            if "测试" in title or "test" in title:
                for j in range(i):
                    prev_title = tasks[j].get("title", "")
                    if not any(keyword in prev_title.lower() for keyword in ["测试", "test", "文档", "document"]):
                        task_with_deps["depends_on"].append(prev_title)

            dependencies.append(task_with_deps)

        return dependencies

    def _validate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        验证任务列表的完整性

        Args:
            tasks: 待验证的任务列表

        Returns:
            验证后的任务列表
        """
        validated = []

        for task in tasks:
            # 确保必需字段存在
            if not task.get("title"):
                continue

            # 确保有描述
            if not task.get("description"):
                task["description"] = "实现 " + task["title"]

            # 确保有时间估算
            if not task.get("estimated_time"):
                task["estimated_time"] = self._estimate_time(task["title"])

            validated.append(task)

        return validated

    def _estimate_time(self, title: str) -> int:
        """
        估算任务所需时间（分钟）

        Args:
            title: 任务标题

        Returns:
            估算的时间（分钟）
        """
        title_lower = title.lower()

        # 检查高复杂度关键词
        for keyword in self.COMPLEXITY_KEYWORDS["high"]:
            if keyword in title_lower:
                return 120  # 2小时

        # 检查中等复杂度关键词
        for keyword in self.COMPLEXITY_KEYWORDS["medium"]:
            if keyword in title_lower:
                return 60  # 1小时

        # 默认为低复杂度
        return 30  # 30分钟

    def _generate_tasks(self, goal: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据目标生成任务列表

        Args:
            goal: 目标字符串
            context: 上下文信息

        Returns:
            任务列表
        """
        language = context.get("language", "python")
        features = context.get("features", [])

        # 提取目标中的功能特征
        goal_features = self._extract_features_from_goal(goal)

        # 合并 features 和 goal_features
        all_features = list(set(features + goal_features))

        tasks = []

        # 根据功能生成任务
        for feature in all_features:
            feature_lower = feature.lower()

            # 查找匹配的任务模板
            if language == "python" and feature_lower in self.PYTHON_TASK_TEMPLATES:
                template_tasks = self.PYTHON_TASK_TEMPLATES[feature_lower]
            else:
                template_tasks = self.PYTHON_TASK_TEMPLATES["default"]

            # 添加任务（避免重复）
            for task in template_tasks:
                task_title = task["title"]
                # 检查是否已存在相同标题的任务
                if not any(t.get("title") == task_title for t in tasks):
                    new_task = {
                        "title": task["title"],
                        "description": task["description"],
                        "estimated_time": self._estimate_time(task["title"])
                    }
                    tasks.append(new_task)

        # 如果没有生成任何任务，使用默认模板
        if not tasks:
            for task in self.PYTHON_TASK_TEMPLATES["default"]:
                tasks.append({
                    "title": task["title"],
                    "description": task["description"],
                    "estimated_time": self._estimate_time(task["title"])
                })

        return tasks

    def _extract_features_from_goal(self, goal: str) -> List[str]:
        """
        从目标字符串中提取功能特征

        Args:
            goal: 目标字符串

        Returns:
            功能特征列表
        """
        goal_lower = goal.lower()
        features = []

        # 检查已知的功能关键词
        feature_keywords = {
            "authentication": ["认证", "authentication", "auth", "登录", "login"],
            "user_registration": ["注册", "registration", "signup", "用户", "user"],
            "jwt": ["jwt", "token", "令牌"],
            "password_reset": ["密码重置", "password reset", "重置密码"],
            "database": ["数据库", "database", "db", "存储"],
            "api": ["接口", "api", "endpoint", "路由"],
        }

        for feature, keywords in feature_keywords.items():
            for keyword in keywords:
                if keyword in goal_lower and feature not in features:
                    features.append(feature)
                    break

        return features
