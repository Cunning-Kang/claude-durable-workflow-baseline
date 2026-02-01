"""项目扫描器 - 扫描项目结构和检测技术配置"""

from pathlib import Path
from typing import Dict, List, Any
import re


class ProjectScanner:
    """扫描项目结构，检测技术配置和现有代码"""

    # 常见入口点文件模式
    ENTRY_POINT_PATTERNS = [
        "src/main.py",
        "src/app.py",
        "app.py",
        "main.py",
        "src/index.ts",
        "src/index.js",
        "index.ts",
        "index.js",
        "server.py",
        "app.js",
        "main.go",
        "src/main.go",
    ]

    # 测试框架指示器
    TEST_FRAMEWORK_INDICATORS = {
        "pytest": [
            "pytest.ini",
            "pyproject.toml",
            "setup.cfg",
            "tox.ini",
        ],
        "jest": [
            "jest.config.js",
            "jest.config.ts",
            "jest.config.json",
            "package.json",  # 需要检查内容
        ],
        "go": [
            "go.mod",
            "*_test.go",
        ],
        "mocha": [
            ".mocharc.yml",
            ".mocharc.json",
            "mocha.opts",
        ],
        "jasmine": [
            "jasmine.json",
            "spec/support/jasmine.yml",
        ],
        "unittest": [
            # Python 的 unittest 没有特定配置文件，通过文件名模式检测
            "test_*.py",
            "*_test.py",
        ],
    }

    # 应该忽略的目录模式
    IGNORED_DIRS = {
        "node_modules",
        ".git",
        ".svn",
        ".hg",
        "__pycache__",
        "venv",
        ".venv",
        "env",
        ".env",
        "virtualenv",
        "build",
        "dist",
        "target",
        "bin",
        "obj",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        ".next",
        ".nuxt",
        "coverage",
        ".coverage",
    }

    def __init__(self, project_root: Path):
        """
        初始化项目扫描器

        Args:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)

    def detect_entry_points(self) -> List[str]:
        """
        检测项目入口点文件

        Returns:
            入口点文件路径列表（相对于项目根目录）
        """
        entry_points = []

        # 如果项目目录不存在，返回空列表
        if not self.project_root.exists():
            return entry_points

        for pattern in self.ENTRY_POINT_PATTERNS:
            path = self.project_root / pattern
            if path.exists() and path.is_file():
                # 返回相对于项目根目录的路径
                entry_points.append(pattern)

        return entry_points

    def detect_test_framework(self) -> str:
        """
        检测项目使用的测试框架

        Returns:
            测试框架名称（pytest, jest, go, mocha, jasmine, unittest, unknown）
        """
        # 如果项目目录不存在，返回 unknown
        if not self.project_root.exists():
            return "unknown"

        # 检查每种测试框架的指示器
        for framework, indicators in self.TEST_FRAMEWORK_INDICATORS.items():
            for indicator in indicators:
                if self._check_test_indicator(indicator):
                    return framework

        return "unknown"

    def get_project_structure(self) -> Dict[str, Any]:
        """
        获取项目目录结构

        Returns:
            包含 directories, files, root 的字典
        """
        directories = []
        files = []

        if not self.project_root.exists():
            return {
                "directories": [],
                "files": [],
                "root": str(self.project_root),
            }

        # 遍历项目根目录
        for item in self.project_root.iterdir():
            if item.is_dir():
                if not self._should_ignore_dir(item.name):
                    directories.append(item.name)
            elif item.is_file():
                # 只统计文件名，不包括路径
                files.append(item.name)

        return {
            "directories": sorted(directories),
            "files": sorted(files),
            "root": str(self.project_root),
        }

    def find_existing_models(self) -> List[str]:
        """
        查找项目中已存在的模型类

        Returns:
            模型类名称列表
        """
        models = []

        # 常见的模型目录位置
        model_dirs = [
            self.project_root / "src" / "models",
            self.project_root / "models",
            self.project_root / "app" / "models",
            self.project_root / "server" / "models",
            self.project_root / "src" / "entities",
            self.project_root / "entities",
        ]

        for model_dir in model_dirs:
            if model_dir.exists() and model_dir.is_dir():
                # 扫描目录中的 Python 文件
                for py_file in model_dir.glob("*.py"):
                    if py_file.name == "__init__.py":
                        continue

                    # 从文件中提取类名
                    file_models = self._extract_models_from_file(py_file)
                    models.extend(file_models)

        # 去重并返回
        return list(set(models))

    def _should_ignore_dir(self, dir_name: str) -> bool:
        """
        判断目录是否应该被忽略

        Args:
            dir_name: 目录名称

        Returns:
            True 如果应该忽略，否则 False
        """
        return dir_name in self.IGNORED_DIRS

    def _check_test_indicator(self, indicator: str) -> bool:
        """
        检查测试框架指示器是否存在

        Args:
            indicator: 指示器文件模式

        Returns:
            True 如果指示器存在，否则 False
        """
        # 处理通配符模式
        if "*" in indicator:
            # 如 test_*.py, *_test.go
            pattern = indicator.replace("*", ".*")
            regex = re.compile(f"^{pattern}$")

            for item in self.project_root.iterdir():
                if item.is_file() and regex.match(item.name):
                    return True

            # 检查常见测试目录
            test_dirs = ["tests", "test", "src/tests", "src/test"]
            for test_dir in test_dirs:
                test_path = self.project_root / test_dir
                if test_path.exists() and test_path.is_dir():
                    for item in test_path.rglob("*"):
                        if item.is_file() and regex.match(item.name):
                            return True

            return False

        # 处理普通文件名
        path = self.project_root / indicator

        if not path.exists():
            return False

        # 特殊处理 package.json（需要检查内容）
        if indicator == "package.json":
            content = path.read_text()
            # 检查是否有 jest 相关配置或依赖
            return (
                '"jest"' in content
                or '"test.*jest' in content
                or 'jest.config' in content
            )

        # 特殊处理 pyproject.toml（需要检查内容）
        if indicator == "pyproject.toml":
            content = path.read_text()
            return (
                '[tool.pytest' in content
                or 'pytest' in content
            )

        # 特殊处理 setup.cfg（需要检查内容）
        if indicator == "setup.cfg":
            content = path.read_text()
            return '[pytest]' in content or 'pytest' in content

        return True

    def _extract_models_from_file(self, file_path: Path) -> List[str]:
        """
        从 Python 文件中提取模型类名

        Args:
            file_path: Python 文件路径

        Returns:
            类名列表
        """
        models = []

        try:
            content = file_path.read_text()

            # 匹配 class 定义（简单的正则，不包括嵌套类）
            # 匹配 class ModelName 或 class ModelName(...):
            pattern = r"^class\s+([A-Z][a-zA-Z0-9_]*)"

            for line in content.split("\n"):
                match = re.match(pattern, line.strip())
                if match:
                    class_name = match.group(1)
                    # 过滤掉一些非模型类
                    if not self._is_excluded_class(class_name):
                        models.append(class_name)

        except Exception:
            # 如果读取失败，返回空列表
            pass

        return models

    def _is_excluded_class(self, class_name: str) -> bool:
        """
        判断是否应该排除某个类（非模型类）

        Args:
            class_name: 类名

        Returns:
            True 如果应该排除，否则 False
        """
        excluded_patterns = [
            "Test",  # 测试类
            "Base",  # 基类
            "Abstract",  # 抽象类
            "Mixin",  # Mixin 类
            "Config",  # 配置类
            "Exception",  # 异常类
            "Error",  # 错误类
            "Validator",  # 验证器
            "Serializer",  # 序列化器
            "View",  # 视图
            "Controller",  # 控制器
            "Router",  # 路由
        ]

        return any(pattern in class_name for pattern in excluded_patterns)
