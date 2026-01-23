import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


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

        content = readme_path.read_text().strip()

        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else readme_path.stem

        # 提取主要章节
        sections = {}
        section_pattern = re.compile(r'^##\s+(.+?)$\n(.*?)(?=^##|\Z)', re.MULTILINE | re.DOTALL)
        for match in section_pattern.finditer(content):
            section_name = match.group(1).strip()
            section_content = match.group(2).strip()
            if section_name:  # 确保章节名不为空
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
