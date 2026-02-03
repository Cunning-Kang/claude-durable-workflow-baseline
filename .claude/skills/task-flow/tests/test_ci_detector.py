"""Tests for CI command detection"""

import pytest
from pathlib import Path
import tempfile
from ci_detector import detect_ci_command
from execution_engine import run_quality_gate


class TestQualityGate:
    """测试质量门执行器"""

    def test_quality_gate_passes_on_success(self, tmp_path):
        """质量门在命令成功时返回 passed"""
        result = run_quality_gate("true", tmp_path)
        assert result["status"] == "passed"

    def test_quality_gate_fails_on_command_error(self, tmp_path):
        """质量门在命令失败时返回 failed"""
        result = run_quality_gate("false", tmp_path)
        assert result["status"] == "failed"

    def test_quality_gate_passes_on_no_command(self, tmp_path):
        """没有配置质量门命令时返回 passed"""
        result = run_quality_gate("", tmp_path)
        assert result["status"] == "passed"
        assert "note" in result


class TestCIDetector:
    """测试 CI 命令检测器"""

    def test_detect_wt_workflow_command(self, tmp_path):
        """检测 wt-workflow 的 CI 命令"""
        # 创建 .wt-workflow 配置
        wt_workflow = tmp_path / ".wt-workflow"
        wt_workflow.write_text("""version: 1
ci:
  command: wt ci
""")

        ci_command = detect_ci_command(tmp_path)
        assert ci_command == "wt ci"

    def test_detect_ci_local_script(self, tmp_path):
        """检测 scripts/ci-local.sh"""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        ci_script = scripts_dir / "ci-local.sh"
        ci_script.write_text("#!/bin/bash\nnpm test\n")

        ci_command = detect_ci_command(tmp_path)
        assert ci_command == "./scripts/ci-local.sh"

    def test_detect_mise_task(self, tmp_path):
        """检测 mise.toml 中的 ci 任务"""
        mise_file = tmp_path / "mise.toml"
        mise_file.write_text("""[tasks.ci]
run = "pytest"
""")

        ci_command = detect_ci_command(tmp_path)
        assert ci_command == "mise run ci"

    def test_detect_package_json(self, tmp_path):
        """检测 package.json 中的 test 脚本"""
        package_json = tmp_path / "package.json"
        package_json.write_text('{"scripts": {"test": "jest"}}')

        ci_command = detect_ci_command(tmp_path)
        assert ci_command == "npm test"

    def test_no_ci_returns_placeholder(self, tmp_path):
        """没有 CI 配置时返回占位符"""
        # 空目录，没有任何 CI 配置
        ci_command = detect_ci_command(tmp_path)
        assert ci_command == "# 请配置 CI 命令"

    def test_priority_order(self, tmp_path):
        """测试检测优先级：wt-workflow > ci-local.sh > mise > package.json"""
        # 创建多个配置，应该选择优先级最高的 wt-workflow
        (tmp_path / ".wt-workflow").write_text("version: 1\nci:\n  command: wt ci")
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "ci-local.sh").write_text("#!/bin/bash\nnpm test")
        (tmp_path / "mise.toml").write_text('[tasks.ci]\nrun = "pytest"')
        (tmp_path / "package.json").write_text('{"scripts": {"test": "jest"}}')

        ci_command = detect_ci_command(tmp_path)
        # 应该选择 wt-workflow（优先级最高）
        assert ci_command == "wt ci"

    def test_wt_workflow_string_ci(self, tmp_path):
        """测试 wt-workflow 中 ci 为字符串的情况"""
        wt_workflow = tmp_path / ".wt-workflow"
        wt_workflow.write_text("""version: 1
ci: "wt ci"
""")

        ci_command = detect_ci_command(tmp_path)
        assert ci_command == "wt ci"

    def test_malformed_wt_workflow_ignored(self, tmp_path):
        """格式错误的 wt-workflow 应该被忽略，检测下一个"""
        wt_workflow = tmp_path / ".wt-workflow"
        wt_workflow.write_text("this is not valid yaml{")

        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "ci-local.sh").write_text("#!/bin/bash\nnpm test")

        ci_command = detect_ci_command(tmp_path)
        # 应该fallback到 ci-local.sh
        assert ci_command == "./scripts/ci-local.sh"
