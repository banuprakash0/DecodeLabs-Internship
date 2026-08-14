"""Presentation & UI View Layer for TaskManager System.

Builds a modern, dark-themed, responsive terminal user interface using Rich.
Renders panels, tables, badges, statistics cards, progress bars, and prompts.
"""

import sys
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, BarColumn, TextColumn
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule

from models import Task, Priority, Status
from utils import format_date, format_datetime, truncate_text
from config import config

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(legacy_windows=False)



class TerminalView:
    """Renders visual components, forms, tables, and statistics dashboard."""

    @staticmethod
    def clear() -> None:
        """Clear terminal console screen."""
        console.clear()

    @staticmethod
    def render_header() -> None:
        """Render stylish top header banner."""
        header_text = Text()
        header_text.append("⚡ ", style="bold gold1")
        header_text.append(config.app_name.upper(), style="bold cyan")
        header_text.append(f"  v{config.version}", style="bold dim white")
        header_text.append("  |  Production Enterprise CLI", style="italic dim bright_blue")
        
        console.print(Panel(Align.center(header_text), border_style="bold cyan", expand=True))

    @staticmethod
    def render_menu() -> str:
        """Render main menu options and return selected choice."""
        menu_table = Table(show_header=False, box=None, padding=(0, 2))
        menu_table.add_column("Key", style="bold yellow", justify="right")
        menu_table.add_column("Action", style="bold white")

        options = [
            ("1", "➕ Add New Task"),
            ("2", "📋 View All Tasks"),
            ("3", "🔍 Search Tasks"),
            ("4", "🎯 Filter Tasks (Status / Priority / Category)"),
            ("5", "↕️  Sort Tasks"),
            ("6", "✏️  Edit Task"),
            ("7", "✅ Mark Task as Completed"),
            ("8", "🗑️  Delete Task"),
            ("9", "↩️  Undo Last Delete"),
            ("10", "📊 Statistics Dashboard"),
            ("11", "💾 CSV Data & Backup / Restore"),
            ("12", "📜 View Activity Logs"),
            ("13", "🔐 Password Security Settings"),
            ("0", "🚪 Exit Application"),
        ]

        for key, action in options:
            menu_table.add_row(f"[{key}]", action)

        panel = Panel(
            menu_table,
            title="[bold magenta]MAIN MENU[/bold magenta]",
            subtitle="Select option [0-13]",
            border_style="magenta",
            expand=True,
        )
        console.print(panel)
        return Prompt.ask("[bold green]Enter choice[/bold green]", choices=[str(i) for i in range(14)], default="2")

    @staticmethod
    def render_empty_state(title: str, message: str, tip: str = "") -> None:
        """Render a visually polished empty-state callout panel."""
        content = f"[bold yellow]📭 {title}[/bold yellow]\n[white]{message}[/white]"
        if tip:
            content += f"\n\n[dim italic]💡 Tip: {tip}[/dim italic]"
        console.print(Panel(Align.center(content), border_style="yellow", expand=True))

    @staticmethod
    def render_tasks_table(tasks: List[Task], title: str = "TASK LIST") -> None:
        """Render formatted data table of tasks."""
        if not tasks:
            TerminalView.render_empty_state(
                title="No Tasks Found",
                message="No task records match your selection or search criteria.",
                tip="Try clearing your active filters, using broader search keywords, or adding a new task.",
            )
            return

        table = Table(
            title=f"[bold cyan]{title}[/bold cyan] ({len(tasks)} items)",
            header_style="bold magenta",
            border_style="dim white",
            caption=f"[dim]Total {len(tasks)} task(s) displayed[/dim]",
            expand=True,
        )

        table.add_column("ID", style="bold yellow", width=11)
        table.add_column("Title", style="bold white", min_width=22)
        table.add_column("Category", style="cyan", width=14)
        table.add_column("Priority", justify="center", width=12)
        table.add_column("Status", justify="center", width=16)
        table.add_column("Due Date", justify="center", width=14)
        table.add_column("Overdue", justify="center", width=10)

        for task in tasks:
            priority_cell = f"[{task.priority.badge_color}]{task.priority.value}[/{task.priority.badge_color}]"
            status_cell = f"{task.status.icon} [{task.status.badge_color}]{task.status.value}[/{task.status.badge_color}]"
            due_str = format_date(task.due_date)
            
            overdue_cell = "[bold red]YES ⚠️[/bold red]" if task.is_overdue() else ("[green]NO[/green]" if task.due_date else "-")
            if task.is_due_today():
                due_str = f"[bold yellow]{due_str} (Today)[/bold yellow]"

            table.add_row(
                task.id,
                truncate_text(task.title, 32),
                task.category,
                priority_cell,
                status_cell,
                due_str,
                overdue_cell,
            )

        console.print(table)

    @staticmethod
    def render_dashboard(stats: Dict[str, Any]) -> None:
        """Render metrics dashboard panels and progress indicators."""
        total = stats["total_tasks"]
        completed = stats["completed_tasks"]
        pending = stats["pending_tasks"]
        in_progress = stats["in_progress_tasks"]
        high_prio = stats["high_priority_tasks"]
        low_prio = stats.get("low_priority_tasks", 0)
        pct = stats["completion_percentage"]
        due_today = stats["tasks_due_today"]
        overdue = stats["overdue_tasks"]

        # Metric Cards
        p1 = Panel(f"[bold cyan]{total}[/bold cyan]", title="Total Tasks", border_style="cyan")
        p2 = Panel(f"[bold green]{completed}[/bold green]", title="Completed", border_style="green")
        p3 = Panel(f"[bold magenta]{pending}[/bold magenta]", title="Pending", border_style="magenta")
        p4 = Panel(f"[bold blue]{in_progress}[/bold blue]", title="In Progress", border_style="blue")
        p5 = Panel(f"[bold red]{high_prio}[/bold red]", title="High Priority", border_style="red")
        p6 = Panel(f"[bold cyan]{low_prio}[/bold cyan]", title="Low Priority", border_style="cyan")
        p7 = Panel(f"[bold red]{overdue}[/bold red]", title="Overdue ⚠️", border_style="bright_red")
        p8 = Panel(f"[bold yellow]{due_today}[/bold yellow]", title="Due Today 📅", border_style="yellow")

        console.print(Columns([p1, p2, p3, p4, p5, p6, p7, p8], expand=True))

        # Completion Progress Bar
        bar_color = "green" if pct >= 75 else ("yellow" if pct >= 40 else "red")
        progress_text = f"[bold {bar_color}]{pct}% Completed[/bold {bar_color}] ({completed}/{total} tasks finished)"
        
        # Visual Progress Bar
        bar_length = 30
        filled = int(bar_length * (pct / 100))
        bar_str = f"[{'█' * filled}{'░' * (bar_length - filled)}]"
        
        console.print(Rule(style="dim white"))
        console.print(Panel(Align.center(f"{progress_text}\n[{bar_color}]{bar_str}[/{bar_color}]\n[dim]Operational task completion status[/dim]"), title="COMPLETION RATE", border_style=bar_color))

        # Category Breakdown
        if stats.get("category_distribution"):
            cat_table = Table(title="Tasks by Category", header_style="bold yellow", border_style="dim white")
            cat_table.add_column("Category", style="cyan")
            cat_table.add_column("Count", justify="right", style="bold white")
            cat_table.add_column("Share", justify="right", style="dim white")
            
            for cat, count in stats["category_distribution"].items():
                share_pct = round((count / total * 100), 1) if total > 0 else 0.0
                cat_table.add_row(cat, str(count), f"{share_pct}%")

            console.print(Align.center(cat_table))

    @staticmethod
    def render_task_detail(task: Task) -> None:
        """Render detailed view card for a single task."""
        detail_text = f"""
[bold yellow]ID:[/bold yellow] {task.id}
[bold yellow]Title:[/bold yellow] {task.title}
[bold yellow]Description:[/bold yellow] {task.description or 'No description provided.'}
[bold yellow]Category:[/bold yellow] {task.category}
[bold yellow]Priority:[/bold yellow] [{task.priority.badge_color}]{task.priority.value}[/{task.priority.badge_color}]
[bold yellow]Status:[/bold yellow] {task.status.icon} [{task.status.badge_color}]{task.status.value}[/{task.status.badge_color}]
[bold yellow]Created At:[/bold yellow] {format_datetime(task.created_at)}
[bold yellow]Due Date:[/bold yellow] {format_datetime(task.due_date)}
[bold yellow]Last Updated:[/bold yellow] {format_datetime(task.updated_at)}
"""
        console.print(Panel(detail_text.strip(), title=f"TASK DETAILS: {task.id}", border_style="cyan"))

    @staticmethod
    def render_logs(logs: List[str]) -> None:
        """Render audit activity log formatted inside a structured Rich Table."""
        if not logs:
            TerminalView.render_empty_state(
                title="No Activity Logs",
                message="No system operations have been logged yet.",
                tip="Task operations like creation, updates, and deletes will automatically generate audit logs.",
            )
            return

        log_table = Table(title="ACTIVITY AUDIT LOG (Recent)", header_style="bold magenta", border_style="dim white", expand=True)
        log_table.add_column("Timestamp", style="cyan", width=22)
        log_table.add_column("Event / Action", style="bold yellow", width=18)
        log_table.add_column("Details", style="white")

        import re
        for line in logs:
            match = re.match(r"^\[(.*?)\]\s+\[(.*?)\]\s+(.*)$", line)
            if match:
                ts, action, details = match.groups()
                log_table.add_row(ts, f"[bold yellow]{action}[/bold yellow]", details)
            else:
                log_table.add_row("-", "INFO", line)

        console.print(log_table)

    @staticmethod
    def render_success(msg: str) -> None:
        """Render success message box."""
        console.print(Panel(f"[bold green]✔ SUCCESS:[/bold green] {msg}", border_style="bold green"))

    @staticmethod
    def render_error(msg: str) -> None:
        """Render error message box."""
        console.print(Panel(f"[bold red]✖ ERROR:[/bold red] {msg}", border_style="bold red"))

    @staticmethod
    def render_warning(msg: str) -> None:
        """Render warning message box."""
        console.print(Panel(f"[bold yellow]⚠️ WARNING:[/bold yellow] {msg}", border_style="bold yellow"))
