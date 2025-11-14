"""
Task data model with enhanced features.

Supports priorities, due dates, categories, and backward compatibility
with the original simple task format.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum


class Priority(Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Task:
    """Enhanced task with priority, due date, and categories."""

    id: int
    text: str
    done: bool = False
    priority: Optional[str] = None  # "high", "medium", "low", or None
    due_date: Optional[str] = None  # ISO format: "YYYY-MM-DD"
    categories: List[str] = field(default_factory=list)
    created_at: Optional[str] = None  # ISO datetime

    def __post_init__(self):
        """Validate and normalize fields after initialization."""
        # Validate priority
        if self.priority is not None:
            if self.priority not in ["high", "medium", "low"]:
                raise ValueError(f"Invalid priority: {self.priority}")

        # Validate due_date format if present
        if self.due_date is not None:
            try:
                datetime.fromisoformat(self.due_date)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid due_date format: {self.due_date}")

        # Ensure categories is a list
        if not isinstance(self.categories, list):
            self.categories = []

        # Set created_at if not present
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary, handling legacy format."""
        return cls(
            id=data.get('id', 0),
            text=data.get('text', ''),
            done=data.get('done', False),
            priority=data.get('priority'),
            due_date=data.get('due_date'),
            categories=data.get('categories', []),
            created_at=data.get('created_at')
        )

    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if self.due_date is None or self.done:
            return False
        try:
            due = datetime.fromisoformat(self.due_date).date()
            return due < date.today()
        except (ValueError, TypeError):
            return False

    def is_due_soon(self, days: int = 3) -> bool:
        """Check if task is due within specified days."""
        if self.due_date is None or self.done:
            return False
        try:
            due = datetime.fromisoformat(self.due_date).date()
            today = date.today()
            if due < today:
                return False  # Overdue, not "due soon"
            delta = (due - today).days
            return delta <= days
        except (ValueError, TypeError):
            return False

    def has_category(self, category: str) -> bool:
        """Check if task has a specific category."""
        return category.lower() in [c.lower() for c in self.categories]

    def matches_priority(self, priority: Optional[str]) -> bool:
        """Check if task matches given priority (None matches no-priority tasks)."""
        return self.priority == priority

    def get_priority_emoji(self) -> str:
        """Get emoji representation of priority."""
        if self.priority == "high":
            return "🔴"
        elif self.priority == "medium":
            return "🟡"
        elif self.priority == "low":
            return "🟢"
        return ""

    def get_due_date_indicator(self) -> str:
        """Get visual indicator for due date status."""
        if self.due_date is None:
            return ""
        if self.is_overdue():
            return "⚠️"
        if self.is_due_soon():
            return "📅"
        return "📆"


def migrate_legacy_task(old_task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate legacy task format to new format.

    Legacy format:
        {"id": 1, "text": "Task", "done": false}

    New format adds:
        priority, due_date, categories, created_at
    """
    migrated = {
        "id": old_task.get("id", 0),
        "text": old_task.get("text", ""),
        "done": old_task.get("done", False),
        "priority": old_task.get("priority"),  # None if not present
        "due_date": old_task.get("due_date"),  # None if not present
        "categories": old_task.get("categories", []),
        "created_at": old_task.get("created_at", datetime.now().isoformat())
    }
    return migrated


def migrate_task_list(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Migrate a list of tasks from legacy to new format."""
    return [migrate_legacy_task(task) for task in tasks]


def validate_task_data(data: Dict[str, Any]) -> bool:
    """Validate task data structure."""
    required_fields = ['id', 'text', 'done']
    return all(field in data for field in required_fields)


def sort_tasks(tasks: List[Task], sort_by: str = "created") -> List[Task]:
    """
    Sort tasks by various criteria.

    Args:
        tasks: List of tasks to sort
        sort_by: Sort criteria - "created", "priority", "due_date", "text"

    Returns:
        Sorted list of tasks
    """
    if sort_by == "priority":
        # High > Medium > Low > None
        priority_order = {"high": 0, "medium": 1, "low": 2, None: 3}
        return sorted(tasks, key=lambda t: (priority_order.get(t.priority, 3), t.created_at or ""))

    elif sort_by == "due_date":
        # Soonest due date first, None at end
        return sorted(tasks, key=lambda t: (t.due_date is None, t.due_date or "9999-12-31"))

    elif sort_by == "text":
        return sorted(tasks, key=lambda t: t.text.lower())

    else:  # "created" or default
        return sorted(tasks, key=lambda t: t.created_at or "")


def filter_tasks(
    tasks: List[Task],
    priority: Optional[str] = None,
    category: Optional[str] = None,
    show_done: bool = True
) -> List[Task]:
    """
    Filter tasks by various criteria.

    Args:
        tasks: List of tasks to filter
        priority: Filter by priority ("high", "medium", "low", or None)
        category: Filter by category tag
        show_done: Whether to include completed tasks

    Returns:
        Filtered list of tasks
    """
    filtered = tasks

    if not show_done:
        filtered = [t for t in filtered if not t.done]

    if priority is not None:
        filtered = [t for t in filtered if t.matches_priority(priority)]

    if category is not None:
        filtered = [t for t in filtered if t.has_category(category)]

    return filtered
