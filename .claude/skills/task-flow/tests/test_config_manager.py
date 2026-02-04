"""Tests for ConfigManager"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from config.manager import ConfigManager


class TestConfigManager:
    """配置管理器测试"""

    def test_is_initialized_with_marker(self):
        """已初始化项目：标记文件存在"""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ConfigManager.INIT_MARKER).touch()

            assert ConfigManager.is_initialized(root) is True

    def test_is_initialized_without_marker(self):
        """未初始化项目：标记文件不存在"""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            assert ConfigManager.is_initialized(root) is False

    def test_detect_existing_version(self):
        """检测现有版本"""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            claudemd = root / "CLAUDE.md"
            claudemd.write_text(
                "<!-- TASK-FLOW-VERSION:2.1.0 -->\n"
                "<!-- TASK-FLOW-SECTION -->\n"
                "content\n"
                "<!-- END-TASK-FLOW-SECTION -->\n"
            )

            manager = ConfigManager(root)
            version = manager.detect_existing_version()
            assert version == "2.1.0"

    def test_detect_version_no_marker(self):
        """无版本标记：返回 None"""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            claudemd = root / "CLAUDE.md"
            claudemd.write_text("# Project Docs\n")

            manager = ConfigManager(root)
            version = manager.detect_existing_version()
            assert version is None

    def test_needs_update_true(self):
        """需要更新：版本低于当前"""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            claudemd = root / "CLAUDE.md"
            claudemd.write_text(
                "<!-- TASK-FLOW-VERSION:2.0.0 -->\n"
                "<!-- TASK-FLOW-SECTION -->\n"
                "<!-- END-TASK-FLOW-SECTION -->\n"
            )

            manager = ConfigManager(root)
            assert manager.needs_update() is True

    def test_needs_update_false(self):
        """无需更新：已是最新版本"""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            current = ConfigManager.CURRENT_VERSION
            claudemd = root / "CLAUDE.md"
            claudemd.write_text(
                f"<!-- TASK-FLOW-VERSION:{current} -->\n"
                "<!-- TASK-FLOW-SECTION -->\n"
                "<!-- END-TASK-FLOW-SECTION -->\n"
            )

            manager = ConfigManager(root)
            assert manager.needs_update() is False

    @pytest.mark.parametrize("filename,expected", [
        ("CLAUDE.md", "CLAUDE.md"),
        ("AGENTS.md", "AGENTS.md"),
    ])
    def test_find_config_file(self, filename, expected):
        """查找配置文件"""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / filename).write_text("# Test\n")

            manager = ConfigManager(root)
            if expected:
                assert manager.config_file.name == expected

    def test_is_ci_environment(self):
        """测试 CI 环境检测"""
        assert ConfigManager.is_ci_environment() is False

    def test_get_status(self):
        """获取状态信息"""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            manager = ConfigManager(root)
            status = manager.get_status()

            assert hasattr(status, 'initialized')
            assert hasattr(status, 'config_file')
            assert hasattr(status, 'existing_version')
            assert hasattr(status, 'current_version')
            assert hasattr(status, 'needs_update')
            assert hasattr(status, 'is_ci')
            assert status.current_version == '2.3.0'


class TestConfigManagerIntegration:
    """集成测试"""

    def test_full_initialization_flow(self, tmp_path):
        """完整初始化流程"""
        root = tmp_path

        assert ConfigManager.is_initialized(root) is False

        manager = ConfigManager(root)

        from config.template_loader import TemplateLoader

        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "minimal.md").write_text("# Test Template\nContent here.")

        loader = TemplateLoader(skill_dir=tmp_path)
        manager._template_loader = loader

        result = manager.initialize(
            template_type="minimal",
            interactive=False
        )

        assert result.success is True
        assert (root / "CLAUDE.md").exists()
        assert (root / ConfigManager.INIT_MARKER).exists()
        assert ConfigManager.is_initialized(root) is True
