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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.repo: Optional[Repo] = None
        self.content_widget: Optional[Static] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Static("Git Status", classes="panel-title")
        self.content_widget = Static("", classes="panel-content")
        yield self.content_widget

    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.refresh_data()
        # Set up periodic refresh every 5 seconds
        self.set_interval(5, self.refresh_data)

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

            # Get status counts
            changed_files = [item.a_path for item in self.repo.index.diff(None)]
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            untracked_files = self.repo.untracked_files

            staged_count = len(staged_files)
            modified_count = len(changed_files)
            untracked_count = len(untracked_files)

            # Determine status
            if staged_count + modified_count + untracked_count == 0:
                status_text = "[green]Clean[/]"
            else:
                total = staged_count + modified_count + untracked_count
                status_text = f"[yellow]Modified ({total} files)[/]"

            # Get recent commits (last 3)
            commits = list(self.repo.iter_commits(max_count=3))
            commit_lines = []
            for commit in commits:
                short_hash = commit.hexsha[:7]
                message = commit.message.strip().split('\n')[0][:50]
                commit_lines.append(f"  • {short_hash} - {message}")

            commits_text = "\n".join(commit_lines) if commit_lines else "  [dim]No commits[/]"

            # Build content
            self.git_content = f"""[bold cyan]Branch:[/] {branch}
[bold]Status:[/] {status_text}

[dim]Staged:[/] {staged_count}  [dim]Modified:[/] {modified_count}  [dim]Untracked:[/] {untracked_count}

[bold]Recent Commits:[/]
{commits_text}
"""

        except InvalidGitRepositoryError:
            self.git_content = "[yellow]Not a git repository[/]\n\n[dim]Navigate to a git repository to see status[/]"
        except GitCommandError as e:
            self.git_content = f"[red]Git error:[/]\n{str(e)}"
        except Exception as e:
            self.git_content = f"[red]Error:[/]\n{str(e)}"
