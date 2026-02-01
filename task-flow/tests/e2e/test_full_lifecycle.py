"""End-to-End tests for task-flow core components

These tests follow TDD methodology:
- Write failing test first
- Watch it fail
- Implement minimal code to pass

E2E tests verify GitOperations and MergeOracle work together correctly.
"""

import pytest
from pathlib import Path
import subprocess
import sys
import tempfile

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from git_operations import GitOperations
from merge_oracle import MergeOracle


class E2EBase:
    """E2E 测试基类"""

    @staticmethod
    def create_git_repo_with_task(tmp_path, task_status="In Progress"):
        """创建一个带任务文件的 git 仓库"""
        repo = tmp_path / "test-repo"
        repo.mkdir()

        # 初始化 git
        subprocess.run(["git", "init"], cwd=repo, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, capture_output=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=repo, capture_output=True)

        # 创建初始提交
        (repo / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=repo, capture_output=True)

        # 创建任务目录和任务文件
        tasks_dir = repo / "docs" / "tasks"
        tasks_dir.mkdir(parents=True)

        task_file = tasks_dir / "TASK-001-test-task.md"
        task_file.write_text(f"""---
id: TASK-001
title: Test Task
status: {task_status}
---
# Test Task
""")

        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Add task"], cwd=repo, capture_output=True)

        return repo


class TestGitOperationsAndMergeOracleIntegration(E2EBase):
    """测试 GitOperations 和 MergeOracle 的集成"""

    def test_full_workflow_no_conflicts(self, tmp_path):
        """E2E 测试:完整工作流(无冲突)"""
        # Arrange: 创建 git 仓库和任务
        repo = self.create_git_repo_with_task(tmp_path, "In Progress")
        git_ops = GitOperations(repo_path=repo)
        oracle = MergeOracle(git_ops)

        # Act: 创建 worktree
        worktree_path = repo / ".worktrees" / "feature"
        result = git_ops.create_worktree("feature", worktree_path)

        # Assert: worktree 创建成功
        assert result.success is True
        assert worktree_path.exists()

        # 在 feature 分支完成任务
        feature_task = worktree_path / "docs" / "tasks" / "TASK-001-test-task.md"
        feature_task.write_text("""---
id: TASK-001
title: Test Task
status: Done
---
# Test Task
""")

        subprocess.run(["git", "add", "."], cwd=worktree_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Complete task"], cwd=worktree_path, capture_output=True)

        # 检测冲突
        risk = oracle.detect_potential_conflicts("feature", target_branch="main")

        # Assert: 应该检测到 MEDIUM 风险(status 字段冲突)
        assert risk.risk_level == "MEDIUM"
        assert len(risk.files) > 0

        # 合并
        merge_result = oracle.smart_merge("feature", target_branch="main")

        # Assert: 合并成功
        assert merge_result.success is True

        # 验证任务状态已更新
        main_task = repo / "docs" / "tasks" / "TASK-001-test-task.md"
        content = main_task.read_text()
        assert "status: Done" in content

        # 清理
        cleanup_result = git_ops.cleanup_branch("feature", worktree_path)

        # Assert: 清理成功
        assert cleanup_result.branch_deleted is True
        assert not worktree_path.exists()

    def test_workflow_with_remote_detection(self, tmp_path):
        """E2E 测试:带远程仓库检测的工作流"""
        # Arrange: 创建 git 仓库
        repo = self.create_git_repo_with_task(tmp_path)
        git_ops = GitOperations(repo_path=repo)

        # Act: 检测远程仓库(应该没有)
        has_remote = git_ops.has_remote()

        # Assert: 应该返回 False
        assert has_remote is False

        # 添加远程仓库
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/test/repo.git"],
            cwd=repo,
            capture_output=True
        )

        # Act: 再次检测
        has_remote = git_ops.has_remote()

        # Assert: 现在应该返回 True
        assert has_remote is True

    def test_auto_push_skips_when_no_remote(self, tmp_path):
        """E2E 测试:无远程时智能跳过推送"""
        # Arrange: 创建没有远程的仓库
        repo = self.create_git_repo_with_task(tmp_path)
        git_ops = GitOperations(repo_path=repo)

        # Act: 尝试智能推送
        result = git_ops.smart_push("main")

        # Assert: 应该跳过推送
        assert result.skipped is True
        assert "no remote" in result.message.lower()

    def test_cleanup_sequence_in_real_workflow(self, tmp_path):
        """E2E 测试:真实工作流中的清理顺序"""
        # Arrange: 创建仓库、worktree 和分支
        repo = self.create_git_repo_with_task(tmp_path)
        git_ops = GitOperations(repo_path=repo)

        worktree_path = repo / ".worktrees" / "to-be-cleaned"
        git_ops.create_worktree("to-be-cleaned", worktree_path)

        # 在 worktree 中做些修改
        (worktree_path / "change.md").write_text("# Change")
        subprocess.run(["git", "add", "."], cwd=worktree_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Change"], cwd=worktree_path, capture_output=True)

        # Act: 清理
        result = git_ops.cleanup_branch("to-be-cleaned", worktree_path)

        # Assert: 按正确顺序清理
        assert result.worktree_removed is True
        # 分支未合并,所以删除失败是预期行为
        assert result.branch_deleted is False
        assert len(result.errors) > 0
        error_message = result.errors[0]
        assert "not fully merged" in error_message or "没有完全合并" in error_message
        assert result.order == ["worktree"]
        assert not worktree_path.exists()


class TestE2EErrorScenarios(E2EBase):
    """测试 E2E 错误场景"""

    def test_handles_duplicate_worktree_creation(self, tmp_path):
        """E2E 测试:处理重复创建 worktree"""
        # Arrange: 创建仓库
        repo = self.create_git_repo_with_task(tmp_path)
        git_ops = GitOperations(repo_path=repo)

        worktree_path = repo / ".worktrees" / "feature"

        # Act: 第一次创建
        result1 = git_ops.create_worktree("feature", worktree_path)
        assert result1.success is True

        # Act: 第二次创建同名 worktree
        result2 = git_ops.create_worktree("feature", worktree_path)

        # Assert: 应该失败
        assert result2.success is False
        assert result2.error is not None

    def test_cleanup_nonexistent_branch(self, tmp_path):
        """E2E 测试:清理不存在的分支"""
        # Arrange: 创建仓库(但没有 worktree)
        repo = self.create_git_repo_with_task(tmp_path)
        git_ops = GitOperations(repo_path=repo)

        # Act: 尝试清理不存在的 worktree 和分支
        result = git_ops.cleanup_branch(
            "nonexistent-branch",
            repo / ".worktrees" / "nonexistent-branch"
        )

        # Assert: 应该优雅处理
        assert result is not None
        assert isinstance(result.branch_deleted, bool)
        # branch 可能删除失败,但不应该崩溃


class TestE2EPerformance(E2EBase):
    """测试 E2E 性能"""

    def test_full_workflow_performance(self, tmp_path):
        """E2E 性能测试:完整工作流应该在合理时间内完成"""
        import time

        start_time = time.time()

        # 执行完整工作流
        repo = self.create_git_repo_with_task(tmp_path)
        git_ops = GitOperations(repo_path=repo)
        oracle = MergeOracle(git_ops)

        # 创建 worktree
        worktree_path = repo / ".worktrees" / "feature"
        git_ops.create_worktree("feature", worktree_path)

        # 完成任务
        task_file = worktree_path / "docs" / "tasks" / "TASK-001-test-task.md"
        task_file.write_text("""---
id: TASK-001
title: Test Task
status: Done
---
# Test Task
""")

        subprocess.run(["git", "add", "."], cwd=worktree_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Complete"], cwd=worktree_path, capture_output=True)

        # 合并
        oracle.smart_merge("feature", target_branch="main")

        # 清理
        git_ops.cleanup_branch("feature", worktree_path)

        elapsed_time = time.time() - start_time

        # Assert: 应该在 10 秒内完成(E2E 测试应该快速)
        assert elapsed_time < 10.0, f"E2E workflow took {elapsed_time:.2f}s, expected < 10s"
