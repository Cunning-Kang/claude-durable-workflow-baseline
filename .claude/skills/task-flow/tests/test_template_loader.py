"""Tests for TemplateLoader"""

import pytest
from pathlib import Path

from config.template_loader import TemplateLoader
from config.exceptions import TemplateNotFoundError


@pytest.fixture
def builtin_loader():
    """加载项目内置模板目录"""
    skill_dir = Path(__file__).parent.parent
    return TemplateLoader(skill_dir=skill_dir)


class TestTemplateLoader:
    """模板加载器测试"""

    def test_load_existing_template(self, tmp_path):
        """加载存在的模板"""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "minimal.md"
        template_file.write_text("Test template with {VERSION}")

        loader = TemplateLoader(skill_dir=tmp_path)
        content = loader.load_template("minimal")

        assert "Test template" in content
        assert "{VERSION}" in content

    def test_load_nonexistent_template(self, tmp_path):
        """加载不存在的模板"""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        loader = TemplateLoader(skill_dir=tmp_path)

        with pytest.raises(TemplateNotFoundError, match="Template.*not found"):
            loader.load_template("nonexistent")

    def test_template_exists(self, tmp_path):
        """检查模板是否存在"""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "minimal.md").touch()

        loader = TemplateLoader(skill_dir=tmp_path)

        assert loader.template_exists("minimal") is True
        assert loader.template_exists("nonexistent") is False

    def test_list_available_templates(self, tmp_path):
        """列出可用模板"""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "minimal.md").touch()
        (template_dir / "standard.md").touch()
        (template_dir / "full.md").touch()

        loader = TemplateLoader(skill_dir=tmp_path)
        templates = loader._list_available_templates()

        assert "minimal" in templates
        assert "standard" in templates
        assert "full" in templates

    def test_get_section_template(self, tmp_path):
        """获取章节模板"""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "section_template.md").write_text("Section content")

        loader = TemplateLoader(skill_dir=tmp_path)
        content = loader.get_section_template()

        assert "Section content" in content

    def test_template_dir_not_found(self):
        """模板目录不存在时使用默认路径"""
        loader = TemplateLoader(skill_dir=Path("/nonexistent"))
        assert loader is not None

    def test_builtin_standard_template_contains_machine_readable_start_task_contract(self, builtin_loader):
        """standard 内置模板应使用 active/events 机器可读流转"""
        content = builtin_loader.load_template("standard")

        assert "启动任务（docs gate + active registry + events + PLAN 路由）" in content
        assert "task_plan.md" not in content
        assert "findings.md" not in content
        assert "progress.md" not in content

    def test_builtin_minimal_template_contains_machine_readable_start_task_description(self, builtin_loader):
        """minimal 内置模板包含 machine-readable start-task 描述"""
        content = builtin_loader.load_template("minimal")

        assert "启动任务（docs gate/active/events/PLAN）" in content
        assert "sidecar" not in content

    def test_builtin_full_template_contains_machine_readable_start_task_and_metadata_term(self, builtin_loader):
        """full 内置模板包含 machine-readable start-task 描述与第 8 项新术语"""
        content = builtin_loader.load_template("full")

        assert "启动任务（docs gate + active registry + events + PLAN 路由）" in content
        assert "任务元数据（Task Metadata）" in content
        assert "task_plan.md" not in content
        assert "findings.md" not in content
        assert "progress.md" not in content
