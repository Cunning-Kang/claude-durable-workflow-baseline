"""Tests for execution engine"""

import pytest
from execution_engine import ExecutionEngine, execute_plan, ExecutionResult, run_step, parse_plan_steps, PlanStep, build_execution_report, StepResult
from plan_generator import ExecutionPlan, Task, TaskStatus


class TestExecutionFailsOnInvalidPlan:
    """Test that execution fails when plan validation detects errors"""

    def test_missing_expect_returns_failed_status(self):
        """Test that a plan missing Expect: line fails validation"""
        plan_text = """
### Step 1: Run tests
Run: pytest -q
"""
        result = execute_plan(plan_text=plan_text)
        assert result.status == "failed"
        assert len(result.errors) == 1
        assert "Expect" in result.errors[0]

    def test_missing_run_returns_failed_status(self):
        """Test that a plan missing Run: line fails validation"""
        plan_text = """
### Step 1: Check results
Expect: All tests pass
"""
        result = execute_plan(plan_text=plan_text)
        assert result.status == "failed"
        assert len(result.errors) == 1
        assert "Run" in result.errors[0]

    def test_multiple_validation_errors_all_reported(self):
        """Test that all validation errors are reported"""
        plan_text = """
### Step 1: Missing both
Some content here

### Step 2: Missing Run
Expect: Something

### Step 3: Missing Expect
Run: command
"""
        result = execute_plan(plan_text=plan_text)
        assert result.status == "failed"
        # Step 1 has 2 errors (missing Run and Expect), Step 2 has 1, Step 3 has 1 = 4 total
        assert len(result.errors) == 4

    def test_valid_plan_returns_success_result(self):
        """Test that a valid plan can be executed"""
        plan_text = """
### Step 1: Simple command
Run: echo "test"
Expect: test output

### Step 2: Another command
Run: true
Expect: success
"""
        result = execute_plan(plan_text=plan_text)
        # Should not fail validation
        assert result.status != "failed" or len(result.errors) == 0


class TestExecutionEngineIntegration:
    """Test ExecutionEngine with plan validation"""

    def test_engine_rejects_plan_text_with_errors(self):
        """Test that ExecutionEngine can be used with validated plan text"""
        from pathlib import Path
        import tempfile

        plan_text = """
### Step 1: Bad step
Run: command
"""
        result = execute_plan(plan_text=plan_text)

        # Result should indicate validation failure
        assert result.status == "failed"
        assert any("Expect" in e for e in result.errors)

    def test_engine_accepts_valid_plan(self):
        """Test that ExecutionEngine accepts validated plans"""
        plan_text = """
### Step 1: Valid step
Run: echo "hello"
Expect: hello printed
"""
        result = execute_plan(plan_text=plan_text)

        # Should not fail validation
        # (execution might fail for other reasons, but not validation)
        assert result.status != "failed" or not any("Expect" in e or "Run" in e for e in result.errors)


class TestStepRunner:
    """Test step runner functionality"""

    def test_step_runner_marks_failed_on_command_error(self):
        """Test that step runner marks step as failed when command returns non-zero exit code"""
        plan = """
### Step 1: Bad command
Run: false
Expect: PASS
"""
        result = execute_plan(plan_text=plan)
        assert result.status == "failed"
        assert len(result.steps) == 1
        assert result.steps[0].status == "failed"
        assert "exited with code" in result.steps[0].error or "Command" in result.steps[0].error

    def test_step_runner_success_when_command_passes(self):
        """Test that step runner marks step as passed when command succeeds"""
        plan = """
### Step 1: Good command
Run: true
Expect: PASS
"""
        result = execute_plan(plan_text=plan)
        assert result.status == "passed"
        assert len(result.steps) == 1
        assert result.steps[0].status == "passed"

    def test_step_runner_stops_on_first_failure(self):
        """Test that execution stops on first failed step"""
        plan = """
### Step 1: Good command
Run: true
Expect: PASS

### Step 2: Bad command
Run: false
Expect: PASS

### Step 3: Should not run
Run: echo "never executed"
Expect: Should not see this
"""
        result = execute_plan(plan_text=plan)
        assert result.status == "failed"
        # Should have executed first two steps, but not the third
        assert len(result.steps) == 2
        assert result.steps[0].status == "passed"
        assert result.steps[1].status == "failed"


class TestExecutionReport:
    """Test execution report generation"""

    def test_execution_report_contains_steps_and_gate_result(self):
        """Test that build_execution_report includes steps and quality gate information"""
        # Create a mock ExecutionResult with steps and quality gate
        result = ExecutionResult(
            status="passed",
            errors=[],
            steps=[
                StepResult(
                    step_number=1,
                    title="Run tests",
                    status="passed",
                    output="All tests passed"
                ),
                StepResult(
                    step_number=2,
                    title="Build project",
                    status="passed",
                    output="Build successful"
                )
            ],
            quality_gate={
                "status": "passed",
                "output": "All checks passed"
            }
        )

        report = build_execution_report(result)

        # Verify steps are included
        assert "Steps:" in report
        assert "Step 1: Run tests" in report
        assert "Step 2: Build project" in report
        assert "All tests passed" in report

        # Verify quality gate is included
        assert "Quality Gate:" in report
        assert "Status: passed" in report
        assert "All checks passed" in report

        # Verify overall status
        assert "Execution Status: PASSED" in report
