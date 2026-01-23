import os
from typing import List, Dict, Optional
from itertools import islice
from github import Github, GithubException, RateLimitExceededException
from datetime import datetime
from scripts.scoring import calculate_repo_score


class GitHubClient:
    """GitHub API 客户端"""

    def __init__(self, token: Optional[str] = None):
        """
        初始化 GitHub 客户端

        Args:
            token: GitHub Personal Access Token (可选)
        """
        if token is None:
            # 尝试从环境变量或文件读取
            token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
            if token is None and os.path.exists(os.path.expanduser("~/.github-token")):
                with open(os.path.expanduser("~/.github-token")) as f:
                    token = f.read().strip()

        self.token = token
        if token:
            self.github = Github(token)
        else:
            self.github = Github()

    def search_repos(self, query: str, limit: int = 10) -> List[Dict]:
        """
        搜索仓库

        Args:
            query: 搜索查询
            limit: 返回结果数量限制

        Returns:
            仓库信息列表

        Raises:
            RateLimitExceededException: 超过速率限制
            GithubException: 其他 GitHub API 错误
        """
        try:
            # 搜索仓库
            repos = self.github.search_repositories(
                query=query,
                sort="stars",
                order="desc"
            )

            results = []
            for repo in islice(repos, limit):
                # 获取 contributors 数量
                try:
                    contributors = list(repo.get_contributors())[:50]  # 限制获取数量
                    contributor_count = len(contributors)
                except:
                    contributor_count = 1

                # 获取 issues 统计
                try:
                    open_issues = repo.open_issues_count
                    # 估算 closed issues (API 不直接提供)
                    closed_issues = min(open_issues * 2, 1000)  # 简化估算
                except:
                    open_issues = 0
                    closed_issues = 0

                results.append({
                    'name': repo.full_name,
                    'description': repo.description or "No description",
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'open_issues': open_issues,
                    'closed_issues': closed_issues,
                    'contributors': contributor_count,
                    'language': repo.language or "Unknown",
                    'updated_at': repo.updated_at,
                    'url': repo.html_url
                })

            return results

        except RateLimitExceededException as e:
            raise RateLimitExceededException(
                e.status,
                {**e.data, "message": "GitHub API rate limit exceeded. Please provide a token or wait."}
            )
        except GithubException as e:
            raise GithubException(
                e.status,
                {**e.data, "message": f"GitHub API error: {e}"}
            )


def search_repositories(query: str, token: Optional[str] = None, limit: int = 10) -> List[Dict]:
    """
    搜索 GitHub 仓库的便捷函数

    Args:
        query: 搜索查询
        token: GitHub token (可选)
        limit: 结果数量限制

    Returns:
        仓库信息列表
    """
    client = GitHubClient(token=token)
    return client.search_repos(query, limit=limit)
