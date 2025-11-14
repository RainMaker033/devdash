# Changelog

All notable changes to devdash will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Configuration file support (.devdash.toml)
- Custom theme support
- Plugin system
- Sound notifications for timer
- Export tasks to Markdown
- Multi-repository support
- Performance optimizations

## [0.1.0] - 2025-11-13

### Added

#### Core Features
- **Terminal Dashboard** - Unified interface showing all developer tools in one screen
- **Four Panel Layout** - Git, System, Tasks, and Timer panels in a responsive grid

#### Git Panel
- Real-time repository status monitoring
- Current branch display
- File change counts (staged, modified, untracked)
- Last 3 commits with messages
- Auto-refresh every 5 seconds
- Graceful handling of non-git directories
- Uses GitPython for reliable git operations

#### System Panel
- Real-time CPU usage monitoring with visual progress bars
- RAM usage with human-readable formatting (GB/MB)
- Disk usage for current directory
- Session uptime tracking
- Load average display (Unix/Linux/macOS)
- Color-coded metrics (green/yellow/red based on usage)
- Updates every 1 second

#### Tasks Panel
- JSON-based task persistence (.devdash_tasks.json)
- Add tasks with 'a' key
- Toggle task completion with 'space'
- Delete tasks with 'd' key
- Navigate tasks with arrow keys
- Visual checkboxes for completion status
- Selected task highlighting
- Automatic save on all changes

#### Timer Panel (Pomodoro)
- Three states: idle, focus, break
- 25-minute focus sessions
- 5-minute break sessions
- Countdown timer display (MM:SS format)
- Visual progress bar
- Keyboard controls: 'f' (focus), 'b' (break), 's' (stop)
- Auto-stop when timer completes
- Real-time updates every second

#### User Interface
- Keyboard-driven navigation
- Help modal ('?' key) with all shortcuts
- Quit with 'q' or Ctrl+C
- Refresh all panels with 'r'
- Footer with visible keybindings
- Header with current directory and time
- Color-coded panels for visual distinction
- Responsive layout using Textual framework

#### Developer Experience
- Clean project structure
- Comprehensive README with installation and usage
- MIT License
- CONTRIBUTING.md with development guidelines
- Type hints throughout codebase
- Modular panel architecture
- Error handling for all external operations

### Technical Details
- **Framework**: Textual 0.47.0+
- **Language**: Python 3.9+
- **Dependencies**:
  - textual (TUI framework)
  - psutil (system metrics)
  - GitPython (git operations)
- **Development**: Black, Ruff, pytest
- **Packaging**: Modern pyproject.toml configuration

### Known Limitations
- Tasks are stored per-directory (no global task list)
- No configuration file support yet
- No custom timer durations
- No notifications when timer completes
- Git panel may be slow on very large repositories
- No Windows testing yet (should work but unverified)

## Project Links

- **Homepage**: https://github.com/yourusername/devdash
- **Issues**: https://github.com/yourusername/devdash/issues
- **Releases**: https://github.com/yourusername/devdash/releases

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.1.0 | 2025-11-13 | Initial release with all four panels |

[Unreleased]: https://github.com/yourusername/devdash/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/devdash/releases/tag/v0.1.0
