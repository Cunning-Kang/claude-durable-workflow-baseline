"""Execution engine for task-flow"""

import json
import re
import shlex
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

from plan_generator import ExecutionPlan, Task, TaskStatus, ExecutionStats, validate_plan_steps


@dataclass
class StateTracker:
    """Tracks execution state for tasks"""
    completed: set = field(default_factory=set)
    failed: set = field(default_factory=set)
    in_progress: set = field(default_factory=set)
    skipped: set = field(default_factory=set)

    def mark_completed(self, task_id: str):
        self.completed.add(task_id)

    def mark_failed(self, task_id: str):
        self.failed.add(task_id)

    def mark_in_progress(self, task_id: str):
        self.in_progress.add(task_id)

    def mark_skipped(self, task_id: str):
        self.skipped.add(task_id)

    def is_completed(self, task_id: str) -> bool:
        return task_id in self.completed

    def is_failed(self, task_id: str) -> bool:
        return task_id in self.failed

    def is_in_progress(self, task_id: str) -> bool:
        return task_id in self.in_progress

    def is_skipped(self, task_id: str) -> bool:
        return task_id in self.skipped

    def can_execute(self, task: Task) -> bool:
        """Check if task can be executed based on its dependencies"""
        for dep_id in task.dependencies:
            if not self.is_completed(dep_id):
                return False
        return True


@dataclass
class ExecutionController:
    """Controls execution behavior"""
    batch_size: int = 1
    auto_continue: bool = False
    checkpoint_interval: int = 3


class ExecutionEngine:
    """
    Executes tasks from an ExecutionPlan in dependency order.

    The engine supports:
    - Batch execution with configurable batch size
    - Dependency resolution
    - Checkpoint tracking
    - Optional callable execution (defaults to no-op)
    - Step callback for task status synchronization

    Note: This class operates on structured ExecutionPlan/Task objects.
    For markdown plan text execution, use execute_plan(plan_text, ...) below.
    """

    def __init__(
        self,
        plan: ExecutionPlan,
        project_root: Path,
        task_callable: Optional[Callable[[Task], bool]] = None,
        step_callback: Optional[Callable[[int], None]] = None,
    ):
        """
        Initialize the execution engine.

        Args:
            plan: The execution plan to run
            project_root: Root directory for the project
            task_callable: Optional function to execute each task.
                          If None, tasks are marked as completed without execution.
            step_callback: Optional callback function called after each successful step execution,
                          receives step number as argument. Can be used to update task status.
        """
        self.plan = plan
        self.project_root = project_root
        self.task_callable = task_callable
        self.step_callback = step_callback
        self.controller = ExecutionController()
        self.state = StateTracker()

        # Create task_id index dictionary for O(1) lookup
        self._task_id_index = {task.id: task for task in self.plan.tasks}

        # Load previous execution state if exists
        self._load_state()

    def _load_state(self):
        """Load execution state from task file if present"""
        # Try to load from execution_state in the task file
        # This is called from cli.py with the task file parent
        pass

    def _get_ready_tasks(self) -> List[Task]:
        """Get tasks that are ready to execute (dependencies satisfied)"""
        ready_tasks = []
        for task in self.plan.tasks:
            if (
                task.status == TaskStatus.PENDING
                and not self.state.is_completed(task.id)
                and not self.state.is_failed(task.id)
                and not self.state.is_in_progress(task.id)
                and self.state.can_execute(task)
            ):
                ready_tasks.append(task)
        return ready_tasks

    def execute_next_batch(self) -> Dict[str, Any]:
        """
        Execute the next batch of ready tasks.

        Returns:
            Dictionary with execution statistics:
            - tasks_executed: Number of tasks executed in this batch
            - total_completed: Total number of completed tasks
            - errors: List of error messages if any
            - skipped: List of skipped task IDs
        """
        ready_tasks = self._get_ready_tasks()

        # Limit by batch size
        tasks_to_execute = ready_tasks[: self.controller.batch_size]

        tasks_executed = 0
        errors = []

        for task in tasks_to_execute:
            self.state.mark_in_progress(task.id)

            # Execute the task if callable is provided
            success = True
            if self.task_callable:
                try:
                    success = self.task_callable(task)
                except Exception as e:
                    success = False
                    errors.append(f"Task {task.id} failed: {str(e)}")

            if success:
                self.state.mark_completed(task.id)
                self.state.in_progress.discard(task.id)
                task.status = TaskStatus.COMPLETED
                tasks_executed += 1
            else:
                self.state.mark_failed(task.id)
                self.state.in_progress.discard(task.id)
                task.status = TaskStatus.FAILED

        return {
            "tasks_executed": tasks_executed,
            "total_completed": len(self.state.completed),
            "errors": errors,
            "skipped": list(self.state.skipped),  # Convert set to list for backward compatibility
        }

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID"""
        return self._task_id_index.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus):
        """Update the status of a task"""
        task = self.get_task_by_id(task_id)
        if task:
            task.status = status


@dataclass
class PlanStep:
    """A single step parsed from a markdown plan"""
    number: int
    title: str
    run: str
    expect: str


@dataclass
class StepResult:
    """Result of executing a single step"""
    step_number: int
    title: str
    status: str  # "passed", "failed"
    output: str = ""
    error: str = ""


@dataclass
class ExecutionResult:
    """Result of plan execution"""
    status: str  # "passed", "failed"
    errors: List[str] = field(default_factory=list)
    steps: List[StepResult] = field(default_factory=list)
    quality_gate: Optional[Dict[str, Any]] = None


def parse_plan_steps(plan_text: str) -> List[PlanStep]:
    """Parse markdown plan text into structured PlanStep objects.

    Args:
        plan_text: Markdown plan text with ### Step N: Title sections

    Returns:
        List of PlanStep objects
    """
    steps: List[PlanStep] = []

    # Find all ### Step sections
    step_pattern = r'### Step\s+(\d+[:：\s]*)\s*(.+?)(?:\n|$)'
    step_matches = list(re.finditer(step_pattern, plan_text))

    for i, match in enumerate(step_matches):
        step_number = int(re.sub(r'[:：\s]', '', match.group(1)))
        step_title = match.group(2).strip()

        # Find the end of this step (next step or end of text)
        start_pos = match.start()
        if i + 1 < len(step_matches):
            end_pos = step_matches[i + 1].start()
        else:
            end_pos = len(plan_text)

        step_content = plan_text[start_pos:end_pos]

        # Extract Run: line
        run_match = re.search(r'^Run:\s*(.+)$', step_content, re.MULTILINE)
        run_command = run_match.group(1).strip() if run_match else ""

        # Extract Expect: line
        expect_match = re.search(r'^Expect:\s*(.+)$', step_content, re.MULTILINE)
        expect_statement = expect_match.group(1).strip() if expect_match else ""

        steps.append(PlanStep(
            number=step_number,
            title=step_title,
            run=run_command,
            expect=expect_statement
        ))

    return steps


def run_step(step: PlanStep, step_callback: Optional[Callable[[int], None]] = None) -> StepResult:
    """Execute a single step's Run command and validate against Expect statement.

    Args:
        step: The PlanStep to execute
        step_callback: Optional callback function called after step execution,
                      receives step number as argument

    Returns:
        StepResult with execution status
    """
    try:
        run_args = shlex.split(step.run)
        completed = subprocess.run(
            run_args,
            capture_output=True,
            text=True,
            timeout=60  # Default timeout
        )
        if completed.returncode != 0:
            return StepResult(
                step_number=step.number,
                title=step.title,
                status="failed",
                output=completed.stdout,
                error=completed.stderr or f"Command exited with code {completed.returncode}"
            )

        # Check if the output matches the expected result
        output = completed.stdout.strip()
        expected = step.expect.strip()

        # Handle PASS/FAIL explicitly, otherwise treat Expect as keyword
        if expected:
            normalized = expected.lower()
            if normalized == "pass":
                pass
            elif normalized == "fail":
                return StepResult(
                    step_number=step.number,
                    title=step.title,
                    status="failed",
                    output=output,
                    error="Expect assertion requested FAIL"
                )
            else:
                # Check if expected string is contained in the output (case-insensitive)
                if normalized not in output.lower():
                    return StepResult(
                        step_number=step.number,
                        title=step.title,
                        status="failed",
                        output=output,
                        error=f"Expect assertion failed: Expected '{expected}' not found in output '{output}'."
                    )

        # Call step callback after successful execution and validation
        if step_callback:
            step_callback(step.number)
        return StepResult(
            step_number=step.number,
            title=step.title,
            status="passed",
            output=output
        )
    except ValueError as e:
        return StepResult(
            step_number=step.number,
            title=step.title,
            status="failed",
            error=f"Invalid command: {e}"
        )
    except subprocess.TimeoutExpired:
        return StepResult(
            step_number=step.number,
            title=step.title,
            status="failed",
            error="Command timed out after 60 seconds"
        )
    except Exception as e:
        return StepResult(
            step_number=step.number,
            title=step.title,
            status="failed",
            error=str(e)
        )


def run_quality_gate(cmd: str, project_root: Path) -> Dict[str, Any]:
    """
    Run quality gate command and return result.

    Args:
        cmd: The quality gate command to run (e.g., "pytest", "npm test")
        project_root: Root directory for running the command

    Returns:
        Dict with 'status' ("passed" or "failed") and optional 'error'/'output'
    """
    if not cmd or cmd.startswith("#"):
        return {"status": "passed", "note": "No quality gate configured"}

    try:
        gate_args = shlex.split(cmd)
        result = subprocess.run(
            gate_args,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes for CI commands
            cwd=str(project_root),
        )
        if result.returncode != 0:
            return {
                "status": "failed",
                "output": result.stdout,
                "error": result.stderr or f"Quality gate exited with code {result.returncode}"
            }
        return {
            "status": "passed",
            "output": result.stdout
        }
    except ValueError as e:
        return {
            "status": "failed",
            "error": f"Invalid command: {e}"
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "failed",
            "error": "Quality gate timed out after 300 seconds"
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


def execute_plan(plan_text: str, quality_gate_cmd: str = "", project_root: Optional[Path] = None,
                step_callback: Optional[Callable[[int], None]] = None) -> ExecutionResult:
    """
    Execute a markdown plan text, with validation before execution.

    Args:
        plan_text: Markdown plan text to validate and execute
        quality_gate_cmd: Optional quality gate command to run after steps
        project_root: Root directory for running quality gate command
        step_callback: Optional callback function called after each successful step execution,
                      receives step number as argument

    Returns:
        ExecutionResult with status and any errors

    Assumption: plan_text is trusted input (generated by the workflow) and
    may contain shell commands. Use with caution for untrusted content.
    """
    # Validate plan steps first
    errors = validate_plan_steps(plan_text)
    if errors:
        return ExecutionResult(status="failed", errors=errors)

    # Parse steps
    steps = parse_plan_steps(plan_text)

    # Execute each step
    step_results: List[StepResult] = []
    for step in steps:
        result = run_step(step, step_callback=step_callback)
        step_results.append(result)

        # Fail fast on first error
        if result.status == "failed":
            return ExecutionResult(
                status="failed",
                errors=[f"Step {step.number} ({step.title}) failed: {result.error}"],
                steps=step_results
            )

    # Run quality gate after all steps pass
    quality_gate_result = None
    if quality_gate_cmd and project_root:
        quality_gate_result = run_quality_gate(quality_gate_cmd, project_root)
        if quality_gate_result["status"] == "failed":
            return ExecutionResult(
                status="failed",
                errors=[f"Quality gate failed: {quality_gate_result.get('error', 'Unknown error')}"],
                steps=step_results,
                quality_gate=quality_gate_result
            )

    return ExecutionResult(
        status="passed",
        errors=[],
        steps=step_results,
        quality_gate=quality_gate_result
    )


def build_execution_report(result: ExecutionResult) -> str:
    """
    Build a human-readable execution report.

    Args:
        result: The ExecutionResult to report on

    Returns:
        Formatted report string including steps and quality gate results
    """
    lines = []

    # Header
    lines.append(f"Execution Status: {result.status.upper()}")
    lines.append("")

    # Steps section
    if result.steps:
        lines.append("Steps:")
        for step in result.steps:
            status_label = "PASS" if step.status == "passed" else "FAIL"
            lines.append(f"  [{status_label}] Step {step.step_number}: {step.title}")
            if step.output:
                lines.append(f"    Output: {step.output[:100]}{'...' if len(step.output) > 100 else ''}")
            if step.error:
                lines.append(f"    Error: {step.error[:100]}{'...' if len(step.error) > 100 else ''}")
        lines.append("")

    # Quality gate section
    if result.quality_gate is not None:
        lines.append("Quality Gate:")
        gate_status = result.quality_gate.get("status", "unknown")
        status_label = "PASS" if gate_status == "passed" else "FAIL"
        lines.append(f"  [{status_label}] Status: {gate_status}")
        if "output" in result.quality_gate:
            lines.append(f"  Output: {result.quality_gate['output'][:100]}{'...' if len(result.quality_gate['output']) > 100 else ''}")
        if "error" in result.quality_gate:
            lines.append(f"  Error: {result.quality_gate['error'][:100]}{'...' if len(result.quality_gate['error']) > 100 else ''}")
        if "note" in result.quality_gate:
            lines.append(f"  Note: {result.quality_gate['note']}")
    else:
        lines.append("Quality Gate: Not run")

    # Errors section
    if result.errors:
        lines.append("")
        lines.append("Errors:")
        for error in result.errors:
            lines.append(f"  - {error}")

    return "\n".join(lines)
