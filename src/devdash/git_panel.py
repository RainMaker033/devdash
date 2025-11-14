"""
Git panel widget - displays repository information
"""

from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Container
from textual.reactive import reactive

try:
    from git import Repo, InvalidGitRepositoryError, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

from devdash.config.schema import GitConfig


class GitPanel(Container):
    """Widget displaying Git repository information."""

    DEFAULT_CSS = """
    GitPanel {
        border: solid $accent;
        padding: 1;
        height: auto;
    }

    GitPanel .panel-title {
        background: $accent;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }

    GitPanel .panel-content {
        padding: 1;
    }
    """

    git_content = reactive("")

    def __init__(self, config: Optional[GitConfig] = None, *args, **kwargs):
        """Initialize Git panel.

        Args:
            config: Git panel configuration. If None, uses defaults.
        """
        super().__init__(*args, **kwargs)
        self.config = config or GitConfig()
        self.repo: Optional[Repo] = None
        self.content_widget: Optional[Static] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("Git Status", classes="panel-title")
        self.content_widget = Static("", classes="panel-content")
        yield self.content_widget

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        if not self.config.enabled:
            self.git_content = "[dim]Git panel disabled in configuration[/]"
            return

        self.refresh_data()
        # Set up periodic refresh using configured interval
        self.set_interval(self.config.refresh_interval, self.refresh_data)

    def watch_git_content(self, new_content: str) -> None:
        """Update content when git_content changes."""
        if self.content_widget:
            self.content_widget.update(new_content)

    def refresh_data(self) -> None:
        """Refresh git data from repository."""
        if not GIT_AVAILABLE:
            self.git_content = "[red]GitPython not available[/]"
            return

        try:
            # Try to open repo from current directory
            if self.repo is None:
                self.repo = Repo(Path.cwd(), search_parent_directories=True)

            # Get current branch
            branch = self.repo.active_branch.name

            # Get status counts (respecting config)
            staged_count = 0
            modified_count = 0
            untracked_count = 0

            if self.config.show_staged:
                staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
                staged_count = len(staged_files)

            if self.config.show_modified:
                changed_files = [item.a_path for item in self.repo.index.diff(None)]
                modified_count = len(changed_files)

            if self.config.show_untracked:
                untracked_files = self.repo.untracked_files
                untracked_count = len(untracked_files)

            # Determine status
            total = staged_count + modified_count + untracked_count
            if total == 0:
                status_text = "[green]Clean[/]"
            else:
                status_text = f"[yellow]Modified ({total} files)[/]"

            # Build file counts line (only show enabled counts)
            file_counts = []
            if self.config.show_staged:
                file_counts.append(f"[dim]Staged:[/] {staged_count}")
            if self.config.show_modified:
                file_counts.append(f"[dim]Modified:[/] {modified_count}")
            if self.config.show_untracked:
                file_counts.append(f"[dim]Untracked:[/] {untracked_count}")
            file_counts_text = "  ".join(file_counts) if file_counts else "[dim]No changes tracked[/]"

            # Get recent commits (use configured max_commits)
            commits_text = ""
            if self.config.max_commits > 0:
                commits = list(self.repo.iter_commits(max_count=self.config.max_commits))
                commit_lines = []
                for commit in commits:
                    short_hash = commit.hexsha[:7]
                    message = commit.message.strip().split('\n')[0][:50]
                    commit_lines.append(f"  • {short_hash} - {message}")
                commits_text = "\n".join(commit_lines) if commit_lines else "  [dim]No commits[/]"

            # Build content
            content_parts = [
                f"[bold cyan]Branch:[/] {branch}",
                f"[bold]Status:[/] {status_text}",
                "",
                file_counts_text,
            ]

            if self.config.max_commits > 0:
                content_parts.extend([
                    "",
                    "[bold]Recent Commits:[/]",
                    commits_text
                ])

            self.git_content = "\n".join(content_parts)

        except InvalidGitRepositoryError:
            self.git_content = "[yellow]Not a git repository[/]\n\n[dim]Navigate to a git repository to see status[/]"
        except GitCommandError as e:
            self.git_content = f"[red]Git error:[/]\n{str(e)}"
        except Exception as e:
            self.git_content = f"[red]Error:[/]\n{str(e)}"

    def update_config(self, new_config: GitConfig) -> None:
        """Update the git configuration and apply changes.

        Args:
            new_config: New git configuration
        """
        old_interval = self.config.refresh_interval
        self.config = new_config

        # If refresh interval changed, restart the timer
        if old_interval != new_config.refresh_interval and self.config.enabled:
            # Clear old interval and set new one
            self.set_interval(self.config.refresh_interval, self.refresh_data, name="git_refresh")

        # Refresh display immediately with new settings
        self.refresh_data()
