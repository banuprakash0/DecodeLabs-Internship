"""
Cryptographically secure password generator module.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator
"""

import secrets
from typing import List, Optional
from config import PasswordPolicy
from validator import validate_policy, validate_length


class SecurePasswordGenerator:
    """
    Enterprise-grade cryptographically secure password generator using Python's `secrets` module.
    
    Security note: Uses `secrets.choice()` and `secrets.SystemRandom().shuffle()` for CSPRNG
    guarantees. Never uses insecure pseudo-random generation methods.
    """

    def __init__(self, default_policy: Optional[PasswordPolicy] = None):
        self.policy = default_policy or PasswordPolicy()

    def generate(self, length: int, policy: Optional[PasswordPolicy] = None) -> str:
        """
        Generate a secure random password adhering to the given length and policy.

        Args:
            length: Desired length of the password.
            policy: PasswordPolicy instance (uses default if None).

        Returns:
            Secure random password string.

        Raises:
            ValueError: If input length or policy is invalid.
        """
        active_policy = policy or self.policy

        # 1. Validate Policy
        policy_valid, policy_err = validate_policy(active_policy)
        if not policy_valid:
            raise ValueError(policy_err)

        # 2. Validate Length
        length_valid, parsed_len, length_err = validate_length(str(length), active_policy)
        if not length_valid:
            raise ValueError(length_err)

        active_pools = active_policy.get_active_pools()
        combined_pool = active_policy.get_combined_pool()

        # 3. Efficient List Accumulator Pattern (O(n) complexity)
        char_list: List[str] = []

        # Step 4: Guarantee at least one character from each active class using secrets.choice()
        for category_name, char_set in active_pools.items():
            guaranteed_char = secrets.choice(char_set)
            char_list.append(guaranteed_char)

        # Step 5: Fill remaining length using secrets.choice() from the combined pool
        remaining_count = parsed_len - len(char_list)
        for _ in range(remaining_count):
            char_list.append(secrets.choice(combined_pool))

        # Step 6: Secure Shuffle using CSPRNG SystemRandom
        # Standard random.shuffle is predictable; secrets.SystemRandom().shuffle uses OS CSPRNG.
        secrets.SystemRandom().shuffle(char_list)

        # Step 7: Create Final Password efficiently
        final_password = "".join(char_list)

        # Step 8: Validate Generated Password Policy Compliance
        self._verify_policy_compliance(final_password, active_policy)

        return final_password

    def generate_multiple(
        self, count: int, length: int, policy: Optional[PasswordPolicy] = None
    ) -> List[str]:
        """
        Generate multiple secure random passwords.

        Args:
            count: Number of passwords to generate.
            length: Length of each password.
            policy: Optional PasswordPolicy instance.

        Returns:
            List of generated password strings.
        """
        if count <= 0:
            raise ValueError(f"Count must be a positive integer. Received: {count}")

        passwords = [self.generate(length, policy) for _ in range(count)]
        return passwords

    def _verify_policy_compliance(self, password: str, policy: PasswordPolicy) -> None:
        """
        Internal integrity check to verify that a generated password satisfies all policy rules.

        Raises:
            RuntimeError: If policy validation fails post-generation.
        """
        pools = policy.get_active_pools()
        for category_name, char_set in pools.items():
            set_chars = set(char_set)
            if not any(c in set_chars for c in password):
                raise RuntimeError(
                    f"Generated password failed policy verification: missing required category '{category_name}'."
                )


def generate_password(length: int, policy: Optional[PasswordPolicy] = None) -> str:
    """Convenience function for generating a single password."""
    generator = SecurePasswordGenerator(policy)
    return generator.generate(length, policy)


def generate_multiple_passwords(
    count: int, length: int, policy: Optional[PasswordPolicy] = None
) -> List[str]:
    """Convenience function for generating multiple passwords."""
    generator = SecurePasswordGenerator(policy)
    return generator.generate_multiple(count, length, policy)
