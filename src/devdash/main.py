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

    def action_help(self) -> None:
        """Show help popup."""
        self.push_screen(HelpModal())

    def action_refresh(self) -> None:
        """Refresh all panels."""
        # Will implement when panels have refresh methods
        pass


def cli():
    """Command-line interface entry point."""
    app = DevDashApp()
    app.run()


if __name__ == "__main__":
    cli()
