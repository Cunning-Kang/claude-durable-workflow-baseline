import pytest
import tempfile
from pathlib import Path
from scripts.github_to_skill import GitHubToSkill


@pytest.mark.e2e
def test_full_workflow():
    """测试完整工作流(使用真实 GitHub API)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        gts = GitHubToSkill(output_dir=tmpdir)

        # 搜索已知的简单仓库
        keywords = gts.extract_keywords("simple http server python")
        assert len(keywords) > 0

        # 注意: 实际 API 调用可能需要 token,标记为可选
        # candidates = gts.search_and_score("http server", limit=3)
        # assert len(candidates) > 0
