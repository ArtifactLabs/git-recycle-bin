"""Tests for git recycle bin command functionality."""
from types import SimpleNamespace

import git_recycle_bin as grb
from git_recycle_bin.utils.string import (
    sanitize_branch_name,
    sanitize_slashes,
)


def test_push_branch_force():
    """Test pushing branch with force option."""
    calls = []
    dummy = SimpleNamespace(
        cmd=lambda *a, **_k: calls.append(a)
    )
    args = SimpleNamespace(force_branch=True)
    d = {'bin_branch_name': 'b', 'bin_ref_only_metadata': 'm'}
    grb.push_branch(args, d, dummy, 'remote')
    assert ('push', '--force', 'remote', 'b') in calls
    assert ('push', '--force', 'remote', 'm') in calls


def test_push_branch_skip_existing():
    """Test skipping push when branch already exists."""
    calls = []

    class Dummy:
        """Mock RbGit for testing branch skip logic."""
        def cmd(self, *a, **_k):
            """Mock command execution."""
            calls.append(a)
            return ''

        def remote_already_has_ref(self, _remote, ref):
            """Mock remote ref checking."""
            return ref == 'b'

    dummy = Dummy()
    args = SimpleNamespace(force_branch=False)
    d = {'bin_branch_name': 'b', 'bin_ref_only_metadata': 'm'}
    grb.push_branch(args, d, dummy, 'remote')
    assert ('push', 'remote', 'm') in calls
    assert ('push', 'remote', 'b') not in calls


def test_push_tag_new():
    """Test pushing new tag."""
    calls = []

    class Dummy:
        """Mock RbGit for testing new tag push."""
        def fetch_current_tag_value(self, _r, _t):
            """Mock tag value fetching."""
            return None

        def cmd(self, *a, **_k):
            """Mock command execution."""
            calls.append(a)
            return ''

    dummy = Dummy()
    args = SimpleNamespace(force_tag=False)
    d = {
        'bin_tag_name': 'tag',
        'src_commits_ahead': '',
        'bin_sha_commit': 'sha',
        'src_time_commit': 'Wed, 21 Jun 2023 12:00:00 +0000',
    }
    grb.push_tag(args, d, dummy, 'remote')
    assert ('push', 'remote', 'tag') in calls


def test_push_tag_force_when_newer():
    """Test force pushing tag when newer version exists."""
    calls = []

    class Dummy:
        """Mock RbGit for testing tag force push logic."""
        def fetch_current_tag_value(self, _r, _t):
            """Mock tag value fetching."""
            return 'abc'

        def fetch_cat_pretty(self, _r, _ref):
            """Mock pretty printing of objects."""
            return 'src-git-commit-time-commit: Wed, 21 Jun 2023 11:00:00 +0000'

        def cmd(self, *a, **_k):
            """Mock command execution."""
            calls.append(a)
            return ''

    dummy = Dummy()
    args = SimpleNamespace(force_tag=False)
    d = {
        'bin_tag_name': 'tag',
        'src_commits_ahead': '',
        'bin_sha_commit': 'ours',
        'src_time_commit': 'Wed, 21 Jun 2023 12:00:00 +0000',
    }
    grb.push_tag(args, d, dummy, 'remote')
    assert ('push', '--force', 'remote', 'tag') in calls


def test_remote_delete_expired_branches():
    """Test deleting expired branches from remote."""
    lines = (
        'sha1\trefs/heads/artifact/expire/9999-01-01/00.00+0000/foo',
        'sha2\trefs/heads/artifact/expire/2000-01-01/00.00+0000/foo',
    )
    calls = []

    class Dummy:
        """Mock RbGit for testing branch deletion."""
        def cmd(self, *a, **_k):
            """Mock command execution."""
            if a[:3] == ('ls-remote', '--heads', 'remote'):
                return '\n'.join(lines)
            calls.append(a)
            return ''

    dummy = Dummy()
    grb.remote_delete_expired_branches(dummy, 'remote')
    assert ('push', 'remote', '--delete', 'refs/heads/artifact/expire/2000-01-01/00.00+0000/foo') in calls
    assert ('push', 'remote', '--delete', 'refs/heads/artifact/expire/9999-01-01/00.00+0000/foo') not in calls


def test_remote_flush_meta_for_commit():
    """Test flushing meta data for commit from remote."""
    sha1 = 'a' * 40
    sha2 = 'b' * 40
    calls = []

    class Dummy:
        """Mock RbGit for testing meta data flushing."""
        def cmd(self, *a, **_k):
            """Mock command execution."""
            if a[:4] == ('ls-remote', '--refs', 'remote', 'refs/artifact/meta-for-commit/*'):
                return f'{sha1}\trefs/artifact/meta-for-commit/{sha1}\n{sha2}\trefs/artifact/meta-for-commit/{sha2}'
            if a[:3] == ('ls-remote', '--heads', 'remote'):
                return f'{sha2}\trefs/heads/main'
            if a[:3] == ('ls-remote', '--tags', 'remote'):
                return ''
            calls.append(a)
            return ''

    dummy = Dummy()
    grb.remote_flush_meta_for_commit(dummy, 'remote')
    assert ('push', 'remote', '--delete', 'refs/artifact/meta-for-commit/' + sha1) in calls
    assert all('refs/artifact/meta-for-commit/' + sha2 not in a for a in calls)


def test_note_append_push(monkeypatch):
    """Test appending note and pushing to remote."""
    calls = []

    def fake_exec(cmd, env=None):
        """Mock exec function."""
        calls.append(("exec", cmd, env))
        return ''

    def fake_exec_nostderr(cmd, env=None):
        """Mock exec_nostderr function."""
        calls.append(("exec_nostderr", cmd, env))
        return ''

    monkeypatch.setattr(grb.commands.push, 'exec', fake_exec)
    monkeypatch.setattr(grb.commands.push, 'exec_nostderr', fake_exec_nostderr)
    monkeypatch.setattr(grb.commands.push, 'get_user', lambda: 'u')
    monkeypatch.setattr(grb.commands.push, 'get_hostname', lambda: 'h')

    args = SimpleNamespace(
        remote='https://remote',
        name='artifact',
        src_remote_name='origin',
        user_name='me',
        user_email='me@example.com',
    )
    d = {
        'src_status': '',
        'bin_time_commit': 't',
        'bin_branch_expire': 'exp',
        'bin_sha_commit': 'sha',
    }

    grb.note_append_push(args, d)

    gitenv = calls[0][2]
    expected_ref = sanitize_branch_name(
        f"refs/notes/artifact/{sanitize_slashes(args.remote)}/{sanitize_slashes(args.name)}/{d['bin_sha_commit']}-clean"
    )
    assert gitenv['GIT_NOTES_REF'] == expected_ref
    assert gitenv['GIT_AUTHOR_NAME'] == 'me'
    assert any(c[1][:2] == ['git', 'notes'] and 'append' in c[1] for c in calls)
    assert any(c[1][:2] == ['git', 'push'] for c in calls)
