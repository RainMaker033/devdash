"""
Help modal widget - displays keyboard shortcuts and usage information
"""

from typing import Optional
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from textual.screen import ModalScreen

from devdash.config import DevDashConfig, get_default_config


class HelpModal(ModalScreen):
    """Modal screen displaying help information."""

    def __init__(self, config: Optional[DevDashConfig] = None):
        """Initialize help modal.

        Args:
            config: Configuration object to read keybindings from. If None, uses defaults.
        """
        super().__init__()
        self.config = config or get_default_config()

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
        """Generate help text content using configured keybindings."""
        kb = self.config.keybindings
        return f"""[bold cyan]General[/]
  {kb.quit} / Ctrl+C  - Quit DevDash
  {kb.help}           - Show this help
  {kb.config}         - Open configuration editor
  {kb.refresh}        - Refresh all panels

[bold cyan]Tasks Panel - Basic[/]
  {kb.add_task}       - Add new task (quick)
  {kb.edit_task}      - Edit task (full editor with priority, due date, categories)
  {kb.toggle_task}    - Toggle task done/undone
  {kb.delete_task}    - Delete selected task
  ↑/↓                 - Navigate tasks

[bold cyan]Tasks Panel - Advanced[/]
  {kb.quick_priority} - Quick set priority
  {kb.filter_tasks}   - Toggle filter (show/hide completed)
  {kb.sort_tasks}     - Cycle sort (created/priority/due date/text)
  {kb.export_tasks}   - Export tasks to Markdown
  {kb.filter_high}/{kb.filter_medium}/{kb.filter_low} - Filter by priority (high/medium/low)
  {kb.clear_filters}  - Clear all filters

[bold cyan]Timer Panel[/]
  {kb.timer_focus}    - Start focus session ({self.config.timer.focus_duration} minutes)
  {kb.timer_break}    - Start break ({self.config.timer.break_duration} minutes)
  {kb.timer_stop}     - Stop timer / return to idle

[bold cyan]Task Features[/]
  • Priorities: 🔴 High, 🟡 Medium, 🟢 Low
  • Due dates with indicators: ⚠️ Overdue, 📅 Due soon
  • Categories/tags for organization
  • Export to Markdown (grouped, flat, or by category)
  • Filter and sort capabilities

[bold cyan]Panels[/]
  • Git Panel displays repository status and recent commits
  • System Panel shows CPU, RAM, and disk usage
  • Tasks Panel manages TODO with priorities, dates, categories
  • Timer Panel provides Pomodoro time management

[dim]Press ESC or {kb.quit} to close this help[/]
"""

    def action_dismiss(self) -> None:
        """Close the help modal."""
        self.app.pop_screen()
