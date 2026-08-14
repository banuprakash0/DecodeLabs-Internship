"""
Input and policy validation module.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator
"""

from typing import Tuple
from config import PasswordPolicy, MIN_ALLOWED_LENGTH, MAX_ALLOWED_LENGTH, MAX_BULK_COUNT


def validate_length(input_str: str, policy: PasswordPolicy) -> Tuple[bool, int, str]:
    """
    Validate a user-provided password length input string.

    Args:
        input_str: Raw user input from terminal.
        policy: The active PasswordPolicy instance.

    Returns:
        Tuple of (is_valid, parsed_length, error_message)
    """
    if input_str is None:
        return False, 0, "Input cannot be None."

    cleaned = str(input_str).strip()
    if not cleaned:
        return False, 0, "❌ Input cannot be empty. Please enter a valid integer."

    try:
        # Check float-like strings like "12.5" by strict int check
        if "." in cleaned:
            return False, 0, "❌ Decimal numbers are not allowed. Please enter a whole integer."
        
        length = int(cleaned)
    except ValueError:
        return False, 0, "❌ Invalid input. Please enter a valid integer."

    if length <= 0:
        return False, 0, f"❌ Password length must be a positive integer (greater than 0). Received: {length}"

    if length < policy.min_length:
        return False, 0, (
            f"❌ Password length ({length}) is below the configured minimum length of {policy.min_length}."
        )

    if length > policy.max_length:
        return False, 0, (
            f"❌ Password length ({length}) exceeds the configured maximum length of {policy.max_length}."
        )

    return True, length, ""


def validate_count(input_str: str, max_count: int = MAX_BULK_COUNT) -> Tuple[bool, int, str]:
    """
    Validate a user-provided bulk password count input string.

    Args:
        input_str: Raw user input.
        max_count: Upper bound limit for count.

    Returns:
        Tuple of (is_valid, parsed_count, error_message)
    """
    if input_str is None:
        return False, 0, "Input cannot be None."

    cleaned = str(input_str).strip()
    if not cleaned:
        return False, 0, "❌ Input cannot be empty. Please enter a valid integer."

    try:
        if "." in cleaned:
            return False, 0, "❌ Decimal numbers are not allowed. Please enter a whole integer."
        count = int(cleaned)
    except ValueError:
        return False, 0, "❌ Invalid input. Please enter a valid integer."

    if count <= 0:
        return False, 0, f"❌ Password count must be at least 1. Received: {count}"

    if count > max_count:
        return False, 0, f"❌ Password count cannot exceed {max_count}. Received: {count}"

    return True, count, ""


def validate_policy(policy: PasswordPolicy) -> Tuple[bool, str]:
    """
    Validate that a PasswordPolicy instance is self-consistent and secure.

    Args:
        policy: PasswordPolicy instance to inspect.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if policy.min_length < 1:
        return False, "Policy error: Minimum length must be at least 1."

    if policy.max_length < policy.min_length:
        return False, (
            f"Policy error: Maximum length ({policy.max_length}) cannot be less than "
            f"minimum length ({policy.min_length})."
        )

    if policy.active_categories_count() == 0:
        return False, "Policy error: At least one character category (uppercase, lowercase, numbers, special) must be selected."

    if policy.min_length < policy.active_categories_count():
        return False, (
            f"Policy error: Password length ({policy.min_length}) must be at least equal "
            f"to the number of selected character categories ({policy.active_categories_count()}) "
            "to guarantee category representation."
        )

    return True, ""
