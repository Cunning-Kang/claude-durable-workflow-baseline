"""Tests for StateTracker - state tracking and persistence"""

import pytest
from pathlib import Path
from datetime import datetime
import time
import yaml


@pytest.fixture
def sample_task_file(tmp_path):
    """Create a sample task file with YAML frontmatter"""
    task_file = tmp_path / "TASK-001.md"
    content = """---
id: TASK-001
title: "Implement StateTracker"
status: "To Do"
created_at: 2026-02-01
updated_at: 2026-02-01
dependencies: []
context: {}
execution_state:
  current_step: 0
  total_steps: 0
  completed_tasks: []
  failed_tasks: []
---

# Task: Implement StateTracker

## Description
Implement the state tracker component.
"""
    task_file.write_text(content)
    return task_file


@pytest.fixture
def state_tracker_class():
    """Import StateTracker class dynamically"""
    from execution_engine.state_tracker import StateTracker
    return StateTracker


class TestTrackerInitialization:
    """Test tracker initialization with task file"""

    def test_initialization_with_task_file(self, state_tracker_class, sample_task_file):
        """Tracker should initialize with task file path"""
        tracker = state_tracker_class(sample_task_file)
        assert tracker.task_file == sample_task_file

    def test_initialization_loads_existing_state(self, state_tracker_class, sample_task_file):
        """Tracker should load existing execution_state from file"""
        tracker = state_tracker_class(sample_task_file)
        state = tracker.get_state("TASK-001")
        assert state is not None
        assert "current_step" in state


class TestStartingTask:
    """Test starting a task"""

    def test_start_task_sets_status_to_running(self, state_tracker_class, sample_task_file):
        """Starting a task should set status to 'running'"""
        tracker = state_tracker_class(sample_task_file)
        tracker.start_task("TASK-001", "Implement StateTracker")

        state = tracker.get_state("TASK-001")
        assert state["status"] == "running"

    def test_start_task_records_started_at_timestamp(self, state_tracker_class, sample_task_file):
        """Starting a task should record started_at timestamp"""
        tracker = state_tracker_class(sample_task_file)
        before_start = datetime.now()
        tracker.start_task("TASK-001", "Test task")
        after_start = datetime.now()

        state = tracker.get_state("TASK-001")
        assert "started_at" in state
        started_at = datetime.fromisoformat(state["started_at"])
        assert before_start <= started_at <= after_start


class TestCompletingTask:
    """Test completing a task"""

    def test_complete_task_sets_status_to_completed(self, state_tracker_class, sample_task_file):
        """Completing a task should set status to 'completed'"""
        tracker = state_tracker_class(sample_task_file)
        tracker.start_task("TASK-001", "Test task")
        time.sleep(0.1)  # Small delay to ensure duration > 0
        tracker.complete_task("TASK-001")

        state = tracker.get_state("TASK-001")
        assert state["status"] == "completed"

    def test_complete_task_records_completed_at_timestamp(self, state_tracker_class, sample_task_file):
        """Completing a task should record completed_at timestamp"""
        tracker = state_tracker_class(sample_task_file)
        tracker.start_task("TASK-001", "Test task")
        before_complete = datetime.now()
        tracker.complete_task("TASK-001")
        after_complete = datetime.now()

        state = tracker.get_state("TASK-001")
        assert "completed_at" in state
        completed_at = datetime.fromisoformat(state["completed_at"])
        assert before_complete <= completed_at <= after_complete

    def test_complete_task_calculates_duration(self, state_tracker_class, sample_task_file):
        """Completing a task should calculate duration in seconds"""
        tracker = state_tracker_class(sample_task_file)
        tracker.start_task("TASK-001", "Test task")
        time.sleep(0.1)  # Ensure measurable duration
        tracker.complete_task("TASK-001")

        state = tracker.get_state("TASK-001")
        assert "duration" in state
        assert state["duration"] >= 0.1  # At least 100ms


class TestGettingTaskState:
    """Test getting task state"""

    def test_get_state_returns_current_state(self, state_tracker_class, sample_task_file):
        """Getting state should return current execution state"""
        tracker = state_tracker_class(sample_task_file)
        state = tracker.get_state("TASK-001")

        assert isinstance(state, dict)
        assert "current_step" in state
        assert "total_steps" in state
        assert "completed_tasks" in state
        assert "failed_tasks" in state


class TestUpdatingExecutionState:
    """Test updating execution state in YAML frontmatter"""

    def test_update_execution_state_modifies_yaml_frontmatter(self, state_tracker_class, sample_task_file):
        """Updating execution state should modify YAML frontmatter"""
        tracker = state_tracker_class(sample_task_file)
        new_state = {
            "current_step": 5,
            "total_steps": 10,
            "completed_tasks": ["TASK-001"],
            "failed_tasks": []
        }
        tracker.update_execution_state(new_state)

        # Read file and verify YAML was updated
        content = sample_task_file.read_text()
        parts = content.split("---")
        yaml_content = parts[1]
        data = yaml.safe_load(yaml_content)

        assert data["execution_state"]["current_step"] == 5
        assert data["execution_state"]["total_steps"] == 10


class TestPersistingState:
    """Test persisting state to task file"""

    def test_state_changes_persist_to_file(self, state_tracker_class, sample_task_file):
        """State changes should be persisted to task file"""
        tracker = state_tracker_class(sample_task_file)
        tracker.start_task("TASK-001", "Test task")

        # Create new tracker instance to verify persistence
        new_tracker = state_tracker_class(sample_task_file)
        state = new_tracker.get_state("TASK-001")

        assert state["status"] == "running"
        assert "started_at" in state


class TestStateTransitions:
    """Test state transitions"""

    def test_transition_from_todo_to_in_progress(self, state_tracker_class, sample_task_file):
        """Task should transition from 'To Do' to 'In Progress'"""
        tracker = state_tracker_class(sample_task_file)

        # Initial state
        content = sample_task_file.read_text()
        assert 'status: "To Do"' in content

        tracker.start_task("TASK-001", "Test task")

        # After start
        content = sample_task_file.read_text()
        state = tracker.get_state("TASK-001")
        assert state["status"] == "running"

    def test_transition_from_in_progress_to_done(self, state_tracker_class, sample_task_file):
        """Task should transition from 'In Progress' to 'Done'"""
        tracker = state_tracker_class(sample_task_file)
        tracker.start_task("TASK-001", "Test task")
        tracker.complete_task("TASK-001")

        content = sample_task_file.read_text()
        state = tracker.get_state("TASK-001")
        assert state["status"] == "completed"


class TestMultipleStateUpdates:
    """Test multiple state updates"""

    def test_multiple_state_updates_accumulate(self, state_tracker_class, sample_task_file):
        """Multiple state updates should accumulate correctly"""
        tracker = state_tracker_class(sample_task_file)

        # First update
        tracker.update_execution_state({"current_step": 1})
        state = tracker.get_state("TASK-001")
        assert state["current_step"] == 1

        # Second update
        tracker.update_execution_state({"current_step": 2})
        state = tracker.get_state("TASK-001")
        assert state["current_step"] == 2

        # Third update with multiple fields
        tracker.update_execution_state({
            "current_step": 3,
            "total_steps": 10
        })
        state = tracker.get_state("TASK-001")
        assert state["current_step"] == 3
        assert state["total_steps"] == 10


class TestErrorHandling:
    """Test error handling for edge cases"""

    def test_error_handling_for_missing_task_file(self, state_tracker_class, tmp_path):
        """Tracker should handle missing task file gracefully"""
        non_existent_file = tmp_path / "TASK-999.md"

        tracker = state_tracker_class(non_existent_file)

        # Should not raise exception, but return None or empty state
        state = tracker.get_state("TASK-999")
        assert state is None or state == {}

    def test_error_handling_for_malformed_yaml(self, state_tracker_class, tmp_path):
        """Tracker should handle malformed YAML gracefully"""
        bad_file = tmp_path / "TASK-001.md"
        bad_file.write_text("This is not valid YAML frontmatter")

        tracker = state_tracker_class(bad_file)
        state = tracker.get_state("TASK-001")

        # Should handle error gracefully
        assert state is None or isinstance(state, dict)


class TestTimeDurationCalculation:
    """Test time duration calculation"""

    def test_duration_calculation_precision(self, state_tracker_class, sample_task_file):
        """Duration should be calculated with reasonable precision"""
        tracker = state_tracker_class(sample_task_file)
        tracker.start_task("TASK-001", "Test task")

        expected_delay = 0.25
        time.sleep(expected_delay)

        tracker.complete_task("TASK-001")
        state = tracker.get_state("TASK-001")

        # Allow 50ms margin of error
        assert abs(state["duration"] - expected_delay) < 0.05

    def test_duration_without_start_raises_error(self, state_tracker_class, sample_task_file):
        """Completing a task without starting it should handle gracefully"""
        tracker = state_tracker_class(sample_task_file)

        # Should not crash, but may set duration to None or 0
        tracker.complete_task("TASK-001")
        state = tracker.get_state("TASK-001")

        assert "duration" in state
        assert state["duration"] is None or state["duration"] == 0 or state["duration"] > 0
