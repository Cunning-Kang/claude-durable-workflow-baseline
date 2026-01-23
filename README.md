# Skills Development Workspace

这是一个用于开发和测试 Claude Code skills 的工作空间。

## 工作空间说明

这个工作空间用于快速开发和验证新的 Claude Code skills 项目。

## 环境设置

本项目使用 [mise](https://mise.jdx.dev/) 进行环境管理。

```bash
# 安装 mise（如果尚未安装）
curl https://mise.jdx.dev/install.sh | sh

# 安装项目依赖
mise install
```

## 项目结构

```
.
├── .gitignore       # Git 忽略规则
├── mise.toml        # 项目环境配置
└── README.md        # 本文件
```

## 开始新项目

1. 在当前目录下创建新的项目文件夹
2. 使用 mise 管理项目特定的工具和依赖
3. 开发和测试你的 skill

## 资源

- [Claude Code Documentation](https://claude.ai/code)
- [Skill Creation Guide](https://github.com/anthropics/claude-code-skills)
