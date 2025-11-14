# Contributing to devdash

Thank you for your interest in contributing to devdash! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Running Tests](#running-tests)
- [Submitting Changes](#submitting-changes)
- [Style Guide](#style-guide)

## Code of Conduct

Be respectful, constructive, and professional. We're all here to build something useful together.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A terminal emulator (iTerm2, Windows Terminal, etc.)

### Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/yourusername/devdash.git
cd devdash
```

2. **Create a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install in development mode**

```bash
pip install -e ".[dev]"
```

4. **Run devdash to verify setup**

```bash
devdash
```

## Making Changes

### Creating a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Use descriptive branch names:
- `feature/add-git-log-view`
- `fix/timer-not-stopping`
- `docs/update-readme`

### Project Structure

```
devdash/
├── src/devdash/           # Main source code
│   ├── main.py           # Entry point & app
│   ├── git_panel.py      # Git panel widget
│   ├── system_panel.py   # System metrics widget
│   ├── tasks_panel.py    # Tasks management widget
│   ├── timer_panel.py    # Pomodoro timer widget
│   └── help_modal.py     # Help popup
├── tests/                # Test files
├── docs/                 # Documentation
└── pyproject.toml        # Package configuration
```

### Code Style

This project uses:
- **Black** for code formatting
- **Ruff** for linting

Before committing:

```bash
# Format code
black src/

# Check linting
ruff check src/
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=devdash

# Run specific test file
pytest tests/test_git_panel.py
```

## Submitting Changes

### Before Submitting

- [ ] Code passes all tests
- [ ] Code is formatted with Black
- [ ] No linting errors from Ruff
- [ ] Documentation updated (if needed)
- [ ] CHANGELOG.md updated (if significant change)

### Pull Request Process

1. **Push your changes**

```bash
git push origin feature/your-feature-name
```

2. **Create a Pull Request**

- Go to the GitHub repository
- Click "New Pull Request"
- Select your branch
- Fill in the PR template

3. **PR Title Format**

Use conventional commits style:

- `feat: add custom theme support`
- `fix: timer not stopping correctly`
- `docs: update installation instructions`
- `refactor: simplify git panel logic`
- `test: add tests for tasks panel`

4. **PR Description**

Include:
- What changed and why
- Any breaking changes
- Screenshots (if UI changes)
- Related issues (e.g., "Closes #123")

### After Submitting

- Respond to review feedback
- Make requested changes
- Push updates to the same branch

## Style Guide

### Python Code

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for classes and functions
- Keep functions focused and small

Example:

```python
def format_time(seconds: int) -> str:
    """
    Format seconds as MM:SS.

    Args:
        seconds: Number of seconds to format

    Returns:
        Formatted time string (e.g., "05:30")
    """
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"
```

### Textual Widgets

- Use reactive properties for dynamic content
- Separate logic from display
- Handle errors gracefully
- Add CSS in DEFAULT_CSS constant

### Commit Messages

- Use present tense ("Add feature" not "Added feature")
- First line: short summary (50 chars or less)
- Blank line, then detailed explanation if needed
- Reference issues: "Fixes #123"

Example:

```
Add custom theme support

- Add theme configuration to config file
- Support dark/light mode toggle
- Update README with theme instructions

Closes #45
```

## Good First Issues

Look for issues labeled `good first issue` or `help wanted`. These are great entry points for new contributors.

Some ideas:
- Add tests for existing panels
- Improve error messages
- Add configuration options
- Write documentation
- Fix typos or improve README

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to devdash! Your efforts help make this tool better for everyone.
