"""
Password strength analyzer and information entropy estimator module.

DecodeLabs Industrial Training Kit - Project 3: Enterprise Random Password Generator
"""

import math
from typing import Dict, Any, List
from config import UPPERCASE_SET, LOWERCASE_SET, NUMBER_SET, SPECIAL_SET


class PasswordStrengthAnalyzer:
    """
    Analyzes password strength based on entropy calculation, character diversity, and length metrics.
    
    Ratings:
    - VERY WEAK
    - WEAK
    - MEDIUM
    - STRONG
    - VERY STRONG
    """

    @staticmethod
    def analyze(password: str) -> Dict[str, Any]:
        """
        Analyze a password string and return comprehensive strength metrics.

        Args:
            password: Password string to analyze.

        Returns:
            Dictionary containing strength details, metrics, and recommendations.
        """
        if not password:
            return {
                "length": 0,
                "has_uppercase": False,
                "has_lowercase": False,
                "has_numbers": False,
                "has_special": False,
                "entropy_bits": 0.0,
                "rating": "VERY WEAK",
                "pool_size": 0,
                "recommendations": ["Password cannot be empty."],
            }

        length = len(password)
        has_upper = any(c in UPPERCASE_SET for c in password)
        has_lower = any(c in LOWERCASE_SET for c in password)
        has_number = any(c in NUMBER_SET for c in password)
        has_special = any(c in SPECIAL_SET for c in password)

        # Estimate character pool size based on character types present
        pool_size = 0
        if has_lower:
            pool_size += len(LOWERCASE_SET)
        if has_upper:
            pool_size += len(UPPERCASE_SET)
        if has_number:
            pool_size += len(NUMBER_SET)
        if has_special:
            pool_size += len(SPECIAL_SET)

        # Catch potential custom characters outside standard pools
        custom_chars = set(password) - set(
            UPPERCASE_SET + LOWERCASE_SET + NUMBER_SET + SPECIAL_SET
        )
        if custom_chars:
            pool_size += len(custom_chars)

        if pool_size == 0:
            pool_size = 1

        # Entropy calculation: E = L * log2(R)
        entropy_bits = length * math.log2(pool_size)

        # Strength Rating Matrix
        if length < 8 or entropy_bits < 28:
            rating = "VERY WEAK"
        elif entropy_bits < 36:
            rating = "WEAK"
        elif entropy_bits < 60:
            rating = "MEDIUM"
        elif entropy_bits < 80:
            rating = "STRONG"
        else:
            rating = "VERY STRONG"

        # Actionable Recommendations
        recommendations: List[str] = []
        if length < 12:
            recommendations.append("Increase length to at least 12-16 characters for significantly better entropy.")
        if not has_upper:
            recommendations.append("Add uppercase letters.")
        if not has_lower:
            recommendations.append("Add lowercase letters.")
        if not has_number:
            recommendations.append("Add numeric digits.")
        if not has_special:
            recommendations.append("Add special characters (e.g. !@#$%^&*).")

        return {
            "length": length,
            "has_uppercase": has_upper,
            "has_lowercase": has_lower,
            "has_numbers": has_number,
            "has_special": has_special,
            "pool_size": pool_size,
            "entropy_bits": round(entropy_bits, 2),
            "rating": rating,
            "recommendations": recommendations,
        }


def check_password_strength(password: str) -> Dict[str, Any]:
    """Convenience function for password strength analysis."""
    return PasswordStrengthAnalyzer.analyze(password)
