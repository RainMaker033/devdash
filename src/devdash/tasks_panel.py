"""
Tasks panel widget - displays and manages TODO tasks with enhanced features.
"""

import json
from pathlib import Path
from typing import Optional, List

from textual.app import ComposeResult
from textual.widgets import Static, Input
from textual.containers import Container
from textual.reactive import reactive

from devdash.task_model import Task, migrate_task_list, sort_tasks, filter_tasks
from devdash.task_edit_modal import TaskEditModal, QuickPriorityModal
from devdash.task_export import export_tasks_to_file


class TasksPanel(Container):
    """Widget displaying and managing tasks with priorities, due dates, and categories."""

    DEFAULT_CSS = """
    TasksPanel {
        border: solid $warning;
        padding: 1;
        height: auto;
    }

    TasksPanel .panel-title {
        background: $warning;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }

    TasksPanel .panel-content {
        padding: 1;
    }

    TasksPanel .task-input {
        margin: 1 0;
    }
    """

    BINDINGS = [
        ("a", "add_task", "Add Task"),
        ("e", "edit_task", "Edit Task"),
        ("space", "toggle_task", "Toggle Done"),
        ("d", "delete_task", "Delete Task"),
        ("p", "quick_priority", "Set Priority"),
        ("f", "toggle_filter", "Filter"),
        ("s", "cycle_sort", "Sort"),
        ("x", "export_tasks", "Export"),
        ("up", "move_up", "Move Up"),
        ("down", "move_down", "Move Down"),
        ("1", "filter_high", "High Priority"),
        ("2", "filter_medium", "Medium Priority"),
        ("3", "filter_low", "Low Priority"),
        ("0", "clear_filter", "All Tasks"),
    ]

    tasks_content = reactive("")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_widget: Optional[Static] = None
        self.input_widget: Optional[Input] = None
        self.tasks: List[Task] = []
        self.selected_index: int = 0
        self.tasks_file = Path.cwd() / ".devdash_tasks.json"
        self.adding_task = False

        # Filter and sort state
        self.current_filter_priority: Optional[str] = None
        self.current_filter_category: Optional[str] = None
        self.show_done: bool = True
        self.sort_by: str = "created"  # "created", "priority", "due_date", "text"

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("Tasks", classes="panel-title")
        self.content_widget = Static("", classes="panel-content")
        yield self.content_widget
        self.input_widget = Input(placeholder="Enter task description...", classes="task-input")
        self.input_widget.display = False
        yield self.input_widget

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.load_tasks()
        self.refresh_display()

    def watch_tasks_content(self, new_content: str) -> None:
        """Update content when tasks_content changes."""
        if self.content_widget:
            self.content_widget.update(new_content)

    def load_tasks(self) -> None:
        """Load tasks from JSON file with migration support."""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r') as f:
                    task_dicts = json.load(f)

                # Migrate legacy tasks
                migrated = migrate_task_list(task_dicts)

                # Convert to Task objects
                self.tasks = [Task.from_dict(t) for t in migrated]
            else:
                self.tasks = []
        except (json.JSONDecodeError, IOError):
            self.tasks = []

    def save_tasks(self) -> None:
        """Save tasks to JSON file."""
        try:
            task_dicts = [task.to_dict() for task in self.tasks]
            with open(self.tasks_file, 'w') as f:
                json.dump(task_dicts, f, indent=2)
        except IOError:
            pass

    def get_filtered_sorted_tasks(self) -> List[Task]:
        """Get tasks after applying filters and sorting."""
        # Apply filters
        filtered = filter_tasks(
            self.tasks,
            priority=self.current_filter_priority,
            category=self.current_filter_category,
            show_done=self.show_done
        )

        # Apply sorting
        sorted_tasks = sort_tasks(filtered, sort_by=self.sort_by)

        return sorted_tasks

    def refresh_display(self) -> None:
        """Refresh the tasks display with enhanced formatting."""
        display_tasks = self.get_filtered_sorted_tasks()

        if not display_tasks:
            if self.current_filter_priority or self.current_filter_category:
                self.tasks_content = "[dim]No tasks match current filter.[/]\n\n[dim]Press '0' to show all tasks[/]"
            else:
                self.tasks_content = "[dim]No tasks yet.[/]\n\n[dim]Press 'a' to add a task[/]"
            return

        lines = []

        # Show filter/sort status
        status_parts = []
        if self.current_filter_priority:
            status_parts.append(f"Priority: {self.current_filter_priority}")
        if not self.show_done:
            status_parts.append("Hide completed")
        if self.sort_by != "created":
            status_parts.append(f"Sort: {self.sort_by}")

        if status_parts:
            lines.append(f"[dim]({', '.join(status_parts)})[/]\n")

        lines.append("[bold]TODO List:[/]\n")

        for i, task in enumerate(display_tasks):
            # Find original index in full task list
            original_idx = self.tasks.index(task) if task in self.tasks else -1

            # Checkbox
            checkbox = "[green]✓[/]" if task.done else "[ ]"

            # Priority emoji
            priority_emoji = task.get_priority_emoji()

            # Due date indicator
            due_indicator = task.get_due_date_indicator()

            # Task text (truncate if needed)
            text = task.text
            if len(text) > 40:
                text = text[:37] + "..."

            # Categories
            if task.categories:
                categories_str = " " + " ".join(f"[dim]#{c}[/]" for c in task.categories[:2])
            else:
                categories_str = ""

            # Due date text
            due_text = ""
            if task.due_date:
                due_text = f" [cyan]{task.due_date}[/]"

            # Build line
            line = f"{checkbox} {priority_emoji}{text}{categories_str}{due_indicator}{due_text}"

            # Highlight selected task
            if original_idx == self.selected_index:
                line = f"[reverse]{line}[/]"

            lines.append(line)

        lines.append("")
        lines.append("[dim]a:add e:edit space:toggle d:delete p:priority f:filter[/]")

        self.tasks_content = "\n".join(lines)

    def action_add_task(self) -> None:
        """Show input to add a new task (quick mode)."""
        if self.input_widget:
            self.input_widget.display = True
            self.input_widget.focus()
            self.adding_task = True

    def action_edit_task(self) -> None:
        """Open full edit dialog for selected task."""
        if 0 <= self.selected_index < len(self.tasks):
            task = self.tasks[self.selected_index]
            self.app.push_screen(TaskEditModal(task=task), self.handle_edit_save)
        else:
            # No task selected, create new
            next_id = max([t.id for t in self.tasks], default=0) + 1
            self.app.push_screen(TaskEditModal(task_id=next_id), self.handle_edit_save)

    def handle_edit_save(self, message: TaskEditModal.SaveTask) -> None:
        """Handle task save from edit modal."""
        task_data = message.task_data
        task = Task.from_dict(task_data)

        # Find if this is an update or new task
        existing_idx = next((i for i, t in enumerate(self.tasks) if t.id == task.id), None)

        if existing_idx is not None:
            # Update existing task
            self.tasks[existing_idx] = task
        else:
            # Add new task
            self.tasks.append(task)
            self.selected_index = len(self.tasks) - 1

        self.save_tasks()
        self.refresh_display()

    def action_quick_priority(self) -> None:
        """Open quick priority selection modal."""
        if 0 <= self.selected_index < len(self.tasks):
            self.app.push_screen(QuickPriorityModal(), self.handle_priority_set)

    def handle_priority_set(self, message: QuickPriorityModal.SetPriority) -> None:
        """Handle priority selection from modal."""
        if 0 <= self.selected_index < len(self.tasks):
            self.tasks[self.selected_index].priority = message.priority
            self.save_tasks()
            self.refresh_display()

    def action_toggle_task(self) -> None:
        """Toggle the selected task's done status."""
        if 0 <= self.selected_index < len(self.tasks):
            self.tasks[self.selected_index].done = not self.tasks[self.selected_index].done
            self.save_tasks()
            self.refresh_display()

    def action_delete_task(self) -> None:
        """Delete the selected task."""
        if 0 <= self.selected_index < len(self.tasks):
            self.tasks.pop(self.selected_index)
            if self.selected_index >= len(self.tasks) and self.tasks:
                self.selected_index = len(self.tasks) - 1
            self.save_tasks()
            self.refresh_display()

    def action_move_up(self) -> None:
        """Move selection up."""
        if self.selected_index > 0:
            self.selected_index -= 1
            self.refresh_display()

    def action_move_down(self) -> None:
        """Move selection down."""
        if self.selected_index < len(self.tasks) - 1:
            self.selected_index += 1
            self.refresh_display()

    def action_toggle_filter(self) -> None:
        """Toggle show/hide completed tasks."""
        self.show_done = not self.show_done
        self.refresh_display()

    def action_filter_high(self) -> None:
        """Filter to show only high priority tasks."""
        self.current_filter_priority = "high"
        self.refresh_display()

    def action_filter_medium(self) -> None:
        """Filter to show only medium priority tasks."""
        self.current_filter_priority = "medium"
        self.refresh_display()

    def action_filter_low(self) -> None:
        """Filter to show only low priority tasks."""
        self.current_filter_priority = "low"
        self.refresh_display()

    def action_clear_filter(self) -> None:
        """Clear all filters."""
        self.current_filter_priority = None
        self.current_filter_category = None
        self.show_done = True
        self.refresh_display()

    def action_cycle_sort(self) -> None:
        """Cycle through sort options."""
        sort_options = ["created", "priority", "due_date", "text"]
        current_idx = sort_options.index(self.sort_by)
        self.sort_by = sort_options[(current_idx + 1) % len(sort_options)]
        self.refresh_display()

    def action_export_tasks(self) -> None:
        """Export tasks to Markdown."""
        if not self.tasks:
            return

        try:
            # Export with grouped format by default
            filepath = export_tasks_to_file(
                self.tasks,
                directory=Path.cwd(),
                format_type="grouped"
            )
            # Could show success notification here
            # For now, tasks are exported silently to current directory
        except Exception:
            # Silently fail - could show error notification in future
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle task input submission (quick add)."""
        if self.adding_task and event.value.strip():
            # Get next ID
            next_id = max([task.id for task in self.tasks], default=0) + 1

            # Create simple task (can be enhanced with edit later)
            task = Task(
                id=next_id,
                text=event.value.strip()
            )
            self.tasks.append(task)
            self.save_tasks()

            # Reset input
            if self.input_widget:
                self.input_widget.value = ""
                self.input_widget.display = False

            self.adding_task = False
            self.selected_index = len(self.tasks) - 1
            self.refresh_display()
            self.focus()
