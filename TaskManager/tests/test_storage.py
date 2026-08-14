"""Unit Tests for Storage Layer and Resilience."""

import json
from pathlib import Path
import pytest

from storage import JSONStorage, CSVExporterImporter
from models import Task, Priority


@pytest.fixture
def temp_storage(tmp_path):
    """Provide a temporary JSONStorage instance."""
    file_path = tmp_path / "test_tasks.json"
    backup_path = tmp_path / "test_tasks_backup.json"
    return JSONStorage(file_path=file_path, backup_path=backup_path)


def test_storage_save_and_load(temp_storage):
    """Test saving tasks to JSON and reloading them."""
    task1 = Task.create(title="Task One", priority=Priority.LOW)
    task2 = Task.create(title="Task Two", priority=Priority.HIGH)
    
    success = temp_storage.save_tasks([task1, task2])
    assert success is True

    loaded = temp_storage.load_tasks()
    assert len(loaded) == 2
    assert loaded[0].title == "Task One"
    assert loaded[1].title == "Task Two"


def test_corrupted_json_recovery(temp_storage):
    """Test automatic recovery handling when JSON file is corrupted."""
    # Create valid initial state & backup
    t1 = Task.create(title="Good Task")
    temp_storage.save_tasks([t1])
    temp_storage.create_backup()

    # Intentionally corrupt main file
    with open(temp_storage.file_path, "w", encoding="utf-8") as f:
        f.write("{ INVALID CORRUPTED JSON CONTENT }")

    recovered_tasks = temp_storage.load_tasks()
    assert len(recovered_tasks) == 1
    assert recovered_tasks[0].title == "Good Task"


def test_csv_export_import(tmp_path):
    """Test CSV export and import."""
    csv_file = tmp_path / "export_test.csv"
    t1 = Task.create(title="CSV Task 1", category="Dev")
    t2 = Task.create(title="CSV Task 2", category="Ops")

    export_success = CSVExporterImporter.export_to_csv([t1, t2], csv_file)
    assert export_success is True

    imported = CSVExporterImporter.import_from_csv(csv_file)
    assert len(imported) == 2
    assert imported[0].title == "CSV Task 1"
    assert imported[1].title == "CSV Task 2"


def test_csv_resilient_import_edge_cases(tmp_path):
    """Test importing CSV files with BOM, extra spaces, and malformed rows."""
    csv_file = tmp_path / "edge_case.csv"
    content = (
        "\ufeffid,title,description,category,priority,status,created_at,due_date,updated_at\n"
        " TSK-001 ,  Valid Task  , Description , Dev , High , Pending , 2026-08-06 12:00:00 , 2026-08-10 , 2026-08-06 12:00:00 \n"
        " ,, ,,, , ,\n"  # Empty row
        " TSK-002 , Task 2 , , Ops , InvalidPriority , Pending , 2026-08-06 12:00:00 , , 2026-08-06 12:00:00 \n"
    )
    with open(csv_file, "w", encoding="utf-8-sig") as f:
        f.write(content)

    tasks = CSVExporterImporter.import_from_csv(csv_file)
    assert len(tasks) == 1
    assert tasks[0].title == "Valid Task"
    assert tasks[0].priority == Priority.HIGH


def test_pre_save_auto_backup(temp_storage):
    """Test that pre-save auto backup preserves existing state before file replacement."""
    task1 = Task.create(title="Original State Task")
    temp_storage.save_tasks([task1])

    # Ensure backup file was created
    assert temp_storage.backup_path.exists()
    
    # Modify tasks and save again
    task2 = Task.create(title="New Task")
    temp_storage.save_tasks([task1, task2])
    
    # Storage contains 2 tasks
    loaded = temp_storage.load_tasks()
    assert len(loaded) == 2
