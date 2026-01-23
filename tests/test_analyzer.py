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
        (repo_dir / "README.md").write_text("""# Test Tool

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
