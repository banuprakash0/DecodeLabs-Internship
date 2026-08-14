"""Unit Tests for Date Parsing and Utility Helpers."""

from datetime import datetime, date, timedelta
import pytest

from utils import parse_date_string, truncate_text, validate_non_empty


def test_parse_date_string_shortcuts():
    """Test parsing relative date shortcuts."""
    today = parse_date_string("today")
    assert today.date() == date.today()

    tomorrow = parse_date_string("tomorrow")
    assert tomorrow.date() == (date.today() + timedelta(days=1))

    three_days = parse_date_string("+3d")
    assert three_days.date() == (date.today() + timedelta(days=3))


def test_parse_date_string_standard():
    """Test standard date string formats."""
    parsed = parse_date_string("2026-12-31")
    assert parsed.year == 2026
    assert parsed.month == 12
    assert parsed.day == 31


def test_parse_date_string_invalid():
    """Test invalid date inputs."""
    with pytest.raises(ValueError, match="Invalid date format"):
        parse_date_string("invalid-date-string")


def test_truncate_text():
    """Test text truncation helper."""
    short = "Hello"
    assert truncate_text(short, 10) == "Hello"

    long_text = "This is a very long task description that needs truncation"
    assert truncate_text(long_text, 15) == "This is a ve..."
