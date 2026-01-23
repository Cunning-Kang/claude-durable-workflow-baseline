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

    def _cleanup_clone(self, clone_dir: Path):
        """
        清理克隆的仓库

        Args:
            clone_dir: 克隆目录
        """
        try:
            if clone_dir.exists():
                import shutil
                shutil.rmtree(clone_dir)
                print(f"已清理临时仓库: {clone_dir}")
        except Exception as e:
            print(f"警告: 清理临时仓库失败: {e}")

    def _validate_generated_skill(self, skill_dir: Path):
        """
        验证生成的 skill

        Args:
            skill_dir: skill 目录
        """
        try:
            # 导入验证模块
            import subprocess

            # 运行验证脚本
            result = subprocess.run(
                ['python', 'scripts/validate_skill.py', str(skill_dir)],
                capture_output=True,
                text=True,
                timeout=10
            )

            # 打印验证结果
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        print(f"  {line}")

            # 检查退出码
            if result.returncode == 10:
                print("⚠️  Skill 验证失败,但已生成")
            elif result.returncode != 0:
                print(f"⚠️  验证脚本错误: {result.stderr}")

        except Exception as e:
            print(f"⚠️  无法运行验证脚本: {e}")

    def select_candidate(self, candidates: List[Dict], interactive: bool = True) -> Dict:
        """
        从候选工具中选择一个

        Args:
            candidates: 候选工具列表
            interactive: 是否交互式选择

        Returns:
            选中的工具信息
        """
        if not interactive or len(candidates) == 1:
            # 非交互模式或只有一个候选,直接返回第一个
            selected = candidates[0]
            print(f"\n已选择: {selected['name']}")
            return selected

        # 交互式选择
        while True:
            try:
                choice = input("\n请输入数字 (1-{}) 选择工具,或 0 取消: ".format(len(candidates)))
                choice = choice.strip()

                if choice == '0':
                    print("操作已取消")
                    return None

                index = int(choice) - 1
                if 0 <= index < len(candidates):
                    selected = candidates[index]
                    print(f"\n已选择: {selected['name']}")
                    return selected
                else:
                    print(f"❌ 请输入 1-{len(candidates)} 之间的数字")
            except ValueError:
                print("❌ 请输入有效的数字")
            except KeyboardInterrupt:
                print("\n\n操作已取消")
                return None

    def run(self, user_query: str, interactive: bool = True) -> Optional[Path]:
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

        # 4. 选择工具
        selected = self.select_candidate(candidates, interactive=interactive)
        if not selected:
            return None

        # 5. 克隆仓库
        repo_url = selected['url']
        clone_dir = self.output_dir / "cloned_repo"

        print(f"克隆仓库: {repo_url}")
        if not self.clone_repo(repo_url, str(clone_dir)):
            print("克隆失败")
            return None

        try:
            # 6. 分析仓库
            print("分析仓库...")
            analyzer = RepoAnalyzer(str(clone_dir))
            analysis = analyzer.analyze()

            # 7. 生成 skill
            print("生成 skill...")
            skill_dir = self.generator.generate(selected, analysis)

            print(f"\n✅ Skill 已生成: {skill_dir}")
            print(f"   SKILL.md: {skill_dir / 'SKILL.md'}")

            # 8. 验证 skill
            print("验证 skill 质量...")
            self._validate_generated_skill(skill_dir)

            return skill_dir
        finally:
            # 8. 清理临时仓库
            self._cleanup_clone(clone_dir)
