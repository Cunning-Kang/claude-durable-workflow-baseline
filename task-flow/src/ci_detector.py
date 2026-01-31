"""CI Command Detector - 自动检测项目的 CI 命令"""

from pathlib import Path
import yaml


def detect_ci_command(project_root: Path) -> str:
    """
    自动检测项目的 CI 命令

    优先级顺序：
    1. .wt-workflow 配置 → wt ci
    2. scripts/ci-local.sh → ./scripts/ci-local.sh
    3. mise.toml 的 ci 任务 → mise run ci
    4. package.json 的 test 脚本 → npm test
    5. 默认占位符

    Args:
        project_root: 项目根目录

    Returns:
        检测到的 CI 命令字符串
    """
    # 1. 检测 .wt-workflow 配置
    wt_workflow_file = project_root / ".wt-workflow"
    if wt_workflow_file.exists():
        try:
            with open(wt_workflow_file) as f:
                config = yaml.safe_load(f)
                if config and "ci" in config and "command" in config["ci"]:
                    return config["ci"]["command"]
                elif config and "ci" in config:
                    # 如果只有 ci 但没有 command 字段，尝试其他格式
                    ci_config = config["ci"]
                    if isinstance(ci_config, str):
                        return ci_config
        except Exception:
            pass

    # 2. 检测 scripts/ci-local.sh
    ci_local_script = project_root / "scripts" / "ci-local.sh"
    if ci_local_script.exists() and ci_local_script.is_file():
        return "./scripts/ci-local.sh"

    # 3. 检测 mise.toml 的 ci 任务
    mise_file = project_root / "mise.toml"
    if mise_file.exists():
        try:
            # mise.toml 是 TOML 格式，尝试简单解析
            with open(mise_file) as f:
                content = f.read()
                # 简单检查是否有 [tasks.ci] 或 [tasks.ci.*]
                if "[tasks.ci]" in content or "[tasks.ci." in content:
                    return "mise run ci"
        except Exception:
            pass

    # 4. 检测 package.json 的 test 脚本
    package_json = project_root / "package.json"
    if package_json.exists():
        try:
            import json
            with open(package_json) as f:
                config = json.load(f)
                if config and "scripts" in config and "test" in config["scripts"]:
                    return "npm test"
        except Exception:
            pass

    # 5. 默认占位符
    return "# 请配置 CI 命令"
