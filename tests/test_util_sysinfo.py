"""Tests for system information utility functions."""
from util_sysinfo import get_user, get_hostname


def test_get_user_env(monkeypatch):
    """Test getting user from environment variables."""
    monkeypatch.setenv('USER', 'foo')
    assert get_user() == 'foo'
    monkeypatch.delenv('USER', raising=False)
    monkeypatch.setenv('USERNAME', 'bar')
    assert get_user() == 'bar'


def test_get_hostname_env(monkeypatch):
    """Test getting hostname from environment variables."""
    monkeypatch.setenv('HOSTNAME', 'host1')
    assert get_hostname() == 'host1'
