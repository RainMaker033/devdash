# devdash

> A terminal dashboard for developers

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**devdash** is a terminal dashboard that brings together the essential information you need while coding:

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
- Simple JSON-based task storage
- Add, toggle, delete tasks with keyboard shortcuts
- Persistent across sessions
- Stored locally in `.devdash_tasks.json`

### Timer Panel
- Pomodoro technique: 25min focus, 5min break
- Visual countdown timer
- States: idle, focus, break
- Keyboard controls for start/stop

## Installation

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/devdash.git
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
| `q` or `Ctrl+C` | Quit devdash |
| `?` | Show help popup |
| `r` | Refresh all panels |
| **Tasks Panel** | |
| `a` | Add new task |
| `space` | Toggle task done/undone |
| `d` | Delete selected task |
| **Timer Panel** | |
| `f` | Start focus session (25min) |
| `b` | Start break (5min) |
| `s` | Stop timer / return to idle |

## Configuration

(Coming in future versions)

Create a `.devdash.toml` in your home directory or project root:

```toml
[git]
enabled = true
refresh_interval = 5  # seconds

[system]
enabled = true
refresh_interval = 1  # seconds

[timer]
focus_duration = 25  # minutes
break_duration = 5   # minutes

[tasks]
file_path = ".devdash_tasks.json"
```

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
