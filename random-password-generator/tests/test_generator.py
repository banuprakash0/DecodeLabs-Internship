"""
Unit tests for SecurePasswordGenerator module.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator
"""

import sys
import os
import pytest
import string

# Add parent directory to sys.path for test discovery
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import PasswordPolicy, UPPERCASE_SET, LOWERCASE_SET, NUMBER_SET, SPECIAL_SET
from generator import SecurePasswordGenerator, generate_password, generate_multiple_passwords


def test_password_length_accuracy():
    """Verify generated passwords match requested lengths precisely."""
    policy = PasswordPolicy()
    generator = SecurePasswordGenerator(policy)

    for target_len in [8, 12, 15, 16, 32, 64, 128]:
        pwd = generator.generate(target_len)
        assert len(pwd) == target_len


def test_character_class_guarantees():
    """Verify that generated passwords contain at least 1 char from every active class."""
    policy = PasswordPolicy(
        include_uppercase=True,
        include_lowercase=True,
        include_numbers=True,
        include_special=True,
    )
    generator = SecurePasswordGenerator(policy)

    for _ in range(20):
        pwd = generator.generate(16)
        assert any(c in UPPERCASE_SET for c in pwd), "Missing uppercase character"
        assert any(c in LOWERCASE_SET for c in pwd), "Missing lowercase character"
        assert any(c in NUMBER_SET for c in pwd), "Missing numeric digit"
        assert any(c in SPECIAL_SET for c in pwd), "Missing special character"


def test_single_category_policies():
    """Test generating passwords with only digits or only uppercase letters."""
    # Only numbers
    digits_policy = PasswordPolicy(
        include_uppercase=False,
        include_lowercase=False,
        include_numbers=True,
        include_special=False,
    )
    pwd_digits = generate_password(16, digits_policy)
    assert len(pwd_digits) == 16
    assert all(c in NUMBER_SET for c in pwd_digits)

    # Only uppercase
    upper_policy = PasswordPolicy(
        include_uppercase=True,
        include_lowercase=False,
        include_numbers=False,
        include_special=False,
    )
    pwd_upper = generate_password(12, upper_policy)
    assert len(pwd_upper) == 12
    assert all(c in UPPERCASE_SET for c in pwd_upper)


def test_multiple_password_generation():
    """Test generating multiple passwords at once."""
    policy = PasswordPolicy()
    passwords = generate_multiple_passwords(5, 16, policy)

    assert len(passwords) == 5
    assert len(set(passwords)) == 5  # High entropy: all generated passwords should be unique
    for pwd in passwords:
        assert len(pwd) == 16


def test_invalid_policy_raises_exception():
    """Verify that generating with no active categories raises ValueError."""
    empty_policy = PasswordPolicy(
        include_uppercase=False,
        include_lowercase=False,
        include_numbers=False,
        include_special=False,
    )
    generator = SecurePasswordGenerator(empty_policy)

    with pytest.raises(ValueError, match="At least one character category"):
        generator.generate(16)


def test_invalid_length_raises_exception():
    """Verify that generating with below min length raises ValueError."""
    policy = PasswordPolicy(min_length=8, max_length=128)
    generator = SecurePasswordGenerator(policy)

    with pytest.raises(ValueError):
        generator.generate(5)

    with pytest.raises(ValueError):
        generator.generate(200)


def test_security_import_audit():
    """Verify generator.py uses secrets module and does not import random.choice."""
    import generator

    # Check source file content for insecure random.choice usage
    gen_file_path = generator.__file__
    with open(gen_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "import secrets" in content
    assert "secrets.choice" in content
    assert "random.choice" not in content
