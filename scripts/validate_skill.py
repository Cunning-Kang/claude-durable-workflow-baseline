#!/usr/bin/env python3
"""
验证生成的 skill 质量

Usage:
    python scripts/validate_skill.py <skill_directory>
"""

import sys
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

    def add_error(self, message: str):
        """添加错误"""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """添加警告"""
        self.warnings.append(message)

    def add_info(self, message: str):
        """添加信息"""
        self.info.append(message)


def validate_skill_md(skill_dir: Path) -> ValidationResult:
    """验证 SKILL.md 文件"""
    result = ValidationResult(is_valid=True)

    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        result.add_error("SKILL.md 文件不存在")
        return result

    content = skill_md.read_text()

    # 检查 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        result.add_error("缺少 frontmatter (---) 标记")
        return result

    frontmatter = frontmatter_match.group(1)

    # 检查必需字段
    if not re.search(r'^name:\s*\S+', frontmatter, re.MULTILINE):
        result.add_error("frontmatter 中缺少 name 字段")

    if not re.search(r'^description:\s*\S+', frontmatter, re.MULTILINE):
        result.add_error("frontmatter 中缺少 description 字段")

    # 检查 name 格式 (hyphen-case)
    name_match = re.search(r'^name:\s*(\S+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1)
        if len(name) > 64:
            result.add_warning(f"name 长度超过 64 字符: {len(name)}")

        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', name):
            result.add_warning(f"name 不符合 hyphen-case 格式: {name}")

    # 检查描述长度
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
    if desc_match:
        description = desc_match.group(1)
        if len(description) > 1024:
            result.add_error(f"description 长度超过 1024 字符: {len(description)}")

        if '<' in description or '>' in description:
            result.add_error("description 中包含尖括号 < >")

    # 检查内容质量
    if len(content) < 200:
        result.add_warning("SKILL.md 内容过短 (< 200 字符)")

    # 检查代码示例
    if '```' not in content:
        result.add_warning("SKILL.md 中没有代码示例")

    # 检查使用场景
    if '使用场景' not in content and '使用此技能当' not in content:
        result.add_info("SKILL.md 中没有明确的使用场景")

    return result


def validate_skill_structure(skill_dir: Path) -> ValidationResult:
    """验证 skill 目录结构"""
    result = ValidationResult(is_valid=True)

    # 必需的文件/目录
    required_files = ['SKILL.md']
    for filename in required_files:
        if not (skill_dir / filename).exists():
            result.add_error(f"缺少必需文件: {filename}")

    # 可选但推荐的目录
    optional_dirs = {
        'references': '深度文档',
        'scripts': '自动化脚本',
        'assets': '资源文件'
    }

    for dirname, purpose in optional_dirs.items():
        if (skill_dir / dirname).exists():
            result.add_info(f"包含 {dirname}/ 目录 ({purpose})")

    return result


def validate_skill_quality(skill_dir: Path) -> ValidationResult:
    """验证 skill 质量"""
    result = ValidationResult(is_valid=True)

    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        result.add_error("SKILL.md 不存在")
        return result

    content = skill_md.read_text()

    # 质量指标
    checks = {
        '触发器': ('触发', 'triggers', '使用此技能当'),
        '快速开始': ('快速开始', 'Quick Start', '使用方法'),
        '功能列表': ('功能', '特性', 'Features'),
        '文档链接': ('参考资料', '文档', 'references'),
    }

    for check_name, patterns in checks.items():
        if not any(pattern in content for pattern in patterns):
            result.add_warning(f"SKILL.md 中可能缺少 {check_name} 部分")

    return result


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python validate_skill.py <skill_directory>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])

    if not skill_dir.exists():
        print(f"错误: 目录不存在: {skill_dir}")
        sys.exit(1)

    if not skill_dir.is_dir():
        print(f"错误: 不是目录: {skill_dir}")
        sys.exit(1)

    print(f"验证 skill: {skill_dir}\n")

    # 运行验证
    structure_result = validate_skill_structure(skill_dir)
    content_result = validate_skill_md(skill_dir)
    quality_result = validate_skill_quality(skill_dir)

    # 汇总结果
    all_errors = (structure_result.errors +
                  content_result.errors +
                  quality_result.errors)
    all_warnings = (structure_result.warnings +
                    content_result.warnings +
                    quality_result.warnings)
    all_info = (structure_result.info +
                content_result.info +
                quality_result.info)

    # 输出结果
    if all_errors:
        print("❌ 错误:")
        for error in all_errors:
            print(f"  - {error}")
        print()

    if all_warnings:
        print("⚠️  警告:")
        for warning in all_warnings:
            print(f"  - {warning}")
        print()

    if all_info:
        print("ℹ️  信息:")
        for info in all_info:
            print(f"  - {info}")
        print()

    # 返回状态码
    if all_errors:
        print(f"验证失败: {len(all_errors)} 个错误")
        sys.exit(10)  # 验证失败退出码
    elif all_warnings:
        print(f"验证通过,但有 {len(all_warnings)} 个警告")
        sys.exit(0)
    else:
        print("✅ 验证通过")
        sys.exit(0)


if __name__ == '__main__':
    main()
