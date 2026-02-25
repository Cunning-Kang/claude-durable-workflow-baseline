from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

ENV_SETUP_CMD = "ENV_SETUP_CMD"
TEST_CMD = "TEST_CMD"
LINT_CMD = "LINT_CMD"
TYPECHECK_CMD = "TYPECHECK_CMD"
BUILD_CMD = "BUILD_CMD"

OVERRIDE_KEYS = [ENV_SETUP_CMD, TEST_CMD, LINT_CMD, TYPECHECK_CMD, BUILD_CMD]


def extract_commands(init_text: str) -> dict[str, str]:
    commands = {key: "" for key in OVERRIDE_KEYS}

    for raw_line in init_text.splitlines():
        line = raw_line.strip()
        for key in OVERRIDE_KEYS:
            if line.startswith(f"{key}:"):
                commands[key] = line.split(":", 1)[1].strip()
                break
            if line.startswith(f"{key} ="):
                commands[key] = line.split("=", 1)[1].strip()
                break

    return commands


def extract_project_overrides(init_snapshot: str) -> str:
    marker = "## Project Overrides"
    lines = init_snapshot.splitlines()

    in_section = False
    collected: list[str] = []

    for line in lines:
        if not in_section:
            if line.strip() == marker:
                in_section = True
            continue

        if line.startswith("## "):
            break

        collected.append(line)

    if not in_section:
        msg = "Missing required section: ## Project Overrides"
        raise ValueError(msg)

    return "\n".join(collected).strip()


def render_template(template: str, init_snapshot: str) -> str:
    overrides = extract_project_overrides(init_snapshot)
    return template.replace("{{PROJECT_OVERRIDES}}", overrides)


def write_with_backup(target: Path, content: str) -> Path | None:
    backup: Path | None = None

    if target.exists():
        backup = target.with_name(f"{target.name}.bak")
        backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")

    with NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        tmp_path.replace(target)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise

    return backup


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--init-source")
    parser.add_argument("--target")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--default-branch", default="main")

    args = parser.parse_args(argv)

    project_root = Path(args.project_root)
    target = Path(args.target) if args.target else project_root / "CLAUDE.md"
    source = Path(args.init_source) if args.init_source else target

    if not source.exists():
        raise SystemExit("run /init first or pass --init-source")

    try:
        template_text = Path(args.template).read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"failed to read template: {args.template}") from exc

    init_text = source.read_text(encoding="utf-8")

    try:
        overrides = extract_project_overrides(init_text)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    rendered = template_text.replace("{{PROJECT_OVERRIDES}}", overrides)
    backup = write_with_backup(target, rendered)

    commands = extract_commands(overrides)
    filled = sum(1 for value in commands.values() if value)
    empty = sum(1 for value in commands.values() if not value)

    print(
        json.dumps(
            {
                "target": str(target),
                "backup": str(backup) if backup is not None else None,
                "filled": filled,
                "empty": empty,
            },
            ensure_ascii=False,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
