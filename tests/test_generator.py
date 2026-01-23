import pytest
import tempfile
import os
from pathlib import Path
from scripts.generator import SkillGenerator


@pytest.fixture
def sample_analysis():
    """示例分析结果"""
    return {
        'readme': {
            'title': 'Test Tool',
            'description': 'A test tool',
            'sections': {
                'Installation': 'pip install test-tool',
                'Usage': 'testtool.run()'
            },
            'examples': [('python', 'import testtool')]
        },
        'language': 'python',
        'structure': {
            'directories': ['src', 'tests'],
            'main_files': ['setup.py'],
            'test_files': ['test_tool.py'],
            'doc_files': ['README.md']
        },
        'dependencies': ['requests', 'click'],
        'tool_type': 'python-library'
    }


@pytest.fixture
def sample_repo_info():
    """示例仓库信息"""
    return {
        'name': 'test/tool',
        'description': 'Test tool for testing',
        'stars': 1000,
        'url': 'https://github.com/test/tool'
    }


def test_generator_initialization():
    """测试生成器初始化"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = SkillGenerator(tmpdir)
        assert str(generator.output_dir) == tmpdir


def test_generate_skill_md(sample_analysis, sample_repo_info):
    """测试生成 SKILL.md"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = SkillGenerator(tmpdir)
        output_path = generator.generate_skill_md(sample_repo_info, sample_analysis)

        assert output_path.exists()
        content = output_path.read_text()

        assert 'name:' in content
        assert 'description:' in content
        assert 'Test Tool' in content


def test_generate_skill_full(sample_analysis, sample_repo_info):
    """测试完整生成流程"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = SkillGenerator(tmpdir)
        skill_dir = generator.generate(sample_repo_info, sample_analysis)

        assert skill_dir.exists()
        assert (skill_dir / 'SKILL.md').exists()
