"""Data Storage & Persistence Layer for TaskManager System.

Provides Abstract Base Class interface and concrete implementations for:
- Atomic JSON persistence
- Data corruption recovery & auto-backup
- CSV import/export
- Activity audit logging
"""

from abc import ABC, abstractmethod
import csv
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import config, TASKS_FILE, BACKUP_FILE, ACTIVITY_LOG_FILE
from models import Task, Priority, Status


class StorageInterface(ABC):
    """Abstract Storage Interface to support multi-database backends."""

    @abstractmethod
    def load_tasks(self) -> List[Task]:
        """Load all tasks from storage."""
        pass

    @abstractmethod
    def save_tasks(self, tasks: List[Task]) -> bool:
        """Save tasks to storage."""
        pass

    @abstractmethod
    def create_backup(self) -> bool:
        """Create a backup of current data."""
        pass

    @abstractmethod
    def restore_backup(self) -> List[Task]:
        """Restore tasks from latest backup."""
        pass


class JSONStorage(StorageInterface):
    """Production-ready JSON Storage Handler with Atomic Writes & Recovery."""

    def __init__(self, file_path: Path = TASKS_FILE, backup_path: Path = BACKUP_FILE) -> None:
        self.file_path: Path = file_path
        self.backup_path: Path = backup_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure data file directory and file exist."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write_raw([])

    def _write_raw(self, data: List[Dict[str, Any]]) -> None:
        """Atomic write using temporary file to prevent file corruption."""
        temp_file = self.file_path.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_file.replace(self.file_path)
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise IOError(f"Failed to write data atomically: {str(e)}")

    def load_tasks(self) -> List[Task]:
        """Load and deserialize tasks from JSON file with error recovery."""
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            if not isinstance(raw_data, list):
                raise ValueError("JSON root element must be a list.")

            tasks: List[Task] = []
            for item in raw_data:
                try:
                    tasks.append(Task.from_dict(item))
                except Exception as parse_err:
                    # Skip malformed task items while preserving valid ones
                    print(f"[Warning] Skipped corrupted task record: {parse_err}")

            return tasks

        except (json.JSONDecodeError, ValueError) as json_err:
            print(f"[Error] Corrupted JSON detected in {self.file_path.name}: {json_err}")
            self._handle_corrupted_file()
            # Attempt restore from backup if available
            if self.backup_path.exists():
                print("[Info] Attempting automatic recovery from backup...")
                return self.restore_backup()
            return []
        except Exception as err:
            print(f"[Error] Unexpected read error: {err}")
            return []

    def verify_data_integrity(self, tasks: List[Task]) -> bool:
        """Verify task records satisfy structure and non-null constraints."""
        for t in tasks:
            if not isinstance(t, Task) or not t.id or not t.title:
                return False
        return True

    def save_tasks(self, tasks: List[Task]) -> bool:
        """Save tasks list atomically with pre-save auto-backup and data integrity verification."""
        try:
            if not self.verify_data_integrity(tasks):
                raise ValueError("Data integrity check failed: corrupt or incomplete task entities.")

            if config.auto_backup and self.file_path.exists():
                self.create_backup()

            serialized_tasks = [task.to_dict() for task in tasks]
            self._write_raw(serialized_tasks)
            return True
        except Exception as e:
            ActivityLogger().log("ERROR", f"Failed to save tasks: {e}")
            return False

    def create_backup(self) -> bool:
        """Create a copy of current tasks file as backup."""
        try:
            if self.file_path.exists():
                shutil.copy2(self.file_path, self.backup_path)
                ActivityLogger().log("BACKUP_CREATE", f"Created database backup: {self.backup_path.name}")
                return True
            return False
        except Exception as e:
            ActivityLogger().log("ERROR", f"Failed to create backup: {e}")
            return False

    def restore_backup(self) -> List[Task]:
        """Restore tasks from the backup file."""
        if not self.backup_path.exists():
            raise FileNotFoundError("No backup file found to restore from.")

        try:
            shutil.copy2(self.backup_path, self.file_path)
            restored = self.load_tasks()
            ActivityLogger().log("BACKUP_RESTORE", f"Restored {len(restored)} tasks from backup: {self.backup_path.name}")
            return restored
        except Exception as e:
            ActivityLogger().log("ERROR", f"Failed to restore backup: {e}")
            raise IOError(f"Failed to restore backup: {e}")

    def _handle_corrupted_file(self) -> None:
        """Quarantine corrupted file with timestamped suffix."""
        if self.file_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            corrupt_path = self.file_path.with_name(f"tasks_corrupted_{timestamp}.json")
            try:
                shutil.move(self.file_path, corrupt_path)
                ActivityLogger().log("QUARANTINE", f"Moved corrupted JSON file to: {corrupt_path.name}")
            except Exception as e:
                ActivityLogger().log("ERROR", f"Could not quarantine corrupted file: {e}")


class CSVExporterImporter:
    """Handles importing and exporting tasks to/from CSV format."""

    @staticmethod
    def export_to_csv(tasks: List[Task], export_path: Path) -> bool:
        """Export tasks list to CSV file."""
        export_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = ["id", "title", "description", "category", "priority", "status", "created_at", "due_date", "updated_at"]

        try:
            with open(export_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for task in tasks:
                    writer.writerow(task.to_dict())
            return True
        except Exception as e:
            print(f"[Error] CSV export failed: {e}")
            return False

    @staticmethod
    def import_from_csv(import_path: Path) -> List[Task]:
        """Import tasks from CSV file with per-row resilience."""
        if not import_path.exists():
            raise FileNotFoundError(f"CSV file not found at: {import_path}")

        imported_tasks: List[Task] = []
        try:
            with open(import_path, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                for line_num, row in enumerate(reader, start=2):
                    if not row or not any(row.values()):
                        continue
                    cleaned_row = {k.strip(): (v.strip() if isinstance(v, str) else "") for k, v in row.items() if k}
                    if not cleaned_row.get("title"):
                        continue
                    try:
                        task = Task.from_dict(cleaned_row)
                        imported_tasks.append(task)
                    except Exception as err:
                        ActivityLogger().log("WARNING", f"Skipped malformed CSV row at line {line_num}: {err}")
            return imported_tasks
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {e}")


class ActivityLogger:
    """Audit Logging System for tracking system operations."""

    def __init__(self, log_path: Path = ACTIVITY_LOG_FILE) -> None:
        self.log_path: Path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, action: str, details: str) -> None:
        """Log an event to the activity file."""
        timestamp = datetime.now().strftime(config.datetime_format)
        log_line = f"[{timestamp}] [{action.upper()}] {details}\n"
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception as e:
            print(f"[Error] Could not write activity log: {e}")

    def read_recent_logs(self, limit: int = 15) -> List[str]:
        """Read recent log entries."""
        if not self.log_path.exists():
            return []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return [line.strip() for line in lines[-limit:]]
        except Exception as e:
            print(f"[Error] Could not read activity log: {e}")
            return []
