import pytest
import tempfile
from pathlib import Path
from scripts.github_to_skill import GitHubToSkill


@pytest.fixture
def temp_output():
    """临时输出目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_github_to_skill_initialization(temp_output):
    """测试初始化"""
    gts = GitHubToSkill(output_dir=temp_output)
    assert gts.output_dir == Path(temp_output)


def test_extract_keywords():
    """测试关键词提取"""
    gts = GitHubToSkill()

    # 测试简单查询
    keywords = gts.extract_keywords("I want to create a PDF converter")
    assert 'pdf' in keywords
    assert 'converter' in keywords

    # 测试复杂查询
    keywords = gts.extract_keywords("Need a tool for image processing in Python")
    assert 'image' in keywords
    assert 'processing' in keywords
    assert 'python' in keywords


def test_format_candidates():
    """测试候选格式化"""
    gts = GitHubToSkill()

    candidates = [
        {
            'name': 'test/repo1',
            'description': 'Test repo 1',
            'stars': 1000,
            'forks': 100,
            'language': 'Python',
            'score': 85.5,
            'updated_at': __import__('datetime').datetime.now()
        },
        {
            'name': 'test/repo2',
            'description': 'Test repo 2',
            'stars': 500,
            'forks': 50,
            'language': 'JavaScript',
            'score': 72.3,
            'updated_at': __import__('datetime').datetime.now()
        }
    ]

    formatted = gts.format_candidates(candidates)
    assert '[1]' in formatted
    assert 'test/repo1' in formatted
    assert '85.5' in formatted


def test_select_candidate_non_interactive():
    """测试非交互式选择"""
    gts = GitHubToSkill()

    candidates = [
        {
            'name': 'test/repo1',
            'description': 'Test repo 1',
            'stars': 1000,
        },
        {
            'name': 'test/repo2',
            'description': 'Test repo 2',
            'stars': 500,
        }
    ]

    # 非交互模式应该返回第一个
    selected = gts.select_candidate(candidates, interactive=False)
    assert selected['name'] == 'test/repo1'


def test_select_candidate_single():
    """测试单个候选时自动选择"""
    gts = GitHubToSkill()

    candidates = [
        {
            'name': 'test/repo1',
            'description': 'Test repo 1',
            'stars': 1000,
        }
    ]

    # 即使交互模式,单个候选也应该自动选择
    selected = gts.select_candidate(candidates, interactive=True)
    assert selected['name'] == 'test/repo1'


def test_cleanup_clone(temp_output):
    """测试清理克隆目录"""
    from unittest.mock import patch

    gts = GitHubToSkill(output_dir=temp_output)

    # 创建测试目录
    test_dir = Path(temp_output) / "test_clone"
    test_dir.mkdir()
    (test_dir / "test.txt").write_text("test")

    assert test_dir.exists()

    # 清理
    gts._cleanup_clone(test_dir)

    assert not test_dir.exists()

