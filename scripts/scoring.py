import math
from datetime import datetime
from dataclasses import dataclass


@dataclass
class RepoInfo:
    """仓库信息"""
    name: str
    stars: int
    forks: int
    open_issues: int
    closed_issues: int
    contributors: int
    updated_at: datetime


def calculate_repo_score(repo: RepoInfo) -> float:
    """
    计算仓库综合评分

    评分组成:
    - Stars (30%): 使用对数避免大数优势
    - 更新时间 (25%): 最近更新的得分高
    - Issues 响应率 (20%): closed/(open+closed)
    - Forks (15%): 使用对数
    - Contributors (10%): 贡献者数量

    Returns:
        float: 0-100 的评分
    """
    # Stars 分数 (30%)
    stars_score = min(math.log(repo.stars + 1) * 3, 30)

    # 更新时间分数 (25%)
    days_since_update = (datetime.now() - repo.updated_at).days
    if days_since_update <= 30:
        update_score = 25
    elif days_since_update <= 90:
        update_score = 20
    elif days_since_update <= 180:
        update_score = 15
    elif days_since_update <= 365:
        update_score = 10
    else:
        update_score = 5

    # Issues 响应率 (20%)
    total_issues = repo.open_issues + repo.closed_issues
    if total_issues > 0:
        issues_score = (repo.closed_issues / total_issues) * 20
    else:
        issues_score = 10  # 默认中等分数

    # Forks 分数 (15%)
    forks_score = min(math.log(repo.forks + 1) * 2, 15)

    # Contributors 分数 (10%)
    contributors_score = min(repo.contributors / 10, 1.0) * 10

    total_score = stars_score + update_score + issues_score + forks_score + contributors_score
    return round(total_score, 2)
