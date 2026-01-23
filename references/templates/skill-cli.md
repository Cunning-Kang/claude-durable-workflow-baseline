---
name: {{ skill_name }}
description: {{ description }} - 命令行工具,用于{{ use_cases }}
---

# {{ readme_title }}

{{ readme_description }}

## 快速开始

### 安装

```bash
{{ installation_command }}
```

### 基本使用

```bash
{{ cli_example }}
```

## 主要功能

{% for feature in features %}
- {{ feature }}
{% endfor %}

## 使用场景

此工具特别适合:
{% for scenario in use_cases_list %}
- {{ scenario }}
{% endfor %}

## 脚本

查看 [scripts/](scripts/) 目录获取可用的辅助脚本。
