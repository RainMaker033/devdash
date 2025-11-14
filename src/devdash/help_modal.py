"""
Help modal widget - displays keyboard shortcuts and usage information
"""

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from textual.screen import ModalScreen


class HelpModal(ModalScreen):
    """Modal screen displaying help information."""

    DEFAULT_CSS = """
    HelpModal {
        align: center middle;
    }

    #help-dialog {
        width: 80;
        height: 30;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }

    #help-title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 1;
        text-style: bold;
    }

    #help-content {
        padding: 2;
        height: auto;
    }
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Create help dialog."""
        with Container(id="help-dialog"):
            yield Static("devdash - Keyboard Shortcuts", id="help-title")
            yield Static(self._get_help_text(), id="help-content")

    def _get_help_text(self) -> str:
        """Generate help text content."""
        return """[bold cyan]General[/]
  q / Ctrl+C  - Quit devdash
  ?           - Show this help
  r           - Refresh all panels

[bold cyan]Tasks Panel[/]
  a           - Add new task
  space       - Toggle task done/undone
  d           - Delete selected task
  ↑/↓         - Navigate tasks

[bold cyan]Timer Panel[/]
  f           - Start focus session (25 minutes)
  b           - Start break (5 minutes)
  s           - Stop timer / return to idle

[bold cyan]Panels[/]
  • Git Panel displays repository status and recent commits
  • System Panel shows CPU, RAM, and disk usage
  • Tasks Panel manages your TODO list
  • Timer Panel provides Pomodoro time management

[dim]Press ESC or q to close this help[/]
"""

    def action_dismiss(self) -> None:
        """Close the help modal."""
        self.app.pop_screen()
