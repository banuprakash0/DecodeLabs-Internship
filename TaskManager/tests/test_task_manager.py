"""Unit Tests for TaskManager Business Logic Service."""

import pytest
from task_manager import TaskManagerService
from storage import JSONStorage
from models import Priority, Status


@pytest.fixture
def service(tmp_path):
    """Fixture providing isolated TaskManagerService."""
    file_path = tmp_path / "service_tasks.json"
    backup_path = tmp_path / "service_backup.json"
    storage = JSONStorage(file_path=file_path, backup_path=backup_path)
    return TaskManagerService(storage=storage)


def test_add_and_duplicate_title_prevention(service):
    """Test adding tasks and preventing duplicate titles."""
    service.add_task(title="Unique Task", priority=Priority.HIGH)
    assert len(service.get_all_tasks()) == 1

    with pytest.raises(ValueError, match="already exists"):
        service.add_task(title="Unique Task")


def test_update_and_delete_with_undo(service):
    """Test updating, deleting, and restoring a task via undo stack."""
    task = service.add_task(title="Task to Delete")
    task_id = task.id

    # Delete
    deleted = service.delete_task(task_id)
    assert deleted.title == "Task to Delete"
    assert len(service.get_all_tasks()) == 0

    # Undo Delete
    restored = service.undo_last_delete()
    assert restored is not None
    assert restored.id == task_id
    assert len(service.get_all_tasks()) == 1


def test_search_and_filter(service):
    """Test search and filter capabilities."""
    service.add_task(title="Fix Bug in Backend", category="Dev", priority=Priority.HIGH)
    service.add_task(title="Design UI Layout", category="Design", priority=Priority.MEDIUM)
    service.add_task(title="Write Backend Documentation", category="Dev", priority=Priority.LOW)

    # Search query
    backend_results = service.search_tasks("Backend")
    assert len(backend_results) == 2

    # Filter by category
    dev_filtered = service.filter_tasks(category="Dev")
    assert len(dev_filtered) == 2

    # Filter by priority
    high_filtered = service.filter_tasks(priority=Priority.HIGH)
    assert len(high_filtered) == 1
    assert high_filtered[0].title == "Fix Bug in Backend"


def test_dashboard_statistics(service):
    """Test statistics calculations."""
    t1 = service.add_task(title="T1", priority=Priority.HIGH)
    t2 = service.add_task(title="T2", priority=Priority.LOW)
    service.mark_completed(t1.id)

    stats = service.get_statistics()
    assert stats["total_tasks"] == 2
    assert stats["completed_tasks"] == 1
    assert stats["pending_tasks"] == 1
    assert stats["high_priority_tasks"] == 1
    assert stats["low_priority_tasks"] == 1
    assert stats["completion_percentage"] == 50.0


def test_combined_filter_with_field_skipping(service):
    """Test combined filtering with status, priority, category, and skipped fields."""
    t1 = service.add_task(title="Task A", category="Backend", priority=Priority.HIGH)
    t2 = service.add_task(title="Task B", category="Backend", priority=Priority.LOW)
    t3 = service.add_task(title="Task C", category="Frontend", priority=Priority.HIGH)
    service.mark_completed(t1.id)

    # Combined: Status=Completed, Priority=HIGH, Category=Backend -> matches t1
    match1 = service.filter_tasks(status=Status.COMPLETED, priority=Priority.HIGH, category="Backend")
    assert len(match1) == 1
    assert match1[0].id == t1.id

    # Skip status (None), Priority=HIGH, Category=Backend -> matches t1
    match2 = service.filter_tasks(status=None, priority=Priority.HIGH, category="Backend")
    assert len(match2) == 1

    # Skip category (None), Status=Pending, Priority=HIGH -> matches t3
    match3 = service.filter_tasks(status=Status.PENDING, priority=Priority.HIGH, category=None)
    assert len(match3) == 1
    assert match3[0].id == t3.id

    # Skip all -> returns all tasks
    match_all = service.filter_tasks(status=None, priority=None, category=None)
    assert len(match_all) == 3


def test_manual_backup_and_restore(service):
    """Test manual creation and restoration of storage backups."""
    from config import config
    service.add_task(title="Persistent Task 1")
    service.add_task(title="Persistent Task 2")

    # Create manual backup and disable auto_backup to test static restore
    backup_ok = service.create_backup()
    assert backup_ok is True
    
    orig_auto_backup = config.auto_backup
    config.auto_backup = False
    try:
        # Mutate current task list by adding a 3rd task
        service.add_task(title="Temporary Task 3")
        assert len(service.get_all_tasks()) == 3

        # Restore from manual backup
        restored = service.restore_backup()
        assert len(restored) == 2
        assert restored[0].title == "Persistent Task 1"
        assert restored[1].title == "Persistent Task 2"
    finally:
        config.auto_backup = orig_auto_backup
