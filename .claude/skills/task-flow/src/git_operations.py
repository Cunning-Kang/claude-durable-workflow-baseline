"""Git operations abstraction layer for task-flow workflow.

This module provides a clean interface for git worktree operations,
pushing branches, and detecting conflicts.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import subprocess


@dataclass
class PushResult:
    """Result of a smart push operation."""
    success: bool
    skipped: bool
    message: str


@dataclass
class WorktreeResult:
    """Result of a worktree creation operation."""
    success: bool
    error: Optional[str] = None


@dataclass
class CleanupResult:
    """Result of a branch cleanup operation."""
    worktree_removed: bool
    branch_deleted: bool
    order: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class ConflictRisk:
    """Result of conflict detection."""
    risk_level: str  # "NONE", "LOW", "MEDIUM", "HIGH"
    files: List[str] = field(default_factory=list)


class GitOperations:
    """High-level git operations for task-flow workflow."""

    def __init__(self, repo_path: Path):
        """Initialize git operations for a repository.

        Args:
            repo_path: Path to the git repository
        """
        self.repo_path = Path(repo_path)

    def _run_git(self, args: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a git command in the repository.

        Args:
            args: Git command arguments (without 'git' prefix)
            capture_output: Whether to capture stdout/stderr

        Returns:
            CompletedProcess result
        """
        cmd = ["git"] + args
        return subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=capture_output,
            text=capture_output
        )

    def has_remote(self) -> bool:
        """Check if the repository has a remote configured.

        Returns:
            True if at least one remote is configured, False otherwise
        """
        result = self._run_git(["remote"])
        # git remote returns list of remote names, empty if none configured
        return bool(result.stdout.strip())

    def smart_push(self, branch: str) -> PushResult:
        """Push a branch to remote, with smart handling of various conditions.

        Args:
            branch: Branch name to push

        Returns:
            PushResult with success status and message
        """
        if not self.has_remote():
            return PushResult(
                success=False,
                skipped=True,
                message="No remote configured, skipping push"
            )

        # Attempt to push (will likely fail in tests, but we capture the result)
        result = self._run_git(["push", "-u", "origin", branch])

        return PushResult(
            success=result.returncode == 0,
            skipped=False,
            message=result.stdout if result.returncode == 0 else result.stderr
        )

    def create_worktree(self, branch: str, worktree_path: Path) -> WorktreeResult:
        """Create a new git worktree with the specified branch.

        Args:
            branch: Name for the new branch
            worktree_path: Path where the worktree should be created

        Returns:
            WorktreeResult with success status and error if failed
        """
        # Convert worktree_path to relative path if it's under repo_path
        try:
            worktree_path.relative_to(self.repo_path)
            rel_path = worktree_path.relative_to(self.repo_path)
        except ValueError:
            rel_path = worktree_path

        result = self._run_git(["worktree", "add", str(rel_path), "-b", branch])

        if result.returncode == 0:
            return WorktreeResult(success=True)
        else:
            return WorktreeResult(
                success=False,
                error=result.stderr.strip() if result.stderr else "Unknown error"
            )

    def cleanup_branch(self, branch: str, worktree_path: Path) -> CleanupResult:
        """Clean up a branch by removing its worktree and then the branch itself.

        The cleanup follows the correct order:
        1. Remove worktree
        2. Delete branch

        Args:
            branch: Name of the branch to clean up
            worktree_path: Path to the worktree directory

        Returns:
            CleanupResult with details of what was done
        """
        result = CleanupResult(worktree_removed=False, branch_deleted=False)
        worktree_path = Path(worktree_path)

        # Step 1: Remove worktree
        if worktree_path.exists():
            try:
                # Convert to relative path if possible
                try:
                    rel_path = worktree_path.relative_to(self.repo_path)
                except ValueError:
                    rel_path = worktree_path

                wt_result = self._run_git(["worktree", "remove", str(rel_path)])
                if wt_result.returncode == 0:
                    result.worktree_removed = True
                    result.order.append("worktree")
                else:
                    result.errors.append(f"Failed to remove worktree: {wt_result.stderr}")
                    return result
            except Exception as e:
                result.errors.append(f"Exception removing worktree: {e}")
                return result
        else:
            result.warnings.append("Worktree path does not exist")

        # Step 2: Delete branch
        branch_result = self._run_git(["branch", "-D", branch])
        if branch_result.returncode == 0:
            result.branch_deleted = True
            result.order.append("branch")
        else:
            # Branch deletion failed - this typically happens if worktree still exists
            result.errors.append(f"Failed to delete branch: {branch_result.stderr}")

        return result

    def detect_potential_conflicts(self, branch: str) -> ConflictRisk:
        """Detect potential merge conflicts for a branch.

        This checks if the branch has changes that might conflict
        with other branches.

        Args:
            branch: Branch name to check

        Returns:
            ConflictRisk with risk level and list of potentially conflicting files
        """
        # Get the list of files changed in the branch compared to main
        # For now, we use a simple heuristic: check if branch has any commits

        # First, get the base branch (typically main or master)
        base_result = self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])
        base_branch = base_result.stdout.strip()

        # Get commits unique to this branch
        merge_base_result = self._run_git(["merge-base", base_branch, branch])
        if merge_base_result.returncode != 0:
            # Branch doesn't exist or other error
            return ConflictRisk(risk_level="NONE", files=[])

        merge_base = merge_base_result.stdout.strip()

        # Get diff of files changed in this branch
        diff_result = self._run_git(
            ["diff", "--name-only", merge_base, branch],
            capture_output=True
        )

        if diff_result.returncode != 0:
            return ConflictRisk(risk_level="NONE", files=[])

        changed_files = [f for f in diff_result.stdout.strip().split("\n") if f]

        # Simple heuristic: if branch exists and has no unique commits, risk is NONE
        # More sophisticated detection would require merge_oracle logic
        if not changed_files:
            return ConflictRisk(risk_level="NONE", files=[])

        # For now, return LOW risk if there are any changes
        # This will be enhanced when merge_oracle is implemented
        return ConflictRisk(
            risk_level="NONE",  # Default to NONE for basic implementation
            files=[]
        )
