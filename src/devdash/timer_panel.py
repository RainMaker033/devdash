"""
Timer panel widget - Pomodoro timer functionality
"""

import time
from enum import Enum
from typing import Optional

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from textual.reactive import reactive

from devdash.config.schema import TimerConfig


class TimerState(Enum):
    """Timer states."""
    IDLE = "idle"
    FOCUS = "focus"
    BREAK = "break"


class TimerPanel(Container):
    """Widget displaying Pomodoro timer."""

    DEFAULT_CSS = """
    TimerPanel {
        border: solid $error;
        padding: 1;
        height: auto;
    }

    TimerPanel .panel-title {
        background: $error;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }

    TimerPanel .panel-content {
        padding: 1;
        text-align: center;
    }
    """

    # Bindings are now handled at App level
    # Keep action methods for delegation

    timer_content = reactive("")

    def __init__(self, config: Optional[TimerConfig] = None, *args, **kwargs):
        """Initialize Timer panel.

        Args:
            config: Timer panel configuration. If None, uses defaults.
        """
        super().__init__(*args, **kwargs)
        self.config = config or TimerConfig()
        self.content_widget: Optional[Static] = None
        self.state: TimerState = TimerState.IDLE
        self.remaining_seconds: int = 0
        self.end_time: float = 0
        self.update_timer_handle = None

        # Convert minutes to seconds for internal use
        self.focus_duration = self.config.focus_duration * 60
        self.break_duration = self.config.break_duration * 60

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("Pomodoro Timer", classes="panel-title")
        self.content_widget = Static("", classes="panel-content")
        yield self.content_widget

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        if not self.config.enabled:
            self.timer_content = "[dim]Timer panel disabled in configuration[/]"
            return
        self.refresh_display()

    def watch_timer_content(self, new_content: str) -> None:
        """Update content when timer_content changes."""
        if self.content_widget:
            self.content_widget.update(new_content)

    def _format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS."""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def refresh_display(self) -> None:
        """Refresh the timer display."""
        if self.state == TimerState.IDLE:
            self.timer_content = f"""[bold cyan]IDLE[/]

Ready to start

[dim]Press 'Shift+F' for focus ({self.config.focus_duration}min)
Press 'Shift+B' for break ({self.config.break_duration}min)[/]
"""
        elif self.state == TimerState.FOCUS:
            time_str = self._format_time(self.remaining_seconds)
            progress = self._create_progress_bar()
            self.timer_content = f"""[bold red]FOCUS SESSION[/]

[bold cyan]{time_str}[/]

{progress}

[dim]Press 'Shift+S' to stop[/]
"""
        elif self.state == TimerState.BREAK:
            time_str = self._format_time(self.remaining_seconds)
            progress = self._create_progress_bar()
            self.timer_content = f"""[bold green]BREAK TIME[/]

[bold cyan]{time_str}[/]

{progress}

[dim]Press 'Shift+S' to stop[/]
"""

    def _create_progress_bar(self) -> str:
        """Create a visual progress bar for the timer."""
        if self.state == TimerState.FOCUS:
            total = self.focus_duration
        elif self.state == TimerState.BREAK:
            total = self.break_duration
        else:
            return ""

        if not self.config.show_progress_bar:
            return ""

        percentage = (self.remaining_seconds / total) * 100
        width = self.config.progress_bar_width
        filled = int((percentage / 100) * width)
        empty = width - filled

        return f"[cyan]{'█' * filled}{'░' * empty}[/]"

    def update_timer(self) -> None:
        """Update the countdown timer."""
        if self.state != TimerState.IDLE:
            now = time.time()
            self.remaining_seconds = max(0, int(self.end_time - now))

            if self.remaining_seconds <= 0:
                # Timer finished
                self.stop_timer()
                # Could add notification here
            else:
                self.refresh_display()

    def action_start_focus(self) -> None:
        """Start a focus session."""
        self.state = TimerState.FOCUS
        self.remaining_seconds = self.focus_duration
        self.end_time = time.time() + self.focus_duration

        # Start periodic updates
        if self.update_timer_handle:
            self.update_timer_handle.stop()
        self.update_timer_handle = self.set_interval(1, self.update_timer)

        self.refresh_display()

    def action_start_break(self) -> None:
        """Start a break session."""
        self.state = TimerState.BREAK
        self.remaining_seconds = self.break_duration
        self.end_time = time.time() + self.break_duration

        # Start periodic updates
        if self.update_timer_handle:
            self.update_timer_handle.stop()
        self.update_timer_handle = self.set_interval(1, self.update_timer)

        self.refresh_display()

    def action_stop_timer(self) -> None:
        """Stop the current timer."""
        if self.update_timer_handle:
            self.update_timer_handle.stop()
            self.update_timer_handle = None

        self.state = TimerState.IDLE
        self.remaining_seconds = 0
        self.end_time = 0
        self.refresh_display()

    def stop_timer(self) -> None:
        """Stop timer (called when countdown reaches zero)."""
        self.action_stop_timer()
        # TODO: Implement notification based on config.notification_enabled

    def update_config(self, new_config: TimerConfig) -> None:
        """Update the timer configuration and apply changes.

        Args:
            new_config: New timer configuration
        """
        self.config = new_config

        # Update durations (convert minutes to seconds)
        self.focus_duration = self.config.focus_duration * 60
        self.break_duration = self.config.break_duration * 60

        # Refresh display to show new durations
        self.refresh_display()
