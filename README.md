# GitHub to Skill

自动将 GitHub 上的顶级开源工具封装成 Claude Code skill。

## 项目状态

项目已使用 **macos-mise-bootstrap** 完成初始化并实现了全部功能。

## 功能

- 🔍 智能搜索 GitHub 上的优质工具
- 📊 多维度综合评分(stars、更新时间、issues 响应等)
- 🔬 深度分析仓库结构和依赖
- ⚡ 自动生成完整 skill
- 🚀 一键安装到 Claude Code
- ✅ 交互式工具选择
- ✅ 自动质量验证
- ✅ 临时文件自动清理

## 环境配置

- **Python 版本**: 3.10+ (通过 mise 管理)
- **虚拟环境**: `.venv` (已创建并激活)
- **依赖管理**: requirements.txt

## 快速开始

### 激活虚拟环境

```bash
# 方式 1: 使用 mise (推荐)
mise exec -- python <script>

# 方式 2: 直接激活
source .venv/bin/activate
```

### 安装依赖

```bash
# 使用 mise task
mise run install

# 或手动安装
pip install -r requirements.txt
```

### 使用

```python
from scripts.github_to_skill import GitHubToSkill

gts = GitHubToSkill()
skill_dir = gts.run("I want to create a PDF converter tool")
```

### 运行测试

```bash
# 使用 mise task
mise run test

# 或手动运行
python -m pytest tests/ -v
```

## 可用任务

项目配置了以下 mise tasks:

- `mise run test` - 运行测试
- `mise run test-coverage` - 运行测试并生成覆盖率报告
- `mise run install` - 安装依赖
- `mise run dev` - 安装开发依赖
- `mise run format` - 格式化代码 (black)
- `mise run lint` - 代码检查 (pylint)
- `mise run check` - 类型检查 (mypy)

## 项目结构

```
.
├── .venv/              # Python 虚拟环境
├── docs/               # 项目文档
│   └── plans/         # 设计和实现计划
├── scripts/           # Python 源代码
│   ├── github_client.py    # GitHub API 客户端
│   ├── scoring.py          # 评分算法
│   ├── analyzer.py         # 仓库分析器
│   ├── generator.py        # Skill 生成器
│   ├── github_to_skill.py  # 主流程
│   ├── validate_skill.py   # 质量验证
│   └── __init__.py        # 模块初始化
├── tests/             # 测试代码
│   └── __init__.py   # 测试初始化
├── references/        # 参考文档
│   ├── github-api.md
│   ├── scoring-algorithm.md
│   └── templates/    # Skill 模板
├── examples/         # 使用示例
├── mise.toml          # Mise 配置文件
├── requirements.txt   # Python 依赖
├── pytest.ini         # Pytest 配置
├── SKILL.md          # Skill 文档
└── .gitignore         # Git 忽略规则
```

## 配置 GitHub Token (可选)

为了获得更高的 GitHub API 限额,可以配置 Personal Access Token:

```bash
# 方式 1: 环境变量
export GITHUB_TOKEN="your_token_here"

# 方式 2: 文件 (复制示例文件)
cp .github-token.example .github-token
# 编辑 .github-token 并粘贴 token
```

获取 Token: https://github.com/settings/tokens
需要权限: `repo` (full control)

## 文档

- [设计文档](docs/plans/2025-01-23-github-to-skill-design.md)
- [实现计划](docs/plans/2025-01-23-github-to-skill-implementation.md)
- [GitHub API 参考](references/github-api.md)
- [评分算法](references/scoring-algorithm.md)
- [SKILL.md](SKILL.md) - 技能使用文档

## 测试

项目采用 **TDD (测试驱动开发)** 方法,每个模块都有完整的测试覆盖。

测试覆盖:
- ✅ 25 个测试全部通过
- ✅ 46% 代码覆盖率
- ✅ 包含单元测试和端到端测试

## License

MIT
