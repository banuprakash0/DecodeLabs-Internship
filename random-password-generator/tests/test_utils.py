"""
Unit tests for Utils and GenerationHistory modules.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import PasswordPolicy, UPPERCASE_SET, LOWERCASE_SET, NUMBER_SET, SPECIAL_SET
from utils import secure_shuffle, calculate_pool_size, sanitize_input
from history import GenerationHistory


def test_secure_shuffle_integrity():
    """Verify secure_shuffle maintains element multiset identity."""
    original = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    shuffled = list(original)
    secure_shuffle(shuffled)

    assert len(shuffled) == len(original)
    assert sorted(shuffled) == sorted(original)


def test_calculate_pool_size():
    """Verify combined pool size calculations."""
    full_policy = PasswordPolicy()
    expected_full = len(UPPERCASE_SET) + len(LOWERCASE_SET) + len(NUMBER_SET) + len(SPECIAL_SET)
    assert calculate_pool_size(full_policy) == expected_full

    digits_only = PasswordPolicy(
        include_uppercase=False,
        include_lowercase=False,
        include_numbers=True,
        include_special=False,
    )
    assert calculate_pool_size(digits_only) == 10


def test_sanitize_input():
    """Test whitespace stripping helper."""
    assert sanitize_input("  hello  ") == "hello"
    assert sanitize_input(None) == ""


def test_generation_history_zero_plaintext_assertion():
    """Verify history logger records metadata only and never stores plaintext passwords."""
    history = GenerationHistory()
    policy = PasswordPolicy()

    rec = history.record_generation(16, policy, "VERY STRONG")

    assert rec["length"] == 16
    assert rec["strength"] == "VERY STRONG"
    assert rec["classes"] == "All Classes"
    assert "timestamp" in rec

    # Verify no password string key exists anywhere in history records
    all_keys = [key for record in history.get_records() for key in record.keys()]
    assert "password" not in all_keys
    assert "plaintext" not in all_keys

    # Verify clearing history
    history.clear_history()
    assert history.count == 0
