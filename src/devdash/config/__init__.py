"""DevDash configuration module.

This module provides configuration loading, validation, and schema definitions
for the DevDash application.

Example usage:
    from devdash.config import load_config

    # Load config from default locations or use defaults
    config = load_config()

    # Access configuration values
    print(config.timer.focus_duration)
    print(config.git.refresh_interval)
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
from .loader import ConfigLoader, ConfigLoadError
from .validator import ConfigValidator
from .defaults import get_default_config

__all__ = [
    # Main loader function
    "load_config",
    # Schema classes
    "DevDashConfig",
    "GeneralConfig",
    "GitConfig",
    "SystemConfig",
    "TasksConfig",
    "TimerConfig",
    "UIConfig",
    "KeybindingsConfig",
    # Utilities
    "ConfigLoader",
    "ConfigLoadError",
    "ConfigValidator",
    "get_default_config",
]


def load_config(custom_path=None):
    """Load DevDash configuration from file or use defaults.

    Args:
        custom_path: Optional custom path to config file

    Returns:
        DevDashConfig: Loaded configuration merged with defaults

    Raises:
        ConfigLoadError: If config file cannot be loaded or parsed
    """
    loader = ConfigLoader()
    return loader.load_config(custom_path=custom_path)
