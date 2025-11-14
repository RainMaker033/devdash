"""
Main entry point for devdash application.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.containers import Container, Horizontal, Vertical

from devdash.git_panel import GitPanel
from devdash.system_panel import SystemPanel
from devdash.tasks_panel import TasksPanel
from devdash.timer_panel import TimerPanel
from devdash.help_modal import HelpModal
from devdash.config_editor_modal import ConfigEditorModal
from devdash.config import (
    load_config,
    DevDashConfig,
    ConfigLoadError,
    ConfigLoader,
    ConfigValidator,
    get_default_config,
)


class DevDashApp(App):
    """A terminal dashboard for developers."""

    def __init__(self, config: Optional[DevDashConfig] = None):
        """Initialize the DevDash application.

        Args:
            config: Configuration object. If None, loads from default locations.
        """
        super().__init__()
        self.config = config or self._load_config_with_fallback()

    def _load_config_with_fallback(self) -> DevDashConfig:
        """Load configuration with error handling.

        Returns:
            DevDashConfig: Loaded configuration or defaults if loading fails
        """
        try:
            return load_config()
        except ConfigLoadError as e:
            # Log error but continue with defaults
            print(f"Warning: {e}", file=sys.stderr)
            print("Using default configuration.", file=sys.stderr)
            from devdash.config import get_default_config
            return get_default_config()

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
        ("c", "config", "Config"),
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
                yield GitPanel(config=self.config.git, classes="panel-half")
                yield SystemPanel(config=self.config.system, classes="panel-half")

            # Bottom row: Tasks (left) and Timer (right)
            with Horizontal(id="bottom-panels"):
                yield TasksPanel(config=self.config.tasks, classes="panel-half")
                yield TimerPanel(config=self.config.timer, classes="panel-half")

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

    def action_config(self) -> None:
        """Show configuration editor."""
        loader = ConfigLoader()
        config_path = loader.find_config_file()

        def handle_config_result(result) -> None:
            """Handle config editor result."""
            if result is True:
                # Reload and apply the new configuration
                self.reload_config()
            elif result is False:
                self.notify("Configuration changes cancelled", severity="information", timeout=1)

        self.push_screen(
            ConfigEditorModal(self.config, config_path),
            handle_config_result
        )

    def reload_config(self) -> None:
        """Reload configuration from file and apply to all panels."""
        try:
            # Reload config from file
            new_config = load_config()

            # Validate it
            warnings = ConfigValidator.validate_config(new_config)
            if warnings:
                # Show warnings but continue
                for warning in warnings:
                    self.notify(f"Config warning: {warning}", severity="warning", timeout=3)

            # Update app config
            self.config = new_config

            # Update each panel with new config
            git_panel = self.query_one(GitPanel)
            git_panel.update_config(new_config.git)

            system_panel = self.query_one(SystemPanel)
            system_panel.update_config(new_config.system)

            tasks_panel = self.query_one(TasksPanel)
            tasks_panel.update_config(new_config.tasks)

            timer_panel = self.query_one(TimerPanel)
            timer_panel.update_config(new_config.timer)

            # Show success notification
            self.notify("Configuration reloaded successfully", severity="information", timeout=2)

        except Exception as e:
            # If reload fails, keep using old config
            self.notify(f"Error reloading config: {e}", severity="error", timeout=5)

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


def generate_example_config() -> str:
    """Generate an example configuration file content.

    Returns:
        String containing example TOML configuration
    """
    return """# DevDash Configuration File
# See https://github.com/RainMaker033/devdash for full documentation

[general]
theme = "default"  # Options: "default", "dark", "light"
layout = "default"
update_header = true

[git]
enabled = true
refresh_interval = 5  # seconds
max_commits = 3       # number of recent commits to display
show_staged = true
show_modified = true
show_untracked = true

[system]
enabled = true
refresh_interval = 1  # seconds
show_cpu = true
show_ram = true
show_disk = true
show_uptime = true
show_load_avg = true  # Linux/Mac only

# Thresholds for color coding (percentage, 0-100)
cpu_warning_threshold = 60.0
cpu_critical_threshold = 80.0
ram_warning_threshold = 60.0
ram_critical_threshold = 80.0
disk_warning_threshold = 60.0
disk_critical_threshold = 80.0

# Progress bar configuration
progress_bar_width = 10
progress_bar_style = "blocks"  # Options: "blocks", "bars", "dots"

[tasks]
enabled = true
file_path = ".devdash_tasks.json"  # Relative to current directory
default_sort = "created"  # Options: "created", "priority", "due_date", "text"
show_completed = true
default_priority_filter = null  # null, "high", "medium", "low"
default_category_filter = null  # null or category name
max_visible_tasks = 20
truncate_length = 40
show_categories = true
show_due_dates = true
show_priority_emoji = true
due_soon_days = 3  # Days threshold for "due soon" indicator
export_format = "grouped"  # Options: "grouped", "simple", "detailed"

[timer]
enabled = true
focus_duration = 25  # minutes
break_duration = 5   # minutes
long_break_duration = 15  # minutes (future feature)
auto_start_break = false
notification_enabled = false  # Future feature
notification_sound = "bell"   # Options: "bell", "chime", "silent"
show_progress_bar = true
progress_bar_width = 20

[ui]
border_style = "solid"  # Options: "solid", "double", "rounded", "heavy", "none"
panel_padding = 1
show_footer = true
show_header = true
compact_view = false

[keybindings]
# Future feature: custom keybindings
quit = "q"
help = "?"
refresh = "r"
"""


def show_current_config(config: DevDashConfig) -> None:
    """Display the current configuration.

    Args:
        config: Configuration object to display
    """
    print("Current DevDash Configuration:")
    print("=" * 50)
    print(f"\nGit Panel:")
    print(f"  Enabled: {config.git.enabled}")
    print(f"  Refresh interval: {config.git.refresh_interval}s")
    print(f"  Max commits: {config.git.max_commits}")
    print(f"\nSystem Panel:")
    print(f"  Enabled: {config.system.enabled}")
    print(f"  Refresh interval: {config.system.refresh_interval}s")
    print(f"  CPU warning/critical: {config.system.cpu_warning_threshold}% / {config.system.cpu_critical_threshold}%")
    print(f"  Progress bar width: {config.system.progress_bar_width}")
    print(f"\nTasks Panel:")
    print(f"  Enabled: {config.tasks.enabled}")
    print(f"  File path: {config.tasks.file_path}")
    print(f"  Default sort: {config.tasks.default_sort}")
    print(f"  Max visible: {config.tasks.max_visible_tasks}")
    print(f"\nTimer Panel:")
    print(f"  Enabled: {config.timer.enabled}")
    print(f"  Focus duration: {config.timer.focus_duration} minutes")
    print(f"  Break duration: {config.timer.break_duration} minutes")
    print(f"  Show progress bar: {config.timer.show_progress_bar}")


def validate_config_file(config_path: Optional[Path] = None) -> int:
    """Validate a configuration file.

    Args:
        config_path: Optional path to config file. If None, searches default locations.

    Returns:
        Exit code: 0 if valid, 1 if errors found
    """
    loader = ConfigLoader()

    # Determine which config file to validate
    if config_path:
        file_to_validate = config_path
    else:
        file_to_validate = loader.find_config_file()

    if not file_to_validate:
        print("No configuration file found.", file=sys.stderr)
        print("\nSearched locations:")
        print("  - ./.devdash.toml (current directory)")
        print("  - ~/.config/devdash/config.toml")
        print("  - ~/.devdash.toml")
        print("\nTip: Generate an example config with: devdash --generate-config > .devdash.toml")
        return 1

    print(f"Validating: {file_to_validate}")
    print("-" * 50)

    try:
        # Try to load the config
        config = loader.load_config(custom_path=file_to_validate)
        print("✓ TOML syntax is valid")

        # Validate config values
        warnings = ConfigValidator.validate_config(config)

        if warnings:
            print(f"\n⚠ Found {len(warnings)} warning(s):")
            for warning in warnings:
                print(f"  - {warning}")
            print("\nConfiguration will use default values for invalid fields.")
            return 1
        else:
            print("✓ All configuration values are valid")
            print("\nConfiguration is valid!")
            return 0

    except ConfigLoadError as e:
        print(f"✗ Configuration error:\n{e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error:\n{e}", file=sys.stderr)
        return 1


def cli():
    """Command-line interface entry point."""
    parser = argparse.ArgumentParser(
        prog="devdash",
        description="A terminal dashboard for developers - Git status, system metrics, tasks, and Pomodoro timer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  devdash                          # Run with default or discovered config
  devdash --config my-config.toml  # Run with custom config file
  devdash --validate-config        # Validate configuration file
  devdash --show-config            # Display current configuration
  devdash --generate-config > .devdash.toml  # Generate example config

Config file locations (in priority order):
  1. ./.devdash.toml (current directory)
  2. ~/.config/devdash/config.toml
  3. ~/.devdash.toml
"""
    )

    parser.add_argument(
        "--config",
        type=Path,
        metavar="FILE",
        help="Path to custom configuration file"
    )

    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration file and exit"
    )

    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Display current configuration and exit"
    )

    parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Generate example configuration file to stdout"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="devdash 0.3.1"
    )

    args = parser.parse_args()

    # Handle --generate-config
    if args.generate_config:
        print(generate_example_config())
        sys.exit(0)

    # Handle --validate-config
    if args.validate_config:
        exit_code = validate_config_file(args.config)
        sys.exit(exit_code)

    # Load configuration
    try:
        if args.config:
            loader = ConfigLoader()
            config = loader.load_config(custom_path=args.config)
            config_source = str(args.config)
        else:
            loader = ConfigLoader()
            config_path = loader.find_config_file()
            config = load_config()
            config_source = str(config_path) if config_path else "defaults"

        # Validate config and show warnings
        warnings = ConfigValidator.validate_config(config)
        if warnings:
            print("Configuration warnings:", file=sys.stderr)
            for warning in warnings:
                print(f"  - {warning}", file=sys.stderr)
            print("", file=sys.stderr)

    except ConfigLoadError as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        print("Using default configuration.", file=sys.stderr)
        config = get_default_config()
        config_source = "defaults (due to error)"

    # Handle --show-config
    if args.show_config:
        print(f"Configuration source: {config_source}\n")
        show_current_config(config)
        sys.exit(0)

    # Show config source on startup
    print(f"Using configuration: {config_source}")

    # Run the app
    app = DevDashApp(config=config)
    app.run()


if __name__ == "__main__":
    cli()
