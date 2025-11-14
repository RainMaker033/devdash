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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_widget: Optional[Static] = None
        self.start_time = time.time()

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("System Resources", classes="panel-title")
        self.content_widget = Static("", classes="panel-content")
        yield self.content_widget

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.refresh_data()
        # Set up periodic refresh every 1 second
        self.set_interval(1, self.refresh_data)

    def watch_system_content(self, new_content: str) -> None:
        """Update content when system_content changes."""
        if self.content_widget:
            self.content_widget.update(new_content)

    def _create_progress_bar(self, percentage: float, width: int = 10) -> tuple[str, str]:
        """Create a visual progress bar."""
        filled = int((percentage / 100) * width)
        empty = width - filled

        # Color based on percentage
        if percentage >= 80:
            color = "red"
        elif percentage >= 60:
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
            # Get CPU usage (with interval for accuracy)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_bar, _ = self._create_progress_bar(cpu_percent)

            # Get RAM usage
            ram = psutil.virtual_memory()
            ram_bar, _ = self._create_progress_bar(ram.percent)
            ram_used = self._format_bytes(ram.used)
            ram_total = self._format_bytes(ram.total)

            # Get disk usage for current directory
            disk = psutil.disk_usage(str(Path.cwd()))
            disk_bar, _ = self._create_progress_bar(disk.percent)
            disk_used = self._format_bytes(disk.used)
            disk_total = self._format_bytes(disk.total)

            # Session uptime
            uptime = self._format_uptime(time.time() - self.start_time)

            # Load average (if available on this platform)
            try:
                load_avg = psutil.getloadavg()
                load_text = f"[dim]Load:[/] {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
            except (AttributeError, OSError):
                # getloadavg not available on Windows
                load_text = ""

            # Build content
            content_lines = [
                f"[bold cyan]CPU:[/]  {cpu_bar} {cpu_percent:.1f}%",
                f"[bold cyan]RAM:[/]  {ram_bar} {ram.percent:.1f}%",
                f"         {ram_used} / {ram_total}",
                f"[bold cyan]Disk:[/] {disk_bar} {disk.percent:.1f}%",
                f"         {disk_used} / {disk_total}",
                "",
                f"[dim]Session:[/] {uptime}",
            ]

            if load_text:
                content_lines.append(load_text)

            self.system_content = "\n".join(content_lines)

        except Exception as e:
            self.system_content = f"[red]Error:[/]\n{str(e)}"
