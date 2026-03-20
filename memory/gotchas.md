# Gotchas

- Do not mirror native Task tool state into repo task files.
- Do not reintroduce worktree or branch-finishing assumptions through vendored skills.
- Do not add PM fields like owner, priority, deadline, or estimates to durable task files.

## L1 Test Task Gotchas — 2026-03-20

- **pytest-cov 依赖未预装** — 覆盖率检查会 fail 但不阻测试通过。如果覆盖率是关键验证点，需要先确认环境中有 pytest-cov。
- **PYTHONPATH 问题已修复** — `mise.toml` test/test-coverage 任务已持久化 `PYTHONPATH=src`，不再需要手动设置。

## Operating Model Trial Gotchas — 2026-03-20（修正版）

- **"文件存在" ≠ "正在发挥作用"** — `.claude/skills/` 目录存在但为空（repo级），不代表全局级安装状态。必须检查 `~/.claude/skills/`（全局级）。
- **"plugin enabled" ≠ "主控行为已验证"** — Superpowers 已激活不等于 Superpowers 主控的默认行为接管效果已验证。L0 任务太小，必须用 L1+ 任务才能验证。
- **不要在 L0 任务上声称完成了"主控+增强层"架构验证** — scope 太小，验证不充分。

## Skill Content Validator Gotchas — 2026-03-20

- **Frontmatter regex 要求 closing ---后有换行** — `^---\s*\n.*?\n---\s*\n` 模式要求 closing `---` 后必须紧跟换行符，否则 body 提取会失败。
- **Keyword substring 匹配有假阳性** — "valid" 会匹配 "invalid" 或 "validate" 中的子串，可能导致关键词误报缺失。
- **Keyword 提取仅处理纯字母单词** —  hyphenated words ("code-quality") 和数字会被忽略。
