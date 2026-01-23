---
name: {{ skill_name }}
description: {{ description }} 使用此技能来{{ use_cases }}
---

# {{ readme_title }}

{{ readme_description }}

## 快速开始

### 安装

```bash
{{ installation_command }}
```

### 基本使用

{{ usage_example }}

## 主要功能

{% for feature in features %}
- {{ feature }}
{% endfor %}

## 使用场景

使用此技能当您需要:
{% for scenario in use_cases_list %}
- {{ scenario }}
{% endfor %}

## 高级功能

详见 [高级功能文档](references/advanced.md)

## 故障排除

### 常见问题

**问题**: 无法导入模块
**解决**: 确保已正确安装所有依赖

更多问题请查看 [故障排除指南](references/troubleshooting.md)
