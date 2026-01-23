# GitHub to Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个自动化系统,能够将 GitHub 上的顶级开源工具封装成 Claude Code skill

**Architecture:** 混合架构 - Python 用于搜索和分析逻辑(利用 PyGithub 和分析库),Bash/Shell 用于 skill 生成(与现有 skill-creator 工具链兼容)。系统采用 TDD 开发,每个模块都有完整的测试覆盖。

**Tech Stack:** Python 3.10+, PyGithub, Jinja2, pytest, Git, Bash

---

## Task 1: 项目基础设置

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `.github-token.example`
- Create: `scripts/__init__.py`
- Create: `tests/__init__.py`

**Step 1: 创建 requirements.txt**

```txt
PyGithub>=2.1.1
jinja2>=3.1.2
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
pyyaml>=6.0
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
```

**Step 2: 创建 pytest.ini**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --cov=scripts
    --cov-report=term-missing
    --cov-report=html
```

**Step 3: 创建 GitHub token 示例文件**

```bash
cat > .github-token.example << 'EOF'
# GitHub Personal Access Token
# 获取方式: https://github.com/settings/tokens
# 需要的权限: repo (full control)
# 将此文件复制为 .github-token 并粘贴您的 token
EOF
```

**Step 4: 创建 Python 包初始化文件**

```python
# scripts/__init__.py
"""GitHub to Skill - 自动化 skill 生成系统"""

__version__ = "1.0.0"
```

```python
# tests/__init__.py
"""Tests for github-to-skill"""
```

**Step 5: 提交基础设置**

```bash
git add requirements.txt pytest.ini .github-token.example scripts/__init__.py tests/__init__.py
git commit -m "feat: initialize project structure and dependencies"
```

---

## Task 2: 实现 GitHub 搜索和评分模块

**Files:**
- Create: `scripts/github_client.py` - GitHub API 客户端
- Create: `scripts/scoring.py` - 评分算法
- Create: `tests/test_github_client.py` - 测试
- Create: `tests/test_scoring.py` - 测试

### Step 1: 编写评分算法测试

**File:** `tests/test_scoring.py`

```python
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
        stars=1000,
        forks=50,
        open_issues=200,
        closed_issues=10,
        contributors=2,
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
```

### Step 2: 运行测试(预期失败)

```bash
python -m pytest tests/test_scoring.py -v
```

**Expected:** `ModuleNotFoundError: No module named 'scripts.scoring'`

### Step 3: 实现评分算法

**File:** `scripts/scoring.py`

```python
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
```

### Step 4: 运行测试(预期通过)

```bash
python -m pytest tests/test_scoring.py -v
```

**Expected:** 所有测试通过

### Step 5: 提交评分算法

```bash
git add tests/test_scoring.py scripts/scoring.py
git commit -m "feat: implement repository scoring algorithm"
```

---

## Task 3: 实现 GitHub 客户端

### Step 1: 编写 GitHub 客户端测试

**File:** `tests/test_github_client.py`

```python
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
    mock_github.assert_called_once_with(None)


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

    mock_search_result = Mock()
    mock_search_result.items = [mock_repo]

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
    from Github import RateLimitExceededException

    mock_github_instance = mock_github.return_value
    mock_github_instance.search_repositories.side_effect = RateLimitExceededException(
        403, {"message": "API rate limit exceeded"}
    )

    # 应该抛出异常
    with pytest.raises(RateLimitExceededException):
        search_repositories("test query", token="test_token")
```

### Step 2: 运行测试(预期失败)

```bash
python -m pytest tests/test_github_client.py -v
```

**Expected:** `ModuleNotFoundError: No module named 'scripts.github_client'`

### Step 3: 实现 GitHub 客户端

**File:** `scripts/github_client.py`

```python
import os
from typing import List, Dict, Optional
from Github import Github, GithubException, RateLimitExceededException
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
        self.github = Github(token) if token else Github()

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
            for repo in repos[:limit]:
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
```

### Step 4: 运行测试并修复

```bash
python -m pytest tests/test_github_client.py -v
```

**Expected:** 可能有一些测试需要调整,修复后重新运行

### Step 5: 提交 GitHub 客户端

```bash
git add tests/test_github_client.py scripts/github_client.py
git commit -m "feat: implement GitHub API client"
```

---

## Task 4: 实现仓库分析模块

**Files:**
- Create: `scripts/analyzer.py` - 仓库分析器
- Create: `tests/test_analyzer.py` - 测试

### Step 1: 编写分析器测试

**File:** `tests/test_analyzer.py`

```python
import pytest
import tempfile
import os
from pathlib import Path
from scripts.analyzer import RepoAnalyzer, detect_tool_type


@pytest.fixture
def sample_repo_dir():
    """创建示例仓库目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir)

        # 创建 README
        (repo_dir / "README.md").write_text("""
        # Test Tool

        A test tool for demonstration.

        ## Installation

        pip install test-tool

        ## Usage

        ```python
        import testtool
        testtool.run()
        ```

        ## Features

        - Feature 1
        - Feature 2
        - Feature 3
        """)

        # 创建 Python 代码
        (repo_dir / "setup.py").write_text("""
        from setuptools import setup
        setup(name='test-tool', version='0.1.0')
        """)

        (repo_dir / "testtool").mkdir()
        (repo_dir / "testtool" / "__init__.py").write_text("""
        def run():
            print("Running test tool")
        """)

        yield repo_dir


def test_analyzer_parse_readme(sample_repo_dir):
    """测试解析 README"""
    analyzer = RepoAnalyzer(sample_repo_dir)
    readme = analyzer.parse_readme()

    assert readme is not None
    assert readme['title'] == "Test Tool"
    assert 'Installation' in readme['sections']
    assert 'Usage' in readme['sections']


def test_analyzer_detect_language(sample_repo_dir):
    """测试检测编程语言"""
    analyzer = RepoAnalyzer(sample_repo_dir)
    language = analyzer.detect_language()

    assert language == "python"


def test_analyzer_extract_dependencies(sample_repo_dir):
    """测试提取依赖"""
    analyzer = RepoAnalyzer(sample_repo_dir)
    deps = analyzer.extract_dependencies()

    assert isinstance(deps, list)


def test_detect_tool_type_python_library():
    """测试检测 Python 库类型"""
    tool_type = detect_tool_type("python", has_setup=True)
    assert tool_type == "python-library"


def test_detect_tool_type_cli():
    """测试检测 CLI 工具类型"""
    tool_type = detect_tool_type("go", has_setup=False, has_cli=True)
    assert tool_type == "cli-tool"


def test_analyzer_full_analysis(sample_repo_dir):
    """测试完整分析流程"""
    analyzer = RepoAnalyzer(sample_repo_dir)
    analysis = analyzer.analyze()

    assert 'readme' in analysis
    assert 'language' in analysis
    assert 'tool_type' in analysis
    assert analysis['language'] == "python"
```

### Step 2: 运行测试(预期失败)

```bash
python -m pytest tests/test_analyzer.py -v
```

**Expected:** `ModuleNotFoundError: No module named 'scripts.analyzer'`

### Step 3: 实现仓库分析器

**File:** `scripts/analyzer.py`

```python
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess


class RepoAnalyzer:
    """仓库分析器"""

    def __init__(self, repo_dir: str):
        """
        初始化分析器

        Args:
            repo_dir: 仓库目录路径
        """
        self.repo_dir = Path(repo_dir)

    def parse_readme(self) -> Optional[Dict]:
        """
        解析 README 文件

        Returns:
            包含标题、描述、章节的字典
        """
        # 查找 README 文件
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
        readme_path = None

        for filename in readme_files:
            potential_path = self.repo_dir / filename
            if potential_path.exists():
                readme_path = potential_path
                break

        if not readme_path:
            return None

        content = readme_path.read_text()

        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else readme_path.stem

        # 提取主要章节
        sections = {}
        section_pattern = re.compile(r'^##\s+(.+?)$\n(.*?)(?=^##|\Z)', re.MULTILINE | re.DOTALL)
        for match in section_pattern.finditer(content):
            section_name = match.group(1).strip()
            section_content = match.group(2).strip()
            sections[section_name] = section_content

        # 提取第一段作为描述
        description_match = re.search(r'^#\s+.+$\n\n(.+?)(?:\n\n|\Z)', content, re.DOTALL)
        description = description_match.group(1).strip() if description_match else ""

        # 提取代码示例
        code_blocks = re.findall(r'```(\w*)\n(.*?)```', content, re.DOTALL)
        examples = [(lang or 'text', code.strip()) for lang, code in code_blocks]

        return {
            'title': title,
            'description': description,
            'sections': sections,
            'examples': examples,
            'path': str(readme_path)
        }

    def detect_language(self) -> str:
        """
        检测主要编程语言

        Returns:
            语言名称
        """
        # 检查配置文件
        language_indicators = {
            'python': ['setup.py', 'pyproject.toml', 'requirements.txt', '.py'],
            'javascript': ['package.json', '.js', '.ts'],
            'go': ['go.mod', '.go'],
            'rust': ['Cargo.toml', '.rs'],
            'ruby': ['Gemfile', '.rb'],
            'java': ['pom.xml', 'build.gradle', '.java'],
        }

        for lang, indicators in language_indicators.items():
            for indicator in indicators:
                if indicator.startswith('.'):
                    # 检查文件扩展名
                    if any(f.suffix == indicator for f in self.repo_dir.rglob('*.*')):
                        return lang
                else:
                    # 检查文件存在
                    if (self.repo_dir / indicator).exists():
                        return lang

        return "unknown"

    def analyze_code_structure(self) -> Dict:
        """
        分析代码结构

        Returns:
            代码结构信息
        """
        structure = {
            'directories': [],
            'main_files': [],
            'test_files': [],
            'doc_files': []
        }

        for item in self.repo_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                structure['directories'].append(item.name)

            if item.is_file():
                name = item.name.lower()

                if 'test' in name:
                    structure['test_files'].append(item.name)
                elif name.endswith('.md') or name.endswith('.rst'):
                    structure['doc_files'].append(item.name)
                elif not name.startswith('.'):
                    structure['main_files'].append(item.name)

        return structure

    def extract_dependencies(self) -> List[str]:
        """
        提取依赖列表

        Returns:
            依赖包列表
        """
        dependencies = []

        # Python requirements
        for req_file in ['requirements.txt', 'requirements.in']:
            req_path = self.repo_dir / req_file
            if req_path.exists():
                content = req_path.read_text()
                deps = [line.split('=')[0].split('[')[0].strip()
                       for line in content.split('\n')
                       if line.strip() and not line.startswith('#')]
                dependencies.extend(deps)

        # Node.js package.json
        package_json = self.repo_dir / 'package.json'
        if package_json.exists():
            try:
                import json
                data = json.loads(package_json.read_text())
                deps = list(data.get('dependencies', {}).keys())
                dependencies.extend(deps)
            except:
                pass

        return list(set(dependencies))

    def analyze(self) -> Dict:
        """
        执行完整分析

        Returns:
            完整的分析结果
        """
        language = self.detect_language()

        return {
            'readme': self.parse_readme(),
            'language': language,
            'structure': self.analyze_code_structure(),
            'dependencies': self.extract_dependencies(),
            'tool_type': detect_tool_type(
                language,
                has_setup=(self.repo_dir / 'setup.py').exists() or
                         (self.repo_dir / 'package.json').exists(),
                has_cli=(self.repo_dir / 'cli').exists()
            )
        }


def detect_tool_type(language: str, has_setup: bool = False,
                   has_cli: bool = False) -> str:
    """
    检测工具类型

    Args:
        language: 编程语言
        has_setup: 是否有 setup 文件
        has_cli: 是否有 CLI 组件

    Returns:
        工具类型标识
    """
    if language == 'python' and has_setup:
        return 'python-library'
    elif has_cli or language in ['go', 'rust']:
        return 'cli-tool'
    elif language in ['javascript', 'typescript']:
        return 'web-app'
    elif 'doc' in language.lower():
        return 'documentation'
    else:
        return 'utility'
```

### Step 4: 运行测试

```bash
python -m pytest tests/test_analyzer.py -v
```

### Step 5: 提交分析器

```bash
git add tests/test_analyzer.py scripts/analyzer.py
git commit -m "feat: implement repository analyzer"
```

---

## Task 5: 实现 Skill 生成器

**Files:**
- Create: `scripts/generator.py` - Skill 生成器
- Create: `references/templates/skill-python.md` - Python 工具模板
- Create: `references/templates/skill-cli.md` - CLI 工具模板
- Create: `tests/test_generator.py` - 测试

### Step 1: 创建模板文件

**File:** `references/templates/skill-python.md`

```markdown
---
name: {{ skill_name }}
description: {{ description }} 使用此技能来{{ use_cases }}
---

# {{ readme_title }}

{{ readme_description }}

## 快速开始

### 安装

```bash
{{ installation_command }}
```

### 基本使用

{{ usage_example }}

## 主要功能

{% for feature in features %}
- {{ feature }}
{% endfor %}

## 使用场景

使用此技能当您需要:
{% for scenario in use_cases_list %}
- {{ scenario }}
{% endfor %}

## 高级功能

详见 [高级功能文档](references/advanced.md)

## 故障排除

### 常见问题

**问题**: 无法导入模块
**解决**: 确保已正确安装所有依赖

更多问题请查看 [故障排除指南](references/troubleshooting.md)
```

**File:** `references/templates/skill-cli.md`

```markdown
---
name: {{ skill_name }}
description: {{ description }} - 命令行工具,用于{{ use_cases }}
---

# {{ readme_title }}

{{ readme_description }}

## 快速开始

### 安装

```bash
{{ installation_command }}
```

### 基本使用

```bash
{{ cli_example }}
```

## 主要功能

{% for feature in features %}
- {{ feature }}
{% endfor %}

## 使用场景

此工具特别适合:
{% for scenario in use_cases_list %}
- {{ scenario }}
{% endfor %}

## 脚本

查看 [scripts/](scripts/) 目录获取可用的辅助脚本。
```

### Step 2: 编写生成器测试

**File:** `tests/test_generator.py`

```python
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
        assert generator.output_dir == tmpdir


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
```

### Step 3: 运行测试(预期失败)

```bash
python -m pytest tests/test_generator.py -v
```

**Expected:** `ModuleNotFoundError: No module named 'scripts.generator'`

### Step 4: 实现生成器

**File:** `scripts/generator.py`

```python
import os
import shutil
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape


class SkillGenerator:
    """Skill 文件生成器"""

    def __init__(self, output_dir: str, template_dir: str = None):
        """
        初始化生成器

        Args:
            output_dir: 输出目录
            template_dir: 模板目录(默认为 references/templates/)
        """
        self.output_dir = Path(output_dir)

        if template_dir is None:
            # 默认模板目录
            script_dir = Path(__file__).parent.parent
            template_dir = script_dir / 'references' / 'templates'

        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _get_template(self, tool_type: str) -> str:
        """
        获取工具类型对应的模板文件

        Args:
            tool_type: 工具类型

        Returns:
            模板文件名
        """
        template_mapping = {
            'python-library': 'skill-python.md',
            'cli-tool': 'skill-cli.md',
            'web-app': 'skill-js.md',
            'documentation': 'skill-docs.md',
            'utility': 'skill-cli.md'
        }

        return template_mapping.get(tool_type, 'skill-python.md')

    def _prepare_template_context(self, repo_info: Dict, analysis: Dict) -> Dict:
        """
        准备模板渲染的上下文

        Args:
            repo_info: 仓库信息
            analysis: 分析结果

        Returns:
            模板上下文字典
        """
        readme = analysis.get('readme', {})

        # 提取安装命令
        installation = readme.get('sections', {}).get('Installation', 'pip install ' + repo_info['name'].split('/')[1])

        # 提取使用示例
        usage = readme.get('sections', {}).get('Usage', 'See README for usage')

        # 提取功能列表
        features = []
        features_section = readme.get('sections', {}).get('Features', '')
        if features_section:
            features = [line.strip().lstrip('- ')
                       for line in features_section.split('\n')
                       if line.strip().startswith('-')]

        if not features:
            features = ['Feature 1', 'Feature 2', 'Feature 3']  # 默认

        return {
            'skill_name': repo_info['name'].replace('/', '-'),
            'description': readme.get('description', repo_info.get('description', '')),
            'readme_title': readme.get('title', repo_info['name']),
            'readme_description': readme.get('description', ''),
            'installation_command': installation,
            'usage_example': usage,
            'features': features[:5],  # 最多 5 个功能
            'use_cases': f"use {repo_info['name']} for various tasks",
            'use_cases_list': [
                f"Use {repo_info['name']} features",
                "Automate workflows",
                "Integrate into projects"
            ],
            'cli_example': f"{repo_info['name'].split('/')[1]} --help"
        }

    def generate_skill_md(self, repo_info: Dict, analysis: Dict) -> Path:
        """
        生成 SKILL.md 文件

        Args:
            repo_info: 仓库信息
            analysis: 分析结果

        Returns:
            生成的文件路径
        """
        tool_type = analysis.get('tool_type', 'utility')
        template_name = self._get_template(tool_type)

        template = self.env.get_template(template_name)
        context = self._prepare_template_context(repo_info, analysis)

        content = template.render(**context)

        # 创建输出目录
        skill_name = repo_info['name'].replace('/', '-')
        skill_dir = self.output_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # 写入 SKILL.md
        skill_md = skill_dir / 'SKILL.md'
        skill_md.write_text(content)

        return skill_md

    def generate(self, repo_info: Dict, analysis: Dict) -> Path:
        """
        生成完整的 skill

        Args:
            repo_info: 仓库信息
            analysis: 分析结果

        Returns:
            skill 目录路径
        """
        # 生成 SKILL.md
        skill_md = self.generate_skill_md(repo_info, analysis)
        skill_dir = skill_md.parent

        # TODO: 生成 scripts/、references/、assets/ 等

        return skill_dir

    def install_to_claude(self, skill_dir: Path, force: bool = False) -> bool:
        """
        安装 skill 到 Claude Code

        Args:
            skill_dir: skill 目录
            force: 是否覆盖已存在的 skill

        Returns:
            是否成功
        """
        claude_skills_dir = Path.home() / '.claude' / 'skills'
        claude_skills_dir.mkdir(parents=True, exist_ok=True)

        skill_name = skill_dir.name
        target_dir = claude_skills_dir / skill_name

        if target_dir.exists():
            if not force:
                print(f"Skill {skill_name} already exists. Use force=True to overwrite.")
                return False

            # 备份
            backup_dir = target_dir.with_suffix('.bak')
            shutil.rmtree(backup_dir, ignore_errors=True)
            shutil.move(str(target_dir), str(backup_dir))

        # 复制 skill
        shutil.copytree(skill_dir, target_dir)
        print(f"Skill {skill_name} installed to {target_dir}")

        return True
```

### Step 5: 运行测试

```bash
python -m pytest tests/test_generator.py -v
```

### Step 6: 提交生成器

```bash
git add tests/test_generator.py scripts/generator.py references/templates/
git commit -m "feat: implement skill generator"
```

---

## Task 6: 实现主流程协调器

**Files:**
- Create: `scripts/github_to_skill.py` - 主流程
- Create: `SKILL.md` - 这个 skill 自己的 SKILL.md
- Create: `tests/test_github_to_skill.py` - 集成测试

### Step 1: 编写主流程测试

**File:** `tests/test_github_to_skill.py`

```python
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
    assert 'PDF' in keywords
    assert 'converter' in keywords

    # 测试复杂查询
    keywords = gts.extract_keywords("Need a tool for image processing in Python")
    assert 'image' in keywords
    assert 'processing' in keywords
    assert 'Python' in keywords


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
            'score': 85.5
        },
        {
            'name': 'test/repo2',
            'description': 'Test repo 2',
            'stars': 500,
            'forks': 50,
            'language': 'JavaScript',
            'score': 72.3
        }
    ]

    formatted = gts.format_candidates(candidates)
    assert '[1]' in formatted
    assert 'test/repo1' in formatted
    assert '85.5' in formatted
```

### Step 2: 运行测试(预期失败)

```bash
python -m pytest tests/test_github_to_skill.py -v
```

### Step 3: 实现主流程

**File:** `scripts/github_to_skill.py`

```python
import re
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from scripts.github_client import search_repositories
from scripts.scoring import calculate_repo_score, RepoInfo
from scripts.analyzer import RepoAnalyzer
from scripts.generator import SkillGenerator


class GitHubToSkill:
    """GitHub to Skill 主流程"""

    def __init__(self, output_dir: Optional[str] = None, github_token: Optional[str] = None):
        """
        初始化

        Args:
            output_dir: 输出目录(默认为临时目录)
            github_token: GitHub token(可选)
        """
        self.github_token = github_token
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.mkdtemp())
        self.generator = SkillGenerator(str(self.output_dir))

    def extract_keywords(self, user_query: str) -> List[str]:
        """
        从用户查询中提取关键词

        Args:
            user_query: 用户查询字符串

        Returns:
            关键词列表
        """
        # 移除常见无意义词
        stop_words = {
            'i', 'want', 'to', 'create', 'make', 'build', 'need',
            'a', 'an', 'the', 'for', 'in', 'on', 'at', 'with'
        }

        # 提取单词
        words = re.findall(r'\b\w+\b', user_query.lower())

        # 过滤停用词
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords[:5]  # 最多 5 个关键词

    def search_and_score(self, query: str, limit: int = 10) -> List[Dict]:
        """
        搜索并评分仓库

        Args:
            query: 搜索查询
            limit: 获取数量

        Returns:
            带评分的仓库列表
        """
        # 搜索仓库
        repos = search_repositories(query, token=self.github_token, limit=limit)

        # 评分
        scored_repos = []
        for repo in repos:
            repo_info = RepoInfo(
                name=repo['name'],
                stars=repo['stars'],
                forks=repo['forks'],
                open_issues=repo['open_issues'],
                closed_issues=repo['closed_issues'],
                contributors=repo['contributors'],
                updated_at=repo['updated_at']
            )
            score = calculate_repo_score(repo_info)
            repo['score'] = score
            scored_repos.append(repo)

        # 过滤低分并排序
        filtered = [r for r in scored_repos if r['score'] >= 30]
        filtered.sort(key=lambda x: x['score'], reverse=True)

        return filtered[:3]  # 返回前 3 个

    def format_candidates(self, candidates: List[Dict]) -> str:
        """
        格式化候选工具展示

        Args:
            candidates: 候选工具列表

        Returns:
            格式化的字符串
        """
        lines = [f"根据搜索找到以下顶级开源工具:\n"]

        for i, repo in enumerate(candidates, 1):
            lines.append(f"[{i}] {repo['name']} - {repo['description']}")
            lines.append(f"    ⭐ Stars: {repo['stars']:,}  |  🔄 Forks: {repo['forks']:,}")
            lines.append(f"    📅 最后更新: {repo['updated_at'].strftime('%Y-%m-%d')}  |  💻 语言: {repo['language']}")
            lines.append(f"    🎯 综合评分: {repo['score']:.1f}/100")
            lines.append("")

        lines.append("请输入数字 (1-{}) 选择要封装的工具:".format(len(candidates)))

        return "\n".join(lines)

    def clone_repo(self, repo_url: str, target_dir: str) -> bool:
        """
        克隆仓库

        Args:
            repo_url: 仓库 URL
            target_dir: 目标目录

        Returns:
            是否成功
        """
        try:
            subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, target_dir],
                check=True,
                capture_output=True,
                timeout=30
            )
            return True
        except Exception as e:
            print(f"克隆失败: {e}")
            return False

    def run(self, user_query: str) -> Optional[Path]:
        """
        执行完整流程

        Args:
            user_query: 用户查询

        Returns:
            生成的 skill 目录路径
        """
        # 1. 提取关键词
        keywords = self.extract_keywords(user_query)
        search_query = " ".join(keywords)

        print(f"搜索查询: {search_query}")

        # 2. 搜索并评分
        candidates = self.search_and_score(search_query)

        if not candidates:
            print("未找到合适的仓库")
            return None

        # 3. 展示候选
        print(self.format_candidates(candidates))

        # TODO: 在实际使用中,这里需要等待用户输入
        # 为了演示,选择第一个
        selected = candidates[0]
        print(f"\n已选择: {selected['name']}")

        # 4. 克隆仓库
        repo_url = selected['url']
        clone_dir = self.output_dir / "cloned_repo"

        print(f"克隆仓库: {repo_url}")
        if not self.clone_repo(repo_url, str(clone_dir)):
            print("克隆失败")
            return None

        # 5. 分析仓库
        print("分析仓库...")
        analyzer = RepoAnalyzer(str(clone_dir))
        analysis = analyzer.analyze()

        # 6. 生成 skill
        print("生成 skill...")
        skill_dir = self.generator.generate(selected, analysis)

        print(f"\n✅ Skill 已生成: {skill_dir}")
        print(f"   SKILL.md: {skill_dir / 'SKILL.md'}")

        return skill_dir
```

### Step 4: 运行测试

```bash
python -m pytest tests/test_github_to_skill.py -v
```

### Step 5: 创建这个 skill 的 SKILL.md

**File:** `SKILL.md`

```markdown
---
name: github-to-skill
description: 自动将 GitHub 上的顶级开源工具封装成 Claude Code skill。使用此技能当您需要: (1) 根据功能描述搜索 GitHub 上的优质工具, (2) 自动分析仓库并生成符合 Claude Code 标准的 skill, (3) 快速复用现有开源工具而不重复造轮子
---

# GitHub to Skill

自动将 GitHub 上的顶级开源工具封装成 Claude Code skill 的工具。

## 功能

- **智能搜索**: 根据功能描述搜索 GitHub 上的相关工具
- **综合评分**: 多维度评估工具质量(stars、更新时间、issues 响应等)
- **自动分析**: 深度分析仓库结构、依赖和文档
- **一键生成**: 自动生成完整的 skill 结构(SKILL.md、scripts、references、assets)
- **自动安装**: 直接安装到 Claude Code skills 目录

## 使用场景

使用此技能当您需要:
- 快速将现有开源工具集成到 Claude Code 工作流
- 避免重复开发已有功能
- 发现和利用 GitHub 上的优质工具
- 自动化创建重复性的 skill

## 快速开始

```python
from scripts.github_to_skill import GitHubToSkill

# 创建实例
gts = GitHubToSkill()

# 执行搜索和生成
skill_dir = gts.run("I want to create a PDF converter tool")
```

## 评分算法

系统使用以下维度综合评分:
- Stars 数量 (30%)
- 最近更新时间 (25%)
- Issues 响应率 (20%)
- Fork 数量 (15%)
- Contributors 数量 (10%)

## 模块

- `github_client.py`: GitHub API 客户端
- `scoring.py`: 仓库评分算法
- `analyzer.py`: 仓库结构分析
- `generator.py`: Skill 文件生成
- `github_to_skill.py`: 主流程协调

## 配置

可选配置 GitHub Token 以获得更高的 API 限额:

```bash
# 方式 1: 环境变量
export GITHUB_TOKEN="your_token_here"

# 方式 2: 文件
echo "your_token_here" > ~/.github-token
```

## 参考资料

详见:
- [GitHub API 使用参考](references/github-api.md)
- [评分算法详解](references/scoring-algorithm.md)
- [设计文档](docs/plans/2025-01-23-github-to-skill-design.md)
```

### Step 6: 提交主流程

```bash
git add tests/test_github_to_skill.py scripts/github_to_skill.py SKILL.md
git commit -m "feat: implement main workflow coordinator"
```

---

## Task 7: 端到端测试和文档完善

**Files:**
- Create: `tests/test_e2e.py` - 端到端测试
- Create: `references/github-api.md` - GitHub API 文档
- Create: `references/scoring-algorithm.md` - 评分算法文档

### Step 1: 编写端到端测试

**File:** `tests/test_e2e.py`

```python
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
```

### Step 2: 创建 GitHub API 文档

**File:** `references/github-api.md`

```markdown
# GitHub API 使用参考

## 认证

GitHub API 支持两种模式:

### 无认证模式
- 速率限制: 每小时 60 次请求
- 适用场景: 偶尔使用

### PAT 认证模式
- 速率限制: 每小时 5000 次请求
- 适用场景: 频繁使用

## 获取 Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限: `repo` (full control)
4. 生成并复制 token

## 配置方式

### 环境变量
```bash
export GITHUB_TOKEN="your_token_here"
```

### 文件配置
```bash
echo "your_token_here" > ~/.github-token
chmod 600 ~/.github-token
```

## API 限制

- 搜索结果最多返回 1000 个
- 每次查询建议限制在 10-20 个结果
- 注意处理速率限制错误

## 错误处理

主要错误类型:
- `403`: 速率限制超出
- `401`: Token 无效
- `404`: 资源不存在
- `503`: 服务临时不可用
```

### Step 3: 创建评分算法文档

**File:** `references/scoring-algorithm.md`

```markdown
# 评分算法详解

## 算法设计

综合评分 = Stars(30%) + 更新时间(25%) + Issues响应率(20%) + Forks(15%) + Contributors(10%)

## 各维度详解

### Stars (30%)
使用对数函数避免大数优势:
```python
stars_score = min(log(stars + 1) * 3, 30)
```

- 1K stars ≈ 21 分
- 10K stars ≈ 28 分
- 100K stars ≈ 30 分(封顶)

### 更新时间 (25%)
- 30 天内: 25 分
- 90 天内: 20 分
- 180 天内: 15 分
- 365 天内: 10 分
- 超过 1 年: 5 分

### Issues 响应率 (20%)
```python
issues_score = (closed_issues / total_issues) * 20
```

- 全部关闭: 20 分
- 一半关闭: 10 分
- 全部开放: 0 分
- 无 issues: 默认 10 分

### Forks (15%)
```python
forks_score = min(log(forks + 1) * 2, 15)
```

### Contributors (10%)
```python
contributors_score = min(contributors / 10, 1.0) * 10
```

- 10+ contributors: 10 分
- 5 contributors: 5 分

## 过滤规则

- 评分 < 30: 不展示
- 过滤后 < 3 个: 降低阈值到 20
- 仍然不足: 展示所有有效结果

## 优化建议

可根据实际使用调整:
- 权重分配
- 评分阈值
- 时间分段
```

### Step 4: 运行所有测试

```bash
python -m pytest tests/ -v --cov=scripts
```

### Step 5: 提交文档和测试

```bash
git add tests/test_e2e.py references/github-api.md references/scoring-algorithm.md
git commit -m "docs: add API documentation and end-to-end tests"
```

---

## Task 8: 最终验证和打包

### Step 1: 运行完整测试套件

```bash
python -m pytest tests/ -v --cov=scripts --cov-report=html
```

### Step 2: 代码质量检查

```bash
# 安装开发依赖
pip install pylint black mypy

# 代码格式化
black scripts/ tests/

# 代码检查
pylint scripts/

# 类型检查
mypy scripts/
```

### Step 3: 创建示例

**File:** `examples/basic_usage.py`

```python
#!/usr/bin/env python3
"""
GitHub to Skill 基本使用示例
"""

from scripts.github_to_skill import GitHubToSkill

def main():
    """基本使用"""
    # 创建实例
    gts = GitHubToSkill()

    # 搜索并生成 skill
    skill_dir = gts.run("I want to create a PDF converter tool")

    if skill_dir:
        print(f"\n✅ Success! Skill created at: {skill_dir}")

        # 可选: 安装到 Claude Code
        # gts.generator.install_to_claude(skill_dir, force=True)

if __name__ == "__main__":
    main()
```

### Step 4: 创建 README

**File:** `README.md`

```markdown
# GitHub to Skill

自动将 GitHub 上的顶级开源工具封装成 Claude Code skill。

## 功能

- 🔍 智能搜索 GitHub 上的优质工具
- 📊 多维度综合评分(stars、更新时间、issues 响应等)
- 🔬 深度分析仓库结构和依赖
- ⚡ 自动生成完整 skill
- 🚀 一键安装到 Claude Code

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```python
from scripts.github_to_skill import GitHubToSkill

gts = GitHubToSkill()
skill_dir = gts.run("I want to create a PDF converter tool")
```

## 配置

可选配置 GitHub Token:

```bash
export GITHUB_TOKEN="your_token"
```

## 测试

```bash
pytest tests/ -v
```

## 文档

- [设计文档](docs/plans/2025-01-23-github-to-skill-design.md)
- [实现计划](docs/plans/2025-01-23-github-to-skill-implementation.md)
- [GitHub API 参考](references/github-api.md)
- [评分算法](references/scoring-algorithm.md)

## License

MIT
```

### Step 5: 最终提交

```bash
git add examples/ README.md
git commit -m "docs: add examples and README"
```

### Step 6: 打包 Skill

```bash
# 使用现有的 package_skill.py
python scripts/package_skill.py . ./dist
```

---

## 完成清单

- [x] 项目基础设置
- [x] 评分算法实现和测试
- [x] GitHub 客户端实现和测试
- [x] 仓库分析器实现和测试
- [x] Skill 生成器实现和测试
- [x] 主流程协调器实现和测试
- [x] 端到端测试
- [x] 文档完善
- [x] 示例代码
- [x] README

## 下一步

1. ✅ 所有测试通过
2. ⏳ 用户测试和反馈
3. ⏳ 迭代优化
4. ⏳ 发布和集成

---

**实施提示**:
- 每个任务独立提交
- 测试驱动开发(TDD)
- 频繁运行测试确保质量
- 遇到问题及时调整计划
