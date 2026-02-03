"""MergeOracle - intelligent merge conflict detection and resolution.

This module provides intelligent merge conflict detection and resolution
for task-flow workflow, with special handling for task file frontmatter conflicts.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
import re
import subprocess


@dataclass
class ConflictRisk:
    """Result of conflict detection.

    Attributes:
        risk_level: Risk level - "NONE", "MEDIUM", or "HIGH"
        files: List of potentially conflicting files
        suggestion: Human-readable suggestion for handling conflicts
    """
    risk_level: str  # "NONE", "MEDIUM", "HIGH"
    files: List[str] = field(default_factory=list)
    suggestion: str = ""


@dataclass
class MergeResult:
    """Result of a smart merge operation.

    Attributes:
        success: Whether the merge completed successfully
        conflicts_auto_resolved: Number of conflicts automatically resolved
        suggestion: Human-readable suggestion if merge failed or had issues
    """
    success: bool
    conflicts_auto_resolved: int = 0
    suggestion: str = ""


class MergeOracle:
    """Intelligent merge conflict detection and resolution.

    This class analyzes potential merge conflicts between branches,
    with special handling for task file frontmatter (YAML) conflicts.
    """

    def __init__(self, git_ops):
        """Initialize MergeOracle.

        Args:
            git_ops: GitOperations instance for git operations
        """
        self.git_ops = git_ops

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from task file content.

        Args:
            content: File content with YAML frontmatter

        Returns:
            Dictionary of parsed frontmatter fields
        """
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return {}

        frontmatter_text = frontmatter_match.group(1)
        result = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
        return result

    def _get_file_content_at_ref(self, file_path: str, ref: str) -> Optional[str]:
        """Get file content at a specific git reference.

        Args:
            file_path: Path to the file
            ref: Git reference (branch name, commit hash, etc.)

        Returns:
            File content or None if not found
        """
        result = self.git_ops._run_git(
            ["show", f"{ref}:{file_path}"],
            capture_output=True
        )
        if result.returncode == 0:
            return result.stdout
        return None

    def _get_changed_files(self, branch: str, target_branch: str = "main") -> List[str]:
        """Get list of files changed in branch compared to target.

        Args:
            branch: Feature branch name
            target_branch: Target branch name (default: "main")

        Returns:
            List of changed file paths
        """
        # Get merge base
        merge_base_result = self.git_ops._run_git(
            ["merge-base", target_branch, branch],
            capture_output=True
        )
        if merge_base_result.returncode != 0:
            return []

        merge_base = merge_base_result.stdout.strip()

        # Get diff of files changed in this branch
        diff_result = self.git_ops._run_git(
            ["diff", "--name-only", merge_base, branch],
            capture_output=True
        )

        if diff_result.returncode != 0:
            return []

        return [f for f in diff_result.stdout.strip().split("\n") if f]

    def _analyze_task_file_conflict(
        self,
        file_path: str,
        branch: str,
        target_branch: str = "main"
    ) -> Dict[str, Any]:
        """Analyze potential conflicts in a task file.

        Args:
            file_path: Path to the task file
            branch: Feature branch name
            target_branch: Target branch name (default: "main")

        Returns:
            Dictionary with conflict analysis results
        """
        # Get content from both branches
        target_content = self._get_file_content_at_ref(file_path, target_branch)
        branch_content = self._get_file_content_at_ref(file_path, branch)

        # If file doesn't exist in one branch, no frontmatter conflict
        if not target_content or not branch_content:
            return {"has_conflicts": False, "conflicting_fields": []}

        # Parse frontmatter from both
        target_frontmatter = self._parse_frontmatter(target_content)
        branch_frontmatter = self._parse_frontmatter(branch_content)

        # Find conflicting fields
        conflicting_fields = []
        auto_resolvable_fields = []

        for key in set(list(target_frontmatter.keys()) + list(branch_frontmatter.keys())):
            target_val = target_frontmatter.get(key, "")
            branch_val = branch_frontmatter.get(key, "")

            if target_val != branch_val:
                # Status conflicts are generally auto-resolvable
                # (feature branch's Done takes precedence)
                if key == "status":
                    auto_resolvable_fields.append(key)
                else:
                    conflicting_fields.append(key)

        # Determine overall risk
        has_conflicts = len(conflicting_fields) > 0
        has_auto_resolvable = len(auto_resolvable_fields) > 0

        return {
            "has_conflicts": has_conflicts,
            "conflicting_fields": conflicting_fields,
            "auto_resolvable_fields": auto_resolvable_fields,
            "has_auto_resolvable": has_auto_resolvable
        }

    def detect_potential_conflicts(
        self,
        branch: str,
        target_branch: str = "main"
    ) -> ConflictRisk:
        """Detect potential merge conflicts for a branch.

        This analyzes changes in the feature branch and determines
        the risk level of merge conflicts, with special handling
        for task file frontmatter.

        Args:
            branch: Feature branch name
            target_branch: Target branch name (default: "main")

        Returns:
            ConflictRisk with risk level, files, and suggestion
        """
        changed_files = self._get_changed_files(branch, target_branch)

        # Filter to task files (in docs/tasks/ directory)
        task_files = [f for f in changed_files if "docs/tasks" in f or "tasks" in f]

        if not task_files:
            return ConflictRisk(
                risk_level="NONE",
                files=[],
                suggestion="No task file changes detected."
            )

        # Analyze each task file for conflicts
        all_conflicting_fields = []
        all_auto_resolvable = []
        conflicting_files = []

        for file_path in task_files:
            analysis = self._analyze_task_file_conflict(file_path, branch, target_branch)
            if analysis["has_conflicts"] or analysis["has_auto_resolvable"]:
                conflicting_files.append(file_path)
                all_conflicting_fields.extend(analysis["conflicting_fields"])
                all_auto_resolvable.extend(analysis["auto_resolvable_fields"])

        if not conflicting_files:
            return ConflictRisk(
                risk_level="NONE",
                files=[],
                suggestion="No conflicts detected in task files."
            )

        # Determine risk level based on conflicting fields
        if all_conflicting_fields:
            # Has non-auto-resolvable conflicts (e.g., title, current_step)
            risk_level = "HIGH"
            suggestion = (
                f"High risk: Multiple fields conflict in task files: "
                f"{', '.join(set(all_conflicting_fields))}. "
                f"Manual resolution may be required."
            )
        elif all_auto_resolvable:
            # Only auto-resolvable conflicts (status field)
            risk_level = "MEDIUM"
            suggestion = (
                f"Medium risk: Status field conflicts can be auto-resolved. "
                f"Feature branch status will take precedence."
            )
        else:
            risk_level = "MEDIUM"
            suggestion = "Medium risk: Task files have changes that may need review."

        return ConflictRisk(
            risk_level=risk_level,
            files=conflicting_files,
            suggestion=suggestion
        )

    def smart_merge(
        self,
        branch: str,
        target_branch: str = "main"
    ) -> MergeResult:
        """Attempt to merge feature branch into target branch.

        This performs an intelligent merge that:
        1. Checks for potential conflicts first
        2. Attempts the merge
        3. Handles simple status conflicts automatically

        Args:
            branch: Feature branch to merge
            target_branch: Target branch (default: "main")

        Returns:
            MergeResult with success status and details
        """
        # First, detect potential conflicts
        risk = self.detect_potential_conflicts(branch, target_branch)

        # Store current branch
        current_branch_result = self.git_ops._run_git(
            ["rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True
        )
        original_branch = current_branch_result.stdout.strip()

        # Checkout target branch
        checkout_result = self.git_ops._run_git(
            ["checkout", target_branch],
            capture_output=True
        )
        if checkout_result.returncode != 0:
            return MergeResult(
                success=False,
                suggestion=f"Failed to checkout {target_branch}: {checkout_result.stderr}"
            )

        try:
            # Attempt merge
            merge_result = self.git_ops._run_git(
                ["merge", "--no-commit", "--no-ff", branch],
                capture_output=True
            )

            conflicts_auto_resolved = 0

            if merge_result.returncode == 0:
                # Clean merge - commit it
                commit_result = self.git_ops._run_git(
                    ["commit", "-m", f"Merge {branch} into {target_branch}"],
                    capture_output=True
                )
                success = commit_result.returncode == 0

                # For status-only conflicts, count as auto-resolved
                if risk.risk_level == "MEDIUM" and "status" in risk.suggestion.lower():
                    conflicts_auto_resolved = 1

                return MergeResult(
                    success=success,
                    conflicts_auto_resolved=conflicts_auto_resolved,
                    suggestion="" if success else "Merge succeeded but commit failed"
                )
            else:
                # Merge had conflicts
                # Check if they're simple conflicts we can auto-resolve
                if risk.risk_level == "MEDIUM" and "status" in risk.suggestion.lower():
                    self.git_ops._run_git(
                        ["merge", "--abort"],
                        capture_output=True
                    )

                    # Try merge with theirs strategy for simple conflicts
                    merge_result2 = self.git_ops._run_git(
                        ["merge", "-X", "theirs", "--no-commit", "--no-ff", branch],
                        capture_output=True
                    )

                    if merge_result2.returncode == 0:
                        commit_result = self.git_ops._run_git(
                            ["commit", "-m", f"Merge {branch} into {target_branch} (auto-resolved)"],
                            capture_output=True
                        )

                        return MergeResult(
                            success=commit_result.returncode == 0,
                            conflicts_auto_resolved=1,
                            suggestion=""
                        )

                # Abort failed merge
                self.git_ops._run_git(["merge", "--abort"], capture_output=True)

                return MergeResult(
                    success=False,
                    conflicts_auto_resolved=0,
                    suggestion=risk.suggestion or "Merge conflicts detected. Manual resolution required."
                )
        finally:
            if original_branch and original_branch != target_branch:
                self.git_ops._run_git(["checkout", original_branch], capture_output=True)
