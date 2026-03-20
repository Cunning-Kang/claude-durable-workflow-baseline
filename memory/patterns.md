# Patterns

- Use `docs/specs/<feature>/index.md` as the durable front door for L1/L2 cross-session work.
- Keep repo task status coarse: ready, in_progress, blocked, done, dropped, split.
- Add verify/review docs only when evidence must persist beyond the session.
- Treat source repo `global/` as the canonical user-level distribution layer; install only thin cross-repo skills/commands into `~/.claude/*`, and keep workflow protocols, templates, memory, and feature state in repo baseline or repo state.

## L1 Test Task Execution — 2026-03-20

- **L1 测试任务应包含真实实现代码** — 纯文档/配置任务无法验证完整 workflow。
- **PYTHONPATH 问题在小工具中常见** — `src/` 子目录需要显式加入 PYTHONPATH 才能被 tests 导入，mise run test 默认不加。
- **Django/pytest 等框架自带的测试运行器比 mise run test 更可靠** — 如果框架有内置测试命令，优先使用。
- **PYTHONPATH 已在 mise.toml test 命令中持久化** — `env = { PYTHONPATH = "src" }` 已加入 test/test-coverage 任务，不再需要手动传入。

## Operating Model Trial — 2026-03-20（修正版）

- **检查 Superpowers 激活状态时，必须检查全局路径 `~/.claude/skills/` 而非 repo 级 `.claude/skills/`** — repo 级目录可能不存在或为空，不代表全局级安装状态。
- **"plugin enabled" ≠ "主控行为已验证接管"** — 必须用 L1+ 任务实际触发完整流程才能验证。
- **Durable state 文件 (index.md, spec.md, plan.md, tasks/T*.md) 提供最小结构化状态** — 适合跨 session 但不适合作为唯一执行追踪。
- **Native Task tools 是 session 执行追踪的权威工具** — durable files 是跨 session 里程碑追踪，不能混合使用。
- **Memory extraction 应在任务完成时立即进行** — 延迟会导致 pattern 丢失。

## Skill Content Validator — 2026-03-20

- **Keyword matching 需要处理单复数形式** — "validates" 和 "validate" 是不同单词，测试用例中的 content 必须包含与 description 完全匹配的关键词形式。
- **30% keyword 缺失阈值是合理的 heuristic** — 允许一定容错，避免过度报告错误。
- **Stop word list 用于 keyword 提取是有效的** — 3字母以上且非停用词的单词更有意义。
