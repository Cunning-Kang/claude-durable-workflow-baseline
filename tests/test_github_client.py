import pytest
from unittest.mock import Mock, patch
from scripts.github_client import GitHubClient, search_repositories


@pytest.fixture
def mock_github():
    """Mock Github API"""
    with patch('scripts.github_client.Github') as mock:
        yield mock


@pytest.fixture
def mock_token():
    """Mock GitHub token"""
    return "test_token_123"


def test_github_client_with_token(mock_github, mock_token):
    """测试使用 token 创建客户端"""
    client = GitHubClient(token=mock_token)
    assert client.token == mock_token
    mock_github.assert_called_once_with(mock_token)


def test_github_client_without_token(mock_github):
    """测试不使用 token 创建客户端"""
    client = GitHubClient(token=None)
    assert client.token is None
    # 当没有 token 时调用 Github()
    mock_github.assert_called_once_with()


def test_search_repositories_returns_results(mock_github):
    """测试搜索仓库返回结果"""
    # Mock GitHub API 响应
    mock_repo = Mock()
    mock_repo.full_name = "test/repo"
    mock_repo.description = "Test repository"
    mock_repo.stargazers_count = 1000
    mock_repo.forks_count = 100
    mock_repo.open_issues_count = 10
    mock_repo.updated_at = "2024-01-01T00:00:00Z"
    mock_repo.language = "Python"
    mock_repo.html_url = "https://github.com/test/repo"
    mock_repo.get_contributors.return_value = []  # Mock contributors

    mock_search_result = Mock()
    mock_search_result.__iter__ = Mock(return_value=iter([mock_repo]))

    mock_github_instance = mock_github.return_value
    mock_github_instance.search_repositories.return_value = mock_search_result

    # 执行搜索
    results = search_repositories("test query", token="test_token")

    # 验证
    assert len(results) == 1
    assert results[0]['name'] == "test/repo"
    assert results[0]['stars'] == 1000
    mock_github_instance.search_repositories.assert_called_once_with(
        query="test query",
        sort="stars",
        order="desc"
    )


def test_search_repositories_with_rate_limit_error(mock_github):
    """测试速率限制错误处理"""
    from github import RateLimitExceededException

    mock_github_instance = mock_github.return_value
    mock_github_instance.search_repositories.side_effect = RateLimitExceededException(
        403, {"message": "API rate limit exceeded"}
    )

    # 应该抛出异常
    with pytest.raises(RateLimitExceededException):
        search_repositories("test query", token="test_token")
