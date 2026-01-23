# Skills Development Workspace

这是一个用于开发和测试 Claude Code skills 的工作空间。

## 当前状态

✅ **github-to-skill** 项目已成功发布!

该项目已迁移到独立仓库: [Cunning-Kang/github-to-skill](https://github.com/Cunning-Kang/github-to-skill)

## 项目历史

这个工作空间用于开发 `github-to-skill` 工具,该工具可以自动将 GitHub 上的开源工具封装成 Claude Code skill。

### 主要功能

- 🔍 智能搜索 GitHub 上的优质工具
- 📊 多维度综合评分(stars、更新时间、issues 响应等)
- 🔬 深度分析仓库结构和依赖
- ⚡ 自动生成完整 skill
- 🚀 一键安装到 Claude Code
- ✅ 交互式工具选择
- ✅ 自动质量验证
- ✅ 临时文件自动清理

### 相关文档

- [完成报告](COMPLETION_REPORT.md)
- [测试报告](TEST_REPORT.md)
- [设计文档](docs/plans/2025-01-23-github-to-skill-design.md)
- [实现计划](docs/plans/2025-01-23-github-to-skill-implementation.md)

## 使用 github-to-skill

请访问 [Cunning-Kang/github-to-skill](https://github.com/Cunning-Kang/github-to-skill) 获取最新版本和使用说明。

```bash
# 克隆仓库
git clone https://github.com/Cunning-Kang/github-to-skill.git
cd github-to-skill

# 安装依赖
pip install -r requirements.txt

# 使用
from scripts.github_to_skill import GitHubToSkill

gts = GitHubToSkill()
skill_dir = gts.run("I want to create a PDF converter tool")
```

## 未来计划

这个工作空间将继续用于开发新的 Claude Code skills。敬请期待!
