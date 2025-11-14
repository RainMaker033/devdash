"""
System panel widget - displays system resource metrics
"""

import time
from pathlib import Path
from typing import Optional
from datetime import timedelta

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from textual.reactive import reactive

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from devdash.config.schema import SystemConfig


class SystemPanel(Container):
    """Widget displaying system resource metrics."""

    DEFAULT_CSS = """
    SystemPanel {
        border: solid $success;
        padding: 1;
        height: auto;
    }

    SystemPanel .panel-title {
        background: $success;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }

    SystemPanel .panel-content {
        padding: 1;
    }
    """

    system_content = reactive("")

    def __init__(self, config: Optional[SystemConfig] = None, *args, **kwargs):
        """Initialize System panel.

        Args:
            config: System panel configuration. If None, uses defaults.
        """
        super().__init__(*args, **kwargs)
        self.config = config or SystemConfig()
        self.content_widget: Optional[Static] = None
        self.start_time = time.time()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("System Resources", classes="panel-title")
        self.content_widget = Static("", classes="panel-content")
        yield self.content_widget

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        if not self.config.enabled:
            self.system_content = "[dim]System panel disabled in configuration[/]"
            return

        self.refresh_data()
        # Set up periodic refresh using configured interval
        self.set_interval(self.config.refresh_interval, self.refresh_data)

    def watch_system_content(self, new_content: str) -> None:
        """Update content when system_content changes."""
        if self.content_widget:
            self.content_widget.update(new_content)

    def _create_progress_bar(
        self,
        percentage: float,
        width: int = 10,
        warning_threshold: float = 60.0,
        critical_threshold: float = 80.0
    ) -> tuple[str, str]:
        """Create a visual progress bar with configurable thresholds.

        Args:
            percentage: The percentage value (0-100)
            width: Width of the progress bar in characters
            warning_threshold: Percentage for warning (yellow) color
            critical_threshold: Percentage for critical (red) color

        Returns:
            Tuple of (bar string, color name)
        """
        filled = int((percentage / 100) * width)
        empty = width - filled

        # Color based on percentage and thresholds
        if percentage >= critical_threshold:
            color = "red"
        elif percentage >= warning_threshold:
            color = "yellow"
        else:
            color = "green"

        bar = f"[{color}]{'█' * filled}[/]{'░' * empty}"
        return bar, color

    def _format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        td = timedelta(seconds=int(seconds))
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if td.days > 0:
            return f"{td.days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"

    def refresh_data(self) -> None:
        """Refresh system metrics."""
        if not PSUTIL_AVAILABLE:
            self.system_content = "[red]psutil not available[/]"
            return

        try:
            content_lines = []

            # Get CPU usage (with interval for accuracy)
            if self.config.show_cpu:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_bar, _ = self._create_progress_bar(
                    cpu_percent,
                    width=self.config.progress_bar_width,
                    warning_threshold=self.config.cpu_warning_threshold,
                    critical_threshold=self.config.cpu_critical_threshold
                )
                content_lines.append(f"[bold cyan]CPU:[/]  {cpu_bar} {cpu_percent:.1f}%")

            # Get RAM usage
            if self.config.show_ram:
                ram = psutil.virtual_memory()
                ram_bar, _ = self._create_progress_bar(
                    ram.percent,
                    width=self.config.progress_bar_width,
                    warning_threshold=self.config.ram_warning_threshold,
                    critical_threshold=self.config.ram_critical_threshold
                )
                ram_used = self._format_bytes(ram.used)
                ram_total = self._format_bytes(ram.total)
                content_lines.append(f"[bold cyan]RAM:[/]  {ram_bar} {ram.percent:.1f}%")
                content_lines.append(f"         {ram_used} / {ram_total}")

            # Get disk usage for current directory
            if self.config.show_disk:
                disk = psutil.disk_usage(str(Path.cwd()))
                disk_bar, _ = self._create_progress_bar(
                    disk.percent,
                    width=self.config.progress_bar_width,
                    warning_threshold=self.config.disk_warning_threshold,
                    critical_threshold=self.config.disk_critical_threshold
                )
                disk_used = self._format_bytes(disk.used)
                disk_total = self._format_bytes(disk.total)
                content_lines.append(f"[bold cyan]Disk:[/] {disk_bar} {disk.percent:.1f}%")
                content_lines.append(f"         {disk_used} / {disk_total}")

            # Session uptime
            if self.config.show_uptime:
                if content_lines:
                    content_lines.append("")
                uptime = self._format_uptime(time.time() - self.start_time)
                content_lines.append(f"[dim]Session:[/] {uptime}")

            # Load average (if available on this platform)
            if self.config.show_load_avg:
                try:
                    load_avg = psutil.getloadavg()
                    load_text = f"[dim]Load:[/] {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
                    content_lines.append(load_text)
                except (AttributeError, OSError):
                    # getloadavg not available on Windows
                    pass

            self.system_content = "\n".join(content_lines) if content_lines else "[dim]No metrics enabled[/]"

        except Exception as e:
            self.system_content = f"[red]Error:[/]\n{str(e)}"

    def update_config(self, new_config: SystemConfig) -> None:
        """Update the system configuration and apply changes.

        Args:
            new_config: New system configuration
        """
        old_interval = self.config.refresh_interval
        self.config = new_config

        # If refresh interval changed, restart the timer
        if old_interval != new_config.refresh_interval and self.config.enabled:
            # Clear old interval and set new one
            self.set_interval(self.config.refresh_interval, self.refresh_data, name="system_refresh")

        # Refresh display immediately with new settings
        self.refresh_data()
