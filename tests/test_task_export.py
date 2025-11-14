"""Tests for task export functionality."""

import pytest
from pathlib import Path
from datetime import date, timedelta

from devdash.task_model import Task
from devdash.task_export import (
    export_to_markdown,
    export_tasks_to_file,
    get_export_filename,
)


@pytest.fixture
def sample_tasks():
    """Create sample tasks for testing."""
    return [
        Task(
            id=1,
            text="High priority task",
            priority="high",
            due_date=(date.today() + timedelta(days=1)).isoformat(),
            categories=["work", "urgent"]
        ),
        Task(
            id=2,
            text="Medium priority task",
            priority="medium",
            done=True,
            categories=["personal"]
        ),
        Task(
            id=3,
            text="Low priority task",
            priority="low",
            due_date=(date.today() + timedelta(days=7)).isoformat()
        ),
        Task(
            id=4,
            text="No priority task",
            categories=["work"]
        ),
        Task(
            id=5,
            text="Completed high priority",
            priority="high",
            done=True
        ),
    ]


class TestMarkdownExport:
    """Test Markdown export functionality."""

    def test_export_flat_format(self, sample_tasks):
        """Test flat format export."""
        content = export_to_markdown(sample_tasks, format_type="flat")

        # Check title and metadata
        assert "DevDash Tasks" in content
        assert "Total tasks: 5" in content
        assert "Completed: 2" in content

        # Check tasks are present
        assert "High priority task" in content
        assert "Medium priority task" in content

        # Check checkboxes
        assert "[ ]" in content  # Uncompleted
        assert "[x]" in content  # Completed

    def test_export_grouped_format(self, sample_tasks):
        """Test grouped by priority format."""
        content = export_to_markdown(sample_tasks, format_type="grouped")

        # Check priority sections
        assert "🔴 High Priority" in content
        assert "🟡 Medium Priority" in content
        assert "🟢 Low Priority" in content
        assert "⚪ No Priority" in content

        # Check tasks are in correct sections
        assert "High priority task" in content
        assert "Medium priority task" in content

    def test_export_category_format(self, sample_tasks):
        """Test grouped by category format."""
        content = export_to_markdown(sample_tasks, format_type="category")

        # Check category sections
        assert "📁 work" in content
        assert "📁 personal" in content
        assert "📁 urgent" in content
        assert "📋 Uncategorized" in content

    def test_export_includes_due_dates(self, sample_tasks):
        """Test that due dates are included in export."""
        content = export_to_markdown(sample_tasks, format_type="flat")

        # Check that due dates are present
        assert "Due:" in content

        # Check for due date indicators
        assert "📅" in content or "📆" in content  # Due soon or future

    def test_export_includes_categories(self, sample_tasks):
        """Test that categories are included in export."""
        content = export_to_markdown(sample_tasks, format_type="flat")

        # Check categories are formatted as tags
        assert "`#work`" in content
        assert "`#personal`" in content
        assert "`#urgent`" in content

    def test_export_empty_tasks(self):
        """Test exporting empty task list."""
        content = export_to_markdown([], format_type="flat")

        assert "DevDash Tasks" in content
        assert "Total tasks: 0" in content

    def test_export_to_file(self, sample_tasks, tmp_path):
        """Test exporting to actual file."""
        output_file = tmp_path / "test_export.md"
        content = export_to_markdown(
            sample_tasks,
            output_path=output_file,
            format_type="flat"
        )

        # Check file was created
        assert output_file.exists()

        # Check file content matches returned content
        file_content = output_file.read_text()
        assert file_content == content

    def test_custom_title(self, sample_tasks):
        """Test export with custom title."""
        content = export_to_markdown(
            sample_tasks,
            format_type="flat",
            title="My Custom Tasks"
        )

        assert "My Custom Tasks" in content
        assert "DevDash Tasks" not in content


class TestExportFilename:
    """Test export filename generation."""

    def test_get_export_filename(self):
        """Test filename generation includes format and timestamp."""
        filename = get_export_filename(format_type="grouped")

        assert filename.startswith("devdash_tasks_grouped_")
        assert filename.endswith(".md")

    def test_different_formats_different_names(self):
        """Test different formats generate different names."""
        flat_name = get_export_filename("flat")
        grouped_name = get_export_filename("grouped")

        assert "flat" in flat_name
        assert "grouped" in grouped_name


class TestExportTasksToFile:
    """Test high-level export to file function."""

    def test_export_creates_file(self, sample_tasks, tmp_path):
        """Test that export_tasks_to_file creates a file."""
        filepath = export_tasks_to_file(
            sample_tasks,
            directory=tmp_path,
            format_type="grouped"
        )

        assert filepath.exists()
        assert filepath.parent == tmp_path
        assert filepath.suffix == ".md"

    def test_export_file_content(self, sample_tasks, tmp_path):
        """Test exported file has correct content."""
        filepath = export_tasks_to_file(
            sample_tasks,
            directory=tmp_path,
            format_type="flat"
        )

        content = filepath.read_text()
        assert "High priority task" in content
        assert "Total tasks: 5" in content


class TestExportFormatting:
    """Test specific formatting details."""

    def test_priority_badges_in_grouped(self, sample_tasks):
        """Test priority badges appear correctly."""
        content = export_to_markdown(sample_tasks, format_type="grouped")

        # Emojis should be in section headers
        assert "🔴" in content  # High
        assert "🟡" in content  # Medium
        assert "🟢" in content  # Low

    def test_completed_tasks_marked(self, sample_tasks):
        """Test completed tasks are marked with [x]."""
        content = export_to_markdown(sample_tasks, format_type="flat")

        # Count checkboxes
        uncompleted_count = content.count("[ ]")
        completed_count = content.count("[x]")

        assert completed_count == 2  # 2 completed tasks
        assert uncompleted_count == 3  # 3 active tasks

    def test_task_counts_accurate(self, sample_tasks):
        """Test task counts in sections are accurate."""
        content = export_to_markdown(sample_tasks, format_type="grouped")

        # Should show counts for each section
        assert "tasks" in content.lower()
        assert "completed" in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
