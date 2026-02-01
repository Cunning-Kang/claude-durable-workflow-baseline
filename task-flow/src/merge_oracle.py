"""Merge Oracle - intelligent merge conflict detection and resolution

This module provides smart merge capabilities for task-flow:
1. Detect potential merge conflicts before merging
2. Auto-resolve simple conflicts (e.g., status field)
3. Provide suggestions for complex conflicts

Design principles:
- Use git commands to detect conflicts
- Auto-resolve simple, safe conflicts
- Fail gracefully with helpful suggestions for complex conflicts
"""

import subprocess
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List

from git_operations import GitOperations, ConflictRisk


@dataclass
class MergeResult:
    """合并操作的结果"""
    success: bool
    has_conflicts: bool
    conflicts_auto_resolved: int
    suggestions: List[str]


class MergeOracle:
    """智能合并冲突检测和解决"""

    # 可以自动解决的简单字段
    AUTO_RESOLVABLE_FIELDS = {"status", "completed_at", "current_step"}

    def __init__(self, git_ops: GitOperations):
        self.git_ops = git_ops

    def detect_potential_conflicts(self, feature_branch: str, target_branch: str = "main") -> ConflictRisk:
        """检测合并冲突风险

        策略:
        1. 找出 feature 分支相对于 target 分支的修改
        2. 检查这些文件在两个分支中的字段是否不同
        3. 返回风险级别和建议
        """
        # 获取 feature 分支相对于 target 分支的修改
        result = subprocess.run(
            ["git", "-C", str(self.git_ops.repo), "diff",
             "--name-only", target_branch, feature_branch],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # 可能是分支名问题,尝试检测当前分支
            current_branch = subprocess.run(
                ["git", "-C", str(self.git_ops.repo), "branch", "--show-current"],
                capture_output=True,
                text=True
            ).stdout.strip()

            if current_branch:
                result = subprocess.run(
                    ["git", "-C", str(self.git_ops.repo), "diff",
                     "--name-only", current_branch, feature_branch],
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    return ConflictRisk(risk_level="NONE", files=[], suggestion="")

        if not result.stdout.strip():
            return ConflictRisk(risk_level="NONE", files=[], suggestion="")

        changed_files = result.stdout.strip().split("\n")

        # 找出任务文件
        task_files = [f for f in changed_files if f.startswith("docs/tasks/") and f.endswith(".md")]

        if not task_files:
            return ConflictRisk(risk_level="NONE", files=[], suggestion="")

        # 检查每个任务文件的冲突字段
        conflicted_fields = set()
        for task_file in task_files:
            conflicts = self._check_task_file_conflicts_between_branches(
                task_file, target_branch, feature_branch
            )
            conflicted_fields.update(conflicts)

        if conflicted_fields:
            # 判断风险级别
            auto_resolvable = conflicted_fields & self.AUTO_RESOLVABLE_FIELDS
            complex = conflicted_fields - self.AUTO_RESOLVABLE_FIELDS

            if complex:
                return ConflictRisk(
                    risk_level="HIGH",
                    files=list(task_files),
                    suggestion=f"Complex conflicts in fields: {', '.join(complex)}. Manual resolution required."
                )
            elif auto_resolvable:
                return ConflictRisk(
                    risk_level="MEDIUM",
                    files=list(task_files),
                    suggestion=f"Auto-resolvable conflicts in: {', '.join(auto_resolvable)}. Will use feature branch values."
                )

        return ConflictRisk(risk_level="NONE", files=[], suggestion="")

    def _check_task_file_conflicts_between_branches(self, task_file: str, branch1: str, branch2: str) -> set:
        """检查任务文件在两个分支之间的冲突字段"""
        # 获取 branch1 的任务文件内容
        branch1_result = subprocess.run(
            ["git", "-C", str(self.git_ops.repo), "show", f"{branch1}:{task_file}"],
            capture_output=True,
            text=True
        )

        # 获取 branch2 的任务文件内容
        branch2_result = subprocess.run(
            ["git", "-C", str(self.git_ops.repo), "show", f"{branch2}:{task_file}"],
            capture_output=True,
            text=True
        )

        if branch1_result.returncode != 0 or branch2_result.returncode != 0:
            return set()

        # 解析 YAML frontmatter
        branch1_fields = self._parse_yaml_frontmatter(branch1_result.stdout)
        branch2_fields = self._parse_yaml_frontmatter(branch2_result.stdout)

        # 找出冲突的字段
        conflicts = set()
        for key in branch1_fields:
            if key in branch2_fields and branch1_fields[key] != branch2_fields[key]:
                conflicts.add(key)

        return conflicts

    def _parse_yaml_frontmatter(self, content: str) -> dict:
        """简单的 YAML frontmatter 解析器"""
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {}

        frontmatter = {}
        for line in match.group(1).strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return frontmatter

    def smart_merge(self, feature_branch: str, target_branch: str = "main") -> MergeResult:
        """智能合并：自动解决简单冲突

        策略:
        1. 先检测冲突风险
        2. 尝试三方合并
        3. 如果有冲突,尝试自动解决简单字段
        4. 失败则提供恢复建议
        """
        # 1. 检测冲突风险
        risk = self.detect_potential_conflicts(feature_branch)

        # 2. 尝试直接合并
        result = subprocess.run(
            ["git", "-C", str(self.git_ops.repo), "merge",
             "--no-commit", "--no-ff", feature_branch],
            capture_output=True,
            text=True
        )

        # 合并成功
        if result.returncode == 0:
            # 检查是否有冲突标记
            conflict_result = subprocess.run(
                ["git", "-C", str(self.git_ops.repo), "diff", "--name-only", "--diff-filter=U"],
                capture_output=True,
                text=True
            )
            conflicted_files = conflict_result.stdout.strip().split("\n") if conflict_result.stdout.strip() else []

            if not conflicted_files:
                # 没有冲突,完成合并
                subprocess.run(
                    ["git", "-C", str(self.git_ops.repo), "commit", "-m",
                     f"Merge {feature_branch} into {target_branch}"],
                    capture_output=True
                )
                return MergeResult(
                    success=True,
                    has_conflicts=False,
                    conflicts_auto_resolved=0,
                    suggestions=[]
                )

        # 3. 尝试自动解决简单冲突
        conflict_files = self._get_conflicted_files()
        auto_resolved = 0

        for conflict_file in conflict_files:
            if self._auto_resolve_task_file_conflict(conflict_file, feature_branch):
                auto_resolved += 1

        # 4. 检查是否所有冲突都已解决
        remaining_conflicts = self._get_conflicted_files()

        if not remaining_conflicts:
            # 所有冲突已解决,完成合并
            subprocess.run(
                ["git", "-C", str(self.git_ops.repo), "add", "."],
                capture_output=True
            )
            subprocess.run(
                ["git", "-C", str(self.git_ops.repo), "commit", "-m",
                 f"Merge {feature_branch} into {target_branch} (auto-resolved {auto_resolved} conflicts)"],
                capture_output=True
            )
            return MergeResult(
                success=True,
                has_conflicts=False,
                conflicts_auto_resolved=auto_resolved,
                suggestions=[]
            )
        else:
            # 仍有无法解决的冲突,中止合并
            subprocess.run(
                ["git", "-C", str(self.git_ops.repo), "merge", "--abort"],
                capture_output=True
            )
            return MergeResult(
                success=False,
                has_conflicts=True,
                conflicts_auto_resolved=auto_resolved,
                suggestions=[
                    f"Could not auto-resolve {len(remaining_conflicts)} conflicts",
                    f"Conflicting files: {', '.join(remaining_conflicts)}",
                    "Try manual merge with: git merge " + feature_branch,
                    "Or use strategy: git merge -X theirs " + feature_branch
                ]
            )

    def _get_conflicted_files(self) -> List[str]:
        """获取当前有冲突的文件列表"""
        result = subprocess.run(
            ["git", "-C", str(self.git_ops.repo), "diff", "--name-only", "--diff-filter=U"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []

    def _auto_resolve_task_file_conflict(self, conflict_file: str, feature_branch: str) -> bool:
        """尝试自动解决任务文件冲突

        策略:对于任务文件,总是采用 feature 分支的值(因为 feature 分支是最新的工作)
        """
        if not (conflict_file.startswith("docs/tasks/") and conflict_file.endswith(".md")):
            return False

        # 使用 feature 分支的版本
        result = subprocess.run(
            ["git", "-C", str(self.git_ops.repo), "checkout", "--theirs", conflict_file],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # 标记为已解决
            subprocess.run(
                ["git", "-C", str(self.git_ops.repo), "add", conflict_file],
                capture_output=True
            )
            return True

        return False
