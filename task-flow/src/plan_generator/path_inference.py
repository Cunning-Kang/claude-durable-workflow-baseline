"""路径推断器 - 根据功能名称推断文件路径"""

from typing import Dict, List
import re


class PathInference:
    """根据功能名称推断文件路径"""

    # Python 项目路径模板
    PYTHON_PATHS: Dict[str, str] = {
        "model": "src/models/{name}.py",
        "service": "src/services/{name}.py",
        "api": "src/api/routes/{name}.py",
        "middleware": "src/middleware/{name}.py",
        "util": "src/utils/{name}.py",
        "config": "src/config/{name}.py",
        "schema": "src/schemas/{name}.py",
        "default": "src/{name}.py",
    }

    # JavaScript/TypeScript 项目路径模板
    JAVASCRIPT_PATHS: Dict[str, str] = {
        "component": "components/{name}.tsx",
        "hook": "hooks/{name}.ts",
        "util": "utils/{name}.ts",
        "service": "services/{name}.ts",
        "api": "api/{name}.ts",
        "type": "types/{name}.ts",
        "store": "store/{name}.ts",
        "middleware": "middleware/{name}.ts",
        "default": "src/{name}.ts",
    }

    # Go 项目路径模板
    GO_PATHS: Dict[str, str] = {
        "model": "models/{name}.go",
        "handler": "handlers/{name}.go",
        "service": "services/{name}.go",
        "middleware": "middleware/{name}.go",
        "util": "utils/{name}.go",
        "config": "config/{name}.go",
        "default": "{name}.go",
    }

    # 功能类型检测关键词
    FEATURE_TYPE_PATTERNS: Dict[str, List[str]] = {
        "model": [
            r".*Model$", r"User$", r"Product$", r"Order$", r"Profile$",
            r"Entity$", r"Record$", r"Item$", r"Resource$"
        ],
        "service": [
            r".*Service$", r".*Manager$", r".*Handler$",
            r"Auth$", r"Email$", r"Payment$", r"Notification$"
        ],
        "api": [
            r".*Routes$", r".*Controller$", r".*Endpoint$",
            r".*API$", r".*View$"
        ],
        "middleware": [
            r".*Middleware$", r".*Interceptor$", r".*Guard$"
        ],
        "component": [
            r".*Component$", r".*Page$", r".*View$",
            r"User.*", r"Auth.*", r"Dashboard$", r"Header$", r"Footer$"
        ],
        "hook": [
            r"use[A-Z].*"
        ],
        "util": [
            r".*Util$", r".*Helper$", r".*Formatter$",
            r"format.*", r"parse.*", r"validate.*"
        ],
        "config": [
            r".*Config$", r".*Settings$", r".*Options$"
        ],
        "schema": [
            r".*Schema$", r".*DTO$", r".*Request$", r".*Response$"
        ],
    }

    def infer(self, feature: str, project_type: str, tech_stack: List[str]) -> str:
        """
        根据功能名称推断文件路径

        Args:
            feature: 功能名称（如 User, AuthService, UserProfile）
            project_type: 项目类型（python, javascript, go）
            tech_stack: 技术栈列表

        Returns:
            推断的文件路径
        """
        # 检测功能类型
        feature_type = self._detect_feature_type(feature)

        # 根据项目类型获取路径模板
        path_template = self._get_path_template(project_type, feature_type)

        # 清理功能名称（移除常见后缀）
        cleaned_feature = self._clean_feature_name(feature, feature_type)

        # 转换功能名称为文件名格式
        filename = self._convert_to_filename(cleaned_feature, project_type)

        # 生成路径
        path = path_template.format(name=filename)

        return path

    def infer_test_path(self, source_path: str, test_framework: str) -> str:
        """
        根据源文件路径推断测试文件路径

        Args:
            source_path: 源文件路径
            test_framework: 测试框架（pytest, jest, go）

        Returns:
            测试文件路径
        """
        if test_framework == "pytest":
            # Python pytest: src/models/user.py -> tests/models/test_user.py
            path_parts = source_path.split("/")

            # 找到 src 目录并替换为 tests
            if "src/" in source_path:
                test_path = source_path.replace("src/", "tests/")

                # 在文件名前添加 test_
                filename = path_parts[-1]
                if filename.endswith(".py"):
                    name_without_ext = filename[:-3]
                    test_filename = f"test_{name_without_ext}.py"
                    test_path = test_path.replace(filename, test_filename)

                return test_path
            else:
                # 如果没有 src，直接在当前目录添加 test_ 前缀
                filename = path_parts[-1]
                if filename.endswith(".py"):
                    name_without_ext = filename[:-3]
                    test_filename = f"test_{name_without_ext}.py"
                    path_parts[-1] = test_filename
                    return "/".join(path_parts)

        elif test_framework == "jest":
            # JavaScript Jest: components/UserProfile.tsx -> components/__tests__/UserProfile.test.tsx
            path_parts = source_path.split("/")
            filename = path_parts[-1]

            if "." in filename:
                name_without_ext = filename.rsplit(".", 1)[0]
                ext = filename.rsplit(".", 1)[1]
                test_filename = f"{name_without_ext}.test.{ext}"
            else:
                test_filename = f"{filename}.test"

            # 替换文件名
            path_parts[-1] = test_filename

            # 在倒数第二个位置插入 __tests__
            path_parts.insert(-1, "__tests__")

            return "/".join(path_parts)

        elif test_framework == "go":
            # Go: models/user.go -> models/user_test.go
            if source_path.endswith(".go"):
                test_path = source_path.replace(".go", "_test.go")
                return test_path

        # 默认：在同一目录添加 test 前缀
        path_parts = source_path.split("/")
        filename = path_parts[-1]

        if "." in filename:
            name_without_ext = filename.rsplit(".", 1)[0]
            ext = filename.rsplit(".", 1)[1]
            test_filename = f"test_{name_without_ext}.{ext}"
        else:
            test_filename = f"test_{filename}"

        path_parts[-1] = test_filename
        return "/".join(path_parts)

    def _detect_feature_type(self, feature: str) -> str:
        """
        检测功能类型

        Args:
            feature: 功能名称

        Returns:
            功能类型（model, service, api, component, hook, util, middleware, config, schema, default）
        """
        feature_lower = feature.lower()

        # 检查每种类型的模式
        for feature_type, patterns in self.FEATURE_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, feature, re.IGNORECASE):
                    return feature_type

        # 默认返回
        return "default"

    def _get_path_template(self, language: str, feature_type: str) -> str:
        """
        获取路径模板

        Args:
            language: 编程语言
            feature_type: 功能类型

        Returns:
            路径模板字符串
        """
        language_lower = language.lower()

        # 根据语言选择路径字典
        if language_lower == "python":
            paths = self.PYTHON_PATHS
        elif language_lower in ["javascript", "typescript", "js", "ts"]:
            paths = self.JAVASCRIPT_PATHS
        elif language_lower == "go":
            paths = self.GO_PATHS
        else:
            # 默认使用 Python 路径
            paths = self.PYTHON_PATHS

        # 返回对应类型的路径，如果不存在则返回 default
        return paths.get(feature_type, paths.get("default", "{name}.py"))

    def _convert_to_filename(self, feature: str, project_type: str) -> str:
        """
        转换功能名称为文件名格式

        Args:
            feature: 功能名称
            project_type: 项目类型

        Returns:
            文件名
        """
        # 转换为小写或保留驼峰命名
        if project_type.lower() in ["javascript", "typescript", "js", "ts"]:
            # JavaScript/TypeScript 保留驼峰命名
            filename = feature
        elif project_type.lower() == "go":
            # Go 使用蛇形命名（Go 文件名通常是小写）
            filename = self._camel_to_snake(feature)
        else:
            # Python 使用蛇形命名
            filename = self._camel_to_snake(feature)

        return filename

    def _camel_to_snake(self, name: str) -> str:
        """
        将驼峰命名转换为蛇形命名

        Args:
            name: 驼峰命名的字符串

        Returns:
            蛇形命名的字符串
        """
        # 在大写字母前插入下划线
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        # 处理连续大写字母
        snake = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        # 转换为小写
        return snake.lower()

    def _clean_feature_name(self, feature: str, feature_type: str) -> str:
        """
        清理功能名称，移除常见的类型后缀

        Args:
            feature: 功能名称
            feature_type: 功能类型

        Returns:
            清理后的功能名称
        """
        # 定义需要移除的后缀（service 不移除后缀）
        suffixes_to_remove = {
            "api": ["Routes", "Controller", "Endpoint", "API", "View"],
            "service": [],  # 服务保留 Service 后缀
            "model": ["Model", "Entity", "Record"],
            "middleware": ["Middleware", "Interceptor", "Guard"],
            "component": ["Component", "View"],
            "util": ["Util", "Helper", "Formatter"],
            "config": ["Config", "Settings", "Options"],
            "schema": ["Schema", "DTO"],
        }

        # 获取需要移除的后缀列表
        suffixes = suffixes_to_remove.get(feature_type, [])

        # 移除匹配的后缀
        for suffix in suffixes:
            if feature.endswith(suffix):
                return feature[:-len(suffix)]

        return feature
