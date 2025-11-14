"""Tests for configuration schema and defaults."""

import pytest
from devdash.config.schema import (
    DevDashConfig,
    GeneralConfig,
    GitConfig,
    SystemConfig,
    TasksConfig,
    TimerConfig,
    UIConfig,
    KeybindingsConfig,
)
from devdash.config.defaults import get_default_config


class TestSchemaDefaults:
    """Test that schema dataclasses have correct default values."""

    def test_general_config_defaults(self):
        """Test GeneralConfig default values."""
        config = GeneralConfig()
        assert config.theme == "default"
        assert config.layout == "default"
        assert config.update_header is True

    def test_git_config_defaults(self):
        """Test GitConfig default values."""
        config = GitConfig()
        assert config.enabled is True
        assert config.refresh_interval == 5
        assert config.max_commits == 3
        assert config.show_staged is True
        assert config.show_modified is True
        assert config.show_untracked is True
        assert config.compact_mode is False

    def test_system_config_defaults(self):
        """Test SystemConfig default values."""
        config = SystemConfig()
        assert config.enabled is True
        assert config.refresh_interval == 1
        assert config.show_cpu is True
        assert config.show_ram is True
        assert config.show_disk is True
        assert config.show_uptime is True
        assert config.show_load_avg is True
        assert config.cpu_warning_threshold == 60.0
        assert config.cpu_critical_threshold == 80.0
        assert config.ram_warning_threshold == 60.0
        assert config.ram_critical_threshold == 80.0
        assert config.disk_warning_threshold == 60.0
        assert config.disk_critical_threshold == 80.0
        assert config.progress_bar_width == 10
        assert config.progress_bar_style == "blocks"

    def test_tasks_config_defaults(self):
        """Test TasksConfig default values."""
        config = TasksConfig()
        assert config.enabled is True
        assert config.file_path == ".devdash_tasks.json"
        assert config.default_sort == "created"
        assert config.show_completed is True
        assert config.default_priority_filter is None
        assert config.default_category_filter is None
        assert config.max_visible_tasks == 20
        assert config.truncate_length == 40
        assert config.show_categories is True
        assert config.show_due_dates is True
        assert config.show_priority_emoji is True
        assert config.due_soon_days == 3
        assert config.export_format == "grouped"

    def test_timer_config_defaults(self):
        """Test TimerConfig default values."""
        config = TimerConfig()
        assert config.enabled is True
        assert config.focus_duration == 25
        assert config.break_duration == 5
        assert config.long_break_duration == 15
        assert config.auto_start_break is False
        assert config.notification_enabled is False
        assert config.notification_sound == "bell"
        assert config.show_progress_bar is True
        assert config.progress_bar_width == 20

    def test_ui_config_defaults(self):
        """Test UIConfig default values."""
        config = UIConfig()
        assert config.border_style == "solid"
        assert config.panel_padding == 1
        assert config.show_footer is True
        assert config.show_header is True
        assert config.compact_view is False

    def test_keybindings_config_defaults(self):
        """Test KeybindingsConfig default values."""
        config = KeybindingsConfig()
        assert config.quit == "q"
        assert config.help == "?"
        assert config.refresh == "r"

    def test_devdash_config_defaults(self):
        """Test DevDashConfig has all subsections with defaults."""
        config = DevDashConfig()
        assert isinstance(config.general, GeneralConfig)
        assert isinstance(config.git, GitConfig)
        assert isinstance(config.system, SystemConfig)
        assert isinstance(config.tasks, TasksConfig)
        assert isinstance(config.timer, TimerConfig)
        assert isinstance(config.ui, UIConfig)
        assert isinstance(config.keybindings, KeybindingsConfig)


class TestGetDefaultConfig:
    """Test get_default_config factory function."""

    def test_returns_devdash_config(self):
        """Test that get_default_config returns a DevDashConfig instance."""
        config = get_default_config()
        assert isinstance(config, DevDashConfig)

    def test_all_sections_present(self):
        """Test that all config sections are present and correctly typed."""
        config = get_default_config()
        assert isinstance(config.general, GeneralConfig)
        assert isinstance(config.git, GitConfig)
        assert isinstance(config.system, SystemConfig)
        assert isinstance(config.tasks, TasksConfig)
        assert isinstance(config.timer, TimerConfig)
        assert isinstance(config.ui, UIConfig)
        assert isinstance(config.keybindings, KeybindingsConfig)

    def test_default_values_applied(self):
        """Test that default values are correctly applied."""
        config = get_default_config()
        # Check a few key defaults
        assert config.timer.focus_duration == 25
        assert config.git.refresh_interval == 5
        assert config.system.cpu_warning_threshold == 60.0
        assert config.tasks.default_sort == "created"


class TestSchemaCustomValues:
    """Test that schema dataclasses accept custom values."""

    def test_git_config_custom_values(self):
        """Test GitConfig with custom values."""
        config = GitConfig(
            enabled=False,
            refresh_interval=10,
            max_commits=5,
            show_staged=False,
            compact_mode=True,
        )
        assert config.enabled is False
        assert config.refresh_interval == 10
        assert config.max_commits == 5
        assert config.show_staged is False
        assert config.compact_mode is True
        # Check defaults for unspecified
        assert config.show_modified is True
        assert config.show_untracked is True

    def test_timer_config_custom_values(self):
        """Test TimerConfig with custom values."""
        config = TimerConfig(
            focus_duration=50,
            break_duration=10,
            auto_start_break=True,
            show_progress_bar=False,
        )
        assert config.focus_duration == 50
        assert config.break_duration == 10
        assert config.auto_start_break is True
        assert config.show_progress_bar is False

    def test_system_config_custom_thresholds(self):
        """Test SystemConfig with custom thresholds."""
        config = SystemConfig(
            cpu_warning_threshold=70.0,
            cpu_critical_threshold=90.0,
            progress_bar_width=15,
        )
        assert config.cpu_warning_threshold == 70.0
        assert config.cpu_critical_threshold == 90.0
        assert config.progress_bar_width == 15

    def test_tasks_config_custom_values(self):
        """Test TasksConfig with custom values."""
        config = TasksConfig(
            file_path="custom_tasks.json",
            default_sort="priority",
            default_priority_filter="high",
            max_visible_tasks=50,
        )
        assert config.file_path == "custom_tasks.json"
        assert config.default_sort == "priority"
        assert config.default_priority_filter == "high"
        assert config.max_visible_tasks == 50

    def test_devdash_config_custom_sections(self):
        """Test DevDashConfig with custom section objects."""
        git_config = GitConfig(refresh_interval=15)
        timer_config = TimerConfig(focus_duration=30)

        config = DevDashConfig(git=git_config, timer=timer_config)

        assert config.git.refresh_interval == 15
        assert config.timer.focus_duration == 30
        # Other sections should use defaults
        assert config.system.refresh_interval == 1
        assert config.tasks.default_sort == "created"
