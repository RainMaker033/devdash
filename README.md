# DevDash

> A terminal dashboard for developers

![Version](https://img.shields.io/badge/version-0.2.2-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**DevDash** is a terminal dashboard that brings together the essential information you need while coding:

- **Git Status** - Current branch, changes, and recent commits at a glance
- **System Stats** - CPU, RAM, and disk usage monitoring
- **Task List** - Simple TODO tracker integrated into your terminal
- **Pomodoro Timer** - Stay focused with built-in time management

Stop alt-tabbing between multiple terminal windows. Get everything in one unified, beautiful interface.

## Features

### Git Panel
- Current branch name
- Clean/dirty repository status
- Counts: staged, modified, untracked files
- Last 3 commits with messages

### System Panel
- Real-time CPU usage
- RAM usage with visual progress bar
- Disk usage for current directory
- Session uptime (optional)

### Tasks Panel
- **Enhanced task management** with priorities, due dates, and categories
- **Priority levels**: 🔴 High, 🟡 Medium, 🟢 Low with visual indicators
- **Due dates** with smart indicators (⚠️ overdue, 📅 due soon, 📆 future)
- **Categories/tags** for organization and filtering
- **Full-featured editor** with modal dialog for detailed task editing
- **Quick actions**: Add, edit, toggle, delete with keyboard shortcuts
- **Filter & sort**: Filter by priority/category, sort by date/priority/text
- **Export to Markdown**: Generate formatted task lists in multiple formats
- **Backward compatible**: Automatically migrates old task files
- Persistent storage in `.devdash_tasks.json`

### Timer Panel
- Pomodoro technique: 25min focus, 5min break
- Visual countdown timer
- States: idle, focus, break
- Keyboard controls for start/stop

## Installation

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/RainMaker033/devdash.git
cd devdash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run it
devdash
```

### From PyPI (Coming Soon)

```bash
pip install devdash
devdash
```

## Usage

Simply run `devdash` in any directory:

```bash
devdash
```

The dashboard will automatically:
- Detect if you're in a Git repository
- Monitor system resources
- Load tasks from local `.devdash_tasks.json` (if it exists)
- Start in idle timer mode

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **General** | |
| `q` or `Ctrl+C` | Quit DevDash |
| `?` | Show help popup |
| `c` | Open configuration editor |
| `r` | Refresh all panels |
| **Tasks Panel - Basic** | |
| `a` | Add new task (quick mode) |
| `e` | Edit task (full editor with all fields) |
| `space` | Toggle task done/undone |
| `d` | Delete selected task |
| `↑` / `↓` | Navigate tasks |
| **Tasks Panel - Advanced** | |
| `p` | Quick set priority for selected task |
| `f` | Toggle filter (show/hide completed) |
| `s` | Cycle sort (created/priority/due date/text) |
| `x` | Export tasks to Markdown file |
| `1` | Filter to show only high priority |
| `2` | Filter to show only medium priority |
| `3` | Filter to show only low priority |
| `0` | Clear all filters |
| **Timer Panel** | |
| `Shift+F` | Start focus session (25min) |
| `Shift+B` | Start break (5min) |
| `Shift+S` | Stop timer / return to idle |

## Configuration

DevDash can be customized using a `.devdash.toml` configuration file.

### Quick Start

**Option 1: Use the Built-in Config Editor (Easiest)**

1. Run DevDash: `devdash`
2. Press `c` to open the configuration editor
3. Edit settings with a visual TUI interface
4. Press `Ctrl+S` to save (or click "Save" button)

**Option 2: Generate Config File Manually**

Generate an example configuration file:

```bash
devdash --generate-config > .devdash.toml
```

Or create `.devdash.toml` in your project or home directory with your custom settings:

```toml
[timer]
focus_duration = 50  # Longer focus sessions
break_duration = 10

[system]
refresh_interval = 2  # Slower updates
cpu_warning_threshold = 70.0
cpu_critical_threshold = 90.0

[git]
max_commits = 5  # Show more commits
```

### Configuration File Locations

DevDash looks for configuration files in this order (first found wins):

1. `./.devdash.toml` (current directory - project-specific)
2. `~/.config/devdash/config.toml` (user config directory)
3. `~/.devdash.toml` (home directory)

### CLI Options

```bash
devdash                          # Run with default or discovered config
devdash --config my-config.toml  # Use a custom config file
devdash --validate-config        # Check your config for errors
devdash --show-config            # Display current configuration
devdash --generate-config        # Generate example config to stdout
devdash --version                # Show version
devdash --help                   # Show all options
```

### Configuration Options

**Git Panel:**
- `enabled` - Show/hide panel (default: `true`)
- `refresh_interval` - Update frequency in seconds (default: `5`)
- `max_commits` - Number of recent commits to display (default: `3`)
- `show_staged/modified/untracked` - Toggle file categories (default: `true`)

**System Panel:**
- `enabled` - Show/hide panel (default: `true`)
- `refresh_interval` - Update frequency in seconds (default: `1`)
- `show_cpu/ram/disk/uptime/load_avg` - Toggle individual metrics (default: `true`)
- `cpu_warning_threshold` - Yellow warning % (default: `60.0`)
- `cpu_critical_threshold` - Red critical % (default: `80.0`)
- `progress_bar_width` - Progress bar size (default: `10`)

**Tasks Panel:**
- `enabled` - Show/hide panel (default: `true`)
- `file_path` - Tasks file location (default: `.devdash_tasks.json`)
- `default_sort` - Initial sort order: `created`, `priority`, `due_date`, `text` (default: `created`)
- `show_completed` - Show done tasks by default (default: `true`)
- `default_priority_filter` - Initial filter: `null`, `high`, `medium`, `low` (default: `null`)
- `max_visible_tasks` - Pagination limit (default: `20`)
- `truncate_length` - Text truncation threshold (default: `40`)

**Timer Panel:**
- `enabled` - Show/hide panel (default: `true`)
- `focus_duration` - Focus session length in minutes (default: `25`)
- `break_duration` - Break length in minutes (default: `5`)
- `show_progress_bar` - Show progress visualization (default: `true`)
- `progress_bar_width` - Progress bar size (default: `20`)

See [`docs/config-example.toml`](docs/config-example.toml) for a complete example with all available options and detailed comments.

## Requirements

- Python 3.9+
- Git (for Git panel functionality)
- Textual (TUI framework)
- psutil (system metrics)
- GitPython (Git operations)

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

### Project Structure

```
devdash/
├── src/
│   └── devdash/
│       ├── __init__.py
│       ├── main.py          # Entry point & main app
│       ├── git_panel.py     # Git information
│       ├── system_panel.py  # System metrics
│       ├── tasks_panel.py   # Task management
│       └── timer_panel.py   # Pomodoro timer
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Good First Issues

- Add dark/light theme toggle
- Support custom Git remote name display
- Add configuration file support
- Implement sound/notification when timer ends
- Add export tasks to Markdown

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built with:
- [Textual](https://github.com/Textualize/textual) - Amazing TUI framework
- [psutil](https://github.com/giampaolo/psutil) - System monitoring
- [GitPython](https://github.com/gitpython-developers/GitPython) - Git operations

## Roadmap

- [ ] v0.1.0 - MVP with all 4 panels working
- [ ] v0.2.0 - Configuration file support
- [ ] v0.3.0 - Themes and customization
- [ ] v0.4.0 - Plugin system
- [ ] v1.0.0 - Stable release

---

**Note**: This is alpha software under active development. Expect breaking changes before v1.0.
