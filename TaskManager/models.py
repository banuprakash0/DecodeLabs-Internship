"""Domain Models Layer for TaskManager System.

Defines core business entities, status/priority enums, data validation,
serialization, and helper evaluation functions.
"""

from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Dict, Any, Optional, Self
import uuid

from config import config


class Priority(str, Enum):
    """Enumeration of Task Priority Levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

    @property
    def rank(self) -> int:
        """Returns integer rank for sorting (High=3, Medium=2, Low=1)."""
        ranks = {Priority.LOW: 1, Priority.MEDIUM: 2, Priority.HIGH: 3}
        return ranks[self]

    @property
    def badge_color(self) -> str:
        """Returns color tag for terminal view."""
        colors = {
            Priority.LOW: "cyan",
            Priority.MEDIUM: "yellow",
            Priority.HIGH: "bold red",
        }
        return colors[self]

    @classmethod
    def from_string(cls, val: str) -> "Priority":
        """Parse string to Priority enum case-insensitively."""
        normalized = val.strip().capitalize()
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(f"Invalid priority: '{val}'. Must be Low, Medium, or High.")


class Status(str, Enum):
    """Enumeration of Task Statuses."""

    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

    @property
    def badge_color(self) -> str:
        """Returns color tag for terminal view."""
        colors = {
            Status.PENDING: "magenta",
            Status.IN_PROGRESS: "blue",
            Status.COMPLETED: "bold green",
        }
        return colors[self]

    @property
    def icon(self) -> str:
        """Returns status icon."""
        icons = {
            Status.PENDING: "⏳",
            Status.IN_PROGRESS: "🔄",
            Status.COMPLETED: "✅",
        }
        return icons[self]

    @classmethod
    def from_string(cls, val: str) -> "Status":
        """Parse string to Status enum case-insensitively."""
        normalized = val.strip().title()
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(f"Invalid status: '{val}'. Must be Pending, In Progress, or Completed.")


@dataclass
class Task:
    """Core Task Entity representing a single work item."""

    id: str
    title: str
    description: str
    category: str = "General"
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Task title cannot be empty.")
        if len(self.title) > config.max_title_length:
            raise ValueError(f"Task title exceeds maximum length of {config.max_title_length} characters.")
        
        self.description = self.description.strip()
        if len(self.description) > config.max_description_length:
            raise ValueError(f"Task description exceeds maximum length of {config.max_description_length} characters.")
        
        self.category = self.category.strip().title() or "General"

        if isinstance(self.priority, str):
            self.priority = Priority.from_string(self.priority)
            
        if isinstance(self.status, str):
            self.status = Status.from_string(self.status)

    @classmethod
    def create(
        cls,
        title: str,
        description: str = "",
        category: str = "General",
        priority: Priority = Priority.MEDIUM,
        due_date: Optional[datetime] = None,
        task_id: Optional[str] = None,
    ) -> "Task":
        """Factory method to generate a new task with unique ID."""
        now = datetime.now()
        generated_id = task_id or f"TSK-{uuid.uuid4().hex[:6].upper()}"
        return cls(
            id=generated_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=Status.PENDING,
            created_at=now,
            due_date=due_date,
            updated_at=now,
        )

    def mark_completed(self) -> None:
        """Update status to COMPLETED and update timestamp."""
        self.status = Status.COMPLETED
        self.touch()

    def touch(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()

    def is_overdue(self) -> bool:
        """Check if task is overdue (past due date and not completed)."""
        if self.status == Status.COMPLETED or not self.due_date:
            return False
        return datetime.now() > self.due_date

    def is_due_today(self) -> bool:
        """Check if task is due today."""
        if self.status == Status.COMPLETED or not self.due_date:
            return False
        return self.due_date.date() == date.today()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Task instance to dictionary for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.strftime(config.datetime_format),
            "due_date": self.due_date.strftime(config.datetime_format) if self.due_date else None,
            "updated_at": self.updated_at.strftime(config.datetime_format),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Deserialize dictionary to Task instance."""
        def _parse_dt(val: Any) -> datetime:
            if isinstance(val, datetime):
                return val
            if not val:
                return datetime.now()
            from utils import parse_date_string
            try:
                return datetime.strptime(str(val).strip(), config.datetime_format)
            except ValueError:
                parsed = parse_date_string(str(val))
                return parsed if parsed else datetime.now()

        created_at = _parse_dt(data.get("created_at"))
        updated_at = _parse_dt(data.get("updated_at"))
        
        due_date = None
        if data.get("due_date") and str(data["due_date"]).strip().lower() not in ("none", "null", ""):
            due_date = _parse_dt(data["due_date"])

        return cls(
            id=str(data.get("id", f"TSK-{uuid.uuid4().hex[:6].upper()}")).strip(),
            title=str(data.get("title", "")).strip(),
            description=str(data.get("description", "")).strip(),
            category=str(data.get("category", "General")).strip(),
            priority=Priority.from_string(str(data.get("priority", "Medium"))),
            status=Status.from_string(str(data.get("status", "Pending"))),
            created_at=created_at,
            due_date=due_date,
            updated_at=updated_at,
        )


@dataclass
class ActivityLogEntry:
    """Represents an audit entry for system actions."""

    timestamp: datetime
    action: str
    details: str

    def to_dict(self) -> Dict[str, str]:
        """Convert log entry to dictionary format."""
        return {
            "timestamp": self.timestamp.strftime(config.datetime_format),
            "action": self.action,
            "details": self.details,
        }
