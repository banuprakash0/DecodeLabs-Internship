"""Unit Tests for Authentication and Password Protection."""

import pytest
from auth import AuthManager


@pytest.fixture
def auth_mgr(tmp_path):
    """Fixture providing isolated AuthManager."""
    auth_file = tmp_path / "test_auth.json"
    return AuthManager(auth_file=auth_file)


def test_auth_lifecycle(auth_mgr):
    """Test setting password, verifying, changing, and disabling."""
    assert auth_mgr.is_password_set() is False
    assert auth_mgr.verify_password("any") is True

    # Set Password
    auth_mgr.set_password("secret123")
    assert auth_mgr.is_password_set() is True
    assert auth_mgr.verify_password("secret123") is True
    assert auth_mgr.verify_password("wrong") is False

    # Change Password
    auth_mgr.change_password("secret123", "newsecret456")
    assert auth_mgr.verify_password("newsecret456") is True

    # Disable Password
    auth_mgr.disable_password("newsecret456")
    assert auth_mgr.is_password_set() is False


def test_password_complexity_validation(auth_mgr):
    """Test password complexity checks."""
    with pytest.raises(ValueError, match="cannot be empty"):
        auth_mgr.set_password("   ")


def test_session_timeout(auth_mgr):
    """Test session activity tracking and idle timeout expiration."""
    auth_mgr.set_password("supersecret123")
    assert auth_mgr.verify_password("supersecret123") is True
    assert auth_mgr.is_session_expired(timeout_seconds=60) is False

    # Simulate past timestamp beyond timeout threshold
    from datetime import datetime, timedelta
    auth_mgr.last_activity = datetime.now() - timedelta(seconds=120)
    assert auth_mgr.is_session_expired(timeout_seconds=60) is True
