"""
Unit tests for Input and Policy Validator module.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import PasswordPolicy
from validator import validate_length, validate_count, validate_policy


def test_validate_length_valid_inputs():
    """Test valid integer password lengths within policy bounds."""
    policy = PasswordPolicy(min_length=8, max_length=128)

    for valid_str, expected_int in [
        ("8", 8),
        ("15", 15),
        ("16", 16),
        ("32", 32),
        ("64", 64),
        ("128", 128),
        ("  16  ", 16),
    ]:
        is_valid, parsed, err = validate_length(valid_str, policy)
        assert is_valid is True
        assert parsed == expected_int
        assert err == ""


def test_validate_length_invalid_inputs():
    """Test invalid input strings including text, decimals, empty, zero, and negative values."""
    policy = PasswordPolicy(min_length=8, max_length=128)

    invalid_cases = [
        ("0", "must be a positive integer"),
        ("-1", "must be a positive integer"),
        ("-100", "must be a positive integer"),
        ("abc", "Invalid input"),
        ("12.5", "Decimal numbers are not allowed"),
        ("", "cannot be empty"),
        ("   ", "cannot be empty"),
        (None, "cannot be None"),
        ("7", "below the configured minimum"),
        ("129", "exceeds the configured maximum"),
        ("999999", "exceeds the configured maximum"),
    ]

    for raw_input, expected_err_keyword in invalid_cases:
        is_valid, parsed, err = validate_length(raw_input, policy)
        assert is_valid is False
        assert parsed == 0
        assert expected_err_keyword.lower() in err.lower()


def test_validate_count_valid():
    """Test bulk generation count inputs."""
    for count_str, expected_int in [("1", 1), ("5", 5), ("50", 50), ("100", 100)]:
        is_valid, parsed, err = validate_count(count_str)
        assert is_valid is True
        assert parsed == expected_int


def test_validate_count_invalid():
    """Test invalid count inputs."""
    for count_str in ["0", "-5", "abc", "12.5", "101", "", None]:
        is_valid, parsed, err = validate_count(count_str)
        assert is_valid is False
        assert parsed == 0
        assert err != ""


def test_validate_policy():
    """Test PasswordPolicy structural validation."""
    # Valid policy
    valid_policy = PasswordPolicy()
    is_valid, err = validate_policy(valid_policy)
    assert is_valid is True
    assert err == ""

    # Invalid: no categories selected
    no_cat_policy = PasswordPolicy(
        include_uppercase=False,
        include_lowercase=False,
        include_numbers=False,
        include_special=False,
    )
    is_valid, err = validate_policy(no_cat_policy)
    assert is_valid is False
    assert "at least one character category" in err.lower()

    # Invalid: min_length < 1
    zero_min_policy = PasswordPolicy(min_length=0)
    is_valid, err = validate_policy(zero_min_policy)
    assert is_valid is False
    assert "Minimum length must be at least 1" in err

    # Invalid: max_length < min_length
    inverted_bounds = PasswordPolicy(min_length=16, max_length=8)
    is_valid, err = validate_policy(inverted_bounds)
    assert is_valid is False
    assert "cannot be less than minimum" in err
