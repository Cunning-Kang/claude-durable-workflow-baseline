#!/usr/bin/env python3
"""
调试 README 解析
"""

import tempfile
from pathlib import Path
from scripts.analyzer import RepoAnalyzer
from scripts.github_to_skill import GitHubToSkill


def debug_readme_parsing():
    """调试 README 解析"""

    with tempfile.TemporaryDirectory() as tmpdir:
        gts = GitHubToSkill(output_dir=tmpdir)

        # 搜索
        candidates = gts.search_and_score("terminal library python", limit=1)
        if not candidates:
            print("未找到候选")
            return

        # 克隆
        selected = candidates[0]
        clone_dir = Path(tmpdir) / "repo"

        print(f"克隆 {selected['name']}...")
        if not gts.clone_repo(selected['url'], str(clone_dir)):
            print("克隆失败")
            return

        # 分析
        analyzer = RepoAnalyzer(str(clone_dir))
        readme = analyzer.parse_readme()

        print("\n" + "=" * 80)
        print("README 解析结果:")
        print("=" * 80)
        print(f"标题: {readme['title']}")
        print(f"描述: {readme['description'][:100] if readme['description'] else 'N/A'}...")
        print(f"\n章节数量: {len(readme['sections'])}")
        print(f"章节名称: {list(readme['sections'].keys())[:10]}")

        print("\n前 3 个章节内容预览:")
        for i, (name, content) in enumerate(list(readme['sections'].items())[:3]):
            print(f"\n【章节 {i+1}】{name}")
            print(f"内容长度: {len(content)} 字符")
            print(f"预览: {content[:200]}...")

        print(f"\n代码示例数量: {len(readme['examples'])}")
        if readme['examples']:
            print("\n前 2 个代码示例:")
            for i, (lang, code) in enumerate(readme['examples'][:2]):
                print(f"\n【示例 {i+1}】语言: {lang}")
                print(f"代码: {code[:100]}...")


if __name__ == "__main__":
    debug_readme_parsing()
