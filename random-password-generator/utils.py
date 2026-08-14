"""
Reusable utility functions.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator
"""

import secrets
from typing import List, TypeVar
from config import PasswordPolicy

T = TypeVar("T")


def secure_shuffle(items: List[T]) -> List[T]:
    """
    Perform a cryptographically secure Fisher-Yates shuffle in-place using `secrets.randbelow()`.

    Args:
        items: List of elements to shuffle.

    Returns:
        The shuffled list.
    """
    n = len(items)
    for i in range(n - 1, 0, -1):
        # Pick a random index j such that 0 <= j <= i securely
        j = secrets.randbelow(i + 1)
        items[i], items[j] = items[j], items[i]
    return items


def calculate_pool_size(policy: PasswordPolicy) -> int:
    """
    Calculate the total number of unique characters available under the given policy.

    Args:
        policy: PasswordPolicy instance.

    Returns:
        Integer size of the combined character pool.
    """
    return len(policy.get_combined_pool())


def sanitize_input(input_str: str) -> str:
    """Strip leading and trailing whitespace from input string."""
    if input_str is None:
        return ""
    return str(input_str).strip()
