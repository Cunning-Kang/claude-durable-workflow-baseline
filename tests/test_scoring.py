import pytest
from datetime import datetime, timedelta
from scripts.scoring import calculate_repo_score, RepoInfo


def test_calculate_score_with_perfect_repo():
    """测试完美仓库的评分"""
    repo = RepoInfo(
        name="test/repo",
        stars=10000,
        forks=1000,
        open_issues=10,
        closed_issues=990,
        contributors=50,
        updated_at=datetime.now()
    )
    score = calculate_repo_score(repo)
    assert score >= 85  # 高分仓库
    assert score <= 100


def test_calculate_score_with_old_repo():
    """测试旧仓库的评分"""
    repo = RepoInfo(
        name="test/repo",
        stars=5000,
        forks=500,
        open_issues=100,
        closed_issues=100,
        contributors=20,
        updated_at=datetime.now() - timedelta(days=400)
    )
    score = calculate_repo_score(repo)
    assert score < 70  # 旧仓库分数较低


def test_calculate_score_with_unmaintained_repo():
    """测试未维护仓库的评分"""
    repo = RepoInfo(
        name="test/repo",
        stars=100,  # 降低 stars 数量以获得更低的分数
        forks=10,
        open_issues=200,
        closed_issues=10,
        contributors=1,
        updated_at=datetime.now() - timedelta(days=700)
    )
    score = calculate_repo_score(repo)
    assert score < 30  # 低分


def test_calculate_score_with_new_repo():
    """测试新仓库的评分"""
    repo = RepoInfo(
        name="test/repo",
        stars=100,
        forks=10,
        open_issues=5,
        closed_issues=5,
        contributors=3,
        updated_at=datetime.now() - timedelta(days=10)
    )
    score = calculate_repo_score(repo)
    assert score >= 20  # 新活跃仓库有一定分数


def test_score_does_not_exceed_100():
    """测试分数不超过100"""
    repo = RepoInfo(
        name="test/repo",
        stars=1000000,
        forks=100000,
        open_issues=0,
        closed_issues=10000,
        contributors=1000,
        updated_at=datetime.now()
    )
    score = calculate_repo_score(repo)
    assert score <= 100
