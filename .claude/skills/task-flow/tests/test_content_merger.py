"""Tests for ContentMerger"""

import pytest

from config.content_merger import ContentMerger


class TestContentMerger:
    """内容合并器测试"""

    def setup_method(self):
        """每个测试前创建新的 merger"""
        self.merger = ContentMerger()

    def test_merge_new_content_empty_file(self):
        """合并到空文件"""
        existing = ""
        new_section = (
            "<!-- TASK-FLOW-VERSION:2.2.0 -->\n"
            "<!-- TASK-FLOW-SECTION -->\n"
            "New content\n"
            "<!-- END-TASK-FLOW-SECTION -->\n"
        )

        result = self.merger.merge_content(existing, new_section, "2.2.0")

        assert "New content" in result
        assert "TASK-FLOW-SECTION" in result

    def test_merge_new_content_append(self):
        """合并新内容：追加到文件末尾"""
        existing = "# Project\n\nSome content\n"
        new_section = (
            "<!-- TASK-FLOW-VERSION:2.2.0 -->\n"
            "<!-- TASK-FLOW-SECTION -->\n"
            "New content\n"
            "<!-- END-TASK-FLOW-SECTION -->\n"
        )

        result = self.merger.merge_content(existing, new_section, "2.2.0")

        assert result.startswith("# Project")
        assert "New content" in result
        assert "TASK-FLOW-SECTION" in result

    def test_replace_existing_content(self):
        """替换现有内容"""
        existing = (
            "# Project\n"
            "<!-- TASK-FLOW-VERSION:2.1.0 -->\n"
            "<!-- TASK-FLOW-SECTION -->\n"
            "Old content\n"
            "<!-- END-TASK-FLOW-SECTION -->\n"
        )
        new_section = (
            "<!-- TASK-FLOW-VERSION:2.2.0 -->\n"
            "<!-- TASK-FLOW-SECTION -->\n"
            "New content\n"
            "<!-- END-TASK-FLOW-SECTION -->\n"
        )

        result = self.merger.merge_content(existing, new_section, "2.2.0")

        assert "Old content" not in result
        assert "New content" in result
        assert "TASK-FLOW-VERSION:2.2.0" in result

    def test_find_insertion_point_empty(self):
        """查找插入位置：空文件"""
        index = self.merger.find_insertion_point("")
        assert index == 0

    def test_find_insertion_point_end(self):
        """查找插入位置：无工作流章节，返回末尾"""
        content = "# Project\n\nSome content\n"
        index = self.merger.find_insertion_point(content)
        assert index == len(content)

    @pytest.mark.parametrize("content,expected", [
        ("# Project\n## Quick Start\n", 10),
        ("# Project\n## Workflow\n", 10),
        ("# Project\n## 工作流\n", 10),
        ("# Project\n## Development\n", 10),
    ])
    def test_find_insertion_point_before_heading(self, content, expected):
        """查找插入位置：工作流章节前"""
        index = self.merger.find_insertion_point(content)
        assert index == expected

    def test_is_workflow_heading(self):
        """检测工作流章节标题"""
        assert self.merger._is_workflow_heading("## Workflow") is True
        assert self.merger._is_workflow_heading("## Quick Start") is True
        assert self.merger._is_workflow_heading("## 工作流") is True
        assert self.merger._is_workflow_heading("# Development") is True
        assert self.merger._is_workflow_heading("## Something Else") is False

    def test_detect_existing_version(self):
        """检测现有版本"""
        content = (
            "# Project\n"
            "<!-- TASK-FLOW-VERSION:2.1.0 -->\n"
            "Content\n"
        )
        version = self.merger.detect_existing_version(content)
        assert version == "2.1.0"

    def test_detect_existing_version_none(self):
        """检测版本：无版本标记"""
        content = "# Project\nContent\n"
        version = self.merger.detect_existing_version(content)
        assert version is None

    def test_needs_update_true(self):
        """需要更新：版本低于当前"""
        existing = (
            "<!-- TASK-FLOW-VERSION:2.0.0 -->\n"
            "<!-- TASK-FLOW-SECTION -->\n"
            "<!-- END-TASK-FLOW-SECTION -->\n"
        )
        assert self.merger.needs_update(existing, "2.2.0") is True

    def test_needs_update_false(self):
        """无需更新：已是最新版本"""
        existing = (
            "<!-- TASK-FLOW-VERSION:2.2.0 -->\n"
            "<!-- TASK-FLOW-SECTION -->\n"
            "<!-- END-TASK-FLOW-SECTION -->\n"
        )
        assert self.merger.needs_update(existing, "2.2.0") is False

    def test_needs_update_no_existing(self):
        """需要更新：无现有内容"""
        existing = "# Project\nContent\n"
        assert self.merger.needs_update(existing, "2.2.0") is True

    def test_has_taskflow_section_true(self):
        """检查：有 task-flow 章节"""
        content = (
            "# Project\n"
            "<!-- TASK-FLOW-VERSION:2.2.0 -->\n"
            "<!-- TASK-FLOW-SECTION -->\n"
            "Content\n"
            "<!-- END-TASK-FLOW-SECTION -->\n"
        )
        assert self.merger.has_taskflow_section(content) is True

    def test_has_taskflow_section_false(self):
        """检查：无 task-flow 章节"""
        content = "# Project\nContent\n"
        assert self.merger.has_taskflow_section(content) is False

    def test_extract_taskflow_section(self):
        """提取 task-flow 章节"""
        content = (
            "# Project\n"
            "<!-- TASK-FLOW-VERSION:2.2.0 -->\n"
            "<!-- TASK-FLOW-SECTION -->\n"
            "Content\n"
            "<!-- END-TASK-FLOW-SECTION -->\n"
        )
        section = self.merger.extract_taskflow_section(content)
        assert section is not None
        assert "TASK-FLOW-VERSION:2.2.0" in section
        assert "Content" in section

    def test_extract_taskflow_section_none(self):
        """提取：无 task-flow 章节"""
        content = "# Project\nContent\n"
        section = self.merger.extract_taskflow_section(content)
        assert section is None
