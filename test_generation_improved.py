#!/usr/bin/env python3
"""
测试改进后的生成器 - 使用已克隆的仓库
"""

from pathlib import Path
from scripts.analyzer import RepoAnalyzer
from scripts.generator import SkillGenerator


def test_improved_generator():
    """使用已克隆的 rich 仓库测试"""

    # 检查是否有缓存的克隆
    cached_repo = Path.cwd() / "test_repo_cache"

    if not cached_repo.exists():
        print("❌ 未找到缓存的仓库,请先运行: git clone --depth 1 https://github.com/Textualize/rich test_repo_cache")
        return False

    print("=" * 80)
    print("测试改进后的 Skill 生成器")
    print("=" * 80)
    print()

    # 分析仓库
    print("1️⃣  分析仓库...")
    analyzer = RepoAnalyzer(str(cached_repo))
    analysis = analyzer.analyze()

    print(f"   语言: {analysis['language']}")
    print(f"   README 标题: {analysis['readme']['title']}")
    print(f"   README 描述: {analysis['readme']['description'][:100]}...")
    print(f"   章节数: {len(analysis['readme']['sections'])}")
    print(f"   代码示例数: {len(analysis['readme']['examples'])}")
    print()

    # 模拟仓库信息
    repo_info = {
        'name': 'Textualize/rich',
        'description': 'Rich is a Python library for rich text and beautiful formatting in the terminal.',
        'stars': 55221,
        'url': 'https://github.com/Textualize/rich'
    }

    # 生成 skill
    print("2️⃣  生成 skill...")
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = SkillGenerator(tmpdir)
        skill_dir = generator.generate(repo_info, analysis)
        skill_md = skill_dir / 'SKILL.md'

        content = skill_md.read_text()

        print(f"   生成位置: {skill_dir}")
        print(f"   文件大小: {len(content)} 字符")
        print()

        # 显示内容
        print("3️⃣  生成的 Skill 内容:")
        print("=" * 80)
        print(content)
        print("=" * 80)
        print()

        # 验证关键改进
        print("4️⃣  验证关键改进:")

        checks = [
            ("包含仓库 URL", repo_info['url'] in content or 'github.com' in content),
            ("包含实际描述", len(analysis['readme']['description']) > 10 or repo_info['description'] in content),
            ("包含安装说明", 'pip install' in content or 'install' in content.lower()),
            ("包含代码示例", '```' in content),
            ("包含功能列表", any(line.strip().startswith('-') for line in content.split('\n'))),
        ]

        all_passed = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
            all_passed = all_passed and result

        print()
        if all_passed:
            print("✅ 所有检查通过!")
        else:
            print("⚠️  部分检查未通过")

        return all_passed


if __name__ == "__main__":
    import sys
    success = test_improved_generator()
    sys.exit(0 if success else 1)
