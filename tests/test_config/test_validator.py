"""Tests for configuration validator."""

import pytest
from devdash.config.validator import ConfigValidator
from devdash.config.schema import (
    DevDashConfig,
    GitConfig,
    SystemConfig,
    TasksConfig,
    TimerConfig,
    UIConfig,
)


class TestGitConfigValidation:
    """Test Git configuration validation."""

    def test_validate_git_valid_config(self):
        """Test validation of valid Git config."""
        config = GitConfig()
        warnings = ConfigValidator.validate_git(config)
        assert len(warnings) == 0

    def test_validate_git_invalid_refresh_interval(self):
        """Test validation catches invalid refresh_interval."""
        config = GitConfig(refresh_interval=0)
        warnings = ConfigValidator.validate_git(config)
        assert len(warnings) > 0
        assert "refresh_interval must be >= 1" in warnings[0]

    def test_validate_git_large_refresh_interval_warning(self):
        """Test validation warns about very large refresh_interval."""
        config = GitConfig(refresh_interval=7200)
        warnings = ConfigValidator.validate_git(config)
        assert len(warnings) > 0
        assert "very large" in warnings[0]

    def test_validate_git_invalid_max_commits_negative(self):
        """Test validation catches negative max_commits."""
        config = GitConfig(max_commits=-1)
        warnings = ConfigValidator.validate_git(config)
        assert len(warnings) > 0
        assert "max_commits should be 0-20" in warnings[0]

    def test_validate_git_invalid_max_commits_too_large(self):
        """Test validation catches max_commits too large."""
        config = GitConfig(max_commits=50)
        warnings = ConfigValidator.validate_git(config)
        assert len(warnings) > 0
        assert "max_commits should be 0-20" in warnings[0]


class TestSystemConfigValidation:
    """Test System configuration validation."""

    def test_validate_system_valid_config(self):
        """Test validation of valid System config."""
        config = SystemConfig()
        warnings = ConfigValidator.validate_system(config)
        assert len(warnings) == 0

    def test_validate_system_invalid_refresh_interval(self):
        """Test validation catches invalid refresh_interval."""
        config = SystemConfig(refresh_interval=0.1)
        warnings = ConfigValidator.validate_system(config)
        assert len(warnings) > 0
        assert "refresh_interval must be >= 0.5" in warnings[0]

    def test_validate_system_large_refresh_interval(self):
        """Test validation warns about large refresh_interval."""
        config = SystemConfig(refresh_interval=120)
        warnings = ConfigValidator.validate_system(config)
        assert len(warnings) > 0
        assert "very large" in warnings[0]

    def test_validate_system_threshold_out_of_range(self):
        """Test validation catches threshold out of range."""
        config = SystemConfig(cpu_warning_threshold=150.0)
        warnings = ConfigValidator.validate_system(config)
        assert any("must be 0-100" in w for w in warnings)

    def test_validate_system_warning_greater_than_critical(self):
        """Test validation catches warning >= critical."""
        config = SystemConfig(
            cpu_warning_threshold=90.0, cpu_critical_threshold=80.0
        )
        warnings = ConfigValidator.validate_system(config)
        assert any(
            "should be less than" in w and "critical" in w for w in warnings
        )

    def test_validate_system_warning_equals_critical(self):
        """Test validation catches warning == critical."""
        config = SystemConfig(
            ram_warning_threshold=70.0, ram_critical_threshold=70.0
        )
        warnings = ConfigValidator.validate_system(config)
        assert any("should be less than" in w for w in warnings)

    def test_validate_system_negative_threshold(self):
        """Test validation catches negative threshold."""
        config = SystemConfig(disk_warning_threshold=-10.0)
        warnings = ConfigValidator.validate_system(config)
        assert any("must be 0-100" in w for w in warnings)

    def test_validate_system_invalid_progress_bar_width(self):
        """Test validation catches invalid progress_bar_width."""
        config = SystemConfig(progress_bar_width=2)
        warnings = ConfigValidator.validate_system(config)
        assert any("progress_bar_width should be 5-50" in w for w in warnings)

        config = SystemConfig(progress_bar_width=100)
        warnings = ConfigValidator.validate_system(config)
        assert any("progress_bar_width should be 5-50" in w for w in warnings)

    def test_validate_system_invalid_progress_bar_style(self):
        """Test validation catches invalid progress_bar_style."""
        config = SystemConfig(progress_bar_style="invalid")
        warnings = ConfigValidator.validate_system(config)
        assert any("progress_bar_style must be one of" in w for w in warnings)

    def test_validate_system_valid_progress_bar_styles(self):
        """Test validation accepts valid progress_bar_styles."""
        for style in ["blocks", "bars", "dots"]:
            config = SystemConfig(progress_bar_style=style)
            warnings = ConfigValidator.validate_system(config)
            # Should not have style-related warnings
            assert not any("progress_bar_style" in w for w in warnings)


class TestTasksConfigValidation:
    """Test Tasks configuration validation."""

    def test_validate_tasks_valid_config(self):
        """Test validation of valid Tasks config."""
        config = TasksConfig()
        warnings = ConfigValidator.validate_tasks(config)
        assert len(warnings) == 0

    def test_validate_tasks_invalid_default_sort(self):
        """Test validation catches invalid default_sort."""
        config = TasksConfig(default_sort="invalid")
        warnings = ConfigValidator.validate_tasks(config)
        assert any("default_sort must be one of" in w for w in warnings)

    def test_validate_tasks_valid_default_sorts(self):
        """Test validation accepts valid default_sort values."""
        for sort in ["created", "priority", "due_date", "text"]:
            config = TasksConfig(default_sort=sort)
            warnings = ConfigValidator.validate_tasks(config)
            # Should not have sort-related warnings
            assert not any("default_sort" in w for w in warnings)

    def test_validate_tasks_invalid_priority_filter(self):
        """Test validation catches invalid default_priority_filter."""
        config = TasksConfig(default_priority_filter="urgent")
        warnings = ConfigValidator.validate_tasks(config)
        assert any("default_priority_filter must be one of" in w for w in warnings)

    def test_validate_tasks_valid_priority_filters(self):
        """Test validation accepts valid default_priority_filter values."""
        for priority in ["high", "medium", "low", None]:
            config = TasksConfig(default_priority_filter=priority)
            warnings = ConfigValidator.validate_tasks(config)
            # Should not have priority filter warnings
            assert not any("default_priority_filter" in w for w in warnings)

    def test_validate_tasks_invalid_max_visible_tasks(self):
        """Test validation catches invalid max_visible_tasks."""
        config = TasksConfig(max_visible_tasks=0)
        warnings = ConfigValidator.validate_tasks(config)
        assert any("max_visible_tasks should be 1-100" in w for w in warnings)

        config = TasksConfig(max_visible_tasks=200)
        warnings = ConfigValidator.validate_tasks(config)
        assert any("max_visible_tasks should be 1-100" in w for w in warnings)

    def test_validate_tasks_invalid_truncate_length(self):
        """Test validation catches invalid truncate_length."""
        config = TasksConfig(truncate_length=10)
        warnings = ConfigValidator.validate_tasks(config)
        assert any("truncate_length should be 20-200" in w for w in warnings)

        config = TasksConfig(truncate_length=300)
        warnings = ConfigValidator.validate_tasks(config)
        assert any("truncate_length should be 20-200" in w for w in warnings)

    def test_validate_tasks_invalid_due_soon_days(self):
        """Test validation catches invalid due_soon_days."""
        config = TasksConfig(due_soon_days=0)
        warnings = ConfigValidator.validate_tasks(config)
        assert any("due_soon_days should be 1-30" in w for w in warnings)

        config = TasksConfig(due_soon_days=100)
        warnings = ConfigValidator.validate_tasks(config)
        assert any("due_soon_days should be 1-30" in w for w in warnings)

    def test_validate_tasks_invalid_export_format(self):
        """Test validation catches invalid export_format."""
        config = TasksConfig(export_format="xml")
        warnings = ConfigValidator.validate_tasks(config)
        assert any("export_format must be one of" in w for w in warnings)

    def test_validate_tasks_valid_export_formats(self):
        """Test validation accepts valid export_format values."""
        for fmt in ["grouped", "simple", "detailed"]:
            config = TasksConfig(export_format=fmt)
            warnings = ConfigValidator.validate_tasks(config)
            # Should not have format-related warnings
            assert not any("export_format" in w for w in warnings)


class TestTimerConfigValidation:
    """Test Timer configuration validation."""

    def test_validate_timer_valid_config(self):
        """Test validation of valid Timer config."""
        config = TimerConfig()
        warnings = ConfigValidator.validate_timer(config)
        assert len(warnings) == 0

    def test_validate_timer_invalid_focus_duration(self):
        """Test validation catches invalid focus_duration."""
        config = TimerConfig(focus_duration=0)
        warnings = ConfigValidator.validate_timer(config)
        assert any("focus_duration should be 1-240" in w for w in warnings)

        config = TimerConfig(focus_duration=300)
        warnings = ConfigValidator.validate_timer(config)
        assert any("focus_duration should be 1-240" in w for w in warnings)

    def test_validate_timer_invalid_break_duration(self):
        """Test validation catches invalid break_duration."""
        config = TimerConfig(break_duration=0)
        warnings = ConfigValidator.validate_timer(config)
        assert any("break_duration should be 1-60" in w for w in warnings)

        config = TimerConfig(break_duration=100)
        warnings = ConfigValidator.validate_timer(config)
        assert any("break_duration should be 1-60" in w for w in warnings)

    def test_validate_timer_invalid_long_break_duration(self):
        """Test validation catches invalid long_break_duration."""
        config = TimerConfig(long_break_duration=0)
        warnings = ConfigValidator.validate_timer(config)
        assert any("long_break_duration should be 1-120" in w for w in warnings)

        config = TimerConfig(long_break_duration=200)
        warnings = ConfigValidator.validate_timer(config)
        assert any("long_break_duration should be 1-120" in w for w in warnings)

    def test_validate_timer_invalid_progress_bar_width(self):
        """Test validation catches invalid progress_bar_width."""
        config = TimerConfig(progress_bar_width=5)
        warnings = ConfigValidator.validate_timer(config)
        assert any("progress_bar_width should be 10-60" in w for w in warnings)

        config = TimerConfig(progress_bar_width=100)
        warnings = ConfigValidator.validate_timer(config)
        assert any("progress_bar_width should be 10-60" in w for w in warnings)

    def test_validate_timer_invalid_notification_sound(self):
        """Test validation catches invalid notification_sound."""
        config = TimerConfig(notification_sound="invalid")
        warnings = ConfigValidator.validate_timer(config)
        assert any("notification_sound must be one of" in w for w in warnings)

    def test_validate_timer_valid_notification_sounds(self):
        """Test validation accepts valid notification_sound values."""
        for sound in ["bell", "chime", "silent"]:
            config = TimerConfig(notification_sound=sound)
            warnings = ConfigValidator.validate_timer(config)
            # Should not have sound-related warnings
            assert not any("notification_sound" in w for w in warnings)


class TestUIConfigValidation:
    """Test UI configuration validation."""

    def test_validate_ui_valid_config(self):
        """Test validation of valid UI config."""
        config = UIConfig()
        warnings = ConfigValidator.validate_ui(config)
        assert len(warnings) == 0

    def test_validate_ui_invalid_border_style(self):
        """Test validation catches invalid border_style."""
        config = UIConfig(border_style="invalid")
        warnings = ConfigValidator.validate_ui(config)
        assert any("border_style must be one of" in w for w in warnings)

    def test_validate_ui_valid_border_styles(self):
        """Test validation accepts valid border_style values."""
        for style in ["solid", "double", "rounded", "heavy", "none"]:
            config = UIConfig(border_style=style)
            warnings = ConfigValidator.validate_ui(config)
            # Should not have style-related warnings
            assert not any("border_style" in w for w in warnings)

    def test_validate_ui_invalid_panel_padding(self):
        """Test validation catches invalid panel_padding."""
        config = UIConfig(panel_padding=-1)
        warnings = ConfigValidator.validate_ui(config)
        assert any("panel_padding should be 0-5" in w for w in warnings)

        config = UIConfig(panel_padding=10)
        warnings = ConfigValidator.validate_ui(config)
        assert any("panel_padding should be 0-5" in w for w in warnings)


class TestFullConfigValidation:
    """Test validation of complete DevDashConfig."""

    def test_validate_config_all_valid(self):
        """Test validation of fully valid config."""
        config = DevDashConfig()
        warnings = ConfigValidator.validate_config(config)
        assert len(warnings) == 0

    def test_validate_config_multiple_sections_with_errors(self):
        """Test validation catches errors across multiple sections."""
        config = DevDashConfig(
            git=GitConfig(refresh_interval=0),
            system=SystemConfig(cpu_warning_threshold=150.0),
            timer=TimerConfig(focus_duration=0),
        )
        warnings = ConfigValidator.validate_config(config)

        # Should have warnings from multiple sections
        assert len(warnings) >= 3
        assert any("git.refresh_interval" in w for w in warnings)
        assert any("cpu_warning_threshold" in w for w in warnings)
        assert any("focus_duration" in w for w in warnings)

    def test_validate_config_partial_errors(self):
        """Test validation with some sections valid, some invalid."""
        config = DevDashConfig(
            git=GitConfig(refresh_interval=10),  # Valid
            timer=TimerConfig(focus_duration=0),  # Invalid
        )
        warnings = ConfigValidator.validate_config(config)

        # Should only have timer warnings
        assert len(warnings) > 0
        assert any("focus_duration" in w for w in warnings)
        assert not any("git" in w for w in warnings)
