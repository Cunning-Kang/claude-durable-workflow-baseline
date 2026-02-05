"""Tests for execution engine"""

import pytest
from pathlib import Path
from execution_engine import ExecutionEngine, execute_plan, ExecutionResult, run_step, parse_plan_steps, PlanStep, build_execution_report, StepResult, StateTracker
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
Expect: test

### Step 2: Another command
Run: true
Expect: PASS
"""
        result = execute_plan(plan_text=plan_text)
        # Should not fail validation
        assert result.status != "failed" or len(result.errors) == 0


class TestExecutionEngineIntegration:
    """Test ExecutionEngine with plan validation"""

    def test_execute_next_batch_avoids_plan_scan_for_ready_tasks(self):
        plan = ExecutionPlan(tasks=[
            Task(id="TASK-001", title="One", description="", status=TaskStatus.PENDING, dependencies=[]),
            Task(id="TASK-002", title="Two", description="", status=TaskStatus.PENDING, dependencies=["TASK-001"]),
        ])

        class _FailOnIter(list):
            def __iter__(self):
                raise AssertionError("plan.tasks should not be scanned for ready tasks")

        engine = ExecutionEngine(plan, project_root=Path("."))
        engine.plan.tasks = _FailOnIter(engine.plan.tasks)
        stats = engine.execute_next_batch()

        assert stats["tasks_executed"] == 1

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
Expect: hello
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


class TestExpectAssertion:
    """Test Expect assertion logic"""

    def test_expect_keyword_fails_when_output_does_not_match(self):
        """Test that step fails when command output doesn't match Expect statement"""
        plan = """
### Step 1: Test mismatch
Run: echo "actual output"
Expect: Expected different output
"""
        result = execute_plan(plan_text=plan)
        # Should fail because output "actual output" doesn't contain "Expected different output"
        assert result.status == "failed"
        assert len(result.steps) == 1
        assert result.steps[0].status == "failed"
        assert "expectation not met" in result.steps[0].error.lower() or "expected" in result.steps[0].error.lower()

    def test_expect_keyword_passes_when_output_contains_expected_substring(self):
        """Test that step passes when command output contains expected substring"""
        plan = """
### Step 1: Test match
Run: echo "This is the expected output"
Expect: expected
"""
        result = execute_plan(plan_text=plan)
        # Should pass because output contains the expected substring
        assert result.status == "passed"
        assert len(result.steps) == 1
        assert result.steps[0].status == "passed"

    def test_expect_keyword_passes_when_full_output_matches_exactly(self):
        """Test that step passes when command output matches expectation exactly"""
        plan = """
### Step 1: Test exact match
Run: echo "exact match"
Expect: exact match
"""
        result = execute_plan(plan_text=plan)
        # Should pass because output matches expectation exactly (ignoring newlines)
        assert result.status == "passed"
        assert len(result.steps) == 1
        assert result.steps[0].status == "passed"

    def test_expect_keyword_fails_when_output_is_empty_but_expectation_exists(self):
        """Test that step fails when command produces no output but expects something"""
        plan = """
### Step 1: Test empty output
Run: true
Expect: something should appear
"""
        result = execute_plan(plan_text=plan)
        # Should fail because command produced no output but expected something
        assert result.status == "failed"
        assert len(result.steps) == 1
        assert result.steps[0].status == "failed"
        assert "expect assertion failed" in result.steps[0].error.lower() or "expected" in result.steps[0].error.lower()


def test_state_tracker_uses_set_semantics():
    from execution_engine import StateTracker
    s = StateTracker()
    s.mark_completed("TASK-001")
    s.mark_completed("TASK-001")
    assert len(s.completed) == 1
