# Context
用户现在要求的不只是规范化改写，还要求把这些变动**正式落地到当前项目路径**，并在**当前项目新建一个 worktree** 中验证它们是否真的可用：
- custom commands：`.claude/commands/commit-batch.md`、`.claude/commands/finish-branch.md`
- hook：`.claude/hooks/suggest-next-step.sh` + `.claude/settings.json`
- skill：`.claude/skills/spec-kit-execute/SKILL.md`

目标不是静态合规，而是端到端验证“能否正常使用且满足设计目标”。如果测试中暴露 bug、卡点或契约误解，需要做**针对性优化**、重新验证，并且只在完成这轮落地 + worktree 测试 + 必要修复之后，才向用户提交人工审核版本。

已确认约束：
- command / hook / skill 中不能暗示自动执行高风险 git 动作。
- hook 的额外上下文注入应采用官方更稳妥的 `UserPromptSubmit` 方案，而不是 `Stop` 注入。
- `spec-kit-execute` 保持执行型边界，不得违反其 no auto-commit / no auto-push 约束。
- worktree 测试必须尽量隔离主工作区，避免污染用户现有状态。

# Recommended approach
1. 先核对主工作区中的 5 个目标文件是否都已达到当前最终设计版本。
2. 在主工作区做最小化结构验证，确保配置和脚本处于可测试状态。
3. 新建独立 worktree，在 worktree 中构造最小测试场景，分别验证 command、hook、skill。
4. 如果测试失败，记录复现步骤和证据，只做最小必要修复，并在主工作区与 worktree 中重新验证。
5. 在所有目标通过后，再做一次独立官方文档复核或针对性复核，最后向用户提交人工审核版。

# Files to modify
- `/Users/cunning/Workspaces/heavy/skills-creation/.claude/commands/commit-batch.md`
- `/Users/cunning/Workspaces/heavy/skills-creation/.claude/commands/finish-branch.md`
- `/Users/cunning/Workspaces/heavy/skills-creation/.claude/hooks/suggest-next-step.sh`
- `/Users/cunning/Workspaces/heavy/skills-creation/.claude/settings.json`
- `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/spec-kit-execute/SKILL.md`

# Reuse / reference patterns
- command 结构参考：
  - `/Users/cunning/Workspaces/heavy/skills-creation/.worktrees/gsd-eval-local/.claude/commands/gsd/*.md`
- workflow / verification 参考：
  - `/Users/cunning/Workspaces/heavy/skills-creation/.worktrees/gsd-eval-local/.claude/get-shit-done/workflows/validate-phase.md`
  - `/Users/cunning/Workspaces/heavy/skills-creation/.worktrees/gsd-eval-local/.claude/get-shit-done/workflows/verify-work.md`
- 当前 skill 约束参考：
  - `/Users/cunning/Workspaces/heavy/skills-creation/.claude/skills/spec-kit-execute/SKILL.md`

# Planned changes and execution
## 1) Land the final main-workspace version
- 核对 5 个目标文件当前内容
- 如仍有遗留不一致，先在主工作区统一收敛到最终版本
- 确保 hook 脚本有可执行权限
- 不在这一阶段做 commit / push / PR

## 2) Minimal pre-test validation in main workspace
- 验证 `.claude/settings.json` 为合法 JSON
- 验证 command frontmatter 结构稳定
- 验证 `spec-kit-execute` 收尾文案仍为 suggest 而非 auto-run
- 验证 hook 脚本输出 JSON 结构与 `UserPromptSubmit` 方案一致

## 3) Create isolated worktree for runtime validation
- 新建一个测试 worktree（用户已明确要求 worktree）
- 在 worktree 内准备最小测试材料，避免污染主工作区
- 只在测试分支 / worktree 中制造演示性改动与测试文件

## 4) Worktree test matrix
### A. Hook test
- 场景 A1：工作树干净时，验证 `UserPromptSubmit` hook 是否给出偏向 `/finish-branch` 的建议
- 场景 A2：存在少量连贯改动时，验证 hook 是否给出偏向 `/commit-batch` 的建议
- 场景 A3：大量或明显不适合提交的改动时，验证 hook 不会给出误导性建议

### B. Command test
- `/commit-batch`
  - 在 worktree 制造一个小而连贯的 diff
  - 验证命令是否能正确审查、仅在连贯时生成一个 atomic commit
  - 验证不连贯场景下是否拒绝提交并说明拆分建议
- `/finish-branch`
  - 在干净 / 接近完成的场景下验证 readiness review 输出
  - 验证其只做评审与建议，不做自动 merge / delete / cleanup

### C. Skill test
- 准备最小 spec-like artifact 或使用仓库内现有可执行 artifact
- 调用 `spec-kit-execute` 的至少一个有效场景，验证：
  - 只执行已明确的 task / batch
  - 不擅自扩 scope
  - completion 报告中只做 suggest，不自动调用 `/commit-batch` 或 `/finish-branch`

## 5) Bugfix loop
- 若测试失败：
  1. 记录复现步骤、原始输出、触发条件
  2. 判断是否为 command / hook / skill 文案、契约或脚本逻辑问题
  3. 仅做最小必要修复
  4. 复跑失败用例
  5. 追加一轮轻量回归验证，避免引入新问题

## 6) Final review before user audit
- 汇总真实运行证据
- 如修复涉及契约层变更，再发起独立官方文档复核
- 最终向用户提交：
  - 落地文件
  - worktree 测试结果
  - 修复记录（如有）
  - 仍存风险 / 假设（如有）

# Verification evidence to collect
- 主工作区静态检查结果：JSON / frontmatter / wording
- worktree 路径、测试分支名、测试场景描述
- hook 触发时的原始输出或可核验证据
- command 运行结果：成功 / 拒绝、原因、相关 git 状态变化
- skill 运行结果：选择的 task/batch、执行边界、completion 行为
- 若有修复：bug 描述、根因、修复点、复测结果

# Risks
- `UserPromptSubmit` hook 的真实触发需要交互式验证，自动化验证能力有限
- custom command / skill 的“是否被 CLI 实际加载”需要真实运行验证，不能只靠静态文件存在判断
- worktree 中的 Claude 配置、生效时机、环境变量与主工作区可能存在差异
- 测试 `/commit-batch` 时会产生真实 commit，因此必须仅在测试 worktree 中进行，并控制 diff 规模

# Rollback
- 配置回滚：逐文件回退 5 个目标文件
- 测试回滚：删除测试 worktree 与测试分支
- 测试提交仅允许存在于 worktree 测试分支，不进入主分支，除非用户后续明确要求
