"""Configuration validator for DevDash.

This module validates configuration values to ensure they are within acceptable ranges
and meet logical constraints.
"""

from typing import List
from .schema import DevDashConfig, GitConfig, SystemConfig, TasksConfig, TimerConfig, UIConfig


class ConfigValidator:
    """Validates DevDash configuration values."""

    @staticmethod
    def validate_config(config: DevDashConfig) -> List[str]:
        """Validate entire configuration and return list of warnings/errors.

        Args:
            config: Configuration object to validate

        Returns:
            List of warning/error messages (empty if all valid)
        """
        warnings = []
        warnings.extend(ConfigValidator.validate_git(config.git))
        warnings.extend(ConfigValidator.validate_system(config.system))
        warnings.extend(ConfigValidator.validate_tasks(config.tasks))
        warnings.extend(ConfigValidator.validate_timer(config.timer))
        warnings.extend(ConfigValidator.validate_ui(config.ui))
        return warnings

    @staticmethod
    def validate_git(config: GitConfig) -> List[str]:
        """Validate Git panel configuration.

        Args:
            config: Git configuration to validate

        Returns:
            List of warning messages
        """
        warnings = []

        if config.refresh_interval < 1:
            warnings.append(
                f"git.refresh_interval must be >= 1 (got {config.refresh_interval}), "
                "using default: 5"
            )

        if config.refresh_interval > 3600:
            warnings.append(
                f"git.refresh_interval is very large ({config.refresh_interval}s = "
                f"{config.refresh_interval // 60} minutes)"
            )

        if config.max_commits < 0 or config.max_commits > 20:
            warnings.append(
                f"git.max_commits should be 0-20 (got {config.max_commits}), "
                "using default: 3"
            )

        return warnings

    @staticmethod
    def validate_system(config: SystemConfig) -> List[str]:
        """Validate System panel configuration.

        Args:
            config: System configuration to validate

        Returns:
            List of warning messages
        """
        warnings = []

        # Validate refresh interval
        if config.refresh_interval < 0.5:
            warnings.append(
                f"system.refresh_interval must be >= 0.5 (got {config.refresh_interval}), "
                "using default: 1"
            )

        if config.refresh_interval > 60:
            warnings.append(
                f"system.refresh_interval is very large ({config.refresh_interval}s)"
            )

        # Validate thresholds
        threshold_fields = [
            ("cpu_warning_threshold", "cpu_critical_threshold"),
            ("ram_warning_threshold", "ram_critical_threshold"),
            ("disk_warning_threshold", "disk_critical_threshold"),
        ]

        for warning_field, critical_field in threshold_fields:
            warning_val = getattr(config, warning_field)
            critical_val = getattr(config, critical_field)

            # Check range 0-100
            if not (0 <= warning_val <= 100):
                warnings.append(
                    f"system.{warning_field} must be 0-100 (got {warning_val}), "
                    "using default: 60"
                )

            if not (0 <= critical_val <= 100):
                warnings.append(
                    f"system.{critical_field} must be 0-100 (got {critical_val}), "
                    "using default: 80"
                )

            # Check warning < critical
            if warning_val >= critical_val:
                warnings.append(
                    f"system.{warning_field} ({warning_val}) should be less than "
                    f"system.{critical_field} ({critical_val})"
                )

        # Validate progress bar width
        if config.progress_bar_width < 5 or config.progress_bar_width > 50:
            warnings.append(
                f"system.progress_bar_width should be 5-50 (got {config.progress_bar_width}), "
                "using default: 10"
            )

        # Validate progress bar style
        valid_styles = ["blocks", "bars", "dots"]
        if config.progress_bar_style not in valid_styles:
            warnings.append(
                f"system.progress_bar_style must be one of {valid_styles} "
                f"(got '{config.progress_bar_style}'), using default: 'blocks'"
            )

        return warnings

    @staticmethod
    def validate_tasks(config: TasksConfig) -> List[str]:
        """Validate Tasks panel configuration.

        Args:
            config: Tasks configuration to validate

        Returns:
            List of warning messages
        """
        warnings = []

        # Validate sort option
        valid_sorts = ["created", "priority", "due_date", "text"]
        if config.default_sort not in valid_sorts:
            warnings.append(
                f"tasks.default_sort must be one of {valid_sorts} "
                f"(got '{config.default_sort}'), using default: 'created'"
            )

        # Validate priority filter
        if config.default_priority_filter is not None:
            valid_priorities = ["high", "medium", "low"]
            if config.default_priority_filter not in valid_priorities:
                warnings.append(
                    f"tasks.default_priority_filter must be one of {valid_priorities} or null "
                    f"(got '{config.default_priority_filter}'), using default: null"
                )

        # Validate max visible tasks
        if config.max_visible_tasks < 1 or config.max_visible_tasks > 100:
            warnings.append(
                f"tasks.max_visible_tasks should be 1-100 (got {config.max_visible_tasks}), "
                "using default: 20"
            )

        # Validate truncate length
        if config.truncate_length < 20 or config.truncate_length > 200:
            warnings.append(
                f"tasks.truncate_length should be 20-200 (got {config.truncate_length}), "
                "using default: 40"
            )

        # Validate due soon days
        if config.due_soon_days < 1 or config.due_soon_days > 30:
            warnings.append(
                f"tasks.due_soon_days should be 1-30 (got {config.due_soon_days}), "
                "using default: 3"
            )

        # Validate export format
        valid_formats = ["grouped", "simple", "detailed"]
        if config.export_format not in valid_formats:
            warnings.append(
                f"tasks.export_format must be one of {valid_formats} "
                f"(got '{config.export_format}'), using default: 'grouped'"
            )

        return warnings

    @staticmethod
    def validate_timer(config: TimerConfig) -> List[str]:
        """Validate Timer panel configuration.

        Args:
            config: Timer configuration to validate

        Returns:
            List of warning messages
        """
        warnings = []

        # Validate focus duration
        if config.focus_duration < 1 or config.focus_duration > 240:
            warnings.append(
                f"timer.focus_duration should be 1-240 minutes (got {config.focus_duration}), "
                "using default: 25"
            )

        # Validate break duration
        if config.break_duration < 1 or config.break_duration > 60:
            warnings.append(
                f"timer.break_duration should be 1-60 minutes (got {config.break_duration}), "
                "using default: 5"
            )

        # Validate long break duration
        if config.long_break_duration < 1 or config.long_break_duration > 120:
            warnings.append(
                f"timer.long_break_duration should be 1-120 minutes "
                f"(got {config.long_break_duration}), using default: 15"
            )

        # Validate progress bar width
        if config.progress_bar_width < 10 or config.progress_bar_width > 60:
            warnings.append(
                f"timer.progress_bar_width should be 10-60 (got {config.progress_bar_width}), "
                "using default: 20"
            )

        # Validate notification sound
        valid_sounds = ["bell", "chime", "silent"]
        if config.notification_sound not in valid_sounds:
            warnings.append(
                f"timer.notification_sound must be one of {valid_sounds} "
                f"(got '{config.notification_sound}'), using default: 'bell'"
            )

        return warnings

    @staticmethod
    def validate_ui(config: UIConfig) -> List[str]:
        """Validate UI configuration.

        Args:
            config: UI configuration to validate

        Returns:
            List of warning messages
        """
        warnings = []

        # Validate border style
        valid_styles = ["solid", "double", "rounded", "heavy", "none"]
        if config.border_style not in valid_styles:
            warnings.append(
                f"ui.border_style must be one of {valid_styles} "
                f"(got '{config.border_style}'), using default: 'solid'"
            )

        # Validate panel padding
        if config.panel_padding < 0 or config.panel_padding > 5:
            warnings.append(
                f"ui.panel_padding should be 0-5 (got {config.panel_padding}), "
                "using default: 1"
            )

        return warnings
