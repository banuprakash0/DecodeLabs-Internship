"""Business Logic Service Layer for TaskManager System.

Implements core domain operations:
- CRUD Task lifecycle
- Search, Filter, Sort operations
- Task Statistics Dashboard Engine
- Activity logging
- Stack-based Undo deleted task mechanism
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from models import Task, Priority, Status
from storage import StorageInterface, JSONStorage, CSVExporterImporter, ActivityLogger


class TaskManagerService:
    """Core Service managing business logic rules and domain operations."""

    def __init__(self, storage: Optional[StorageInterface] = None) -> None:
        self.storage: StorageInterface = storage or JSONStorage()
        self.logger: ActivityLogger = ActivityLogger()
        self._tasks: List[Task] = []
        self._undo_stack: List[Task] = []
        self.load_all_tasks()

    def load_all_tasks(self) -> None:
        """Reload tasks from persistent storage engine."""
        self._tasks = self.storage.load_tasks()

    def save(self) -> bool:
        """Persist current task collection to storage."""
        return self.storage.save_tasks(self._tasks)

    def add_task(
        self,
        title: str,
        description: str = "",
        category: str = "General",
        priority: Priority = Priority.MEDIUM,
        due_date: Optional[datetime] = None,
    ) -> Task:
        """Create and append a new task after validation."""
        # Duplicate title validation
        if any(t.title.lower() == title.strip().lower() for t in self._tasks):
            raise ValueError(f"A task with title '{title.strip()}' already exists.")

        new_task = Task.create(
            title=title,
            description=description,
            category=category,
            priority=priority,
            due_date=due_date,
        )
        self._tasks.append(new_task)
        self.save()
        self.logger.log("ADD_TASK", f"Created task '{new_task.title}' (ID: {new_task.id})")
        return new_task

    def get_all_tasks(self) -> List[Task]:
        """Return list of all tasks."""
        return list(self._tasks)

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Retrieve task by exact ID case-insensitively."""
        search_id = task_id.strip().upper()
        for task in self._tasks:
            if task.id.upper() == search_id:
                return task
        return None

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[Priority] = None,
        status: Optional[Status] = None,
        due_date: Optional[datetime] = None,
        clear_due_date: bool = False,
    ) -> Task:
        """Update existing task fields and update timestamp."""
        task = self.get_task_by_id(task_id)
        if not task:
            raise KeyError(f"Task with ID '{task_id}' not found.")

        if title is not None and title.strip().lower() != task.title.lower():
            if any(t.title.lower() == title.strip().lower() for t in self._tasks if t.id != task.id):
                raise ValueError(f"A task with title '{title.strip()}' already exists.")
            task.title = title.strip()

        if description is not None:
            task.description = description.strip()

        if category is not None:
            task.category = category.strip().title() or "General"

        if priority is not None:
            task.priority = priority

        if status is not None:
            task.status = status

        if clear_due_date:
            task.due_date = None
        elif due_date is not None:
            task.due_date = due_date

        task.touch()
        self.save()
        self.logger.log("UPDATE_TASK", f"Updated task '{task.title}' (ID: {task.id})")
        return task

    def mark_completed(self, task_id: str) -> Task:
        """Mark task status as COMPLETED."""
        task = self.get_task_by_id(task_id)
        if not task:
            raise KeyError(f"Task with ID '{task_id}' not found.")

        task.mark_completed()
        self.save()
        self.logger.log("COMPLETE_TASK", f"Completed task '{task.title}' (ID: {task.id})")
        return task

    def delete_task(self, task_id: str) -> Task:
        """Delete task by ID and store in undo stack."""
        task = self.get_task_by_id(task_id)
        if not task:
            raise KeyError(f"Task with ID '{task_id}' not found.")

        self._tasks.remove(task)
        self._undo_stack.append(task)
        self.save()
        self.logger.log("DELETE_TASK", f"Deleted task '{task.title}' (ID: {task.id})")
        return task

    def undo_last_delete(self) -> Optional[Task]:
        """Restore the last deleted task from undo stack."""
        if not self._undo_stack:
            return None

        restored_task = self._undo_stack.pop()
        # Avoid duplicate ID collisions if re-created
        if not self.get_task_by_id(restored_task.id):
            self._tasks.append(restored_task)
            self.save()
            self.logger.log("UNDO_DELETE", f"Restored task '{restored_task.title}' (ID: {restored_task.id})")
            return restored_task
        return None

    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by query matching title, description, or category."""
        if not query or not query.strip():
            return self.get_all_tasks()

        q = query.strip().lower()
        return [
            t for t in self._tasks
            if q in t.title.lower() or q in t.description.lower() or q in t.category.lower() or q in t.id.lower()
        ]

    def filter_tasks(
        self,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
        category: Optional[str] = None,
    ) -> List[Task]:
        """Filter tasks by status, priority, or category."""
        filtered = self._tasks

        if status:
            filtered = [t for t in filtered if t.status == status]
        if priority:
            filtered = [t for t in filtered if t.priority == priority]
        if category and category.strip():
            cat = category.strip().lower()
            filtered = [t for t in filtered if t.category.lower() == cat]

        return filtered

    def sort_tasks(self, tasks: Optional[List[Task]] = None, sort_by: str = "due_date", reverse: bool = False) -> List[Task]:
        """Sort tasks by due_date, priority, title, status, or created_at."""
        target_list = tasks if tasks is not None else list(self._tasks)

        if sort_by == "priority":
            return sorted(target_list, key=lambda t: t.priority.rank, reverse=not reverse)
        elif sort_by == "due_date":
            # Tasks without due date placed at end
            return sorted(
                target_list,
                key=lambda t: (t.due_date is None, t.due_date or datetime.max),
                reverse=reverse,
            )
        elif sort_by == "title":
            return sorted(target_list, key=lambda t: t.title.lower(), reverse=reverse)
        elif sort_by == "created_at":
            return sorted(target_list, key=lambda t: t.created_at, reverse=reverse)
        elif sort_by == "category":
            return sorted(target_list, key=lambda t: t.category.lower(), reverse=reverse)
        else:
            return target_list

    def get_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive Task Dashboard metrics."""
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks if t.status == Status.COMPLETED)
        pending = sum(1 for t in self._tasks if t.status == Status.PENDING)
        in_progress = sum(1 for t in self._tasks if t.status == Status.IN_PROGRESS)
        high_priority = sum(1 for t in self._tasks if t.priority == Priority.HIGH)
        low_priority = sum(1 for t in self._tasks if t.priority == Priority.LOW)
        
        completion_pct = (completed / total * 100) if total > 0 else 0.0
        due_today = sum(1 for t in self._tasks if t.is_due_today())
        overdue = sum(1 for t in self._tasks if t.is_overdue())

        categories: Dict[str, int] = {}
        for t in self._tasks:
            categories[t.category] = categories.get(t.category, 0) + 1

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "in_progress_tasks": in_progress,
            "high_priority_tasks": high_priority,
            "low_priority_tasks": low_priority,
            "completion_percentage": round(completion_pct, 1),
            "tasks_due_today": due_today,
            "overdue_tasks": overdue,
            "category_distribution": categories,
        }

    def get_categories(self) -> List[str]:
        """Get unique category names."""
        return sorted(list({t.category for t in self._tasks}))

    def export_to_csv(self, file_path: Path) -> bool:
        """Export active task list to CSV file."""
        success = CSVExporterImporter.export_to_csv(self._tasks, file_path)
        if success:
            self.logger.log("EXPORT_CSV", f"Exported {len(self._tasks)} tasks to {file_path.name}")
        return success

    def import_from_csv(self, file_path: Path) -> int:
        """Import tasks from CSV file, merging non-duplicate tasks."""
        imported = CSVExporterImporter.import_from_csv(file_path)
        count = 0
        for task in imported:
            if not any(t.id == task.id or t.title.lower() == task.title.lower() for t in self._tasks):
                self._tasks.append(task)
                count += 1

        if count > 0:
            self.save()
            self.logger.log("IMPORT_CSV", f"Imported {count} tasks from {file_path.name}")
        return count

    def create_backup(self) -> bool:
        """Manually trigger storage backup."""
        return self.storage.create_backup()

    def restore_backup(self) -> List[Task]:
        """Manually trigger storage restore from backup."""
        restored = self.storage.restore_backup()
        self._tasks = restored
        return self._tasks
