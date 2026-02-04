# Task Flow 自动模板集成设计文档

> **日期**: 2025-02-04
> **版本**: v1.0
> **作者**: Claude Code + 用户协作设计

## 概述

本文档描述了 task-flow 技能的自动模板集成功能：当 task-flow 在任何项目中首次使用时，自动检测并智能更新/添加工作流模板到项目的 `CLAUDE.md` 或 `AGENTS.md` 文件中。

### 设计目标

1. **零配置启动**：用户无需手动复制粘贴模板
2. **版本感知**：自动检测并更新到最新版本
3. **智能合并**：不破坏用户现有内容
4. **LLM 友好**：明确、可预测的行为
5. **性能优化**：使用标记文件避免重复检测

---

## 核心决策

| 方面 | 选择 | 理由 |
|------|------|------|
| **触发方式** | 混合方案：首次检测 + `init` 命令 | LLM 友好 + 性能优化 |
| **版本标记** | HTML 注释：`<!-- TASK-FLOW-VERSION:x.x.x -->` | 非侵入 + LLM 可见 |
| **模板存储** | 独立模板文件（`templates/`） | 易于更新 + LLM 可读 |
| **插入策略** | 智能检测工作流章节 | 更好的文档融合 |
| **文件优先级** | CLAUDE.md > AGENTS.md | 官方推荐优先 |
| **更新策略** | 版本感知替换 + 智能合并 | 保持用户自定义内容 |

---

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Task Flow CLI 命令入口                    │
│                    (create-task, start-task, etc.)           │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              ProjectConfigManager (新增模块)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. 检测项目配置文件                                   │   │
│  │  2. 解析现有 task-flow 内容（如有）                   │   │
│  │  3. 版本比对与智能合并                               │   │
│  │  4. 写入更新后的内容                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
┌──────────────────────┐      ┌──────────────────────────┐
│   CLAUDE.md /        │      │   TemplateLoader         │
│   AGENTS.md          │      │   (从 templates/ 加载)    │
└──────────────────────┘      └──────────────────────────┘
```

### 核心组件

1. **ProjectConfigManager**：配置管理器，负责初始化检测和文件更新
2. **TemplateLoader**：模板加载器，从 `templates/` 目录加载内置模板
3. **VersionDetector**：版本检测器，解析现有的 task-flow 版本标记
4. **ContentMerger**：内容合并器，智能决定插入/更新位置
5. **TemplateRenderer**：模板渲染器，处理变量替换

---

## 数据流与初始化流程

### 完整数据流图

```
┌─────────────────────────────────────────────────────────────────┐
│                      用户运行任何 task-flow 命令                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              ProjectConfigManager.is_initialized()              │
│              检查 .task-flow-initialized 标记文件                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
           已初始化                   未初始化
                │                         │
                ▼                         ▼
        正常执行命令           ┌───────────────────────┐
                              │  显示初始化提示        │
                              │  [1] 自动初始化        │
                              │  [2] 稍后手动          │
                              │  [3] 跳过              │
                              └───────────┬───────────┘
                                          │
                              ┌───────────┴───────────┐
                              │                       │
                         用户选择自动            用户选择跳过
                              │                       │
                              ▼                       ▼
                    ┌─────────────────┐     显示警告信息
                    │  initialize()   │     继续执行命令
                    │  1. 加载模板    │
                    │  2. 检测版本    │
                    │  3. 合并内容    │
                    │  4. 写入文件    │
                    │  5. 创建标记    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ ✓ 初始化完成    │
                    │ 继续执行原命令  │
                    └─────────────────┘
```

### initialize() 方法

```python
def initialize(self,
              template_type: str = "standard",
              force: bool = False,
              interactive: bool = True,
              backup: bool = True) -> bool:
    """
    初始化项目配置

    Args:
        template_type: 模板类型 (minimal/standard/full)
        force: 强制覆盖现有内容
        interactive: 是否显示确认提示
        backup: 是否备份现有文件

    Returns:
        bool: 初始化是否成功
    """
```

---

## 模板设计

### 模板类型

| 类型 | 行数 | 适用场景 |
|------|------|----------|
| **minimal** | ~20 | 小型项目、个人项目 |
| **standard** | ~60 | 中型项目、团队协作 |
| **full** | ~120 | 大型项目、完整文档 |

### 模板文件结构

```
~/.claude/skills/task-flow/templates/
├── minimal.md          # 最小化模板
├── standard.md         # 标准模板
├── full.md             # 完整模板
└── section_template.md # 嵌入用章节模板
```

### 版本标记格式

```markdown
<!-- TASK-FLOW-VERSION:2.2.0 -->
<!-- AUTO-GENERATED BY task-flow v2.2.0 - DO NOT EDIT MANUALLY -->

## Task Flow 工作流

...

<!-- END-TASK-FLOW-SECTION -->
```

---

## 智能合并策略

### 插入位置检测

1. **优先级 1**：检测工作流相关章节前
   - `## 工作流`、`## 流程`、`## Workflow`
   - `## 快速开始`、`## Quick Start`
   - `## 开发流程`、`## Development`

2. **优先级 2**：追加到文件末尾

### 合并逻辑

```python
def merge_content(existing: str, new_section: str, version: str) -> str:
    """合并内容：替换或追加"""
    # 检测现有 task-flow 内容
    pattern = rf'<!-- TASK-FLOW-VERSION:[0-9.]+ -->.*?<!-- END-TASK-FLOW-SECTION -->'

    if re.search(pattern, existing, re.DOTALL):
        # 替换现有内容
        return re.sub(pattern, new_section, existing, flags=re.DOTALL)
    else:
        # 追加新内容
        insertion_point = find_insertion_point(existing)
        return existing[:insertion_point] + new_section + existing[insertion_point:]
```

---

## CLI 命令设计

### 新增命令：`task-flow init`

```bash
# 基本用法
task-flow init

# 选择模板类型
task-flow init --template minimal
task-flow init -t standard

# 强制覆盖
task-flow init --force

# 非交互模式
task-flow init --yes

# 跳过备份
task-flow init --no-backup
```

### 现有命令修改

所有 task-flow 命令在执行前自动检测初始化状态：

```bash
# 首次运行时
$ create-task "实现功能"

╔══════════════════════════════════════════╗
║  检测到项目尚未初始化 task-flow 工作流   ║
║                                           ║
║  [回车] 自动初始化（推荐）               ║
║  [Ctrl+C] 取消                           ║
╚══════════════════════════════════════════╝

✓ 已初始化 CLAUDE.md
✓ 创建任务: TASK-001
```

---

## CI/CD 处理

### 自动检测 CI 环境

```python
def is_ci_environment() -> bool:
    """检测是否在 CI 环境中"""
    ci_indicators = [
        'CI', 'CONTINUOUS_INTEGRATION',
        'GITHUB_ACTIONS', 'GITLAB_CI',
        'JENKINS_HOME', 'TRAVIS',
        'CIRCLECI', 'APPVEYOR'
    ]
    return any(os.environ.get(key) for key in ci_indicators)
```

### CI 环境行为

```bash
# CI 环境中：静默跳过初始化提示
$ create-task "test"

⚠️  CI 环境：跳过初始化提示
   请预先运行: task-flow init
✓ 创建任务: TASK-001
```

---

## 备份策略

### 备份配置

| 选项 | 默认值 | 说明 |
|------|--------|------|
| **备份对象** | - | CLAUDE.md 或 AGENTS.md |
| **备份时机** | 默认开启 | 文件存在且将被修改时 |
| **备份位置** | 同目录 | 与原文件相同目录 |
| **命名格式** | - | `CLAUDE.md.backup_YYYYMMDD_HHMMSS` |

### CLI 选项

```bash
# 默认：创建备份
task-flow init

# 跳过备份（高级用户）
task-flow init --no-backup

# 指定备份目录
task-flow init --backup-dir /tmp/backups
```

---

## 错误处理

### 错误类型

```python
class ProjectConfigManager:
    class ConfigError(Exception):
        """配置相关错误基类"""
        pass

    class TemplateNotFoundError(ConfigError):
        """模板文件未找到"""
        pass

    class FileWriteError(ConfigError):
        """文件写入失败"""
        pass
```

### 边界情况处理

| 场景 | 处理方式 |
|------|----------|
| 项目目录不存在 | 提示错误，建议先创建目录 |
| 无写入权限 | 提示错误，建议检查权限 |
| CLAUDE.md 是符号链接 | 跟随链接，备份原文件 |
| 文件被其他进程锁定 | 提示错误，建议关闭占用程序 |
| 磁盘空间不足 | 提示错误，显示所需空间 |
| 模板文件缺失 | 降级使用内置最小模板 |
| 版本标记格式错误 | 视为未初始化，追加新内容 |

---

## 文件结构

### 完整目录结构

```
~/.claude/skills/task-flow/
├── SKILL.md                          # 技能定义
├── README.md                         # 用户文档
├── requirements.txt                  # Python 依赖
│
├── src/                              # 源代码
│   ├── __init__.py
│   ├── __main__.py                   # Python 模块入口
│   ├── cli.py                        # CLI 命令解析（修改）
│   ├── task_manager.py               # 任务管理器（现有）
│   ├── execution_engine.py           # 执行引擎（现有）
│   ├── plan_generator/               # 计划生成器（现有）
│   ├── todowrite_compat/             # TodoWrite 兼容（现有）
│   ├── ci_detector.py                # CI 检测器（现有）
│   │
│   └── config/                       # 新增：配置管理模块
│       ├── __init__.py
│       ├── manager.py                # ProjectConfigManager
│       ├── template_loader.py        # TemplateLoader
│       ├── content_merger.py         # ContentMerger
│       └── template_renderer.py      # TemplateRenderer
│
├── templates/                        # 新增：模板目录
│   ├── minimal.md                    # 最小化模板
│   ├── standard.md                   # 标准模板
│   ├── full.md                       # 完整模板
│   └── section_template.md           # 章节嵌入模板
│
└── tests/                            # 测试套件
    ├── conftest.py                   # pytest 配置
    ├── test_cli.py                   # CLI 测试（修改）
    ├── test_task_manager.py          # 任务管理器测试（现有）
    ├── test_execution_engine.py      # 执行引擎测试（现有）
    ├── test_config_manager.py        # 配置管理器测试（新增）
    ├── test_template_loader.py       # 模板加载器测试（新增）
    ├── test_content_merger.py        # 内容合并器测试（新增）
    └── test_integration.py           # 集成测试（新增）
```

---

## 测试策略

### 单元测试

```python
# test_config_manager.py
class TestProjectConfigManager:
    def test_is_initialized_with_marker(self)
    def test_is_initialized_without_marker(self)
    def test_detect_existing_version(self)
    def test_detect_version_no_marker(self)
    def test_needs_update_true(self)
    def test_needs_update_false(self)
    def test_find_config_file(self)

# test_content_merger.py
class TestContentMerger:
    def test_merge_new_content(self)
    def test_replace_existing_content(self)
    def test_find_insertion_point(self)
    def test_workflow_heading_detection(self)

# test_template_loader.py
class TestTemplateLoader:
    def test_load_existing_template(self)
    def test_load_nonexistent_template(self)
```

### 集成测试

```python
# test_integration.py
class TestIntegration:
    def test_full_initialization_flow(self)
    def test_upgrade_from_old_version(self)
    def test_ci_environment_detection(self)
    def test_backup_creation(self)
```

---

## 性能优化

### 标记文件机制

```python
class ProjectConfigManager:
    INIT_MARKER = ".task-flow-initialized"
    VERSION_FILE = ".task-flow-version"

    @classmethod
    def is_initialized(cls, project_root: Path) -> bool:
        """O(1) 检测：只需检查标记文件"""
        return (project_root / cls.INIT_MARKER).exists()
```

**性能对比**：

| 操作 | 无标记文件 | 有标记文件 |
|------|-----------|-----------|
| 检测初始化状态 | O(n) 读取文件 | O(1) 检查文件存在 |
| 首次后每次运行 | ~10ms | ~0.1ms |

---

## 实施计划

### 阶段 1：核心功能（第 1 周）

1. 实现 `ProjectConfigManager` 类
2. 实现 `TemplateLoader` 类
3. 实现 `ContentMerger` 类
4. 创建模板文件（minimal/standard/full）
5. 添加 `init` 命令

### 阶段 2：集成与测试（第 2 周）

1. 修改现有命令添加初始化检测
2. 实现 CI 环境自动检测
3. 实现备份功能
4. 编写单元测试
5. 编写集成测试

### 阶段 3：文档与发布（第 3 周）

1. 更新 SKILL.md
2. 更新 README.md
3. 编写迁移指南
4. 发布 v2.3.0

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2025-02-04 | 初始设计文档 |

---

## 附录

### minimal.md 模板内容

```markdown
<!-- TASK-FLOW-TEMPLATE:MINIMAL -->

## Task Flow 快速参考

本项目使用 task-flow 管理任务。

| 命令 | 说明 |
|------|------|
| 创建任务：{标题} | 创建新任务 |
| 启动任务 TASK-XXX | 启动任务 |
| 完成任务 TASK-XXX | 完成任务 |

简化流程：创建 → 启动 → 实现 → 完成

> 由 task-flow v{VERSION} 自动生成
```

### standard.md 模板内容

```markdown
<!-- TASK-FLOW-TEMPLATE:STANDARD -->

## Task Flow 工作流

本项目采用 **task-flow v{VERSION}** 作为任务管理系统。

### 快速开始

```bash
创建任务：实现功能 X
启动任务 TASK-001
完成任务 TASK-001
```

### 核心命令

| 用户语句 | 功能 |
|---------|------|
| 创建任务：{标题} | 创建新任务 |
| 启动任务 TASK-XXX | 启动任务（创建 worktree） |
| 更新任务 TASK-XXX 进度到第 N 步 | 更新进度 |
| 完成任务 TASK-XXX | 完成并归档 |
| 查看任务 TASK-XXX | 查看详情 |
| 列出所有任务 | 显示任务列表 |
| 按计划执行 TASK-XXX | 执行下一批任务 |

### 工作流程

**标准流程**：创建任务 → 需求澄清 → 实施计划 → 启动任务 → 按计划执行 → 完成任务

**简化流程**：创建任务 → 启动任务 → 直接实现 → 完成任务

### 相关技能

- **task-flow**: 任务管理核心
- **superpowers:brainstorming**: 需求澄清
- **superpowers:writing-plans**: 计划编写

> 由 task-flow v{VERSION} 自动生成
```
