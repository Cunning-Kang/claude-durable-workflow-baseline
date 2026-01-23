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
