# Workmux & Tmux Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Modify workmux and tmux configurations to provide a pure single-pane Claude Code experience with a persistent floating terminal.

**Architecture:** Use tmux `display-popup` with `new-session -A` to create per-worktree persistent background terminals, and remove split panes from workmux config.

**Tech Stack:** tmux, workmux (YAML)

---

### Task 1: Update Workmux Configuration

**Files:**
- Modify: `~/.config/workmux/config.yaml`

**Step 1: Backup existing config**

Run: `cp ~/.config/workmux/config.yaml ~/.config/workmux/config.yaml.bak`
Expected: File copied successfully.

**Step 2: Modify the panes section**

Edit `~/.config/workmux/config.yaml` to remove the horizontal split logic so only the main agent pane remains.

```yaml
# ... (existing config)
panes:
  - command: <agent>
    focus: true

# 每次创建新 worktree 后自动执行
post_create:
# ... (rest of file)
```

**Step 3: Verify the yaml syntax**

Run: `cat ~/.config/workmux/config.yaml`
Expected: Valid yaml, no `- split: horizontal` lines.

**Step 4: Commit the plan document**
```bash
git add docs/plans/2026-03-02-workmux-tmux-plan.md
git commit -m "docs: add implementation plan for workmux-tmux integration"
```

### Task 2: Implement Tmux Persistent Popup

**Files:**
- Modify: `~/.config/tmux-vibe/tmux/tmux.conf`

**Step 1: Backup existing tmux config**

Run: `cp ~/.config/tmux-vibe/tmux/tmux.conf ~/.config/tmux-vibe/tmux/tmux.conf.bak`
Expected: File copied.

**Step 2: Add the float popup binding**

Append the following to `~/.config/tmux-vibe/tmux/tmux.conf`:

```tmux
# Task 5: Float terminal for workmux/Claude Code
bind-key f display-popup -w 85% -h 85% -E "tmux new-session -A -s float_#{session_name} -c \"#{pane_current_path}\""
```

**Step 3: Reload tmux configuration**

Run: `tmux source-file ~/.config/tmux-vibe/tmux/tmux.conf`
Expected: No errors output.

**Step 4: Verify keybinding is active**

Run: `tmux list-keys | grep "display-popup"`
Expected: Output showing `bind-key -T prefix f display-popup ...`