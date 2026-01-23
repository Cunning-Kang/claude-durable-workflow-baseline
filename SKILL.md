---
name: github-to-skill
description: 自动将 GitHub 上的顶级开源工具封装成 Claude Code skill。使用此技能当您需要: (1) 根据功能描述搜索 GitHub 上的优质工具, (2) 自动分析仓库并生成符合 Claude Code 标准的 skill, (3) 快速复用现有开源工具而不重复造轮子
---

# GitHub to Skill

自动将 GitHub 上的顶级开源工具封装成 Claude Code skill 的工具。

## 功能

- **智能搜索**: 根据功能描述搜索 GitHub 上的相关工具
- **综合评分**: 多维度评估工具质量(stars、更新时间、issues 响应等)
- **自动分析**: 深度分析仓库结构、依赖和文档
- **一键生成**: 自动生成完整的 skill 结构(SKILL.md、scripts、references、assets)
- **自动安装**: 直接安装到 Claude Code skills 目录

## 使用场景

使用此技能当您需要:
- 快速将现有开源工具集成到 Claude Code 工作流
- 避免重复开发已有功能
- 发现和利用 GitHub 上的优质工具
- 自动化创建重复性的 skill

## 快速开始

```python
from scripts.github_to_skill import GitHubToSkill

# 创建实例
gts = GitHubToSkill()

# 执行搜索和生成
skill_dir = gts.run("I want to create a PDF converter tool")
```

## 评分算法

系统使用以下维度综合评分:
- Stars 数量 (30%)
- 最近更新时间 (25%)
- Issues 响应率 (20%)
- Fork 数量 (15%)
- Contributors 数量 (10%)

## 模块

- `github_client.py`: GitHub API 客户端
- `scoring.py`: 仓库评分算法
- `analyzer.py`: 仓库结构分析
- `generator.py`: Skill 文件生成
- `github_to_skill.py`: 主流程协调

## 配置

可选配置 GitHub Token 以获得更高的 API 限额:

```bash
# 方式 1: 环境变量
export GITHUB_TOKEN="your_token_here"

# 方式 2: 文件
echo "your_token_here" > ~/.github-token
```

## 参考资料

详见:
- [GitHub API 使用参考](references/github-api.md)
- [评分算法详解](references/scoring-algorithm.md)
- [设计文档](docs/plans/2025-01-23-github-to-skill-design.md)
