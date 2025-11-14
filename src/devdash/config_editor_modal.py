"""
Configuration editor modal - TUI interface for editing DevDash configuration.
"""

from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
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
        height: 45;
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

    #config-content {
        width: 100%;
        height: 30;
        border: solid $accent;
        margin: 1 0;
    }

    VerticalScroll {
        height: 100%;
        scrollbar-size: 1 1;
    }

    VerticalScroll:focus {
        border: heavy $accent;
    }

    .config-section {
        border: solid $accent;
        padding: 1;
        margin: 1 0;
        height: auto;
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

    #button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }

    #status-message {
        width: 100%;
        text-align: center;
        height: auto;
        margin-top: 1;
        padding: 1;
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
            yield Static("⚙ Configuration Editor [dim](Use mouse wheel or Tab to navigate)[/]", id="config-title")

            with VerticalScroll(id="config-content"):
                # Instructions
                yield Static(
                    "[yellow]→ Click on any field below to edit it[/]\n"
                    "[dim]Fields have borders around them - look for the boxes on the right side[/]",
                    classes="instructions"
                )

                # Git Configuration
                with Vertical(classes="config-section"):
                    yield Static("━━━ [bold cyan]Git Panel[/] ━━━", classes="section-title")

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

                # System Configuration
                with Vertical(classes="config-section"):
                    yield Static("━━━ [bold green]System Panel[/] ━━━", classes="section-title")

                    with Horizontal(classes="config-row"):
                        yield Static("Refresh Interval (s):", classes="config-label")
                        yield Input(
                            value=str(self.config.system.refresh_interval),
                            placeholder="1",
                            id="system_refresh_interval",
                            classes="config-input"
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
                        yield Static("Progress Bar Width:", classes="config-label")
                        yield Input(
                            value=str(self.config.system.progress_bar_width),
                            placeholder="10",
                            id="system_progress_width",
                            classes="config-input"
                        )

                # Tasks Configuration
                with Vertical(classes="config-section"):
                    yield Static("━━━ [bold yellow]Tasks Panel[/] ━━━", classes="section-title")

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
                        yield Input(
                            value=self.config.tasks.default_sort,
                            placeholder="created",
                            id="tasks_default_sort",
                            classes="config-input"
                        )

                    with Horizontal(classes="config-row"):
                        yield Static("Max Visible Tasks:", classes="config-label")
                        yield Input(
                            value=str(self.config.tasks.max_visible_tasks),
                            placeholder="20",
                            id="tasks_max_visible",
                            classes="config-input"
                        )

                # Timer Configuration
                with Vertical(classes="config-section"):
                    yield Static("━━━ [bold red]Timer Panel[/] ━━━", classes="section-title")

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
                        yield Static("Progress Bar Width:", classes="config-label")
                        yield Input(
                            value=str(self.config.timer.progress_bar_width),
                            placeholder="20",
                            id="timer_progress_width",
                            classes="config-input"
                        )

            # Status message area
            yield Static("", id="status-message")

            # Buttons
            with Horizontal(id="button-row"):
                yield Button("Save (Ctrl+S)", variant="primary", id="save-button")
                yield Button("Cancel (Esc)", variant="default", id="cancel-button")

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

    def _save_config(self) -> None:
        """Save the configuration to file."""
        try:
            # Build updated config from input values
            # Git
            git_refresh = int(self._get_input_value("git_refresh_interval"))
            git_commits = int(self._get_input_value("git_max_commits"))

            # System
            system_refresh = int(self._get_input_value("system_refresh_interval"))
            cpu_warning = float(self._get_input_value("system_cpu_warning"))
            cpu_critical = float(self._get_input_value("system_cpu_critical"))
            progress_width = int(self._get_input_value("system_progress_width"))

            # Tasks
            tasks_file = self._get_input_value("tasks_file_path")
            tasks_sort = self._get_input_value("tasks_default_sort")
            tasks_max = int(self._get_input_value("tasks_max_visible"))

            # Timer
            timer_focus = int(self._get_input_value("timer_focus_duration"))
            timer_break = int(self._get_input_value("timer_break_duration"))
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

            if tasks_max < 1:
                errors.append("Max visible tasks must be >= 1")
            if tasks_sort not in ["created", "priority", "due_date", "text"]:
                errors.append("Invalid sort option")

            if timer_focus < 1:
                errors.append("Focus duration must be >= 1")
            if timer_break < 1:
                errors.append("Break duration must be >= 1")

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
enabled = true
refresh_interval = {git_refresh}
max_commits = {git_commits}
show_staged = true
show_modified = true
show_untracked = true

[system]
enabled = true
refresh_interval = {system_refresh}
show_cpu = true
show_ram = true
show_disk = true
show_uptime = true
show_load_avg = true
cpu_warning_threshold = {cpu_warning}
cpu_critical_threshold = {cpu_critical}
ram_warning_threshold = {self.config.system.ram_warning_threshold}
ram_critical_threshold = {self.config.system.ram_critical_threshold}
disk_warning_threshold = {self.config.system.disk_warning_threshold}
disk_critical_threshold = {self.config.system.disk_critical_threshold}
progress_bar_width = {progress_width}
progress_bar_style = "{self.config.system.progress_bar_style}"

[tasks]
enabled = true
file_path = "{tasks_file}"
default_sort = "{tasks_sort}"
show_completed = {str(self.config.tasks.show_completed).lower()}
max_visible_tasks = {tasks_max}
truncate_length = {self.config.tasks.truncate_length}
show_categories = true
show_due_dates = true
show_priority_emoji = true
due_soon_days = {self.config.tasks.due_soon_days}
export_format = "{self.config.tasks.export_format}"

[timer]
enabled = true
focus_duration = {timer_focus}
break_duration = {timer_break}
long_break_duration = {self.config.timer.long_break_duration}
auto_start_break = {str(self.config.timer.auto_start_break).lower()}
notification_enabled = false
notification_sound = "{self.config.timer.notification_sound}"
show_progress_bar = {str(self.config.timer.show_progress_bar).lower()}
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
        """Focus scroll container when modal opens."""
        # Focus the scroll container so it can receive scroll events
        try:
            scroll = self.query_one(VerticalScroll)
            scroll.can_focus = True
            scroll.focus()
        except Exception:
            pass
