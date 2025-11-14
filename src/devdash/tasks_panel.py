"""
Tasks panel widget - displays and manages TODO tasks
"""

import json
from pathlib import Path
from typing import Optional, List, Dict

from textual.app import ComposeResult
from textual.widgets import Static, Input
from textual.containers import Container
from textual.reactive import reactive
from textual.message import Message


class TasksPanel(Container):
    """Widget displaying and managing tasks."""

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
        ("space", "toggle_task", "Toggle Done"),
        ("d", "delete_task", "Delete Task"),
        ("up", "move_up", "Move Up"),
        ("down", "move_down", "Move Down"),
    ]

    tasks_content = reactive("")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_widget: Optional[Static] = None
        self.input_widget: Optional[Input] = None
        self.tasks: List[Dict] = []
        self.selected_index: int = 0
        self.tasks_file = Path.cwd() / ".devdash_tasks.json"
        self.adding_task = False

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
        """Load tasks from JSON file."""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r') as f:
                    self.tasks = json.load(f)
                    # Ensure tasks have required fields
                    for task in self.tasks:
                        if 'id' not in task:
                            task['id'] = max([t.get('id', 0) for t in self.tasks], default=0) + 1
                        if 'text' not in task:
                            task['text'] = "Untitled Task"
                        if 'done' not in task:
                            task['done'] = False
            else:
                self.tasks = []
        except (json.JSONDecodeError, IOError) as e:
            self.tasks = []
            # Optionally log error

    def save_tasks(self) -> None:
        """Save tasks to JSON file."""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except IOError as e:
            # Optionally handle error
            pass

    def refresh_display(self) -> None:
        """Refresh the tasks display."""
        if not self.tasks:
            self.tasks_content = "[dim]No tasks yet.[/]\n\n[dim]Press 'a' to add a task[/]"
            return

        lines = ["[bold]TODO List:[/]\n"]

        for i, task in enumerate(self.tasks):
            checkbox = "[green]✓[/]" if task['done'] else "[ ]"
            text = task['text']

            # Truncate long task names
            if len(text) > 50:
                text = text[:47] + "..."

            # Highlight selected task
            if i == self.selected_index:
                lines.append(f"[reverse]{checkbox} {text}[/]")
            else:
                lines.append(f"{checkbox} {text}")

        lines.append("")
        lines.append("[dim]a:add  space:toggle  d:delete  ↑/↓:navigate[/]")

        self.tasks_content = "\n".join(lines)

    def action_add_task(self) -> None:
        """Show input to add a new task."""
        if self.input_widget:
            self.input_widget.display = True
            self.input_widget.focus()
            self.adding_task = True

    def action_toggle_task(self) -> None:
        """Toggle the selected task's done status."""
        if 0 <= self.selected_index < len(self.tasks):
            self.tasks[self.selected_index]['done'] = not self.tasks[self.selected_index]['done']
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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle task input submission."""
        if self.adding_task and event.value.strip():
            # Get next ID
            next_id = max([task['id'] for task in self.tasks], default=0) + 1

            # Add new task
            new_task = {
                'id': next_id,
                'text': event.value.strip(),
                'done': False
            }
            self.tasks.append(new_task)
            self.save_tasks()

            # Reset input
            if self.input_widget:
                self.input_widget.value = ""
                self.input_widget.display = False

            self.adding_task = False
            self.selected_index = len(self.tasks) - 1
            self.refresh_display()
            self.focus()
