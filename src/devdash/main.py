"""
Main entry point for devdash application.
"""

import sys
from pathlib import Path
from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container, Horizontal, Vertical

from devdash.git_panel import GitPanel
from devdash.system_panel import SystemPanel
from devdash.tasks_panel import TasksPanel
from devdash.timer_panel import TimerPanel
from devdash.help_modal import HelpModal


class DevDashApp(App):
    """A terminal dashboard for developers."""

    CSS = """
    Screen {
        align: center middle;
    }

    #app-header {
        background: $boost;
        color: $text;
        height: 3;
        padding: 1;
        dock: top;
    }

    #main-container {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    #top-panels {
        height: 50%;
        width: 100%;
    }

    #bottom-panels {
        height: 50%;
        width: 100%;
    }

    .panel-half {
        width: 50%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
        ("r", "refresh", "Refresh"),
        # Task management
        ("a", "add_task", "Add Task"),
        ("e", "edit_task", "Edit Task"),
        ("space", "toggle_task", "Toggle Done"),
        ("d", "delete_task", "Delete Task"),
        ("p", "quick_priority", "Set Priority"),
        ("f", "filter_tasks", "Filter"),
        ("s", "sort_tasks", "Sort"),
        ("x", "export_tasks", "Export"),
        ("1", "filter_high", "High Priority"),
        ("2", "filter_medium", "Medium Priority"),
        ("3", "filter_low", "Low Priority"),
        ("0", "clear_filters", "Clear Filters"),
        # Timer (use Shift+key to avoid conflicts)
        ("F", "timer_focus", "Focus"),
        ("B", "timer_break", "Break"),
        ("S", "timer_stop", "Stop"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        # Header with current directory and time
        yield Container(
            Static(self._get_header_text(), id="header-text"),
            id="app-header"
        )

        # Main container with panels
        with Container(id="main-container"):
            # Top row: Git (left) and System (right)
            with Horizontal(id="top-panels"):
                yield GitPanel(classes="panel-half")
                yield SystemPanel(classes="panel-half")

            # Bottom row: Tasks (left) and Timer (right)
            with Horizontal(id="bottom-panels"):
                yield TasksPanel(classes="panel-half")
                yield TimerPanel(classes="panel-half")

        # Footer with keybindings
        yield Footer()

    def _get_header_text(self) -> str:
        """Generate header text with directory and time."""
        cwd = Path.cwd()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[bold]devdash[/] | [cyan]{cwd}[/] | [dim]{now}[/]"

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def on_unmount(self) -> None:
        """Clean up terminal state on exit."""
        # Reset terminal modes to prevent cursor artifacts
        import os
        # Disable mouse tracking
        os.system('printf "\\033[?1000l\\033[?1003l\\033[?1015l\\033[?1006l"')
        # Reset terminal
        os.system('tput reset 2>/dev/null || true')

    def action_help(self) -> None:
        """Show help popup."""
        self.push_screen(HelpModal())

    def action_refresh(self) -> None:
        """Refresh all panels."""
        # Will implement when panels have refresh methods
        pass

    # Task panel actions - delegate to TasksPanel
    def action_add_task(self) -> None:
        """Add a new task."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_add_task()

    def action_edit_task(self) -> None:
        """Edit selected task."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_edit_task()

    def action_toggle_task(self) -> None:
        """Toggle task completion."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_toggle_task()

    def action_delete_task(self) -> None:
        """Delete selected task."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_delete_task()

    def action_quick_priority(self) -> None:
        """Quick set priority."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_quick_priority()

    def action_filter_tasks(self) -> None:
        """Toggle task filter."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_filter_tasks()

    def action_sort_tasks(self) -> None:
        """Cycle sort order."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_sort_tasks()

    def action_export_tasks(self) -> None:
        """Export tasks to Markdown."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_export_tasks()

    def action_filter_high(self) -> None:
        """Filter high priority tasks."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_filter_high()

    def action_filter_medium(self) -> None:
        """Filter medium priority tasks."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_filter_medium()

    def action_filter_low(self) -> None:
        """Filter low priority tasks."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_filter_low()

    def action_clear_filters(self) -> None:
        """Clear all task filters."""
        tasks_panel = self.query_one(TasksPanel)
        tasks_panel.action_clear_filters()

    # Timer panel actions - delegate to TimerPanel
    def action_timer_focus(self) -> None:
        """Start focus session."""
        timer_panel = self.query_one(TimerPanel)
        timer_panel.action_start_focus()

    def action_timer_break(self) -> None:
        """Start break session."""
        timer_panel = self.query_one(TimerPanel)
        timer_panel.action_start_break()

    def action_timer_stop(self) -> None:
        """Stop timer."""
        timer_panel = self.query_one(TimerPanel)
        timer_panel.action_stop_timer()


def cli():
    """Command-line interface entry point."""
    app = DevDashApp()
    app.run()


if __name__ == "__main__":
    cli()
