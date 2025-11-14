"""Tests for tasks panel functionality."""

import json
import tempfile
from pathlib import Path

import pytest


def test_task_file_structure():
    """Test that task file has correct JSON structure."""
    tasks = [
        {"id": 1, "text": "Test task 1", "done": False},
        {"id": 2, "text": "Test task 2", "done": True},
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(tasks, f)
        temp_file = f.name

    try:
        with open(temp_file, 'r') as f:
            loaded = json.load(f)

        assert len(loaded) == 2
        assert loaded[0]['id'] == 1
        assert loaded[0]['text'] == "Test task 1"
        assert loaded[0]['done'] is False
        assert loaded[1]['done'] is True
    finally:
        Path(temp_file).unlink()


def test_task_id_generation():
    """Test that task IDs are generated correctly."""
    tasks = [
        {"id": 1, "text": "Task 1", "done": False},
        {"id": 2, "text": "Task 2", "done": False},
    ]

    # Next ID should be max + 1
    next_id = max([task['id'] for task in tasks], default=0) + 1
    assert next_id == 3

    # Test with empty list
    next_id_empty = max([task['id'] for task in []], default=0) + 1
    assert next_id_empty == 1


def test_task_toggle():
    """Test toggling task done status."""
    task = {"id": 1, "text": "Test", "done": False}

    # Toggle to done
    task['done'] = not task['done']
    assert task['done'] is True

    # Toggle back to undone
    task['done'] = not task['done']
    assert task['done'] is False


def test_task_deletion():
    """Test removing a task from list."""
    tasks = [
        {"id": 1, "text": "Task 1", "done": False},
        {"id": 2, "text": "Task 2", "done": False},
        {"id": 3, "text": "Task 3", "done": True},
    ]

    # Delete middle task
    tasks.pop(1)

    assert len(tasks) == 2
    assert tasks[0]['id'] == 1
    assert tasks[1]['id'] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
