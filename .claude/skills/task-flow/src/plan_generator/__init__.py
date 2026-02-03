"""Types for execution plan"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """A task in the execution plan"""
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """Execution plan containing tasks"""
    tasks: List[Task]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionStats:
    """Statistics from batch execution"""
    tasks_executed: int
    total_completed: int
    errors: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def validate_plan_steps(plan_text: str) -> List[str]:
    """Validate that each Step section contains both Run: and Expect: lines.

    Args:
        plan_text: Markdown plan text to validate

    Returns:
        List of error messages (empty if validation passes)
    """
    errors: List[str] = []

    # Find all ### Step sections
    step_pattern = r'### Step\s+\d+[:：\s]'
    step_matches = list(re.finditer(step_pattern, plan_text))

    if not step_matches:
        return errors  # No steps found, nothing to validate

    # Extract each step section
    for i, match in enumerate(step_matches):
        start_pos = match.start()
        # Find the end of this step (next step or end of text)
        if i + 1 < len(step_matches):
            end_pos = step_matches[i + 1].start()
        else:
            end_pos = len(plan_text)

        step_content = plan_text[start_pos:end_pos]
        step_header = match.group(0).strip()

        # Check for Run: line
        has_run = bool(re.search(r'^Run:\s*', step_content, re.MULTILINE))

        # Check for Expect: line
        has_expect = bool(re.search(r'^Expect:\s*', step_content, re.MULTILINE))

        if not has_run:
            errors.append(f"{step_header} missing 'Run:' line")

        if not has_expect:
            errors.append(f"{step_header} missing 'Expect:' line")

    return errors
