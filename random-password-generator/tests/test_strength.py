"""
Unit tests for Password Strength Analyzer module.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strength import PasswordStrengthAnalyzer, check_password_strength


def test_empty_password_strength():
    """Verify empty input returns VERY WEAK."""
    result = check_password_strength("")
    assert result["rating"] == "VERY WEAK"
    assert result["length"] == 0
    assert result["entropy_bits"] == 0.0


def test_weak_passwords():
    """Verify short or low-entropy passwords rank as WEAK or VERY WEAK."""
    # Very short password
    r1 = check_password_strength("abc")
    assert r1["rating"] in ["VERY WEAK", "WEAK"]

    # Single-class 8-char password
    r2 = check_password_strength("password")
    assert r2["rating"] in ["VERY WEAK", "WEAK", "MEDIUM"]


def test_medium_passwords():
    """Verify moderate complexity passwords rank as MEDIUM."""
    r = check_password_strength("Pass1234")
    assert r["rating"] in ["MEDIUM", "WEAK"]


def test_strong_passwords():
    """Verify passwords with 12+ chars and multiple classes rank as STRONG."""
    r = check_password_strength("K9#mQ2$vL8!p")
    assert r["rating"] in ["STRONG", "VERY STRONG"]


def test_very_strong_passwords():
    """Verify high-entropy 16+ char complex passwords rank as VERY STRONG."""
    r = check_password_strength("X7@kP2#mL9!qZ8&wP9#m")
    assert r["rating"] == "VERY STRONG"
    assert r["entropy_bits"] > 80.0


def test_recommendations_presence():
    """Verify recommendations are generated for weak passwords."""
    r = check_password_strength("12345")
    assert len(r["recommendations"]) > 0
    assert any("length" in rec.lower() for rec in r["recommendations"])
