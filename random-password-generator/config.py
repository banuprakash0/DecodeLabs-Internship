"""
Application configuration and password policy definitions.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator
"""

from dataclasses import dataclass
import string

APP_NAME = "Enterprise Random Password Generator"
APP_VERSION = "1.0.0"
AUTHOR = "DecodeLabs"

# Default Character Pool Constants using Python's standard `string` module
UPPERCASE_SET = string.ascii_uppercase
LOWERCASE_SET = string.ascii_lowercase
NUMBER_SET = string.digits
SPECIAL_SET = string.punctuation

# System Bounds
MIN_ALLOWED_LENGTH = 8
MAX_ALLOWED_LENGTH = 128
DEFAULT_PASSWORD_LENGTH = 16
DEFAULT_BULK_COUNT = 5
MAX_BULK_COUNT = 100


@dataclass
class PasswordPolicy:
    """Configurable security policy for password generation."""

    min_length: int = MIN_ALLOWED_LENGTH
    max_length: int = MAX_ALLOWED_LENGTH
    include_uppercase: bool = True
    include_lowercase: bool = True
    include_numbers: bool = True
    include_special: bool = True

    def active_categories_count(self) -> int:
        """Return the number of active character categories."""
        return sum(
            [
                self.include_uppercase,
                self.include_lowercase,
                self.include_numbers,
                self.include_special,
            ]
        )

    def get_active_pools(self) -> dict[str, str]:
        """Return a dictionary mapping category names to character sets."""
        pools = {}
        if self.include_uppercase:
            pools["uppercase"] = UPPERCASE_SET
        if self.include_lowercase:
            pools["lowercase"] = LOWERCASE_SET
        if self.include_numbers:
            pools["numbers"] = NUMBER_SET
        if self.include_special:
            pools["special"] = SPECIAL_SET
        return pools

    def get_combined_pool(self) -> str:
        """Return all enabled character sets combined into a single string."""
        pools = self.get_active_pools()
        return "".join(pools.values())
