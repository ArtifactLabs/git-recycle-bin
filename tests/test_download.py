"""Tests for download command functionality."""

from types import SimpleNamespace
from git_recycle_bin import download

class DummyRbGit:
    """Mock RbGit class for testing download functionality."""
    def __init__(self):
        """Initialize mock with empty call list."""
        self.calls = []
    def cmd(self, *args):
        """Mock command execution for download testing."""
        self.calls.append(args)
        if args[0] == 'checkout' and args[-1] == 'fail' and '-f' not in args:
            raise RuntimeError('exists')


def test_download_force_false_error():
    """Test download command with force=False handling errors."""
    rbgit = DummyRbGit()
    args = SimpleNamespace(artifacts=['fail'], force=False)
    ret = download(args, rbgit, 'remote')
    assert ret == 1
    assert ('fetch', 'remote', 'fail') in rbgit.calls
    assert ('checkout', 'fail') in rbgit.calls


def test_download_force_true():
    """Test download command with force=True."""
    rbgit = DummyRbGit()
    args = SimpleNamespace(artifacts=['ok'], force=True)
    ret = download(args, rbgit, 'remote')
    assert ret is None
    assert rbgit.calls == [('fetch', 'remote', 'ok'), ('checkout', '-f', 'ok')]
