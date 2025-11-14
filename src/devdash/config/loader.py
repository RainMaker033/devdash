"""Configuration loader for DevDash.

This module handles discovering, loading, and parsing TOML configuration files.
"""

import sys
from pathlib import Path
from typing import Optional, Any, Dict
from dataclasses import fields, is_dataclass

# Import appropriate TOML library based on Python version
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError(
            "tomli is required for Python < 3.11. "
            "Install it with: pip install tomli"
        )

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
from .defaults import get_default_config


class ConfigLoadError(Exception):
    """Raised when configuration loading fails."""

    pass


class ConfigLoader:
    """Loads and parses DevDash configuration from TOML files."""

    @staticmethod
    def find_config_file() -> Optional[Path]:
        """Find config file in priority order.

        Searches for configuration files in the following order:
        1. ./.devdash.toml (current working directory)
        2. ~/.config/devdash/config.toml (XDG standard)
        3. ~/.devdash.toml (home directory)

        Returns:
            Optional[Path]: Path to the config file if found, None otherwise
        """
        locations = [
            Path.cwd() / ".devdash.toml",
            Path.home() / ".config" / "devdash" / "config.toml",
            Path.home() / ".devdash.toml",
        ]

        for location in locations:
            if location.exists() and location.is_file():
                return location

        return None

    @staticmethod
    def load_toml(path: Path) -> Dict[str, Any]:
        """Load and parse a TOML file.

        Args:
            path: Path to the TOML file

        Returns:
            Dict containing the parsed TOML data

        Raises:
            ConfigLoadError: If file cannot be read or parsed
        """
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except PermissionError:
            raise ConfigLoadError(
                f"Cannot read config file (permission denied): {path}"
            )
        except tomllib.TOMLDecodeError as e:
            raise ConfigLoadError(
                f"Invalid TOML syntax in {path}:\n  {str(e)}"
            )
        except Exception as e:
            raise ConfigLoadError(
                f"Failed to load config from {path}: {str(e)}"
            )

    def load_config(self, custom_path: Optional[Path] = None) -> DevDashConfig:
        """Load configuration from file or return defaults.

        Args:
            custom_path: Optional custom path to config file (overrides discovery)

        Returns:
            DevDashConfig: Loaded configuration merged with defaults
        """
        # Start with defaults
        config = get_default_config()

        # Find config file
        config_path = custom_path if custom_path else self.find_config_file()

        if not config_path:
            # No config file found, use all defaults
            return config

        # Load and merge config
        try:
            raw_config = self.load_toml(config_path)
            config = self._merge_config(config, raw_config)
        except ConfigLoadError:
            # Re-raise config load errors for the caller to handle
            raise

        return config

    def _merge_config(
        self, default_config: DevDashConfig, raw_config: Dict[str, Any]
    ) -> DevDashConfig:
        """Merge raw TOML config with default config.

        Args:
            default_config: Default configuration object
            raw_config: Raw dictionary from TOML file

        Returns:
            DevDashConfig: Merged configuration
        """
        # Create dict to hold merged values
        merged = {}

        # Process each top-level section
        for field in fields(DevDashConfig):
            section_name = field.name
            section_type = field.type
            default_section = getattr(default_config, section_name)

            if section_name in raw_config and is_dataclass(section_type):
                # Merge section with defaults
                raw_section = raw_config[section_name]
                merged_section = self._merge_section(
                    default_section, raw_section, section_type
                )
                merged[section_name] = merged_section
            else:
                # Section not in config, use default
                merged[section_name] = default_section

        return DevDashConfig(**merged)

    def _merge_section(
        self, default_section: Any, raw_section: Dict[str, Any], section_type: type
    ) -> Any:
        """Merge a single config section with its defaults.

        Args:
            default_section: Default section object
            raw_section: Raw dictionary for this section
            section_type: The dataclass type for this section

        Returns:
            Merged section object
        """
        # Get all fields from the section dataclass
        section_fields = {f.name: f.type for f in fields(section_type)}

        # Build merged values
        merged_values = {}
        for field_name, field_type in section_fields.items():
            if field_name in raw_section:
                # Use value from config file
                value = raw_section[field_name]

                # Basic type validation - if type doesn't match, use default
                try:
                    if self._validate_type(value, field_type):
                        merged_values[field_name] = value
                    else:
                        # Type mismatch, use default
                        merged_values[field_name] = getattr(
                            default_section, field_name
                        )
                except Exception:
                    # Any error, use default
                    merged_values[field_name] = getattr(default_section, field_name)
            else:
                # Field not in config, use default
                merged_values[field_name] = getattr(default_section, field_name)

        return section_type(**merged_values)

    def _validate_type(self, value: Any, expected_type: type) -> bool:
        """Basic type validation.

        Args:
            value: Value to validate
            expected_type: Expected type

        Returns:
            bool: True if type matches, False otherwise
        """
        # Handle Optional types
        if hasattr(expected_type, "__origin__"):
            # It's a generic type like Optional[str]
            if expected_type.__origin__ is type(None) or str(
                expected_type
            ).startswith("typing.Union"):
                # For Optional types, check against the inner types
                args = getattr(expected_type, "__args__", ())
                if value is None:
                    return True
                return any(isinstance(value, arg) for arg in args if arg is not type(None))

        # Basic type check
        if expected_type == bool:
            return isinstance(value, bool)
        elif expected_type == int:
            return isinstance(value, int) and not isinstance(value, bool)
        elif expected_type == float:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif expected_type == str:
            return isinstance(value, str)
        else:
            return isinstance(value, expected_type)
