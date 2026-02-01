"""Git operations abstraction layer for task-flow

This module provides a unified, testable interface for Git operations.
All methods use subprocess to call git commands with structured return values.

Design principles:
1. Always use git -C to avoid CWD dependencies
2. Return structured dataclasses for results
3. Provide helpful error messages and suggestions
4. Never raise exceptions - return error results instead
"""

import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PushResult:
    """推送操作的结果"""
    success: bool
    skipped: bool
    message: str


@dataclass
class WorktreeResult:
    """worktree 创建结果"""
    success: bool
    error: Optional[str] = None


@dataclass
class CleanupResult:
    """清理操作的结果"""
    worktree_removed: bool
    branch_deleted: bool
    warnings: List[str]
    errors: List[str]
    order: List[str] = None

    def __post_init__(self):
        if self.order is None:
            self.order = []


@dataclass
class ConflictRisk:
    """合并冲突风险"""
    risk_level: str  # "NONE", "MEDIUM", "HIGH"
    files: List[str]
    suggestion: str = ""


class GitOperations:
    """Git 操作的统一抽象层"""

    def __init__(self, repo_path: Path):
        self.repo = repo_path

    def has_remote(self) -> bool:
        """检测是否有配置的远程仓库"""
        result = subprocess.run(
            ["git", "-C", str(self.repo), "remote", "-v"],
            capture_output=True,
            text=True
        )
        return len(result.stdout.strip()) > 0

    def smart_push(self, branch: str) -> PushResult:
        """智能推送:有 remote 则推,没有则跳过"""
        if not self.has_remote():
            return PushResult(
                success=False,
                skipped=True,
                message="No remote configured, skipping push"
            )

        result = subprocess.run(
            ["git", "-C", str(self.repo), "push", "-u", "origin", branch],
            capture_output=True,
            text=True
        )

        return PushResult(
            success=result.returncode == 0,
            skipped=False,
            message=result.stdout if result.returncode == 0 else result.stderr
        )

    def create_worktree(self, branch: str, worktree_path: Path) -> WorktreeResult:
        """创建 worktree"""
        result = subprocess.run(
            ["git", "-C", str(self.repo), "worktree", "add", str(worktree_path), "-b", branch],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return WorktreeResult(success=True)
        else:
            return WorktreeResult(success=False, error=result.stderr)

    def cleanup_branch(self, branch: str, worktree_path: Path) -> CleanupResult:
        """按正确顺序清理:先删除 worktree,再删除分支"""
        result = CleanupResult(
            worktree_removed=False,
            branch_deleted=False,
            warnings=[],
            errors=[]
        )

        # 1. 尝试删除 worktree
        if worktree_path.exists():
            try:
                subprocess.run(
                    ["git", "-C", str(self.repo), "worktree", "remove", str(worktree_path)],
                    check=True,
                    capture_output=True
                )
                result.worktree_removed = True
                result.order.append("worktree")
            except subprocess.CalledProcessError as e:
                result.errors.append(f"Failed to remove worktree: {e.stderr.decode() if e.stderr else str(e)}")
        else:
            result.warnings.append("Worktree path does not exist (already removed?)")

        # 2. 删除分支(即使 worktree 删除失败,也尝试)
        try:
            subprocess.run(
                ["git", "-C", str(self.repo), "branch", "-d", branch],
                check=True,
                capture_output=True
            )
            result.branch_deleted = True
            result.order.append("branch")
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode() if e.stderr else str(e)
            if "used by worktree" in stderr:
                result.errors.append(f"Cannot delete branch: worktree still exists")
            else:
                result.errors.append(f"Failed to delete branch: {stderr}")

        return result

    def detect_potential_conflicts(self, feature_branch: str) -> ConflictRisk:
        """检测合并冲突风险"""
        # 简化实现:暂时总是返回无风险
        # Phase 2 会实现真正的冲突检测
        return ConflictRisk(
            risk_level="NONE",
            files=[],
            suggestion=""
        )
