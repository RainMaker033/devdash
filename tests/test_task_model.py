"""Tests for enhanced task model."""

import pytest
from datetime import datetime, date, timedelta

from devdash.task_model import (
    Task,
    Priority,
    migrate_legacy_task,
    migrate_task_list,
    validate_task_data,
    sort_tasks,
    filter_tasks,
)


class TestTaskCreation:
    """Test task creation and validation."""

    def test_minimal_task(self):
        """Test creating a task with minimal required fields."""
        task = Task(id=1, text="Test task")
        assert task.id == 1
        assert task.text == "Test task"
        assert task.done is False
        assert task.priority is None
        assert task.due_date is None
        assert task.categories == []
        assert task.created_at is not None

    def test_full_task(self):
        """Test creating a task with all fields."""
        task = Task(
            id=1,
            text="Complete task",
            done=True,
            priority="high",
            due_date="2025-12-31",
            categories=["work", "urgent"],
            created_at="2025-01-01T10:00:00"
        )
        assert task.id == 1
        assert task.text == "Complete task"
        assert task.done is True
        assert task.priority == "high"
        assert task.due_date == "2025-12-31"
        assert task.categories == ["work", "urgent"]
        assert task.created_at == "2025-01-01T10:00:00"

    def test_invalid_priority(self):
        """Test that invalid priority raises error."""
        with pytest.raises(ValueError, match="Invalid priority"):
            Task(id=1, text="Test", priority="invalid")

    def test_invalid_due_date(self):
        """Test that invalid due date raises error."""
        with pytest.raises(ValueError, match="Invalid due_date format"):
            Task(id=1, text="Test", due_date="not-a-date")


class TestTaskMethods:
    """Test task instance methods."""

    def test_is_overdue(self):
        """Test overdue detection."""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        task = Task(id=1, text="Overdue", due_date=yesterday)
        assert task.is_overdue() is True

    def test_not_overdue_future(self):
        """Test that future tasks are not overdue."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        task = Task(id=1, text="Future", due_date=tomorrow)
        assert task.is_overdue() is False

    def test_not_overdue_completed(self):
        """Test that completed tasks are never overdue."""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        task = Task(id=1, text="Done", done=True, due_date=yesterday)
        assert task.is_overdue() is False

    def test_is_due_soon(self):
        """Test due soon detection."""
        soon = (date.today() + timedelta(days=2)).isoformat()
        task = Task(id=1, text="Soon", due_date=soon)
        assert task.is_due_soon(days=3) is True

    def test_not_due_soon(self):
        """Test that far future tasks are not due soon."""
        far = (date.today() + timedelta(days=10)).isoformat()
        task = Task(id=1, text="Far", due_date=far)
        assert task.is_due_soon(days=3) is False

    def test_has_category(self):
        """Test category checking."""
        task = Task(id=1, text="Test", categories=["work", "urgent"])
        assert task.has_category("work") is True
        assert task.has_category("WORK") is True  # Case insensitive
        assert task.has_category("personal") is False

    def test_matches_priority(self):
        """Test priority matching."""
        task = Task(id=1, text="Test", priority="high")
        assert task.matches_priority("high") is True
        assert task.matches_priority("medium") is False
        assert task.matches_priority(None) is False

    def test_get_priority_emoji(self):
        """Test priority emoji generation."""
        assert Task(id=1, text="Test", priority="high").get_priority_emoji() == "🔴"
        assert Task(id=1, text="Test", priority="medium").get_priority_emoji() == "🟡"
        assert Task(id=1, text="Test", priority="low").get_priority_emoji() == "🟢"
        assert Task(id=1, text="Test").get_priority_emoji() == ""

    def test_get_due_date_indicator(self):
        """Test due date indicator generation."""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        soon = (date.today() + timedelta(days=2)).isoformat()
        far = (date.today() + timedelta(days=10)).isoformat()

        assert Task(id=1, text="Test", due_date=yesterday).get_due_date_indicator() == "⚠️"
        assert Task(id=1, text="Test", due_date=soon).get_due_date_indicator() == "📅"
        assert Task(id=1, text="Test", due_date=far).get_due_date_indicator() == "📆"
        assert Task(id=1, text="Test").get_due_date_indicator() == ""


class TestTaskSerialization:
    """Test task serialization and deserialization."""

    def test_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(
            id=1,
            text="Test",
            priority="high",
            categories=["work"]
        )
        data = task.to_dict()
        assert data['id'] == 1
        assert data['text'] == "Test"
        assert data['priority'] == "high"
        assert data['categories'] == ["work"]

    def test_from_dict_full(self):
        """Test creating task from full dictionary."""
        data = {
            "id": 1,
            "text": "Test",
            "done": True,
            "priority": "medium",
            "due_date": "2025-12-31",
            "categories": ["work"],
            "created_at": "2025-01-01T10:00:00"
        }
        task = Task.from_dict(data)
        assert task.id == 1
        assert task.text == "Test"
        assert task.done is True
        assert task.priority == "medium"

    def test_from_dict_legacy(self):
        """Test creating task from legacy format."""
        data = {"id": 1, "text": "Old task", "done": False}
        task = Task.from_dict(data)
        assert task.id == 1
        assert task.text == "Old task"
        assert task.priority is None
        assert task.categories == []


class TestMigration:
    """Test legacy task migration."""

    def test_migrate_legacy_task(self):
        """Test migrating a single legacy task."""
        old = {"id": 1, "text": "Old", "done": False}
        new = migrate_legacy_task(old)
        assert new['id'] == 1
        assert new['text'] == "Old"
        assert new['priority'] is None
        assert new['categories'] == []
        assert 'created_at' in new

    def test_migrate_task_list(self):
        """Test migrating a list of tasks."""
        old_tasks = [
            {"id": 1, "text": "Task 1", "done": False},
            {"id": 2, "text": "Task 2", "done": True},
        ]
        new_tasks = migrate_task_list(old_tasks)
        assert len(new_tasks) == 2
        assert all('priority' in task for task in new_tasks)
        assert all('categories' in task for task in new_tasks)

    def test_validate_task_data(self):
        """Test task data validation."""
        valid = {"id": 1, "text": "Test", "done": False}
        invalid = {"text": "Missing ID"}
        assert validate_task_data(valid) is True
        assert validate_task_data(invalid) is False


class TestSorting:
    """Test task sorting."""

    def test_sort_by_priority(self):
        """Test sorting tasks by priority."""
        tasks = [
            Task(id=1, text="Low", priority="low"),
            Task(id=2, text="High", priority="high"),
            Task(id=3, text="Medium", priority="medium"),
            Task(id=4, text="None"),
        ]
        sorted_tasks = sort_tasks(tasks, sort_by="priority")
        assert sorted_tasks[0].priority == "high"
        assert sorted_tasks[1].priority == "medium"
        assert sorted_tasks[2].priority == "low"
        assert sorted_tasks[3].priority is None

    def test_sort_by_due_date(self):
        """Test sorting tasks by due date."""
        tasks = [
            Task(id=1, text="Far", due_date="2025-12-31"),
            Task(id=2, text="Soon", due_date="2025-01-15"),
            Task(id=3, text="None"),
        ]
        sorted_tasks = sort_tasks(tasks, sort_by="due_date")
        assert sorted_tasks[0].due_date == "2025-01-15"
        assert sorted_tasks[1].due_date == "2025-12-31"
        assert sorted_tasks[2].due_date is None

    def test_sort_by_text(self):
        """Test sorting tasks alphabetically."""
        tasks = [
            Task(id=1, text="Zebra"),
            Task(id=2, text="Apple"),
            Task(id=3, text="Banana"),
        ]
        sorted_tasks = sort_tasks(tasks, sort_by="text")
        assert sorted_tasks[0].text == "Apple"
        assert sorted_tasks[1].text == "Banana"
        assert sorted_tasks[2].text == "Zebra"


class TestFiltering:
    """Test task filtering."""

    def test_filter_by_priority(self):
        """Test filtering tasks by priority."""
        tasks = [
            Task(id=1, text="High", priority="high"),
            Task(id=2, text="Low", priority="low"),
            Task(id=3, text="None"),
        ]
        high_tasks = filter_tasks(tasks, priority="high")
        assert len(high_tasks) == 1
        assert high_tasks[0].priority == "high"

    def test_filter_by_category(self):
        """Test filtering tasks by category."""
        tasks = [
            Task(id=1, text="Work", categories=["work"]),
            Task(id=2, text="Personal", categories=["personal"]),
            Task(id=3, text="Both", categories=["work", "personal"]),
        ]
        work_tasks = filter_tasks(tasks, category="work")
        assert len(work_tasks) == 2

    def test_filter_hide_done(self):
        """Test filtering out completed tasks."""
        tasks = [
            Task(id=1, text="Done", done=True),
            Task(id=2, text="Not done", done=False),
        ]
        active_tasks = filter_tasks(tasks, show_done=False)
        assert len(active_tasks) == 1
        assert active_tasks[0].done is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
