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
from textual.timer import Timer

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
        self.update_timer_handle: Optional[Timer] = None

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
        self._apply_visibility()
        if not self.config.enabled:
            self._reset_timer_state(refresh=False)
            return
        self.refresh_display()

    def on_unmount(self) -> None:
        """Stop timers when widget is removed."""
        self._stop_update_timer()

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
        if not self.config.enabled:
            return

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
        if not self.config.enabled or self.state == TimerState.IDLE:
            return

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
        if not self._interactions_enabled():
            return
        self.state = TimerState.FOCUS
        self.remaining_seconds = self.focus_duration
        self.end_time = time.time() + self.focus_duration

        # Start periodic updates
        self._stop_update_timer()
        self.update_timer_handle = self.set_interval(1, self.update_timer)

        self.refresh_display()

    def action_start_break(self) -> None:
        """Start a break session."""
        if not self._interactions_enabled():
            return
        self.state = TimerState.BREAK
        self.remaining_seconds = self.break_duration
        self.end_time = time.time() + self.break_duration

        # Start periodic updates
        self._stop_update_timer()
        self.update_timer_handle = self.set_interval(1, self.update_timer)

        self.refresh_display()

    def action_stop_timer(self) -> None:
        """Stop the current timer."""
        if not self._interactions_enabled():
            return
        self._reset_timer_state()

    def stop_timer(self) -> None:
        """Stop timer (called when countdown reaches zero)."""
        self._reset_timer_state()
        # TODO: Implement notification based on config.notification_enabled

    def update_config(self, new_config: TimerConfig) -> None:
        """Update the timer configuration and apply changes.

        Args:
            new_config: New timer configuration
        """
        was_enabled = self.config.enabled
        self.config = new_config
        self._apply_visibility()

        # Update durations (convert minutes to seconds)
        self.focus_duration = self.config.focus_duration * 60
        self.break_duration = self.config.break_duration * 60

        if not self.config.enabled:
            self._reset_timer_state(refresh=False)
            return

        if not was_enabled and self.config.enabled:
            self._reset_timer_state(refresh=False)

        # Refresh display to show new durations
        self.refresh_display()

    def _apply_visibility(self) -> None:
        """Show or hide the panel based on configuration."""
        self.display = self.config.enabled

    def _interactions_enabled(self) -> bool:
        """Return True if timer interactions are allowed."""
        return self.config.enabled

    def _stop_update_timer(self) -> None:
        """Stop the interval timer if running."""
        if self.update_timer_handle:
            self.update_timer_handle.stop()
            self.update_timer_handle = None

    def _reset_timer_state(self, refresh: bool = True) -> None:
        """Reset timer state and optionally refresh display."""
        self._stop_update_timer()
        self.state = TimerState.IDLE
        self.remaining_seconds = 0
        self.end_time = 0
        if refresh and self.config.enabled:
            self.refresh_display()
