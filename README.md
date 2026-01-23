# GitHub to Skill

自动将 GitHub 上的顶级开源工具封装成 Claude Code skill。

## 功能

- 🔍 智能搜索 GitHub 上的优质工具
- 📊 多维度综合评分(stars、更新时间、issues 响应等)
- 🔬 深度分析仓库结构和依赖
- ⚡ 自动生成完整 skill
- 🚀 一键安装到 Claude Code

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```python
from scripts.github_to_skill import GitHubToSkill

gts = GitHubToSkill()
skill_dir = gts.run("I want to create a PDF converter tool")
```

## 配置

可选配置 GitHub Token:

```bash
export GITHUB_TOKEN="your_token"
```

## 测试

```bash
pytest tests/ -v
```

## 文档

- [设计文档](docs/plans/2025-01-23-github-to-skill-design.md)
- [实现计划](docs/plans/2025-01-23-github-to-skill-implementation.md)
- [GitHub API 参考](references/github-api.md)
- [评分算法](references/scoring-algorithm.md)

## License

MIT
