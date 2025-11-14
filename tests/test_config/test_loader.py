"""Tests for configuration loader."""

import pytest
import tempfile
from pathlib import Path
from devdash.config.loader import ConfigLoader, ConfigLoadError
from devdash.config.schema import DevDashConfig, GitConfig, TimerConfig


class TestConfigFileDiscovery:
    """Test configuration file discovery."""

    def test_find_config_file_none_exists(self, monkeypatch, tmp_path):
        """Test find_config_file returns None when no config exists."""
        # Change to a temp directory with no config
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("HOME", str(tmp_path))

        loader = ConfigLoader()
        result = loader.find_config_file()
        assert result is None

    def test_find_config_file_project_level(self, monkeypatch, tmp_path):
        """Test find_config_file finds project-level config first."""
        # Create project-level config
        project_config = tmp_path / ".devdash.toml"
        project_config.write_text("[git]\nenabled = true\n")

        monkeypatch.chdir(tmp_path)

        loader = ConfigLoader()
        result = loader.find_config_file()
        assert result == project_config

    def test_find_config_file_user_level(self, monkeypatch, tmp_path):
        """Test find_config_file finds user-level config."""
        # Create user-level config
        user_config_dir = tmp_path / ".config" / "devdash"
        user_config_dir.mkdir(parents=True)
        user_config = user_config_dir / "config.toml"
        user_config.write_text("[git]\nenabled = true\n")

        # Change HOME but use different working directory
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        monkeypatch.chdir(work_dir)
        monkeypatch.setenv("HOME", str(tmp_path))

        loader = ConfigLoader()
        result = loader.find_config_file()
        assert result == user_config

    def test_find_config_file_home_level(self, monkeypatch, tmp_path):
        """Test find_config_file finds home-level config."""
        # Create home-level config
        home_config = tmp_path / ".devdash.toml"
        home_config.write_text("[git]\nenabled = true\n")

        # Use different working directory
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        monkeypatch.chdir(work_dir)
        monkeypatch.setenv("HOME", str(tmp_path))

        loader = ConfigLoader()
        result = loader.find_config_file()
        assert result == home_config

    def test_find_config_file_priority_order(self, monkeypatch, tmp_path):
        """Test that project-level config takes priority over others."""
        # Create all three config files
        project_config = tmp_path / ".devdash.toml"
        project_config.write_text("[git]\nmax_commits = 1\n")

        user_config_dir = tmp_path / ".config" / "devdash"
        user_config_dir.mkdir(parents=True)
        user_config = user_config_dir / "config.toml"
        user_config.write_text("[git]\nmax_commits = 2\n")

        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("HOME", str(tmp_path))

        loader = ConfigLoader()
        result = loader.find_config_file()
        # Should find project-level first
        assert result == project_config


class TestTOMLLoading:
    """Test TOML file loading."""

    def test_load_toml_valid_file(self, tmp_path):
        """Test loading a valid TOML file."""
        config_file = tmp_path / "test.toml"
        config_file.write_text(
            """
[git]
refresh_interval = 10
max_commits = 5

[timer]
focus_duration = 30
"""
        )

        loader = ConfigLoader()
        result = loader.load_toml(config_file)

        assert isinstance(result, dict)
        assert "git" in result
        assert "timer" in result
        assert result["git"]["refresh_interval"] == 10
        assert result["timer"]["focus_duration"] == 30

    def test_load_toml_invalid_syntax(self, tmp_path):
        """Test loading TOML with invalid syntax raises error."""
        config_file = tmp_path / "bad.toml"
        config_file.write_text(
            """
[git
refresh_interval = 10
"""
        )

        loader = ConfigLoader()
        with pytest.raises(ConfigLoadError, match="Invalid TOML syntax"):
            loader.load_toml(config_file)

    def test_load_toml_permission_error(self, tmp_path):
        """Test loading TOML with permission error."""
        config_file = tmp_path / "restricted.toml"
        config_file.write_text("[git]\nenabled = true\n")
        config_file.chmod(0o000)

        loader = ConfigLoader()
        try:
            with pytest.raises(ConfigLoadError, match="permission denied"):
                loader.load_toml(config_file)
        finally:
            # Restore permissions for cleanup
            config_file.chmod(0o644)

    def test_load_toml_empty_file(self, tmp_path):
        """Test loading empty TOML file."""
        config_file = tmp_path / "empty.toml"
        config_file.write_text("")

        loader = ConfigLoader()
        result = loader.load_toml(config_file)
        assert result == {}


class TestConfigLoading:
    """Test full config loading and merging."""

    def test_load_config_no_file(self, monkeypatch, tmp_path):
        """Test loading config when no file exists returns defaults."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("HOME", str(tmp_path))

        loader = ConfigLoader()
        config = loader.load_config()

        assert isinstance(config, DevDashConfig)
        # Should have default values
        assert config.git.refresh_interval == 5
        assert config.timer.focus_duration == 25

    def test_load_config_with_custom_path(self, tmp_path):
        """Test loading config from custom path."""
        config_file = tmp_path / "custom.toml"
        config_file.write_text(
            """
[git]
refresh_interval = 15
"""
        )

        loader = ConfigLoader()
        config = loader.load_config(custom_path=config_file)

        assert config.git.refresh_interval == 15
        # Other values should be defaults
        assert config.timer.focus_duration == 25

    def test_load_config_partial_config(self, tmp_path):
        """Test loading partial config merges with defaults."""
        config_file = tmp_path / ".devdash.toml"
        config_file.write_text(
            """
[timer]
focus_duration = 50
break_duration = 10
"""
        )

        loader = ConfigLoader()
        config = loader.load_config(custom_path=config_file)

        # Timer values from config
        assert config.timer.focus_duration == 50
        assert config.timer.break_duration == 10
        # Timer defaults for unspecified
        assert config.timer.long_break_duration == 15
        # Other sections default
        assert config.git.refresh_interval == 5
        assert config.system.refresh_interval == 1

    def test_load_config_full_config(self, tmp_path):
        """Test loading full config with all sections."""
        config_file = tmp_path / ".devdash.toml"
        config_file.write_text(
            """
[general]
theme = "dark"

[git]
refresh_interval = 10
max_commits = 5
show_staged = false

[system]
refresh_interval = 2
cpu_warning_threshold = 70.0

[tasks]
default_sort = "priority"
max_visible_tasks = 30

[timer]
focus_duration = 40
break_duration = 8

[ui]
border_style = "rounded"
"""
        )

        loader = ConfigLoader()
        config = loader.load_config(custom_path=config_file)

        assert config.general.theme == "dark"
        assert config.git.refresh_interval == 10
        assert config.git.max_commits == 5
        assert config.git.show_staged is False
        assert config.system.refresh_interval == 2
        assert config.system.cpu_warning_threshold == 70.0
        assert config.tasks.default_sort == "priority"
        assert config.tasks.max_visible_tasks == 30
        assert config.timer.focus_duration == 40
        assert config.timer.break_duration == 8
        assert config.ui.border_style == "rounded"

    def test_load_config_type_mismatch(self, tmp_path):
        """Test loading config with type mismatches uses defaults."""
        config_file = tmp_path / ".devdash.toml"
        config_file.write_text(
            """
[git]
refresh_interval = "five"
enabled = 123
max_commits = 3
"""
        )

        loader = ConfigLoader()
        config = loader.load_config(custom_path=config_file)

        # Type mismatches should fall back to defaults
        assert config.git.refresh_interval == 5  # default
        assert config.git.enabled is True  # default
        # Valid value should be used
        assert config.git.max_commits == 3

    def test_load_config_invalid_toml_raises(self, tmp_path):
        """Test loading invalid TOML raises ConfigLoadError."""
        config_file = tmp_path / ".devdash.toml"
        config_file.write_text("[git\ninvalid")

        loader = ConfigLoader()
        with pytest.raises(ConfigLoadError):
            loader.load_config(custom_path=config_file)

    def test_load_config_optional_fields(self, tmp_path):
        """Test loading config with Optional fields."""
        config_file = tmp_path / ".devdash.toml"
        config_file.write_text(
            """
[tasks]
default_priority_filter = "high"
default_category_filter = "work"
"""
        )

        loader = ConfigLoader()
        config = loader.load_config(custom_path=config_file)

        assert config.tasks.default_priority_filter == "high"
        assert config.tasks.default_category_filter == "work"

    def test_load_config_optional_fields_null(self, tmp_path):
        """Test loading config with null Optional fields."""
        config_file = tmp_path / ".devdash.toml"
        config_file.write_text(
            """
[tasks]
default_sort = "priority"
# default_priority_filter not specified (should be None)
"""
        )

        loader = ConfigLoader()
        config = loader.load_config(custom_path=config_file)

        assert config.tasks.default_sort == "priority"
        assert config.tasks.default_priority_filter is None


class TestConfigMerging:
    """Test configuration merging logic."""

    def test_merge_section_partial_values(self):
        """Test merging section with partial values."""
        loader = ConfigLoader()
        default_config = DevDashConfig()
        raw_config = {"git": {"refresh_interval": 20}}

        merged = loader._merge_config(default_config, raw_config)

        # Specified value from raw config
        assert merged.git.refresh_interval == 20
        # Unspecified values from defaults
        assert merged.git.max_commits == 3
        assert merged.git.show_staged is True

    def test_merge_multiple_sections(self):
        """Test merging multiple sections."""
        loader = ConfigLoader()
        default_config = DevDashConfig()
        raw_config = {
            "git": {"refresh_interval": 15, "max_commits": 7},
            "timer": {"focus_duration": 35},
        }

        merged = loader._merge_config(default_config, raw_config)

        assert merged.git.refresh_interval == 15
        assert merged.git.max_commits == 7
        assert merged.timer.focus_duration == 35
        # Unspecified sections use defaults
        assert merged.system.refresh_interval == 1

    def test_merge_missing_section_uses_default(self):
        """Test that missing sections use defaults."""
        loader = ConfigLoader()
        default_config = DevDashConfig()
        raw_config = {"git": {"refresh_interval": 10}}

        merged = loader._merge_config(default_config, raw_config)

        # Git section merged
        assert merged.git.refresh_interval == 10
        # Other sections use full defaults
        assert merged.timer.focus_duration == 25
        assert merged.system.cpu_warning_threshold == 60.0


class TestTypeValidation:
    """Test type validation helper."""

    def test_validate_type_basic_types(self):
        """Test basic type validation."""
        loader = ConfigLoader()

        assert loader._validate_type(5, int) is True
        assert loader._validate_type("hello", str) is True
        assert loader._validate_type(True, bool) is True
        assert loader._validate_type(3.14, float) is True

    def test_validate_type_bool_not_int(self):
        """Test that bool True/False is not considered an int."""
        loader = ConfigLoader()

        # Bool should not match int type
        assert loader._validate_type(True, int) is False
        assert loader._validate_type(False, int) is False

    def test_validate_type_int_as_float(self):
        """Test that int can be used as float."""
        loader = ConfigLoader()

        assert loader._validate_type(5, float) is True
        assert loader._validate_type(5.5, float) is True

    def test_validate_type_type_mismatch(self):
        """Test type mismatches return False."""
        loader = ConfigLoader()

        assert loader._validate_type("5", int) is False
        assert loader._validate_type(5, str) is False
        assert loader._validate_type(123, bool) is False
