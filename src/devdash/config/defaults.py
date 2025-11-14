"""Default configuration values for DevDash.

This module provides factory functions for creating default configuration objects.
"""

from .schema import (
    DevDashConfig,
    GeneralConfig,
    GitConfig,
    SystemConfig,
    TasksConfig,
    TimerConfig,
    UIConfig,
    KeybindingsConfig,
)


def get_default_config() -> DevDashConfig:
    """Create and return a DevDashConfig with all default values.

    Returns:
        DevDashConfig: Configuration object with all defaults applied
    """
    return DevDashConfig(
        general=GeneralConfig(),
        git=GitConfig(),
        system=SystemConfig(),
        tasks=TasksConfig(),
        timer=TimerConfig(),
        ui=UIConfig(),
        keybindings=KeybindingsConfig(),
    )
