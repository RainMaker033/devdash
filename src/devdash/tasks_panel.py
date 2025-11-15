"""
Tasks panel widget - displays and manages TODO tasks with enhanced features.
"""

import json
from pathlib import Path
from typing import Optional, List

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from textual.reactive import reactive

from devdash.task_model import Task, migrate_task_list, sort_tasks, filter_tasks
from devdash.task_edit_modal import TaskEditModal, QuickPriorityModal
from devdash.task_export import export_tasks_to_file
from devdash.config.schema import TasksConfig


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

    # Bindings are now handled at App level
    # Keep action methods for delegation

    tasks_content = reactive("")

    def __init__(self, config: Optional[TasksConfig] = None, *args, **kwargs):
        """Initialize Tasks panel.

        Args:
            config: Tasks panel configuration. If None, uses defaults.
        """
        super().__init__(*args, **kwargs)
        self.config = config or TasksConfig()
        self.content_widget: Optional[Static] = None
        self.tasks: List[Task] = []
        self.selected_index: int = 0

        # Use configured tasks file path (support absolute or relative)
        file_path = Path(self.config.file_path)
        self.tasks_file = file_path if file_path.is_absolute() else Path.cwd() / file_path

        # Filter and sort state - initialize from config
        self.current_filter_priority: Optional[str] = self.config.default_priority_filter
        self.current_filter_category: Optional[str] = self.config.default_category_filter
        self.show_done: bool = self.config.show_completed
        self.sort_by: str = self.config.default_sort

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("Tasks", classes="panel-title")
        self.content_widget = Static("", classes="panel-content")
        yield self.content_widget

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self._apply_visibility()
        if not self.config.enabled:
            return
        self.load_tasks()
        self.refresh_display()

    def watch_tasks_content(self, new_content: str) -> None:
        """Update content when tasks_content changes."""
        if self.content_widget:
            self.content_widget.update(new_content)

    def _apply_visibility(self) -> None:
        """Show or hide the panel based on configuration."""
        self.display = self.config.enabled

    def _interactions_enabled(self) -> bool:
        """Return True if user-triggered actions should run."""
        return self.config.enabled

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
        if not self.config.enabled:
            return

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
        """Open task editor modal to add a new task."""
        if not self._interactions_enabled():
            return
        next_id = max([t.id for t in self.tasks], default=0) + 1
        self.app.push_screen(TaskEditModal(task_id=next_id), self.handle_edit_save)

    def action_edit_task(self) -> None:
        """Open full edit dialog for selected task."""
        if not self._interactions_enabled():
            return
        if 0 <= self.selected_index < len(self.tasks):
            task = self.tasks[self.selected_index]
            self.app.push_screen(TaskEditModal(task=task), self.handle_edit_save)
        else:
            # No task selected, create new
            next_id = max([t.id for t in self.tasks], default=0) + 1
            self.app.push_screen(TaskEditModal(task_id=next_id), self.handle_edit_save)

    def handle_edit_save(self, message: TaskEditModal.SaveTask) -> None:
        """Handle task save from edit modal."""
        if not self.config.enabled or message is None:
            return  # User cancelled or panel disabled
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
        if not self._interactions_enabled():
            return
        if 0 <= self.selected_index < len(self.tasks):
            self.app.push_screen(QuickPriorityModal(), self.handle_priority_set)

    def handle_priority_set(self, message: QuickPriorityModal.SetPriority) -> None:
        """Handle priority selection from modal."""
        if not self.config.enabled or message is None:
            return  # User cancelled or panel disabled
        if 0 <= self.selected_index < len(self.tasks):
            self.tasks[self.selected_index].priority = message.priority
            self.save_tasks()
            self.refresh_display()

    def action_toggle_task(self) -> None:
        """Toggle the selected task's done status."""
        if not self._interactions_enabled():
            return
        if 0 <= self.selected_index < len(self.tasks):
            self.tasks[self.selected_index].done = not self.tasks[self.selected_index].done
            self.save_tasks()
            self.refresh_display()

    def action_delete_task(self) -> None:
        """Delete the selected task."""
        if not self._interactions_enabled():
            return
        if 0 <= self.selected_index < len(self.tasks):
            self.tasks.pop(self.selected_index)
            if self.selected_index >= len(self.tasks) and self.tasks:
                self.selected_index = len(self.tasks) - 1
            self.save_tasks()
            self.refresh_display()

    def action_move_up(self) -> None:
        """Move selection up."""
        if not self._interactions_enabled():
            return
        if self.selected_index > 0:
            self.selected_index -= 1
            self.refresh_display()

    def action_move_down(self) -> None:
        """Move selection down."""
        if not self._interactions_enabled():
            return
        if self.selected_index < len(self.tasks) - 1:
            self.selected_index += 1
            self.refresh_display()

    def action_filter_tasks(self) -> None:
        """Toggle show/hide completed tasks."""
        if not self._interactions_enabled():
            return
        self.show_done = not self.show_done
        self.refresh_display()

    def action_filter_high(self) -> None:
        """Filter to show only high priority tasks."""
        if not self._interactions_enabled():
            return
        self.current_filter_priority = "high"
        self.refresh_display()

    def action_filter_medium(self) -> None:
        """Filter to show only medium priority tasks."""
        if not self._interactions_enabled():
            return
        self.current_filter_priority = "medium"
        self.refresh_display()

    def action_filter_low(self) -> None:
        """Filter to show only low priority tasks."""
        if not self._interactions_enabled():
            return
        self.current_filter_priority = "low"
        self.refresh_display()

    def action_clear_filters(self) -> None:
        """Clear all filters."""
        if not self._interactions_enabled():
            return
        self.current_filter_priority = None
        self.current_filter_category = None
        self.show_done = True
        self.refresh_display()

    def update_config(self, new_config: TasksConfig) -> None:
        """Update the tasks configuration and apply changes.

        Args:
            new_config: New tasks configuration
        """
        old_path = self.config.file_path
        was_enabled = self.config.enabled
        self.config = new_config
        self._apply_visibility()

        # Update file path if it changed
        file_path = Path(self.config.file_path)
        new_tasks_file = file_path if file_path.is_absolute() else Path.cwd() / file_path

        if old_path != self.config.file_path:
            self.tasks_file = new_tasks_file
            # Reload tasks from new location
            self.load_tasks()
        elif self.config.enabled and not was_enabled:
            # Panel was previously disabled; ensure tasks are loaded when enabling
            self.tasks_file = new_tasks_file
            self.load_tasks()

        # Update sort and filters if they changed
        self.sort_by = self.config.default_sort
        self.show_done = self.config.show_completed
        self.current_filter_priority = self.config.default_priority_filter
        self.current_filter_category = self.config.default_category_filter

        if not self.config.enabled:
            return

        # Refresh display with new settings
        self.refresh_display()

    def action_sort_tasks(self) -> None:
        """Cycle through sort options."""
        if not self._interactions_enabled():
            return
        sort_options = ["created", "priority", "due_date", "text"]
        current_idx = sort_options.index(self.sort_by)
        self.sort_by = sort_options[(current_idx + 1) % len(sort_options)]
        self.refresh_display()

    def action_export_tasks(self) -> None:
        """Export tasks to Markdown."""
        if not self._interactions_enabled():
            return
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
