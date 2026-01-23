#!/usr/bin/env python3
"""
真实环境测试 - GitHub to Skill

测试场景: 将 'rich' (Python 终端库) 封装为 skill
"""

import sys
import tempfile
from pathlib import Path
from scripts.github_to_skill import GitHubToSkill


def test_real_github_repo():
    """测试真实的 GitHub 仓库"""

    print("=" * 60)
    print("🧪 真实环境测试: GitHub to Skill")
    print("=" * 60)
    print()

    # 创建临时输出目录
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 输出目录: {tmpdir}")
        print()

        # 初始化
        print("1️⃣  初始化 GitHubToSkill...")
        gts = GitHubToSkill(output_dir=tmpdir)
        print("✅ 初始化成功")
        print()

        # 测试关键词提取
        print("2️⃣  测试关键词提取...")
        query = "I want beautiful terminal output for Python"
        keywords = gts.extract_keywords(query)
        print(f"   查询: {query}")
        print(f"   关键词: {', '.join(keywords)}")
        assert len(keywords) > 0, "关键词提取失败"
        print("✅ 关键词提取成功")
        print()

        # 搜索仓库
        print("3️⃣  搜索 GitHub 仓库...")
        search_query = "terminal library python"
        print(f"   搜索: {search_query}")

        try:
            candidates = gts.search_and_score(search_query, limit=5)

            if not candidates:
                print("⚠️  未找到候选仓库(可能需要 GitHub token)")
                print("   提示: 创建 ~/.github-token 文件并添加 token")
                return False

            print(f"   找到 {len(candidates)} 个候选仓库:")
            for i, repo in enumerate(candidates[:3], 1):
                print(f"   [{i}] {repo['name']} - ⭐{repo['stars']:,} (评分: {repo['score']:.1f})")
            print("✅ 搜索成功")
            print()

            # 选择第一个仓库
            selected = candidates[0]
            print(f"4️⃣  选择仓库: {selected['name']}")
            print(f"   描述: {selected['description']}")
            print(f"   URL: {selected['url']}")
            print()

            # 克隆仓库
            print("5️⃣  克隆仓库...")
            clone_dir = Path(tmpdir) / "cloned_repo"

            if not gts.clone_repo(selected['url'], str(clone_dir)):
                print("❌ 克隆失败")
                return False

            print(f"   克隆到: {clone_dir}")
            print("✅ 克隆成功")
            print()

            # 分析仓库
            print("6️⃣  分析仓库...")
            from scripts.analyzer import RepoAnalyzer

            analyzer = RepoAnalyzer(str(clone_dir))
            analysis = analyzer.analyze()

            print(f"   语言: {analysis['language']}")
            print(f"   工具类型: {analysis['tool_type']}")
            print(f"   README: {analysis['readme']['title'] if analysis['readme'] else 'N/A'}")
            print(f"   依赖数: {len(analysis['dependencies'])}")
            print("✅ 分析成功")
            print()

            # 生成 skill
            print("7️⃣  生成 skill...")
            skill_dir = gts.generator.generate(selected, analysis)

            print(f"   生成位置: {skill_dir}")

            # 验证生成的文件
            skill_md = skill_dir / 'SKILL.md'
            if not skill_md.exists():
                print("❌ SKILL.md 未生成")
                return False

            content = skill_md.read_text()
            print(f"   SKILL.md 大小: {len(content)} 字符")

            # 验证关键内容
            required_fields = ['name:', 'description:', '---']
            for field in required_fields:
                if field not in content:
                    print(f"❌ 缺少字段: {field}")
                    return False

            print("✅ Skill 生成成功")
            print()

            # 显示 skill 内容预览
            print("8️⃣  Skill 内容预览:")
            print("-" * 60)
            lines = content.split('\n')[:20]
            print('\n'.join(lines))
            if len(content.split('\n')) > 20:
                print(f"\n... (还有 {len(content.split('\n')) - 20} 行)")
            print("-" * 60)
            print()

            # 保存结果
            output_file = Path(tmpdir) / "generated_skill.md"
            output_file.write_text(content)
            print(f"💾 Skill 已保存到: {output_file}")
            print()

            print("=" * 60)
            print("✅ 真实环境测试通过!")
            print("=" * 60)
            print()
            print("📊 测试总结:")
            print(f"   ✓ 关键词提取: {', '.join(keywords)}")
            print(f"   ✓ 搜索结果: {len(candidates)} 个候选")
            print(f"   ✓ 选中仓库: {selected['name']}")
            print(f"   ✓ 分析语言: {analysis['language']}")
            print(f"   ✓ Skill 文件: {skill_md.name} ({len(content)} 字符)")

            return True

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    success = test_real_github_repo()
    sys.exit(0 if success else 1)
