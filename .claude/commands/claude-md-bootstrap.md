---
description: 运行 claude-md-bootstrap 脚本以生成或刷新 CLAUDE.md 并回填 Project Overrides
---

执行以下脚本完成 CLAUDE.md 引导：

`python .claude/skills/claude-md-bootstrap/scripts/bootstrap_claude_md.py --project-root . --template .claude/skills/claude-md-bootstrap/templates/claude-md-thin.md --project-name "$(basename "$PWD")"`
