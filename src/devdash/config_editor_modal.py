"""
Configuration editor modal - TUI interface for editing DevDash configuration.
"""

from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static, Switch, Select, TabbedContent, TabPane
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding

from devdash.config import ConfigLoader, DevDashConfig, ConfigValidator


class ConfigEditorModal(ModalScreen):
    """Modal screen for editing DevDash configuration."""

    CSS = """
    ConfigEditorModal {
        align: center middle;
    }

    #config-dialog {
        width: 90;
        height: 55;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #config-title {
        width: 100%;
        text-align: center;
        background: $primary;
        color: $text;
        padding: 1;
        text-style: bold;
    }

    #config-tabs {
        width: 100%;
        height: 38;
        margin: 0;
    }

    TabbedContent {
        height: 100%;
    }

    TabbedContent ContentSwitcher {
        height: 100%;
    }

    TabPane {
        padding: 0;
        height: 100%;
    }

    .tab-content {
        width: 100%;
        height: 100%;
        padding: 1;
        overflow-y: auto;
    }

    .config-section {
        padding: 1;
        height: auto;
        width: 100%;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        height: auto;
    }

    .config-row {
        height: auto;
        min-height: 3;
        margin: 0 0 1 0;
        layout: horizontal;
    }

    .config-label {
        width: 35%;
        padding: 1;
        height: auto;
    }

    .config-input {
        width: 65%;
        height: auto;
    }

    .instructions {
        padding: 1;
        margin: 0 0 1 0;
        background: $boost;
        border: solid yellow;
    }

    Input {
        width: 100%;
        height: auto;
        min-height: 3;
        border: tall $accent;
        background: $surface;
        color: $text;
    }

    Input:focus {
        border: tall cyan;
        background: $boost;
    }

    Input:hover {
        border: tall green;
        background: $surface-lighten-1;
    }

    Switch {
        width: auto;
        height: auto;
        background: $surface;
    }

    Switch:focus {
        background: $boost;
    }

    Select {
        width: 100%;
        height: auto;
        min-height: 3;
        border: tall $accent;
        background: $surface;
    }

    Select:focus {
        border: tall cyan;
        background: $boost;
    }

    #button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin: 1 0;
    }

    Button {
        margin: 0 1;
    }

    #status-message {
        width: 100%;
        text-align: center;
        height: auto;
        min-height: 1;
        margin: 0;
        padding: 0 1;
    }

    #status-message.success {
        background: green;
        color: white;
    }

    #status-message.error {
        background: red;
        color: white;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=True),
        Binding("ctrl+s", "save", "Save", show=True),
        ("tab", "focus_next", "Next field"),
        ("shift+tab", "focus_previous", "Previous field"),
    ]

    def __init__(self, config: DevDashConfig, config_path: Optional[Path] = None):
        """Initialize the config editor modal.

        Args:
            config: Current configuration
            config_path: Path to save config file (None = discover or use default)
        """
        super().__init__()
        self.config = config
        self.config_path = config_path

    def compose(self) -> ComposeResult:
        """Compose the config editor UI."""
        with Container(id="config-dialog"):
            yield Static("⚙ Configuration Editor [dim](Click tabs to switch panels)[/]", id="config-title")

            # Buttons at top
            with Horizontal(id="button-row"):
                yield Button("Save (Ctrl+S)", variant="primary", id="save-button")
                yield Button("Cancel (Esc)", variant="default", id="cancel-button")

            # Status message area
            yield Static("", id="status-message")

            with TabbedContent(id="config-tabs"):
                # Git Panel Tab
                with TabPane("Git", id="git-tab"):
                    with Container(classes="tab-content"):
                        yield Static("━━━ [bold cyan]Git Panel[/] ━━━", classes="section-title")

                        with Horizontal(classes="config-row"):
                            yield Static("Enabled:", classes="config-label")
                            yield Switch(
                                value=self.config.git.enabled,
                                id="git_enabled"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Refresh Interval (s):", classes="config-label")
                            yield Input(
                                value=str(self.config.git.refresh_interval),
                                placeholder="5",
                                id="git_refresh_interval",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Max Commits:", classes="config-label")
                            yield Input(
                                value=str(self.config.git.max_commits),
                                placeholder="3",
                                id="git_max_commits",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Staged:", classes="config-label")
                            yield Switch(
                                value=self.config.git.show_staged,
                                id="git_show_staged"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Modified:", classes="config-label")
                            yield Switch(
                                value=self.config.git.show_modified,
                                id="git_show_modified"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Untracked:", classes="config-label")
                            yield Switch(
                                value=self.config.git.show_untracked,
                                id="git_show_untracked"
                            )

                # System Panel Tab
                with TabPane("System", id="system-tab"):
                    with Container(classes="tab-content"):
                        yield Static("━━━ [bold green]System Panel[/] ━━━", classes="section-title")

                        with Horizontal(classes="config-row"):
                            yield Static("Enabled:", classes="config-label")
                            yield Switch(
                                value=self.config.system.enabled,
                                id="system_enabled"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Refresh Interval (s):", classes="config-label")
                            yield Input(
                                value=str(self.config.system.refresh_interval),
                                placeholder="1",
                                id="system_refresh_interval",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show CPU:", classes="config-label")
                            yield Switch(
                                value=self.config.system.show_cpu,
                                id="system_show_cpu"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show RAM:", classes="config-label")
                            yield Switch(
                                value=self.config.system.show_ram,
                                id="system_show_ram"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Disk:", classes="config-label")
                            yield Switch(
                                value=self.config.system.show_disk,
                                id="system_show_disk"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Uptime:", classes="config-label")
                            yield Switch(
                                value=self.config.system.show_uptime,
                                id="system_show_uptime"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Load Average:", classes="config-label")
                            yield Switch(
                                value=self.config.system.show_load_avg,
                                id="system_show_load_avg"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("CPU Warning %:", classes="config-label")
                            yield Input(
                                value=str(self.config.system.cpu_warning_threshold),
                                placeholder="60.0",
                                id="system_cpu_warning",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("CPU Critical %:", classes="config-label")
                            yield Input(
                                value=str(self.config.system.cpu_critical_threshold),
                                placeholder="80.0",
                                id="system_cpu_critical",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("RAM Warning %:", classes="config-label")
                            yield Input(
                                value=str(self.config.system.ram_warning_threshold),
                                placeholder="60.0",
                                id="system_ram_warning",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("RAM Critical %:", classes="config-label")
                            yield Input(
                                value=str(self.config.system.ram_critical_threshold),
                                placeholder="80.0",
                                id="system_ram_critical",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Disk Warning %:", classes="config-label")
                            yield Input(
                                value=str(self.config.system.disk_warning_threshold),
                                placeholder="60.0",
                                id="system_disk_warning",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Disk Critical %:", classes="config-label")
                            yield Input(
                                value=str(self.config.system.disk_critical_threshold),
                                placeholder="80.0",
                                id="system_disk_critical",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Progress Bar Width:", classes="config-label")
                            yield Input(
                                value=str(self.config.system.progress_bar_width),
                                placeholder="10",
                                id="system_progress_width",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Progress Bar Style:", classes="config-label")
                            yield Select.from_values(
                                ["blocks", "bars", "dots"],
                                value=self.config.system.progress_bar_style,
                                allow_blank=False,
                                id="system_progress_style"
                            )

                # Tasks Panel Tab
                with TabPane("Tasks", id="tasks-tab"):
                    with Container(classes="tab-content"):
                        yield Static("━━━ [bold yellow]Tasks Panel[/] ━━━", classes="section-title")

                        with Horizontal(classes="config-row"):
                            yield Static("Enabled:", classes="config-label")
                            yield Switch(
                                value=self.config.tasks.enabled,
                                id="tasks_enabled"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("File Path:", classes="config-label")
                            yield Input(
                                value=self.config.tasks.file_path,
                                placeholder=".devdash_tasks.json",
                                id="tasks_file_path",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Default Sort:", classes="config-label")
                            yield Select.from_values(
                                ["created", "priority", "due_date", "text"],
                                value=self.config.tasks.default_sort,
                                allow_blank=False,
                                id="tasks_default_sort"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Completed:", classes="config-label")
                            yield Switch(
                                value=self.config.tasks.show_completed,
                                id="tasks_show_completed"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Max Visible Tasks:", classes="config-label")
                            yield Input(
                                value=str(self.config.tasks.max_visible_tasks),
                                placeholder="20",
                                id="tasks_max_visible",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Truncate Length:", classes="config-label")
                            yield Input(
                                value=str(self.config.tasks.truncate_length),
                                placeholder="40",
                                id="tasks_truncate_length",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Categories:", classes="config-label")
                            yield Switch(
                                value=self.config.tasks.show_categories,
                                id="tasks_show_categories"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Due Dates:", classes="config-label")
                            yield Switch(
                                value=self.config.tasks.show_due_dates,
                                id="tasks_show_due_dates"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Priority Emoji:", classes="config-label")
                            yield Switch(
                                value=self.config.tasks.show_priority_emoji,
                                id="tasks_show_priority_emoji"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Due Soon Days:", classes="config-label")
                            yield Input(
                                value=str(self.config.tasks.due_soon_days),
                                placeholder="3",
                                id="tasks_due_soon_days",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Export Format:", classes="config-label")
                            yield Select.from_values(
                                ["grouped", "simple", "detailed"],
                                value=self.config.tasks.export_format,
                                allow_blank=False,
                                id="tasks_export_format"
                            )

                # Timer Panel Tab
                with TabPane("Timer", id="timer-tab"):
                    with Container(classes="tab-content"):
                        yield Static("━━━ [bold red]Timer Panel[/] ━━━", classes="section-title")

                        with Horizontal(classes="config-row"):
                            yield Static("Enabled:", classes="config-label")
                            yield Switch(
                                value=self.config.timer.enabled,
                                id="timer_enabled"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Focus Duration (min):", classes="config-label")
                            yield Input(
                                value=str(self.config.timer.focus_duration),
                                placeholder="25",
                                id="timer_focus_duration",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Break Duration (min):", classes="config-label")
                            yield Input(
                                value=str(self.config.timer.break_duration),
                                placeholder="5",
                                id="timer_break_duration",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Long Break Duration (min):", classes="config-label")
                            yield Input(
                                value=str(self.config.timer.long_break_duration),
                                placeholder="15",
                                id="timer_long_break_duration",
                                classes="config-input"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Auto Start Break:", classes="config-label")
                            yield Switch(
                                value=self.config.timer.auto_start_break,
                                id="timer_auto_start_break"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Show Progress Bar:", classes="config-label")
                            yield Switch(
                                value=self.config.timer.show_progress_bar,
                                id="timer_show_progress_bar"
                            )

                        with Horizontal(classes="config-row"):
                            yield Static("Progress Bar Width:", classes="config-label")
                            yield Input(
                                value=str(self.config.timer.progress_bar_width),
                                placeholder="20",
                                id="timer_progress_width",
                                classes="config-input"
                            )

    def _show_status(self, message: str, error: bool = False) -> None:
        """Show a status message.

        Args:
            message: Message to display
            error: If True, show as error (red), otherwise success (green)
        """
        status_widget = self.query_one("#status-message", Static)
        status_widget.update(message)
        if error:
            status_widget.add_class("error")
            status_widget.remove_class("success")
        else:
            status_widget.add_class("success")
            status_widget.remove_class("error")

    def _get_input_value(self, input_id: str) -> str:
        """Get value from an input field.

        Args:
            input_id: ID of the input field

        Returns:
            The input value as a string
        """
        return self.query_one(f"#{input_id}", Input).value

    def _get_switch_value(self, switch_id: str) -> bool:
        """Get value from a switch widget.

        Args:
            switch_id: ID of the switch widget

        Returns:
            The switch value as a boolean
        """
        return self.query_one(f"#{switch_id}", Switch).value

    def _get_select_value(self, select_id: str) -> str:
        """Get value from a select widget.

        Args:
            select_id: ID of the select widget

        Returns:
            The select value as a string
        """
        return str(self.query_one(f"#{select_id}", Select).value)

    def _save_config(self) -> None:
        """Save the configuration to file."""
        try:
            # Build updated config from input values
            # Git
            git_enabled = self._get_switch_value("git_enabled")
            git_refresh = int(self._get_input_value("git_refresh_interval"))
            git_commits = int(self._get_input_value("git_max_commits"))
            git_show_staged = self._get_switch_value("git_show_staged")
            git_show_modified = self._get_switch_value("git_show_modified")
            git_show_untracked = self._get_switch_value("git_show_untracked")

            # System
            system_enabled = self._get_switch_value("system_enabled")
            system_refresh = int(self._get_input_value("system_refresh_interval"))
            system_show_cpu = self._get_switch_value("system_show_cpu")
            system_show_ram = self._get_switch_value("system_show_ram")
            system_show_disk = self._get_switch_value("system_show_disk")
            system_show_uptime = self._get_switch_value("system_show_uptime")
            system_show_load_avg = self._get_switch_value("system_show_load_avg")
            cpu_warning = float(self._get_input_value("system_cpu_warning"))
            cpu_critical = float(self._get_input_value("system_cpu_critical"))
            ram_warning = float(self._get_input_value("system_ram_warning"))
            ram_critical = float(self._get_input_value("system_ram_critical"))
            disk_warning = float(self._get_input_value("system_disk_warning"))
            disk_critical = float(self._get_input_value("system_disk_critical"))
            system_progress_width = int(self._get_input_value("system_progress_width"))
            system_progress_style = self._get_select_value("system_progress_style")

            # Tasks
            tasks_enabled = self._get_switch_value("tasks_enabled")
            tasks_file = self._get_input_value("tasks_file_path")
            tasks_sort = self._get_select_value("tasks_default_sort")
            tasks_show_completed = self._get_switch_value("tasks_show_completed")
            tasks_max = int(self._get_input_value("tasks_max_visible"))
            tasks_truncate = int(self._get_input_value("tasks_truncate_length"))
            tasks_show_categories = self._get_switch_value("tasks_show_categories")
            tasks_show_due_dates = self._get_switch_value("tasks_show_due_dates")
            tasks_show_priority_emoji = self._get_switch_value("tasks_show_priority_emoji")
            tasks_due_soon_days = int(self._get_input_value("tasks_due_soon_days"))
            tasks_export_format = self._get_select_value("tasks_export_format")

            # Timer
            timer_enabled = self._get_switch_value("timer_enabled")
            timer_focus = int(self._get_input_value("timer_focus_duration"))
            timer_break = int(self._get_input_value("timer_break_duration"))
            timer_long_break = int(self._get_input_value("timer_long_break_duration"))
            timer_auto_start_break = self._get_switch_value("timer_auto_start_break")
            timer_show_progress_bar = self._get_switch_value("timer_show_progress_bar")
            timer_progress = int(self._get_input_value("timer_progress_width"))

            # Validate values
            errors = []

            if git_refresh < 1:
                errors.append("Git refresh interval must be >= 1")
            if git_commits < 0 or git_commits > 20:
                errors.append("Git max commits must be 0-20")

            if system_refresh < 1:
                errors.append("System refresh interval must be >= 1")
            if cpu_warning < 0 or cpu_warning > 100:
                errors.append("CPU warning threshold must be 0-100")
            if cpu_critical < 0 or cpu_critical > 100:
                errors.append("CPU critical threshold must be 0-100")
            if cpu_warning >= cpu_critical:
                errors.append("CPU warning must be less than critical")
            if ram_warning < 0 or ram_warning > 100:
                errors.append("RAM warning threshold must be 0-100")
            if ram_critical < 0 or ram_critical > 100:
                errors.append("RAM critical threshold must be 0-100")
            if ram_warning >= ram_critical:
                errors.append("RAM warning must be less than critical")
            if disk_warning < 0 or disk_warning > 100:
                errors.append("Disk warning threshold must be 0-100")
            if disk_critical < 0 or disk_critical > 100:
                errors.append("Disk critical threshold must be 0-100")
            if disk_warning >= disk_critical:
                errors.append("Disk warning must be less than critical")

            if tasks_max < 1:
                errors.append("Max visible tasks must be >= 1")
            if tasks_sort not in ["created", "priority", "due_date", "text"]:
                errors.append("Invalid sort option")
            if tasks_export_format not in ["grouped", "simple", "detailed"]:
                errors.append("Invalid export format")

            if timer_focus < 1:
                errors.append("Focus duration must be >= 1")
            if timer_break < 1:
                errors.append("Break duration must be >= 1")
            if timer_long_break < 1:
                errors.append("Long break duration must be >= 1")

            if errors:
                self._show_status(f"Validation errors: {', '.join(errors)}", error=True)
                return

            # Determine config file path
            if self.config_path:
                config_file = self.config_path
            else:
                loader = ConfigLoader()
                found = loader.find_config_file()
                if found:
                    config_file = found
                else:
                    # Create in current directory
                    config_file = Path.cwd() / ".devdash.toml"

            # Build TOML content
            toml_content = f"""# DevDash Configuration
# Generated by DevDash Config Editor

[git]
enabled = {str(git_enabled).lower()}
refresh_interval = {git_refresh}
max_commits = {git_commits}
show_staged = {str(git_show_staged).lower()}
show_modified = {str(git_show_modified).lower()}
show_untracked = {str(git_show_untracked).lower()}

[system]
enabled = {str(system_enabled).lower()}
refresh_interval = {system_refresh}
show_cpu = {str(system_show_cpu).lower()}
show_ram = {str(system_show_ram).lower()}
show_disk = {str(system_show_disk).lower()}
show_uptime = {str(system_show_uptime).lower()}
show_load_avg = {str(system_show_load_avg).lower()}
cpu_warning_threshold = {cpu_warning}
cpu_critical_threshold = {cpu_critical}
ram_warning_threshold = {ram_warning}
ram_critical_threshold = {ram_critical}
disk_warning_threshold = {disk_warning}
disk_critical_threshold = {disk_critical}
progress_bar_width = {system_progress_width}
progress_bar_style = "{system_progress_style}"

[tasks]
enabled = {str(tasks_enabled).lower()}
file_path = "{tasks_file}"
default_sort = "{tasks_sort}"
show_completed = {str(tasks_show_completed).lower()}
max_visible_tasks = {tasks_max}
truncate_length = {tasks_truncate}
show_categories = {str(tasks_show_categories).lower()}
show_due_dates = {str(tasks_show_due_dates).lower()}
show_priority_emoji = {str(tasks_show_priority_emoji).lower()}
due_soon_days = {tasks_due_soon_days}
export_format = "{tasks_export_format}"

[timer]
enabled = {str(timer_enabled).lower()}
focus_duration = {timer_focus}
break_duration = {timer_break}
long_break_duration = {timer_long_break}
auto_start_break = {str(timer_auto_start_break).lower()}
notification_enabled = false
notification_sound = "bell"
show_progress_bar = {str(timer_show_progress_bar).lower()}
progress_bar_width = {timer_progress}

[ui]
border_style = "{self.config.ui.border_style}"
panel_padding = {self.config.ui.panel_padding}
show_footer = true
show_header = true
compact_view = false
"""

            # Write to file
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                f.write(toml_content)

            # Dismiss with True to trigger hot-reload in main app
            # Do this immediately without showing status message
            self.dismiss(True)

        except ValueError as e:
            self._show_status(f"Invalid input: {e}", error=True)
        except Exception as e:
            self._show_status(f"Error saving config: {e}", error=True)

    def action_save(self) -> None:
        """Save the configuration."""
        self._save_config()

    def action_cancel(self) -> None:
        """Cancel and close the modal."""
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "save-button":
            self.action_save()
        elif event.button.id == "cancel-button":
            self.action_cancel()

    def on_mount(self) -> None:
        """Focus first tab when modal opens."""
        # TabbedContent handles focus automatically
        pass
