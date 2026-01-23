# GitHub to Skill - 设计方案

**日期**: 2025-01-23
**状态**: 设计已完成,待实现

## 概述

**github-to-skill** 是一个能够将 GitHub 上的顶级开源工具自动封装成 Claude Code skill 的系统。用户只需要描述他们想要做什么,系统就会自动搜索、评估、选择并封装相关工具。

### 核心目标

- **问题**: 将 GitHub 上的顶级开源工具快速、简单地封装成可复用的 skill
- **价值**: 避免重复造轮子,充分利用过去几十年互联网上的优质开源工具
- **成功标准**: 用户只需描述需求,系统自动搜索并封装成符合 Claude Code 标准的 skill

---

## 一、核心工作流

### 1. 用户发起请求
用户输入类似 "我想创建一个 PDF 转换工具的 skill" 的描述

### 2. 智能搜索
系统解析用户意图,提取关键词,使用 GitHub API 搜索相关仓库

### 3. 综合评分
对搜索结果进行多维度评分:
- Stars 数量 (30% 权重)
- 最近更新时间 (25% 权重)
- Issues 响应率 (20% 权重)
- Fork 数量 (15% 权重)
- Contributors 数量 (10% 权重)

### 4. 候选展示
向用户展示排名前 **3** 个候选工具,每个候选包括:
- 仓库名称和描述
- Stars、Forks、Watchers 数量
- 最后更新时间
- 主要编程语言
- 综合评分
- 简短的使用建议

### 5. 用户选择
用户选择一个工具后,系统继续封装流程

### 6. 深度分析
自动分析工具的:
- README 文档(提取安装、使用说明、示例)
- 代码结构(识别主要功能模块)
- 依赖关系(确定所需的脚本和工具)
- 文档完整性(判断是否需要生成额外的 references)

### 7. 全面生成
自动生成完整的 skill 结构:
- **SKILL.md**: 包含详细的 frontmatter 和使用指南
- **scripts/**: 如果工具需要脚本
- **references/**: 如果工具有复杂的文档或配置
- **assets/**: 如果工具需要模板或配置文件

### 8. 自动安装
将生成的 skill 自动安装到 `~/.claude/skills/` 目录

---

## 二、技术架构

### 项目结构

```
github-to-skill/
├── SKILL.md                    # 主技能文件
├── scripts/
│   ├── init_skill.py          # 初始化脚本(复用现有)
│   ├── package_skill.py       # 打包脚本(复用现有)
│   ├── search_github.py       # GitHub 搜索和评分
│   ├── analyze_repo.py        # 仓库深度分析
│   └── generate_skill.py      # Skill 文件生成器
├── references/
│   ├── github-api.md          # GitHub API 使用参考
│   ├── scoring-algorithm.md   # 评分算法详解
│   └── templates/
│       ├── skill-python.md    # Python 工具模板
│       ├── skill-js.md        # JavaScript 工具模板
│       ├── skill-cli.md       # CLI 工具模板
│       └── skill-docs.md      # 文档工具模板
└── assets/
    └── templates/
        └── skill-template/    # 基础 skill 模板结构
```

### 核心模块

#### 1. search_github.py - 搜索模块

**功能**:
- 从用户描述中提取关键词
- 调用 GitHub Search API 搜索仓库
- 支持 GitHub PAT 认证(可选)
- 实现速率限制处理
- 执行综合评分算法

**关键函数**:
```python
def search_repositories(query: str, github_token: Optional[str] = None) -> List[Repo]
def calculate_repo_score(repo: Dict) -> float
def filter_and_sort(repos: List[Repo], limit: int = 3) -> List[Repo]
```

**评分算法**:
- **Stars 分数** = log(stars + 1) * 30 (使用对数避免大数优势)
- **更新时间分数** = 天数转换函数 * 25 (最近 6 个月得分高)
- **Issues 响应率** = (closed_issues / total_issues) * 20
- **Forks 分数** = log(forks + 1) * 15
- **Contributors 分数** = min(contributors / 10, 1.0) * 10

#### 2. analyze_repo.py - 分析模块

**功能**:
- 克隆或下载仓库内容(浅克隆节省时间)
- 解析 README.md/README.rst/README.txt
- 分析代码结构(识别主要模块和入口点)
- 检测编程语言和框架
- 提取依赖信息(requirements.txt, package.json, go.mod 等)
- 识别文档和示例

**关键函数**:
```python
def clone_repository(repo_url: str, target_dir: str) -> str
def parse_readme(repo_dir: str) -> Dict[str, Any]
def analyze_code_structure(repo_dir: str, language: str) -> Dict
def extract_dependencies(repo_dir: str, language: str) -> List[str]
def detect_tool_type(repo_info: Dict, code_analysis: Dict) -> str
```

**工具类型检测**:
- `python-library`: Python 包/库
- `cli-tool`: 命令行工具
- `web-app`: Web 应用
- `documentation`: 文档工具
- `api-client`: API 客户端
- `utility`: 通用工具

#### 3. generate_skill.py - 生成模块

**功能**:
- 根据工具类型选择合适的模板
- 生成 SKILL.md(frontmatter + body)
- 生成必要的 scripts/ 文件
- 生成 references/ 文档
- 复制或生成 assets/ 模板
- 自动安装到 Claude Code skills 目录

**关键函数**:
```python
def generate_skill_md(repo_info: Dict, analysis: Dict, tool_type: str) -> str
def generate_scripts(repo_info: Dict, analysis: Dict) -> Optional[List[str]]
def generate_references(repo_info: Dict, analysis: Dict) -> Optional[List[str]]
def copy_assets(repo_info: Dict, tool_type: str) -> Optional[List[str]]
def install_skill(skill_dir: str, skill_name: str) -> bool
```

**模板系统**:
- 使用 Jinja2 模板引擎
- 每种工具类型有专门的模板
- 支持变量插值和条件块
- 自动提取代码示例和用法说明

---

## 三、数据流

```
用户输入 "我想创建一个 PDF 转换工具的 skill"
    ↓
[1] 意图解析
    - 提取关键词: "PDF", "转换", "工具"
    - 生成 GitHub 搜索查询: "PDF converter tool"
    ↓
[2] GitHub API 调用
    - 检查是否有 GitHub PAT
    - 调用 GET /search/repositories
    - 处理速率限制(等待或降级)
    ↓
[3] 评分和排序
    - 对每个仓库计算综合评分
    - 过滤掉评分过低的(< 30分)
    - 按评分降序排序
    - 取前 3 个
    ↓
[4] 展示候选
    - 格式化输出候选列表
    - 等待用户选择(输入 1-3)
    ↓
[5] 仓库克隆
    - 浅克隆选中的仓库(--depth 1)
    - 临时目录: /tmp/github-to-skill/<repo-name>/
    ↓
[6] 深度分析
    - 读取并解析 README
    - 检测编程语言和框架
    - 分析代码结构
    - 提取依赖
    - 确定工具类型
    ↓
[7] 选择模板
    - 根据工具类型选择模板
    - 加载 Jinja2 模板
    ↓
[8] 生成文件
    - 渲染 SKILL.md
    - 生成 scripts/ (如果需要)
    - 生成 references/ (如果需要)
    - 复制 assets/ (如果需要)
    ↓
[9] 安装 Skill
    - 目标目录: ~/.claude/skills/<skill-name>/
    - 复制所有生成的文件
    - 验证 skill 格式
    ↓
[10] 清理和报告
    - 删除临时克隆目录
    - 输出成功消息和使用建议
    - 可选: 打包成 .skill 文件
```

---

## 四、错误处理策略

### 1. GitHub API 错误

**403 Rate Limit Exceeded**:
- 如果有 PAT: 显示剩余等待时间,建议用户稍后重试
- 如果无 PAT: 提示用户提供 PAT 以获得更高限额
- 优雅降级: 使用缓存的历史搜索结果(如果可用)

**401 Unauthorized**:
- PAT 无效或过期
- 提示用户更新 PAT
- 降级到无认证模式(如果未完全禁用)

**404 Not Found**:
- 仓库已被删除或私有
- 从候选列表中移除
- 如果是唯一选项,提示用户重新搜索

**503 Service Unavailable**:
- GitHub 临时不可用
- 自动重试(最多 3 次,指数退避)
- 超过重试次数后提示用户稍后尝试

### 2. 仓库克隆错误

**网络错误**:
- 重试 3 次
- 超时设置为 30 秒
- 失败后提示用户检查网络连接

**仓库过大**:
- 使用浅克隆(--depth 1)
- 限制克隆大小(最多 100MB)
- 超过限制时询问用户是否继续

**Permission Denied**:
- 私有仓库需要认证
- 提示用户提供 PAT

### 3. 分析错误

**No README Found**:
- 警告用户文档不完整
- 降级到基础分析(仅代码结构)
- 生成的 skill 可能不完整

**无法检测编程语言**:
- 默认使用通用模板
- 提示用户可能需要手动调整

**依赖解析失败**:
- 继续生成,但不包含依赖相关的脚本
- 警告用户可能需要手动安装依赖

### 4. 生成错误

**模板渲染失败**:
- 捕获详细错误信息
- 尝试使用简化模板重试
- 记录错误供调试

**文件写入失败**:
- 检查目标目录权限
- 提示用户手动安装

**Skill 验证失败**:
- 运行 package_skill.py 的验证逻辑
- 报告具体错误(缺少 frontmatter,格式问题等)
- 尝试自动修复简单问题

### 5. 安装错误

**Claude Code 目录不存在**:
- 创建 `~/.claude/skills/` 目录
- 提示用户这是首次安装

**权限不足**:
- 提示用户使用 sudo 或手动复制
- 生成安装脚本供用户执行

**Skill 已存在**:
- 询问用户是否覆盖
- 备份现有 skill
- 更新时间戳

---

## 五、实现细节和优化

### 评分算法优化

**综合评分计算** (满分 100 分):

```python
def calculate_repo_score(repo):
    # Stars 分数 (30%)
    stars_score = min(math.log(repo.stars + 1) * 3, 30)

    # 更新时间分数 (25%)
    days_since_update = (datetime.now() - repo.updated_at).days
    if days_since_update <= 30:
        update_score = 25
    elif days_since_update <= 90:
        update_score = 20
    elif days_since_update <= 180:
        update_score = 15
    elif days_since_update <= 365:
        update_score = 10
    else:
        update_score = 5

    # Issues 响应率 (20%)
    if repo.open_issues + repo.closed_issues > 0:
        issues_score = (repo.closed_issues / (repo.open_issues + repo.closed_issues)) * 20
    else:
        issues_score = 10  # 默认中等分数

    # Forks 分数 (15%)
    forks_score = min(math.log(repo.forks + 1) * 2, 15)

    # Contributors 分数 (10%)
    contributors_score = min(repo.contributors / 10, 1.0) * 10

    total_score = stars_score + update_score + issues_score + forks_score + contributors_score
    return round(total_score, 2)
```

**过滤规则**:
- 评分低于 30 分的工具不展示
- 如果过滤后少于 3 个,降低阈值到 20 分
- 如果仍然不足,展示所有有效结果并提示用户重新搜索

### 用户交互界面

**候选工具展示格式**:

```
根据您的描述 "PDF 转换工具",我找到了以下顶级开源工具:

[1] pdf-lib - 创建和修改 PDF 文档的 JavaScript 库
    ⭐ Stars: 12,534  |  🔄 Forks: 1,234  |  👀 Watchers: 567
    📅 最后更新: 3 天前  |  💻 语言: TypeScript
    🎯 综合评分: 87.5/100
    💡 适合: 需要编程方式处理 PDF 的场景

[2] pdftk-server - PDF 工具包的命令行工具
    ⭐ Stars: 8,923  |  🔄 Forks: 892  |  👀 Watchers: 234
    📅 最后更新: 1 周前  |  💻 语言: C++
    🎯 综合评分: 79.2/100
    💡 适合: 批量处理和服务器端自动化场景

[3] PyPDF2 - PDF 处理的 Python 库
    ⭐ Stars: 6,789  |  🔄 Forks: 1,456  |  👀 Watchers: 345
    📅 最后更新: 2 周前  |  💻 语言: Python
    🎯 综合评分: 75.8/100
    💡 适合: Python 生态系统的 PDF 处理需求

请输入数字 (1-3) 选择要封装的工具,或输入 'q' 重新搜索:
```

### 环境配置

**GitHub Token 配置**:

系统会按以下顺序查找 GitHub Token:
1. 环境变量 `GITHUB_TOKEN`
2. 环境变量 `GITHUB_PAT`
3. `~/.github-token` 文件(第一行)
4. 询问用户是否要提供(可选)

**首次使用向导**:

```
首次使用 github-to-skill!

为了获得更好的搜索体验,建议提供 GitHub Personal Access Token。
有了 Token 后,您每小时可以搜索 5000 次(无 Token 仅 60 次)。

是否要配置 GitHub Token? (y/n): y

请输入您的 GitHub Personal Access Token:
[粘贴 Token]
Token 已保存到 ~/.github-token

现在开始搜索工具...
```

### 缓存机制

**搜索结果缓存**:
- 缓存最近的 100 次搜索结果
- 缓存有效期: 24 小时
- 存储位置: `~/.cache/github-to-skill/search_cache.json`
- 命中缓存时询问用户是否使用缓存结果

**仓库克隆缓存**:
- 临时克隆的仓库保留 1 小时
- 如果用户重新选择同一工具,直接使用缓存
- 定期清理过期缓存

### 性能优化

**并行处理**:
- 同时搜索多个关键词变体
- 并行分析多个仓库的 README(在展示候选时预分析)

**增量分析**:
- 先快速分析 README 获取基本信息
- 用户选择后再进行深度代码结构分析
- 按需下载完整仓库

**智能取消**:
- 用户可以随时中断搜索(Ctrl+C)
- 已获得的结果会保存
- 重新启动时从断点继续

### 模板系统

**工具类型到模板的映射**:

```python
TEMPLATE_MAPPING = {
    'python-library': {
        'skill_template': 'references/templates/skill-python.md',
        'includes': ['scripts', 'references'],
        'examples_from': ['examples/', 'tests/']
    },
    'cli-tool': {
        'skill_template': 'references/templates/skill-cli.md',
        'includes': ['scripts'],
        'examples_from': ['README.md', 'docs/']
    },
    'web-app': {
        'skill_template': 'references/templates/skill-js.md',
        'includes': ['assets'],
        'examples_from': ['examples/', 'demo/']
    },
    'documentation': {
        'skill_template': 'references/templates/skill-docs.md',
        'includes': ['references', 'assets'],
        'examples_from': ['docs/', 'examples/']
    }
}
```

**SKILL.md 生成规则**:

**Frontmatter**:
```yaml
---
name: <repo-name>-<purpose>
description: <从 README 提取的简短描述,包含使用场景>
---
```

**Body 结构**:
1. **关于这个工具** (2-3 句话介绍)
2. **快速开始** (安装方法和最简单的使用示例)
3. **主要功能** (列出 3-5 个核心功能)
4. **使用场景** (何时使用这个技能)
5. **高级功能** (引用 references/ 中的详细文档)
6. **故障排除** (常见问题和解决方案)

### 测试策略

**单元测试**:
- 评分算法的准确性
- 关键词提取的正确性
- 模板渲染的完整性

**集成测试**:
- GitHub API 调用
- 仓库克隆和分析
- Skill 生成和安装

**端到端测试**:
- 完整的用户工作流
- 使用几个知名仓库(如 pdf-lib, PyPDF2)进行测试

### 验证和改进

**自动验证**:
- 使用现有的 `package_skill.py` 验证生成的 skill
- 检查 frontmatter 格式
- 验证必需文件存在

**用户反馈收集**:
- 询问生成的 skill 是否满足需求
- 收集需要手动调整的部分
- 记录到改进日志

**迭代改进**:
- 分析常见的手动调整模式
- 更新模板和生成逻辑
- 持续优化评分算法

---

## 六、技术栈总结

- **核心搜索和分析**: Python (PyGithub, Jinja2,BeautifulSoup4)
- **Skill 生成**: Bash/Shell (与现有 skill-creator 工具链兼容)
- **模板引擎**: Jinja2
- **GitHub API**: PyGithub 库
- **代码分析**: AST (Python), tree-sitter (多语言)
- **配置管理**: YAML/TOML

---

## 七、下一步行动

1. ✅ 完成设计文档
2. ⏳ 创建实现计划 (使用 superpowers:writing-plans)
3. ⏳ 设置开发环境 (使用 superpowers:using-git-worktrees)
4. ⏳ 实现核心模块
5. ⏳ 测试和迭代

---

**设计版本**: 1.0
**最后更新**: 2025-01-23
**设计师**: Claude (with user validation)
