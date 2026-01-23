#!/usr/bin/env python3
"""
展示生成的 skill 内容
"""

import sys
import tempfile
from pathlib import Path
from scripts.github_to_skill import GitHubToSkill


def show_generated_skill():
    """生成并展示完整的 skill"""

    print("生成完整 Skill 示例\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        gts = GitHubToSkill(output_dir=tmpdir)

        # 搜索
        candidates = gts.search_and_score("terminal library python", limit=3)

        if not candidates:
            print("未找到候选仓库")
            return

        # 选择第一个
        selected = candidates[0]
        print(f"选择仓库: {selected['name']}\n")

        # 克隆
        clone_dir = Path(tmpdir) / "cloned_repo"
        if not gts.clone_repo(selected['url'], str(clone_dir)):
            print("克隆失败")
            return

        # 分析
        from scripts.analyzer import RepoAnalyzer
        analyzer = RepoAnalyzer(str(clone_dir))
        analysis = analyzer.analyze()

        # 生成
        skill_dir = gts.generator.generate(selected, analysis)
        skill_md = skill_dir / 'SKILL.md'

        # 显示完整内容
        print("=" * 80)
        print("生成的 SKILL.md 完整内容:")
        print("=" * 80)
        print()
        print(skill_md.read_text())
        print()
        print("=" * 80)

        # 复制到当前目录
        output = Path.cwd() / "demo_skill.md"
        output.write_text(skill_md.read_text())
        print(f"\n✅ Skill 已保存到: {output}")


if __name__ == "__main__":
    show_generated_skill()
