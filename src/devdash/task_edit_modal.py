"""
Task edit modal - comprehensive dialog for editing task details.
"""

from datetime import datetime, date
from typing import Optional, Callable

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input, Button, Select, Label
from textual.message import Message

from devdash.task_model import Task


class TaskEditModal(ModalScreen):
    """Modal dialog for editing task details."""

    DEFAULT_CSS = """
    TaskEditModal {
        align: center middle;
    }

    #edit-dialog {
        width: 70;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }

    #edit-title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 1;
        text-style: bold;
    }

    #edit-content {
        padding: 2;
        height: auto;
    }

    .field-row {
        height: auto;
        margin: 1 0;
    }

    .field-label {
        width: 15;
        text-align: right;
        padding-right: 1;
    }

    .field-input {
        width: 1fr;
    }

    #button-row {
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    #button-row Button {
        margin: 0 1;
    }

    .category-input {
        width: 1fr;
    }

    .help-text {
        color: $text-muted;
        text-style: italic;
        margin-top: 0;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("ctrl+s", "save", "Save"),
    ]

    class SaveTask(Message):
        """Message sent when task is saved."""
        def __init__(self, task_data: dict) -> None:
            self.task_data = task_data
            super().__init__()

    def __init__(self, task: Optional[Task] = None, task_id: Optional[int] = None):
        """
        Initialize edit modal.

        Args:
            task: Existing task to edit (None for new task)
            task_id: ID for new task (ignored if task is provided)
        """
        super().__init__()
        self.task = task
        self.task_id = task_id or (task.id if task else 1)
        self.is_new = task is None

    def compose(self) -> ComposeResult:
        """Create edit dialog widgets."""
        title = "New Task" if self.is_new else "Edit Task"

        with Container(id="edit-dialog"):
            yield Static(title, id="edit-title")

            with Vertical(id="edit-content"):
                # Task text
                with Horizontal(classes="field-row"):
                    yield Label("Task:", classes="field-label")
                    yield Input(
                        value=self.task.text if self.task else "",
                        placeholder="Enter task description...",
                        id="task-text",
                        classes="field-input"
                    )

                # Priority
                with Horizontal(classes="field-row"):
                    yield Label("Priority:", classes="field-label")
                    yield Select(
                        options=[
                            ("None", None),
                            ("🔴 High", "high"),
                            ("🟡 Medium", "medium"),
                            ("🟢 Low", "low"),
                        ],
                        value=self.task.priority if self.task else None,
                        id="task-priority",
                        classes="field-input"
                    )

                # Due date
                with Horizontal(classes="field-row"):
                    yield Label("Due Date:", classes="field-label")
                    yield Input(
                        value=self.task.due_date if self.task else "",
                        placeholder="YYYY-MM-DD (leave empty for none)",
                        id="task-due-date",
                        classes="field-input"
                    )

                yield Static(
                    "[dim]Format: YYYY-MM-DD (e.g., 2025-12-31)[/]",
                    classes="help-text"
                )

                # Categories
                with Horizontal(classes="field-row"):
                    yield Label("Categories:", classes="field-label")
                    yield Input(
                        value=", ".join(self.task.categories) if self.task else "",
                        placeholder="work, personal, urgent (comma-separated)",
                        id="task-categories",
                        classes="category-input"
                    )

                yield Static(
                    "[dim]Separate multiple categories with commas[/]",
                    classes="help-text"
                )

                # Buttons
                with Horizontal(id="button-row"):
                    yield Button("Save (Ctrl+S)", variant="primary", id="save-button")
                    yield Button("Cancel (ESC)", variant="default", id="cancel-button")

    def on_mount(self) -> None:
        """Focus the text input when mounted."""
        self.query_one("#task-text", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-button":
            self.action_save()
        elif event.button.id == "cancel-button":
            self.action_cancel()

    def action_save(self) -> None:
        """Save the task and close modal."""
        # Get form values
        text_input = self.query_one("#task-text", Input)
        priority_select = self.query_one("#task-priority", Select)
        due_date_input = self.query_one("#task-due-date", Input)
        categories_input = self.query_one("#task-categories", Input)

        text = text_input.value.strip()
        if not text:
            # TODO: Show error message
            text_input.focus()
            return

        priority = priority_select.value
        due_date = due_date_input.value.strip() or None
        categories_str = categories_input.value.strip()

        # Parse categories
        if categories_str:
            categories = [c.strip() for c in categories_str.split(",") if c.strip()]
        else:
            categories = []

        # Validate due date if provided
        if due_date:
            try:
                datetime.fromisoformat(due_date)
            except (ValueError, TypeError):
                # TODO: Show error message
                due_date_input.focus()
                return

        # Build task data
        task_data = {
            "id": self.task_id,
            "text": text,
            "done": self.task.done if self.task else False,
            "priority": priority,
            "due_date": due_date,
            "categories": categories,
            "created_at": self.task.created_at if self.task else datetime.now().isoformat()
        }

        # Send message and close
        self.post_message(self.SaveTask(task_data))
        self.dismiss()

    def action_cancel(self) -> None:
        """Cancel editing and close modal."""
        self.dismiss()


class QuickPriorityModal(ModalScreen):
    """Quick modal for setting task priority."""

    DEFAULT_CSS = """
    QuickPriorityModal {
        align: center middle;
    }

    #priority-dialog {
        width: 40;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }

    #priority-title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 1;
        text-style: bold;
    }

    #priority-content {
        padding: 2;
        height: auto;
    }

    #priority-content Button {
        width: 100%;
        margin: 1 0;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("1", "set_high", "High"),
        ("2", "set_medium", "Medium"),
        ("3", "set_low", "Low"),
        ("0", "set_none", "None"),
    ]

    class SetPriority(Message):
        """Message sent when priority is selected."""
        def __init__(self, priority: Optional[str]) -> None:
            self.priority = priority
            super().__init__()

    def compose(self) -> ComposeResult:
        """Create priority selection dialog."""
        with Container(id="priority-dialog"):
            yield Static("Set Priority", id="priority-title")

            with Vertical(id="priority-content"):
                yield Button("🔴 High (1)", id="high-btn", variant="error")
                yield Button("🟡 Medium (2)", id="medium-btn", variant="warning")
                yield Button("🟢 Low (3)", id="low-btn", variant="success")
                yield Button("⚪ None (0)", id="none-btn", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        priority_map = {
            "high-btn": "high",
            "medium-btn": "medium",
            "low-btn": "low",
            "none-btn": None,
        }
        if event.button.id in priority_map:
            self.post_message(self.SetPriority(priority_map[event.button.id]))
            self.dismiss()

    def action_set_high(self) -> None:
        """Set high priority."""
        self.post_message(self.SetPriority("high"))
        self.dismiss()

    def action_set_medium(self) -> None:
        """Set medium priority."""
        self.post_message(self.SetPriority("medium"))
        self.dismiss()

    def action_set_low(self) -> None:
        """Set low priority."""
        self.post_message(self.SetPriority("low"))
        self.dismiss()

    def action_set_none(self) -> None:
        """Clear priority."""
        self.post_message(self.SetPriority(None))
        self.dismiss()

    def action_cancel(self) -> None:
        """Cancel and close."""
        self.dismiss()
