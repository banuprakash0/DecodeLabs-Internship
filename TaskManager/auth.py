"""Security & Authentication Module for TaskManager System.

Provides PBKDF2-HMAC-SHA256 password hashing, salt generation,
credential verification, and secure storage management.
"""

import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

from config import AUTH_FILE, config
from storage import ActivityLogger


class AuthManager:
    """Security controller handling password setup, hashing, session management, and security logging."""

    def __init__(self, auth_file: Path = AUTH_FILE) -> None:
        self.auth_file: Path = auth_file
        self.auth_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger: ActivityLogger = ActivityLogger()
        self.last_activity: Optional[datetime] = None
        self._authenticated: bool = False

    def is_password_set(self) -> bool:
        """Check if an administrator password has been configured."""
        if not self.auth_file.exists():
            return False
        data = self._load_auth_data()
        return bool(data.get("password_hash") and data.get("salt"))

    def validate_password_complexity(self, plain_password: str) -> None:
        """Validate password meets minimum security complexity criteria."""
        if not plain_password or not plain_password.strip():
            raise ValueError("Password cannot be empty.")
        if len(plain_password.strip()) < config.min_password_length and len(plain_password.strip()) < 4:
            raise ValueError(f"Password must be at least {min(config.min_password_length, 4)} characters long.")
        if len(plain_password.strip()) < 4:
            raise ValueError("Password must be at least 4 characters long.")

    def set_password(self, plain_password: str) -> bool:
        """Hash and save new administrator password."""
        self.validate_password_complexity(plain_password)

        salt = secrets.token_hex(16)
        password_hash = self._hash_password(plain_password.strip(), salt)

        auth_data = {
            "password_hash": password_hash,
            "salt": salt,
            "updated_at": datetime.now().strftime(config.datetime_format),
        }
        success = self._save_auth_data(auth_data)
        if success:
            self._authenticated = True
            self.touch_session()
            self.logger.log("SECURITY", "Administrator password configured successfully.")
        return success

    def verify_password(self, plain_password: str) -> bool:
        """Verify entered password against stored hash."""
        if not self.is_password_set():
            self._authenticated = True
            self.touch_session()
            return True

        auth_data = self._load_auth_data()
        stored_hash = auth_data.get("password_hash", "")
        salt = auth_data.get("salt", "")

        computed_hash = self._hash_password(plain_password, salt)
        is_valid = secrets.compare_digest(stored_hash, computed_hash)
        
        if is_valid:
            self._authenticated = True
            self.touch_session()
            self.logger.log("AUTH_SUCCESS", "Administrator authentication successful.")
        else:
            self.logger.log("AUTH_FAILURE", "Failed password authentication attempt.")

        return is_valid

    def change_password(self, current_password: str, new_password: str) -> bool:
        """Change password after verifying current credentials."""
        if not self.verify_password(current_password):
            raise ValueError("Current password is incorrect.")
        success = self.set_password(new_password)
        if success:
            self.logger.log("SECURITY", "Administrator password changed.")
        return success

    def disable_password(self, current_password: str) -> bool:
        """Remove password protection."""
        if not self.verify_password(current_password):
            raise ValueError("Current password is incorrect.")
        if self.auth_file.exists():
            self.auth_file.unlink()
        self._authenticated = True
        self.last_activity = None
        self.logger.log("SECURITY", "Administrator password protection disabled.")
        return True

    def touch_session(self) -> None:
        """Update last active timestamp for current session."""
        self.last_activity = datetime.now()

    def is_session_expired(self, timeout_seconds: Optional[int] = None) -> bool:
        """Check if active authenticated session has timed out due to inactivity."""
        if not self.is_password_set():
            return False

        if not self._authenticated or self.last_activity is None:
            return True

        max_idle_seconds = timeout_seconds if timeout_seconds is not None else (config.session_timeout_minutes * 60)
        idle_duration = (datetime.now() - self.last_activity).total_seconds()
        
        if idle_duration > max_idle_seconds:
            self.logger.log("SESSION_TIMEOUT", f"Session expired after {int(idle_duration)} seconds of inactivity.")
            self._authenticated = False
            return True

        return False

    def invalidate_session(self) -> None:
        """Explicitly end the current session."""
        self._authenticated = False
        self.last_activity = None

    def _hash_password(self, password: str, salt: str) -> str:
        """Generate PBKDF2 HMAC SHA-256 hash with 100,000 iterations."""
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations=100000,
        )
        return key.hex()

    def _load_auth_data(self) -> Dict[str, str]:
        """Load auth json file securely."""
        try:
            if self.auth_file.exists():
                with open(self.auth_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            self.logger.log("ERROR", f"Failed to read auth file: {e}")
        return {}

    def _save_auth_data(self, data: Dict[str, str]) -> bool:
        """Save auth dictionary to file atomically."""
        temp_file = self.auth_file.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            temp_file.replace(self.auth_file)
            return True
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            self.logger.log("ERROR", f"Failed to save auth credentials: {e}")
            return False
