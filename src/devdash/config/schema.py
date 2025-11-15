"""Configuration schema definitions for DevDash.

This module defines the structure and types for all configuration options
using Python dataclasses.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GeneralConfig:
    """General application settings."""

    theme: str = "default"
    layout: str = "default"
    update_header: bool = True


@dataclass
class GitConfig:
    """Git panel configuration."""

    enabled: bool = True
    refresh_interval: int = 5  # seconds
    max_commits: int = 3
    show_staged: bool = True
    show_modified: bool = True
    show_untracked: bool = True
    compact_mode: bool = False
    repository_path: Optional[str] = None  # Path to repository (None = current directory)


@dataclass
class SystemConfig:
    """System panel configuration."""

    enabled: bool = True
    refresh_interval: int = 1  # seconds
    show_cpu: bool = True
    show_ram: bool = True
    show_disk: bool = True
    show_uptime: bool = True
    show_load_avg: bool = True
    # Thresholds for color coding (percentage)
    cpu_warning_threshold: float = 60.0
    cpu_critical_threshold: float = 80.0
    ram_warning_threshold: float = 60.0
    ram_critical_threshold: float = 80.0
    disk_warning_threshold: float = 60.0
    disk_critical_threshold: float = 80.0
    # Progress bar configuration
    progress_bar_width: int = 10
    progress_bar_style: str = "blocks"


@dataclass
class TasksConfig:
    """Tasks panel configuration."""

    enabled: bool = True
    file_path: str = ".devdash_tasks.json"
    default_sort: str = "created"
    show_completed: bool = True
    default_priority_filter: Optional[str] = None
    default_category_filter: Optional[str] = None
    max_visible_tasks: int = 20
    truncate_length: int = 40
    show_categories: bool = True
    show_due_dates: bool = True
    show_priority_emoji: bool = True
    due_soon_days: int = 3
    export_format: str = "grouped"


@dataclass
class TimerConfig:
    """Timer panel configuration."""

    enabled: bool = True
    focus_duration: int = 25  # minutes
    break_duration: int = 5  # minutes
    long_break_duration: int = 15  # minutes
    auto_start_break: bool = False
    notification_enabled: bool = False
    notification_sound: str = "bell"
    show_progress_bar: bool = True
    progress_bar_width: int = 20


@dataclass
class UIConfig:
    """UI customization configuration."""

    border_style: str = "solid"
    panel_padding: int = 1
    show_footer: bool = True
    show_header: bool = True
    compact_view: bool = False


@dataclass
class KeybindingsConfig:
    """Custom keybindings configuration.

    All keybindings can be customized. Use standard key names like:
    - Single chars: "a", "q", "?"
    - Special keys: "space", "enter", "escape"
    - Modified keys: "ctrl+c", "shift+f", "F" (uppercase for Shift+f)
    """

    # General actions
    quit: str = "q"
    help: str = "?"
    config: str = "c"
    refresh: str = "r"

    # Task management
    add_task: str = "a"
    edit_task: str = "e"
    toggle_task: str = "space"
    delete_task: str = "d"
    quick_priority: str = "p"
    filter_tasks: str = "f"
    sort_tasks: str = "s"
    export_tasks: str = "x"

    # Task filters
    filter_high: str = "1"
    filter_medium: str = "2"
    filter_low: str = "3"
    clear_filters: str = "0"

    # Timer controls (use Shift+key to avoid conflicts)
    timer_focus: str = "F"
    timer_break: str = "B"
    timer_stop: str = "S"


@dataclass
class DevDashConfig:
    """Root configuration object containing all settings."""

    general: GeneralConfig = field(default_factory=GeneralConfig)
    git: GitConfig = field(default_factory=GitConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    tasks: TasksConfig = field(default_factory=TasksConfig)
    timer: TimerConfig = field(default_factory=TimerConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    keybindings: KeybindingsConfig = field(default_factory=KeybindingsConfig)
