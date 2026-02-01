"""测试 ProjectScanner"""

import pytest
from pathlib import Path
from plan_generator.project_scanner import ProjectScanner


class TestProjectScanner:
    """测试项目扫描器"""

    def test_scan_project_detect_entry_points(self, temp_project_dir):
        """测试检测项目入口点"""
        # 创建典型的 Python 项目入口点
        (temp_project_dir / "src" / "main.py").parent.mkdir(parents=True, exist_ok=True)
        (temp_project_dir / "src" / "main.py").write_text("print('main')")

        scanner = ProjectScanner(temp_project_dir)
        entry_points = scanner.detect_entry_points()

        assert len(entry_points) > 0
        assert "src/main.py" in entry_points

    def test_scan_project_detect_test_framework_pytest(self, temp_project_dir):
        """测试检测 pytest 测试框架"""
        # 创建 pytest 标记文件
        (temp_project_dir / "pytest.ini").write_text("[pytest]\naddopts = -v")

        scanner = ProjectScanner(temp_project_dir)
        framework = scanner.detect_test_framework()

        assert framework == "pytest"

    def test_scan_project_detect_test_framework_jest(self, temp_project_dir):
        """测试检测 Jest 测试框架"""
        # 创建 Jest 配置文件
        (temp_project_dir / "jest.config.js").write_text("module.exports = {};")

        scanner = ProjectScanner(temp_project_dir)
        framework = scanner.detect_test_framework()

        assert framework == "jest"

    def test_scan_project_detect_test_framework_unknown(self, temp_project_dir):
        """测试未知测试框架"""
        # 空目录，没有任何测试框架标记

        scanner = ProjectScanner(temp_project_dir)
        framework = scanner.detect_test_framework()

        assert framework == "unknown"

    def test_scan_project_get_project_structure(self, temp_project_dir):
        """测试获取项目结构"""
        # 创建典型项目结构
        (temp_project_dir / "src").mkdir()
        (temp_project_dir / "tests").mkdir()
        (temp_project_dir / "docs").mkdir()
        (temp_project_dir / "README.md").write_text("# My Project")
        (temp_project_dir / "src" / "app.py").write_text("print('app')")

        scanner = ProjectScanner(temp_project_dir)
        structure = scanner.get_project_structure()

        assert "directories" in structure
        assert "src" in structure["directories"]
        assert "tests" in structure["directories"]
        assert "docs" in structure["directories"]
        assert structure["root"] == str(temp_project_dir)
        assert len(structure["files"]) > 0

    def test_scan_project_find_existing_models(self, temp_project_dir):
        """测试查找现有模型"""
        # 创建 Python 项目中的模型文件
        models_dir = temp_project_dir / "src" / "models"
        models_dir.mkdir(parents=True, exist_ok=True)

        (models_dir / "user.py").write_text("class User:\n    pass")
        (models_dir / "product.py").write_text("class Product:\n    pass")
        (models_dir / "__init__.py").write_text("")

        scanner = ProjectScanner(temp_project_dir)
        models = scanner.find_existing_models()

        assert len(models) > 0
        assert "User" in models
        assert "Product" in models

    def test_should_ignore_node_modules(self, temp_project_dir):
        """测试应该忽略 node_modules 目录"""
        (temp_project_dir / "node_modules").mkdir()
        (temp_project_dir / "node_modules" / "package").mkdir()

        scanner = ProjectScanner(temp_project_dir)
        structure = scanner.get_project_structure()

        # node_modules 不应该在目录列表中
        assert "node_modules" not in structure["directories"]

    def test_should_ignore_git_directory(self, temp_project_dir):
        """测试应该忽略 .git 目录"""
        (temp_project_dir / ".git").mkdir()
        (temp_project_dir / ".git" / "objects").mkdir()

        scanner = ProjectScanner(temp_project_dir)
        structure = scanner.get_project_structure()

        # .git 不应该在目录列表中
        assert ".git" not in structure["directories"]

    def test_should_ignore_venv_directory(self, temp_project_dir):
        """测试应该忽略虚拟环境目录"""
        (temp_project_dir / "venv").mkdir()
        (temp_project_dir / ".venv").mkdir()
        (temp_project_dir / "env").mkdir()

        scanner = ProjectScanner(temp_project_dir)
        structure = scanner.get_project_structure()

        # 虚拟环境目录不应该在目录列表中
        assert "venv" not in structure["directories"]
        assert ".venv" not in structure["directories"]
        assert "env" not in structure["directories"]
