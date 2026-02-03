"""CI command detection for task-flow"""

from pathlib import Path
import yaml


def detect_ci_command(project_root: Path) -> str:
    """
    Detect CI command from project configuration.

    Priority order:
    1. .wt-workflow (ci.command or ci as string)
    2. scripts/ci-local.sh
    3. mise.toml ([tasks.ci])
    4. package.json (scripts.test)

    Returns:
        CI command string or placeholder if not found
    """
    root = Path(project_root)

    # 1. Check .wt-workflow
    wt_workflow = root / ".wt-workflow"
    if wt_workflow.exists():
        try:
            content = wt_workflow.read_text()
            data = yaml.safe_load(content)
            if data and "ci" in data:
                ci_config = data["ci"]
                if isinstance(ci_config, dict):
                    return ci_config.get("command", "# 请配置 CI 命令")
                elif isinstance(ci_config, str):
                    return ci_config
        except (yaml.YAMLError, Exception):
            # Malformed YAML, fall through to next check
            pass

    # 2. Check scripts/ci-local.sh
    ci_script = root / "scripts" / "ci-local.sh"
    if ci_script.exists():
        return "./scripts/ci-local.sh"

    # 3. Check mise.toml for ci task (TOML format)
    mise_file = root / "mise.toml"
    if mise_file.exists():
        try:
            content = mise_file.read_text()
            # Simple text search for [tasks.ci] section
            if "[tasks.ci]" in content or '["tasks".' in content:
                return "mise run ci"
        except Exception:
            pass

    # 4. Check package.json for test script
    package_json = root / "package.json"
    if package_json.exists():
        try:
            import json
            content = package_json.read_text()
            data = json.loads(content)
            if data and "scripts" in data and "test" in data["scripts"]:
                return "npm test"
        except (json.JSONDecodeError, Exception):
            pass

    # Default placeholder
    return "# 请配置 CI 命令"


def resolve_quality_gate_command(project_root: Path, task_frontmatter: dict) -> str:
    """
    Resolve quality gate command from task frontmatter or fallback to CI detection.

    Priority order:
    1. task_frontmatter.quality_gate (if present and not None/empty)
    2. Default CI detection

    Args:
        project_root: Project root directory
        task_frontmatter: Frontmatter dictionary from task file

    Returns:
        Quality gate command string
    """
    task_frontmatter = task_frontmatter or {}
    # Check if quality_gate is explicitly defined in task frontmatter
    if "quality_gate" in task_frontmatter and task_frontmatter["quality_gate"] is not None and task_frontmatter["quality_gate"] != "":
        return task_frontmatter["quality_gate"]

    # Fallback to default CI detection
    return detect_ci_command(project_root)
