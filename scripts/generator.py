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
