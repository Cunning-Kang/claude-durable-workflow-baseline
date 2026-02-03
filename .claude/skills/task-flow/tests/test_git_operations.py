"""Tests for GitOperations abstraction layer

These tests follow TDD methodology:
- Write failing test first
- Watch it fail
- Implement minimal code to pass
"""

import pytest
from pathlib import Path
import subprocess
import sys

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from git_operations import GitOperations, PushResult, WorktreeResult, CleanupResult, ConflictRisk


@pytest.fixture
def git_repo(tmp_path):
    """创建一个测试用的 git 仓库"""
    repo = tmp_path / "test-repo"
    repo.mkdir()

    # 初始化 git
    subprocess.run(["git", "init"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, capture_output=True)

    # 创建初始提交
    (repo / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "."], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial"], cwd=repo, capture_output=True)

    return repo


class TestHasRemote:
    """测试 has_remote() 方法"""

    def test_has_remote_returns_false_when_no_remote_configured(self, git_repo):
        """当没有配置远程仓库时,has_remote 应该返回 False"""
        git_ops = GitOperations(repo_path=git_repo)
        result = git_ops.has_remote()
        assert result is False

    def test_has_remote_returns_true_when_remote_exists(self, git_repo):
        """当配置了远程仓库时,has_remote 应该返回 True"""
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/test/repo.git"],
            cwd=git_repo,
            capture_output=True
        )
        git_ops = GitOperations(repo_path=git_repo)
        result = git_ops.has_remote()
        assert result is True


class TestSmartPush:
    """测试 smart_push() 方法"""

    def test_smart_push_skips_when_no_remote(self, git_repo):
        """当没有远程仓库时,smart_push 应该跳过并返回 skipped=True"""
        git_ops = GitOperations(repo_path=git_repo)
        result = git_ops.smart_push("main")
        assert result.success is False
        assert result.skipped is True
        assert "no remote" in result.message.lower()

    def test_smart_push_pushes_when_remote_exists(self, git_repo):
        """当有远程仓库时,smart_push 应该执行推送 (注意:会失败因为远程不存在)"""
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/test/nonexistent.git"],
            cwd=git_repo,
            capture_output=True
        )
        git_ops = GitOperations(repo_path=git_repo)
        result = git_ops.smart_push("main")
        assert result.skipped is False
        # 推送会失败,但这是预期的
        assert result.success is False


class TestCreateWorktree:
    """测试 create_worktree() 方法"""

    def test_create_worktree_creates_branch_and_directory(self, git_repo):
        """create_worktree 应该创建新分支和工作目录"""
        git_ops = GitOperations(repo_path=git_repo)
        worktree_path = git_repo / ".worktrees" / "feature-branch"
        result = git_ops.create_worktree("feature-branch", worktree_path)
        assert result.success is True
        assert worktree_path.exists()
        assert (worktree_path / ".git").exists()

        # 验证分支被创建
        branch_result = subprocess.run(
            ["git", "branch", "--list", "feature-branch"],
            cwd=git_repo,
            capture_output=True,
            text=True
        )
        assert "feature-branch" in branch_result.stdout

    def test_create_worktree_returns_error_on_duplicate_branch(self, git_repo):
        """创建已存在的分支名时应该返回错误信息"""
        git_ops = GitOperations(repo_path=git_repo)
        # 第一次创建成功
        worktree_path = git_repo / ".worktrees" / "existing-branch"
        git_ops.create_worktree("existing-branch", worktree_path)

        # 第二次创建同名分支会失败
        result = git_ops.create_worktree("existing-branch", worktree_path)
        assert result.success is False
        assert result.error is not None
        assert len(result.error) > 0


class TestCleanupBranch:
    """测试 cleanup_branch() 方法"""

    def test_cleanup_sequence_removes_worktree_then_branch(self, git_repo):
        """清理应该按照正确顺序:先删除 worktree,再删除分支"""
        git_ops = GitOperations(repo_path=git_repo)
        worktree_path = git_repo / ".worktrees" / "to-be-cleaned"
        git_ops.create_worktree("to-be-cleaned", worktree_path)
        result = git_ops.cleanup_branch("to-be-cleaned", worktree_path)
        assert result.worktree_removed is True
        assert result.branch_deleted is True
        assert result.order == ["worktree", "branch"]
        assert not worktree_path.exists()

        # 验证分支已被删除
        branch_result = subprocess.run(
            ["git", "branch", "--list", "to-be-cleaned"],
            cwd=git_repo,
            capture_output=True,
            text=True
        )
        assert "to-be-cleaned" not in branch_result.stdout

    def test_cleanup_handles_missing_worktree_gracefully(self, git_repo):
        """如果 worktree 已经被手动删除,cleanup 仍然应该能删除分支"""
        git_ops = GitOperations(repo_path=git_repo)
        # 创建分支但不创建 worktree
        subprocess.run(
            ["git", "branch", "orphan-branch"],
            cwd=git_repo,
            capture_output=True
        )
        nonexistent_path = git_repo / ".worktrees" / "orphan-branch"
        result = git_ops.cleanup_branch("orphan-branch", nonexistent_path)
        assert result.branch_deleted is True
        assert result.worktree_removed is False
        assert len(result.warnings) > 0
        assert "worktree" in result.warnings[0].lower()

    def test_cleanup_fails_when_worktree_still_exists(self, git_repo):
        """如果 worktree 删除失败,分支删除也应该失败(Git 的限制)"""
        git_ops = GitOperations(repo_path=git_repo)
        worktree_path = git_repo / ".worktrees" / "test-branch"
        git_ops.create_worktree("test-branch", worktree_path)
        # 手动模拟 worktree 删除失败的情况
        # 我们通过传入一个错误的路径来模拟
        wrong_path = git_repo / "some-other-path"
        result = git_ops.cleanup_branch("test-branch", wrong_path)
        # 由于 worktree 实际上还在,Git 会阻止删除分支
        assert result.branch_deleted is False
        assert len(result.errors) > 0


class TestDetectPotentialConflicts:
    """测试 detect_potential_conflicts() 方法"""

    def test_returns_none_when_no_conflicts(self, git_repo):
        """当没有冲突风险时,应该返回 NONE 风险级别"""
        git_ops = GitOperations(repo_path=git_repo)
        # 创建一个 feature 分支但没有修改
        subprocess.run(
            ["git", "worktree", "add", ".worktrees/feature", "-b", "feature"],
            cwd=git_repo,
            capture_output=True
        )
        result = git_ops.detect_potential_conflicts("feature")
        assert result.risk_level == "NONE"
        assert len(result.files) == 0

    def test_detects_status_conflict_in_task_file(self, git_repo):
        """应该检测到任务文件的状态冲突"""
        # 这个测试会在实现 merge_oracle 时完成
        # 这里先留空,确保测试框架可以运行
        pytest.skip("Will be implemented in Phase 2")
