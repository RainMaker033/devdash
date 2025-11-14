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
- Multi-repository support
- Performance optimizations

## [0.2.0] - 2025-11-13

### Added - Enhanced Task Management

**Major Features:**
- **Task Priorities**: Three levels (High 🔴, Medium 🟡, Low 🟢) with visual indicators
- **Due Dates**: ISO format dates with smart indicators (⚠️ overdue, 📅 due soon, 📆 future)
- **Categories/Tags**: Multiple tags per task for organization
- **Full Task Editor**: Modal dialog for editing all task fields (press `e`)
- **Quick Priority**: Fast priority setting with keyboard shortcut (press `p`)
- **Markdown Export**: Three export formats (grouped, flat, category-based)
- **Filter & Sort**: Multiple filtering and sorting options
- **Backward Compatibility**: Automatic migration of old task files

**New Task Features:**
- Edit modal with form fields for all task attributes
- Priority quick-set modal with number key shortcuts
- Visual display of priorities, due dates, and categories in task list
- Task data model with validation
- Migration system for legacy task format

**Keyboard Shortcuts Added:**
- `e` - Open full task editor
- `p` - Quick set priority
- `f` - Toggle filter (show/hide completed)
- `s` - Cycle sort options
- `x` - Export tasks to Markdown
- `1`/`2`/`3` - Filter by high/medium/low priority
- `0` - Clear all filters

**Export Functionality:**
- Export to Markdown in grouped format (by priority)
- Export to Markdown in flat format (simple list)
- Export to Markdown grouped by category
- Automatic filename generation with timestamps
- Rich formatting with emojis and metadata

### Technical Improvements

**New Modules:**
- `task_model.py` - Enhanced Task dataclass with validation
- `task_edit_modal.py` - Full-featured editing dialogs
- `task_export.py` - Markdown export functionality

**Enhanced Modules:**
- `tasks_panel.py` - Complete rewrite with new features
- `help_modal.py` - Updated with all new shortcuts

**Testing:**
- 25 new tests for task model
- 15 new tests for export functionality
- Total test suite: 48 tests (all passing)
- Comprehensive coverage of new features

**Data Model:**
```json
{
  "id": 1,
  "text": "Task description",
  "done": false,
  "priority": "high|medium|low|null",
  "due_date": "YYYY-MM-DD",
  "categories": ["tag1", "tag2"],
  "created_at": "ISO8601 datetime"
}
```

### Changed
- Tasks panel now uses enhanced Task model instead of plain dictionaries
- Task display includes priority emojis, due date indicators, and category tags
- Filter status now shown in panel header
- Task text truncated at 40 chars (was 50) to make room for metadata

### Documentation
- Updated README with all new features
- Updated keyboard shortcuts table
- Updated help modal with comprehensive shortcuts
- Added detailed feature descriptions

## [0.1.1] - 2025-11-13

### Changed
- Updated branding: "devdash" → "DevDash" in documentation
- Updated all repository URLs to https://github.com/RainMaker033/devdash
- Updated author information in package metadata

### Documentation
- README: Capitalized product name to "DevDash"
- CONTRIBUTING.md: Updated clone URLs
- CHANGELOG.md: Updated project links
- pyproject.toml: Updated repository URLs

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

- **Homepage**: https://github.com/RainMaker033/devdash
- **Issues**: https://github.com/RainMaker033/devdash/issues
- **Releases**: https://github.com/RainMaker033/devdash/releases

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.2.0 | 2025-11-13 | Enhanced task management with priorities, due dates, categories, export |
| 0.1.1 | 2025-11-13 | Documentation and branding updates |
| 0.1.0 | 2025-11-13 | Initial release with all four panels |

[Unreleased]: https://github.com/RainMaker033/devdash/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/RainMaker033/devdash/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/RainMaker033/devdash/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/RainMaker033/devdash/releases/tag/v0.1.0
