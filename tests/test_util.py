"""Tests for utility functions."""
import subprocess
from util import exec, exec_nostderr  # pylint: disable=redefined-builtin


def test_exec_env(monkeypatch):
    """Test exec function with environment variables."""
    called = {}

    def fake_check_output(cmd, env=None, **_kwargs):
        """Mock subprocess.check_output for testing."""
        called['cmd'] = cmd
        called['env'] = env
        called['stderr'] = _kwargs.get('stderr')
        return 'out'

    monkeypatch.setattr(subprocess, 'check_output', fake_check_output)
    res = exec(['echo', 'hi'], env={'FOO': 'BAR'})
    assert res == 'out'
    assert called['cmd'] == ['echo', 'hi']
    assert called['env']['FOO'] == 'BAR'
    assert called['stderr'] is None


def test_exec_nostderr(monkeypatch):
    """Test exec_nostderr function that suppresses stderr."""
    called = {}

    def fake_check_output(_cmd, **_kwargs):
        """Mock subprocess.check_output for testing."""
        called['stderr'] = _kwargs.get('stderr')
        return ''

    monkeypatch.setattr(subprocess, 'check_output', fake_check_output)
    exec_nostderr(['echo'])
    assert called['stderr'] is subprocess.DEVNULL
