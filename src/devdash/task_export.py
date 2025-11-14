"""
Task export functionality - export tasks to various formats.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional
from collections import defaultdict

from devdash.task_model import Task


def export_to_markdown(
    tasks: List[Task],
    output_path: Optional[Path] = None,
    format_type: str = "grouped",
    title: str = "DevDash Tasks"
) -> str:
    """
    Export tasks to Markdown format.

    Args:
        tasks: List of tasks to export
        output_path: Path to save file (None = return string only)
        format_type: "grouped" (by priority), "flat" (simple list), or "category" (by category)
        title: Document title

    Returns:
        Markdown content as string
    """
    if format_type == "grouped":
        content = _export_grouped_by_priority(tasks, title)
    elif format_type == "category":
        content = _export_grouped_by_category(tasks, title)
    else:  # flat
        content = _export_flat(tasks, title)

    # Write to file if path provided
    if output_path:
        output_path.write_text(content)

    return content


def _export_flat(tasks: List[Task], title: str) -> str:
    """Export tasks as flat list."""
    lines = [
        f"# {title}",
        f"",
        f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        f"",
        f"Total tasks: {len(tasks)} | Completed: {sum(1 for t in tasks if t.done)}",
        f"",
        "---",
        f"",
    ]

    # Sort by completion, then priority
    sorted_tasks = sorted(
        tasks,
        key=lambda t: (t.done, {"high": 0, "medium": 1, "low": 2, None: 3}.get(t.priority, 3))
    )

    for task in sorted_tasks:
        checkbox = "[x]" if task.done else "[ ]"
        priority_badge = ""
        if task.priority:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "")
            priority_badge = f" **{priority_emoji} {task.priority.upper()}**"

        due_text = ""
        if task.due_date:
            due_emoji = task.get_due_date_indicator()
            due_text = f" {due_emoji} *Due: {task.due_date}*"

        categories_text = ""
        if task.categories:
            categories_text = " " + " ".join(f"`#{c}`" for c in task.categories)

        lines.append(
            f"- {checkbox} {task.text}{priority_badge}{due_text}{categories_text}"
        )

    return "\n".join(lines)


def _export_grouped_by_priority(tasks: List[Task], title: str) -> str:
    """Export tasks grouped by priority."""
    lines = [
        f"# {title}",
        f"",
        f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        f"",
        f"Total tasks: {len(tasks)} | Completed: {sum(1 for t in tasks if t.done)}",
        f"",
        "---",
        f"",
    ]

    # Group by priority
    priority_groups = {
        "high": [],
        "medium": [],
        "low": [],
        None: []
    }

    for task in tasks:
        priority_groups[task.priority].append(task)

    # Add each priority section
    priority_sections = [
        ("high", "🔴 High Priority", priority_groups["high"]),
        ("medium", "🟡 Medium Priority", priority_groups["medium"]),
        ("low", "🟢 Low Priority", priority_groups["low"]),
        (None, "⚪ No Priority", priority_groups[None]),
    ]

    for priority_key, section_title, group_tasks in priority_sections:
        if not group_tasks:
            continue

        completed = sum(1 for t in group_tasks if t.done)
        lines.append(f"## {section_title}")
        lines.append(f"")
        lines.append(f"*{len(group_tasks)} tasks ({completed} completed)*")
        lines.append(f"")

        # Sort by completion, then due date
        sorted_group = sorted(
            group_tasks,
            key=lambda t: (t.done, t.due_date or "9999-12-31")
        )

        for task in sorted_group:
            checkbox = "[x]" if task.done else "[ ]"

            due_text = ""
            if task.due_date:
                due_emoji = task.get_due_date_indicator()
                due_text = f" {due_emoji} *Due: {task.due_date}*"

            categories_text = ""
            if task.categories:
                categories_text = " " + " ".join(f"`#{c}`" for c in task.categories)

            lines.append(
                f"- {checkbox} {task.text}{due_text}{categories_text}"
            )

        lines.append("")

    return "\n".join(lines)


def _export_grouped_by_category(tasks: List[Task], title: str) -> str:
    """Export tasks grouped by category."""
    lines = [
        f"# {title}",
        f"",
        f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        f"",
        f"Total tasks: {len(tasks)} | Completed: {sum(1 for t in tasks if t.done)}",
        f"",
        "---",
        f"",
    ]

    # Group by categories
    category_tasks = defaultdict(list)
    uncategorized = []

    for task in tasks:
        if task.categories:
            for category in task.categories:
                category_tasks[category].append(task)
        else:
            uncategorized.append(task)

    # Sort categories alphabetically
    sorted_categories = sorted(category_tasks.keys())

    # Add each category section
    for category in sorted_categories:
        group_tasks = category_tasks[category]
        completed = sum(1 for t in group_tasks if t.done)

        lines.append(f"## 📁 {category}")
        lines.append(f"")
        lines.append(f"*{len(group_tasks)} tasks ({completed} completed)*")
        lines.append(f"")

        # Sort by priority, then completion
        sorted_group = sorted(
            group_tasks,
            key=lambda t: (
                {"high": 0, "medium": 1, "low": 2, None: 3}.get(t.priority, 3),
                t.done
            )
        )

        for task in sorted_group:
            checkbox = "[x]" if task.done else "[ ]"

            priority_badge = ""
            if task.priority:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "")
                priority_badge = f" **{priority_emoji}**"

            due_text = ""
            if task.due_date:
                due_emoji = task.get_due_date_indicator()
                due_text = f" {due_emoji} *{task.due_date}*"

            lines.append(
                f"- {checkbox} {task.text}{priority_badge}{due_text}"
            )

        lines.append("")

    # Add uncategorized section
    if uncategorized:
        lines.append(f"## 📋 Uncategorized")
        lines.append(f"")
        lines.append(f"*{len(uncategorized)} tasks*")
        lines.append(f"")

        sorted_uncategorized = sorted(
            uncategorized,
            key=lambda t: (
                {"high": 0, "medium": 1, "low": 2, None: 3}.get(t.priority, 3),
                t.done
            )
        )

        for task in sorted_uncategorized:
            checkbox = "[x]" if task.done else "[ ]"

            priority_badge = ""
            if task.priority:
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "")
                priority_badge = f" **{priority_emoji}**"

            due_text = ""
            if task.due_date:
                due_emoji = task.get_due_date_indicator()
                due_text = f" {due_emoji} *{task.due_date}*"

            lines.append(
                f"- {checkbox} {task.text}{priority_badge}{due_text}"
            )

        lines.append("")

    return "\n".join(lines)


def get_export_filename(format_type: str = "grouped") -> str:
    """Generate a filename for export."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"devdash_tasks_{format_type}_{timestamp}.md"


def export_tasks_to_file(
    tasks: List[Task],
    directory: Path = None,
    format_type: str = "grouped"
) -> Path:
    """
    Export tasks to a Markdown file.

    Args:
        tasks: List of tasks to export
        directory: Directory to save file (defaults to current directory)
        format_type: Export format ("grouped", "flat", or "category")

    Returns:
        Path to created file
    """
    if directory is None:
        directory = Path.cwd()

    filename = get_export_filename(format_type)
    filepath = directory / filename

    content = export_to_markdown(tasks, output_path=filepath, format_type=format_type)

    return filepath
