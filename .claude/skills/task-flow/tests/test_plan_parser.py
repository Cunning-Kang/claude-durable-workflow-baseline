"""Tests for plan parser and validation"""

import pytest
from plan_generator import validate_plan_steps


class TestPlanStepRequiresRunAndExpect:
    """Test that plan steps require both Run: and Expect: lines"""

    def test_valid_step_with_run_and_expect(self):
        """Test that a valid step passes validation"""
        plan_text = """
# Plan

### Step 1: Install dependencies
Run: pip install -r requirements.txt
Expect: All packages installed successfully

### Step 2: Run tests
Run: pytest
Expect: All tests pass
"""
        errors = validate_plan_steps(plan_text)
        assert errors == []

    def test_step_missing_run(self):
        """Test that a step without Run: fails validation"""
        plan_text = """
# Plan

### Step 1: Install dependencies
Expect: All packages installed successfully
"""
        errors = validate_plan_steps(plan_text)
        assert len(errors) == 1
        assert "missing 'Run:' line" in errors[0]

    def test_step_missing_expect(self):
        """Test that a step without Expect: fails validation"""
        plan_text = """
# Plan

### Step 1: Install dependencies
Run: pip install -r requirements.txt
"""
        errors = validate_plan_steps(plan_text)
        assert len(errors) == 1
        assert "missing 'Expect:' line" in errors[0]

    def test_step_missing_both_run_and_expect(self):
        """Test that a step missing both Run: and Expect: fails validation"""
        plan_text = """
# Plan

### Step 1: Install dependencies
Some other content here
"""
        errors = validate_plan_steps(plan_text)
        assert len(errors) == 2
        assert any("missing 'Run:' line" in e for e in errors)
        assert any("missing 'Expect:' line" in e for e in errors)

    def test_multiple_steps_partial_validation(self):
        """Test validation across multiple steps with mixed validity"""
        plan_text = """
# Plan

### Step 1: Valid step
Run: command1
Expect: result1

### Step 2: Missing Run
Expect: result2

### Step 3: Missing Expect
Run: command3

### Step 4: Valid step
Run: command4
Expect: result4
"""
        errors = validate_plan_steps(plan_text)
        assert len(errors) == 2
        assert "Step 2" in errors[0] and "missing 'Run:' line" in errors[0]
        assert "Step 3" in errors[1] and "missing 'Expect:' line" in errors[1]

    def test_no_steps_returns_empty_errors(self):
        """Test that plan without steps returns empty list"""
        plan_text = """
# Plan

Just some content without steps
"""
        errors = validate_plan_steps(plan_text)
        assert errors == []

    def test_step_with_chinese_colon(self):
        """Test that steps with Chinese colon are recognized"""
        plan_text = """
# Plan

### Step 1：安装依赖
Run: pip install -r requirements.txt
Expect: 安装成功
"""
        errors = validate_plan_steps(plan_text)
        assert errors == []

    def test_step_with_space_after_number(self):
        """Test that steps with space after step number are recognized"""
        plan_text = """
# Plan

### Step 1 Install dependencies
Run: pip install -r requirements.txt
Expect: All packages installed successfully
"""
        errors = validate_plan_steps(plan_text)
        assert errors == []

    def test_run_and_expect_case_sensitive(self):
        """Test that Run: and Expect: are case-sensitive"""
        plan_text = """
# Plan

### Step 1: Test
run: lowercase command
expect: lowercase expectation
"""
        errors = validate_plan_steps(plan_text)
        assert len(errors) == 2

    def test_run_and_expect_allow_content_after_colon(self):
        """Test that Run: and Expect: allow content after colon"""
        plan_text = """
# Plan

### Step 1: Test
Run: Some command here
Expect: Some expected result here
"""
        errors = validate_plan_steps(plan_text)
        assert errors == []
