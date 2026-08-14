"""Unit Tests for TaskManager Domain Models."""

from datetime import datetime, timedelta
import pytest

from models import Task, Priority, Status


def test_task_creation_valid():
    """Test creating a valid Task instance."""
    task = Task.create(
        title="Write Unit Tests",
        description="Cover models and services",
        category="Testing",
        priority=Priority.HIGH,
    )
    assert task.title == "Write Unit Tests"
    assert task.category == "Testing"
    assert task.priority == Priority.HIGH
    assert task.status == Status.PENDING
    assert task.id.startswith("TSK-")


def test_task_empty_title_validation():
    """Test that empty titles raise ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        Task.create(title="   ")


def test_task_overdue_check():
    """Test overdue calculation."""
    past_due = datetime.now() - timedelta(days=2)
    task = Task.create(title="Past Task", due_date=past_due)
    assert task.is_overdue() is True

    task.mark_completed()
    assert task.is_overdue() is False


def test_task_serialization_roundtrip():
    """Test dict serialization and deserialization."""
    due = datetime(2026, 12, 25, 23, 59, 59)
    original = Task.create(
        title="Holiday Shopping",
        description="Buy gifts",
        category="Personal",
        priority=Priority.MEDIUM,
        due_date=due,
    )
    data_dict = original.to_dict()
    reconstructed = Task.from_dict(data_dict)

    assert reconstructed.id == original.id
    assert reconstructed.title == original.title
    assert reconstructed.priority == original.priority
    assert reconstructed.status == original.status
    assert reconstructed.due_date == original.due_date
