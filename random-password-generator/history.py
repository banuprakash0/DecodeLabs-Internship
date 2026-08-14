"""
Generation history module for tracking metadata.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator

SECURITY MANDATE:
This module MUST NEVER record or store plaintext password values.
Only non-sensitive metadata (timestamps, lengths, character class options, strength metrics) is logged.
"""

from datetime import datetime
from typing import List, Dict, Any
from config import PasswordPolicy


class GenerationHistory:
    """Manages secure generation history storing safe metadata only."""

    def __init__(self) -> None:
        self._records: List[Dict[str, Any]] = []

    def record_generation(
        self, length: int, policy: PasswordPolicy, strength_rating: str
    ) -> Dict[str, Any]:
        """
        Record metadata for a password generation event.

        Args:
            length: Length of password generated.
            policy: PasswordPolicy used.
            strength_rating: Rating evaluated for the generated password.

        Returns:
            The logged record dictionary.
        """
        categories = []
        if policy.include_uppercase:
            categories.append("Upper")
        if policy.include_lowercase:
            categories.append("Lower")
        if policy.include_numbers:
            categories.append("Digits")
        if policy.include_special:
            categories.append("Special")

        class_summary = ", ".join(categories) if categories else "None"
        if len(categories) == 4:
            class_summary = "All Classes"

        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "length": length,
            "classes": class_summary,
            "strength": strength_rating,
        }

        self._records.append(record)
        return record

    def get_records(self) -> List[Dict[str, Any]]:
        """Return all logged history records."""
        return list(self._records)

    def clear_history(self) -> None:
        """Clear all stored history records."""
        self._records.clear()

    @property
    def count(self) -> int:
        """Return total number of history records."""
        return len(self._records)
