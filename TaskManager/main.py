"""Main Application Controller Entrypoint for TaskManager.

Orchestrates the MVC application lifecycle, routes user commands,
manages user authentication, input validation, and graceful shutdowns.
"""

from datetime import datetime
from pathlib import Path
import sys
from typing import Optional

from rich.prompt import Prompt, Confirm

from task_manager import TaskManagerService
from auth import AuthManager
from views import TerminalView, console
from models import Priority, Status
from utils import parse_date_string, validate_non_empty
from config import config, DATA_DIR, SAMPLE_CSV_FILE


class ApplicationController:
    """Main MVC Controller coordinating Service, Storage, and View layers."""

    def __init__(self) -> None:
        self.view = TerminalView()
        self.service = TaskManagerService()
        self.auth = AuthManager()

    def run(self) -> None:
        """Start application execution loop."""
        self.view.clear()
        self.view.render_header()

        # Handle Security Authentication Prompt if enabled
        if self.auth.is_password_set():
            if not self._authenticate_user():
                self.view.render_error("Authentication failed. Access denied.")
                sys.exit(1)
        self.auth.touch_session()

        # Main Event Loop
        while True:
            try:
                # Check session expiration
                if self.auth.is_password_set() and self.auth.is_session_expired():
                    self.view.render_warning("Session expired due to inactivity. Please re-authenticate.")
                    if not self._authenticate_user():
                        self.view.render_error("Authentication failed. Access denied.")
                        sys.exit(1)

                choice = self.view.render_menu()
                self.auth.touch_session()

                if choice == "1":
                    self._handle_add_task()
                elif choice == "2":
                    self._handle_view_all()
                elif choice == "3":
                    self._handle_search()
                elif choice == "4":
                    self._handle_filter()
                elif choice == "5":
                    self._handle_sort()
                elif choice == "6":
                    self._handle_edit_task()
                elif choice == "7":
                    self._handle_complete_task()
                elif choice == "8":
                    self._handle_delete_task()
                elif choice == "9":
                    self._handle_undo_delete()
                elif choice == "10":
                    self._handle_dashboard()
                elif choice == "11":
                    self._handle_import_export()
                elif choice == "12":
                    self._handle_view_logs()
                elif choice == "13":
                    self._handle_security_settings()
                elif choice == "0":
                    self.view.render_success("Thank you for using Enterprise Task Manager. Goodbye!")
                    sys.exit(0)

                Prompt.ask("\n[dim]Press Enter to return to Main Menu...[/dim]", default="")
                self.view.clear()
                self.view.render_header()

            except KeyboardInterrupt:
                console.print("\n")
                self.view.render_warning("Operation cancelled by user. Exiting safely...")
                sys.exit(0)
            except Exception as e:
                self.view.render_error(f"An unexpected error occurred: {str(e)}")
                Prompt.ask("\n[dim]Press Enter to continue...[/dim]", default="")

    def _authenticate_user(self) -> bool:
        """Prompt user for password authentication."""
        attempts = 3
        while attempts > 0:
            password = Prompt.ask("[bold yellow]Enter Administrator Password[/bold yellow]", password=True)
            if self.auth.verify_password(password):
                self.view.render_success("Access Granted.")
                return True
            attempts -= 1
            self.view.render_error(f"Incorrect password. {attempts} attempts remaining.")
        return False

    def _handle_add_task(self) -> None:
        """Form controller to add a new task."""
        console.print("\n[bold cyan]--- ADD NEW TASK ---[/bold cyan]")

        title = Prompt.ask("[bold white]Task Title[/bold white]")
        if not title.strip():
            self.view.render_error("Task title cannot be empty.")
            return

        description = Prompt.ask("[bold white]Description[/bold white] (optional)", default="")
        category = Prompt.ask("[bold white]Category[/bold white]", default="General")

        prio_choice = Prompt.ask(
            "[bold white]Priority[/bold white] (1=Low, 2=Medium, 3=High)",
            choices=["1", "2", "3"],
            default="2",
        )
        priority_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}
        priority = priority_map[prio_choice]

        due_date_input = Prompt.ask(
            "[bold white]Due Date[/bold white] (e.g. YYYY-MM-DD, 'today', 'tomorrow', '+3d', or leave empty)",
            default="",
        )
        
        due_date = None
        if due_date_input.strip():
            try:
                due_date = parse_date_string(due_date_input)
            except ValueError as ve:
                self.view.render_error(str(ve))
                return

        try:
            task = self.service.add_task(
                title=title,
                description=description,
                category=category,
                priority=priority,
                due_date=due_date,
            )
            self.view.render_success(f"Task '{task.title}' added successfully with ID: [bold yellow]{task.id}[/bold yellow]")
        except Exception as e:
            self.view.render_error(str(e))

    def _handle_view_all(self) -> None:
        """View all tasks with interactive detail inspector option."""
        tasks = self.service.get_all_tasks()
        self.view.render_tasks_table(tasks, title="ALL TASKS")

        if tasks:
            inspect_choice = Prompt.ask("\nEnter Task ID to view full details (or press Enter to skip)", default="")
            if inspect_choice.strip():
                task = self.service.get_task_by_id(inspect_choice)
                if task:
                    self.view.render_task_detail(task)
                else:
                    self.view.render_error(f"Task ID '{inspect_choice}' not found.")

    def _handle_search(self) -> None:
        """Search tasks by keyword."""
        query = Prompt.ask("\n[bold cyan]Search query (matches title, description, category, or ID)[/bold cyan]")
        results = self.service.search_tasks(query)
        self.view.render_tasks_table(results, title=f"SEARCH RESULTS: '{query}'")

    def _handle_filter(self) -> None:
        """Filter tasks by status, priority, or category."""
        console.print("\n[bold cyan]--- FILTER TASKS ---[/bold cyan]")
        console.print("[1] Filter by Status  [2] Filter by Priority  [3] Filter by Category  [4] Combined Filter")

        filter_choice = Prompt.ask("Choose filter option [1-4]", choices=["1", "2", "3", "4"], default="4")

        status_filter: Optional[Status] = None
        priority_filter: Optional[Priority] = None
        category_filter: Optional[str] = None

        if filter_choice in ["1", "4"]:
            s_choice = Prompt.ask(
                "Status (1=Pending, 2=In Progress, 3=Completed, 0=Skip)",
                choices=["1", "2", "3", "0", ""],
                default="0" if filter_choice == "4" else "1",
            )
            s_map = {"1": Status.PENDING, "2": Status.IN_PROGRESS, "3": Status.COMPLETED}
            if s_choice in s_map:
                status_filter = s_map[s_choice]

        if filter_choice in ["2", "4"]:
            p_choice = Prompt.ask(
                "Priority (1=Low, 2=Medium, 3=High, 0=Skip)",
                choices=["1", "2", "3", "0", ""],
                default="0" if filter_choice == "4" else "2",
            )
            p_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}
            if p_choice in p_map:
                priority_filter = p_map[p_choice]

        if filter_choice in ["3", "4"]:
            existing_cats = self.service.get_categories()
            cat_prompt = f"Category ({', '.join(existing_cats)}) (or press Enter to skip)" if existing_cats else "Category (or press Enter to skip)"
            raw_cat = Prompt.ask(cat_prompt, default="")
            if raw_cat.strip():
                category_filter = raw_cat.strip()

        filtered = self.service.filter_tasks(status=status_filter, priority=priority_filter, category=category_filter)
        self.view.render_tasks_table(filtered, title="FILTERED TASKS")

    def _handle_sort(self) -> None:
        """Sort tasks by column criteria."""
        console.print("\n[bold cyan]--- SORT TASKS ---[/bold cyan]")
        console.print("[1] Due Date  [2] Priority  [3] Title  [4] Category  [5] Created Date")
        choice = Prompt.ask("Sort criteria [1-5]", choices=["1", "2", "3", "4", "5"], default="1")

        sort_map = {
            "1": "due_date",
            "2": "priority",
            "3": "title",
            "4": "category",
            "5": "created_at",
        }
        reverse = Confirm.ask("Sort in descending order?", default=False)

        sorted_tasks = self.service.sort_tasks(sort_by=sort_map[choice], reverse=reverse)
        self.view.render_tasks_table(sorted_tasks, title=f"SORTED TASKS (by {sort_map[choice]})")

    def _handle_edit_task(self) -> None:
        """Edit fields of an existing task."""
        task_id = Prompt.ask("\nEnter Task ID to edit")
        task = self.service.get_task_by_id(task_id)

        if not task:
            self.view.render_error(f"Task ID '{task_id}' not found.")
            return

        self.view.render_task_detail(task)
        console.print("\n[dim]Press Enter to keep existing field value.[/dim]")

        new_title = Prompt.ask("New Title", default=task.title)
        new_desc = Prompt.ask("New Description", default=task.description)
        new_cat = Prompt.ask("New Category", default=task.category)

        prio_choice = Prompt.ask(
            f"New Priority (1=Low, 2=Medium, 3=High, default current: {task.priority.value})",
            choices=["1", "2", "3", ""],
            default="",
        )
        new_priority = None
        if prio_choice:
            p_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}
            new_priority = p_map[prio_choice]

        status_choice = Prompt.ask(
            f"New Status (1=Pending, 2=In Progress, 3=Completed, default current: {task.status.value})",
            choices=["1", "2", "3", ""],
            default="",
        )
        new_status = None
        if status_choice:
            s_map = {"1": Status.PENDING, "2": Status.IN_PROGRESS, "3": Status.COMPLETED}
            new_status = s_map[status_choice]

        due_date_str = Prompt.ask("New Due Date (e.g. YYYY-MM-DD, 'none' to clear, or Enter to keep)", default="")
        new_due_date = None
        clear_due_date = False
        if due_date_str.strip():
            if due_date_str.strip().lower() in ("none", "clear", "remove", "0"):
                clear_due_date = True
            else:
                try:
                    new_due_date = parse_date_string(due_date_str)
                except ValueError as ve:
                    self.view.render_error(str(ve))
                    return

        try:
            updated = self.service.update_task(
                task_id=task.id,
                title=new_title if new_title != task.title else None,
                description=new_desc if new_desc != task.description else None,
                category=new_cat if new_cat != task.category else None,
                priority=new_priority,
                status=new_status,
                due_date=new_due_date,
                clear_due_date=clear_due_date,
            )
            self.view.render_success(f"Task '{updated.id}' updated successfully.")
        except Exception as e:
            self.view.render_error(str(e))

    def _handle_complete_task(self) -> None:
        """Mark a task as completed."""
        task_id = Prompt.ask("\nEnter Task ID to mark completed")
        try:
            task = self.service.mark_completed(task_id)
            self.view.render_success(f"Task '{task.title}' marked as COMPLETED ✅")
        except KeyError as ke:
            self.view.render_error(str(ke))
        except Exception as e:
            self.view.render_error(str(e))

    def _handle_delete_task(self) -> None:
        """Delete task with confirmation."""
        task_id = Prompt.ask("\nEnter Task ID to delete")
        task = self.service.get_task_by_id(task_id)

        if not task:
            self.view.render_error(f"Task ID '{task_id}' not found.")
            return

        if Confirm.ask(f"[bold red]Are you sure you want to delete task '{task.title}' ({task.id})?[/bold red]"):
            deleted = self.service.delete_task(task.id)
            self.view.render_success(f"Task '{deleted.title}' deleted. (Use Undo option to restore if needed).")
        else:
            self.view.render_warning("Deletion cancelled.")

    def _handle_undo_delete(self) -> None:
        """Undo last deleted task."""
        restored = self.service.undo_last_delete()
        if restored:
            self.view.render_success(f"Restored deleted task '{restored.title}' (ID: {restored.id}) ✅")
        else:
            self.view.render_warning("No deleted tasks available in undo stack.")

    def _handle_dashboard(self) -> None:
        """Display metrics dashboard."""
        stats = self.service.get_statistics()
        self.view.render_dashboard(stats)

    def _handle_import_export(self) -> None:
        """Import, Export, Backup, or Restore task data."""
        console.print("\n[bold cyan]--- CSV DATA & BACKUP / RESTORE ---[/bold cyan]")
        console.print("[1] Export Tasks to CSV  [2] Import Tasks from CSV  [3] Backup Database  [4] Restore Backup")
        choice = Prompt.ask("Select option [1-4]", choices=["1", "2", "3", "4"], default="1")

        if choice == "1":
            default_path = DATA_DIR / "exported_tasks.csv"
            path_str = Prompt.ask("Export file path", default=str(default_path))
            export_file = Path(path_str)
            if self.service.export_to_csv(export_file):
                self.view.render_success(f"Successfully exported tasks to: {export_file.resolve()}")
        elif choice == "2":
            default_path = SAMPLE_CSV_FILE if SAMPLE_CSV_FILE.exists() else DATA_DIR / "tasks.csv"
            path_str = Prompt.ask("Import CSV file path", default=str(default_path))
            import_file = Path(path_str)
            try:
                count = self.service.import_from_csv(import_file)
                self.view.render_success(f"Successfully imported {count} new tasks.")
            except Exception as e:
                self.view.render_error(str(e))
        elif choice == "3":
            if self.service.create_backup():
                self.view.render_success("Database backup created successfully.")
            else:
                self.view.render_error("Failed to create database backup.")
        elif choice == "4":
            if Confirm.ask("[bold red]Are you sure you want to restore from backup? Existing tasks will be replaced.[/bold red]"):
                try:
                    restored_tasks = self.service.restore_backup()
                    self.view.render_success(f"Successfully restored {len(restored_tasks)} tasks from backup.")
                except Exception as e:
                    self.view.render_error(str(e))
            else:
                self.view.render_warning("Restore operation cancelled.")

    def _handle_view_logs(self) -> None:
        """Render recent audit activity logs."""
        logs = self.service.logger.read_recent_logs(limit=20)
        self.view.render_logs(logs)

    def _handle_security_settings(self) -> None:
        """Manage administrator password security settings."""
        console.print("\n[bold cyan]--- PASSWORD SECURITY SETTINGS ---[/bold cyan]")
        if self.auth.is_password_set():
            console.print("[1] Change Password  [2] Disable Password Protection")
            choice = Prompt.ask("Select option", choices=["1", "2"], default="1")
            
            curr_pass = Prompt.ask("Current Password", password=True)
            if choice == "1":
                new_pass = Prompt.ask("New Password", password=True)
                try:
                    self.auth.change_password(curr_pass, new_pass)
                    self.view.render_success("Password changed successfully.")
                except Exception as e:
                    self.view.render_error(str(e))
            else:
                try:
                    self.auth.disable_password(curr_pass)
                    self.view.render_success("Password protection disabled.")
                except Exception as e:
                    self.view.render_error(str(e))
        else:
            if Confirm.ask("Enable Password Protection for TaskManager?"):
                new_pass = Prompt.ask("Set Administrator Password", password=True)
                try:
                    self.auth.set_password(new_pass)
                    self.view.render_success("Password protection enabled successfully.")
                except Exception as e:
                    self.view.render_error(str(e))


def main() -> None:
    """CLI Driver function."""
    app = ApplicationController()
    app.run()


if __name__ == "__main__":
    main()
