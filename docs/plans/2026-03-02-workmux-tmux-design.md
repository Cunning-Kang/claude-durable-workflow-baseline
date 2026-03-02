# Workmux & Tmux Integration Design for Claude Code

## Context and Goal
The user relies on `workmux` to manage git worktrees and `tmux` for terminal multiplexing. The core workflow uses Claude Code as the primary driver for software engineering tasks. The goal is to optimize the `workmux` and `tmux` configurations based on the first principles of attention, screen real-estate, and verification.

## First Principles
1. **Attention**: The conversation with AI is the primary output channel. AI must monopolize the main visual area.
2. **Space**: Reading diffs or documentation happens <5% of the time. These secondary tasks must consume 0% of the screen when inactive.
3. **Verification**: When diffs/docs are reviewed, they require high clarity and space.

## Architecture: The Persistent Float Model

### 1. Workmux Configuration (`config.yaml`)
- **Single Pane Layout**: Eliminate all horizontal or vertical splits. The `workmux` session will instantiate a single, 100% full-screen pane.
- **Agent Initialization**: The main pane will run `claude --dangerously-skip-permissions`, preserving the raw, empty waiting state without injecting artificial context.
- **Environment**: Keep existing `post_create` hooks (`if [ -f mise.toml ]; then mise install && mise run install; fi`) to ensure dependency consistency.

### 2. Tmux Configuration (`tmux.conf`)
- **Persistent Popup**: Implement a floating terminal (popup) that overlays the main Claude pane at 85% width and 85% height.
- **Keybinding**: Bind `prefix + f` to toggle the popup.
- **Background Persistence**: The popup will attach to a hidden, persistent tmux session. This allows the user to trigger long-running tasks, hide the popup, and recall it later without losing state.
- **Environment Parity**: The popup shell will inherit the exact same `mise` environment and working directory as the parent worktree.

## Data Flow & Lifecycle
1. User enters a worktree via `workmux`.
2. `mise` dependencies are installed via `post_create`.
3. Claude Code starts in the main, exclusive pane.
4. User needs to verify a diff -> User presses `prefix + f`.
5. Tmux opens an 85% sized popup, attaching to a hidden persistent session.
6. User runs `git diff`, reviews it, presses `prefix + f` (or detach) to dismiss.
7. Popup hides; background tasks in the popup (if any) continue running.

## Trade-offs & Considerations
- **Advantages**: 100% screen utilization for the main task, zero context switching overhead, ability to run background verification tasks.
- **Dependencies**: Requires tmux 3.2+ for the `display-popup` feature.