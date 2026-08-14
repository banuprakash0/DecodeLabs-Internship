"""Utility Helpers Module for TaskManager System.

Provides date parsing, input validation, text formatting,
and helper functions for CLI view rendering and core services.
"""

from datetime import datetime, timedelta
import re
from typing import Optional, Any, List

from config import config


def parse_date_string(date_input: str) -> Optional[datetime]:
    """Parse string input into datetime object.

    Supports formats:
    - 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' / ISO format
    - Relative shortcuts: 'today', 'tomorrow', '+3d' (3 days), '+1w' (1 week)
    - Clear keywords: 'none', 'clear', 'remove' (returns None)
    """
    if not date_input or not date_input.strip():
        return None

    cleaned = date_input.strip().lower()

    if cleaned in ("none", "clear", "remove", "null", "0"):
        return None

    if cleaned == "today":
        now = datetime.now()
        return datetime(now.year, now.month, now.day, 23, 59, 59)
    elif cleaned == "tomorrow":
        tomorrow = datetime.now() + timedelta(days=1)
        return datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59, 59)
    
    # Relative offset parsing e.g. +3d, +1w
    rel_match = re.match(r"^\+(\d+)([dw])$", cleaned)
    if rel_match:
        amount = int(rel_match.group(1))
        unit = rel_match.group(2)
        days = amount * 7 if unit == "w" else amount
        target_date = datetime.now() + timedelta(days=days)
        return datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59)

    # Standard date format parsing
    formats = [
        config.datetime_format,
        config.date_format,
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_input.strip(), fmt)
            if fmt in (config.date_format, "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"):
                parsed = datetime(parsed.year, parsed.month, parsed.day, 23, 59, 59)
            return parsed
        except ValueError:
            continue

    raise ValueError(f"Invalid date format: '{date_input}'. Use YYYY-MM-DD, 'today', 'tomorrow', '+3d', or 'none'.")


def format_datetime(dt: Optional[datetime]) -> str:
    """Format datetime object into display string."""
    if not dt:
        return "N/A"
    return dt.strftime(config.datetime_format)


def format_date(dt: Optional[datetime]) -> str:
    """Format datetime object into date display string."""
    if not dt:
        return "N/A"
    return dt.strftime(config.date_format)


def truncate_text(text: str, max_length: int = 40) -> str:
    """Truncate long text string with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def validate_non_empty(val: str, field_name: str) -> str:
    """Validate that string is not empty or whitespace only."""
    stripped = val.strip()
    if not stripped:
        raise ValueError(f"{field_name} cannot be empty.")
    return stripped
