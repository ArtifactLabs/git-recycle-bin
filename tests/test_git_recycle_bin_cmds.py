import datetime
from types import SimpleNamespace
import git_recycle_bin as grb


def test_push_branch_force(monkeypatch):
    calls = []
    dummy = SimpleNamespace(
        cmd=lambda *a, **k: calls.append(a)
    )
    args = SimpleNamespace(force_branch=True)
    d = {'bin_branch_name': 'b', 'bin_ref_only_metadata': 'm'}
    grb.push_branch(args, d, dummy, 'remote')
    assert ('push', '--force', 'remote', 'b') in calls
    assert ('push', '--force', 'remote', 'm') in calls


def test_push_branch_skip_existing(monkeypatch):
    calls = []

    class Dummy:
        def cmd(self, *a, **k):
            calls.append(a)
            return ''

        def remote_already_has_ref(self, remote, ref):
            return ref == 'b'

    dummy = Dummy()
    args = SimpleNamespace(force_branch=False)
    d = {'bin_branch_name': 'b', 'bin_ref_only_metadata': 'm'}
    grb.push_branch(args, d, dummy, 'remote')
    assert ('push', 'remote', 'm') in calls
    assert ('push', 'remote', 'b') not in calls


def test_push_tag_new(monkeypatch):
    calls = []

    class Dummy:
        def fetch_current_tag_value(self, r, t):
            return None

        def cmd(self, *a, **k):
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


def test_push_tag_force_when_newer(monkeypatch):
    calls = []

    class Dummy:
        def fetch_current_tag_value(self, r, t):
            return 'abc'

        def fetch_cat_pretty(self, r, ref):
            return 'src-git-commit-time-commit: Wed, 21 Jun 2023 11:00:00 +0000'

        def cmd(self, *a, **k):
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


def test_remote_delete_expired_branches(monkeypatch):
    lines = (
        'sha1\trefs/heads/artifact/expire/9999-01-01/00.00+0000/foo',
        'sha2\trefs/heads/artifact/expire/2000-01-01/00.00+0000/foo',
    )
    calls = []

    class Dummy:
        def cmd(self, *a, **k):
            if a[:3] == ('ls-remote', '--heads', 'remote'):
                return '\n'.join(lines)
            calls.append(a)
            return ''

    dummy = Dummy()
    grb.remote_delete_expired_branches(dummy, 'remote')
    assert ('push', 'remote', '--delete', 'refs/heads/artifact/expire/2000-01-01/00.00+0000/foo') in calls
    assert ('push', 'remote', '--delete', 'refs/heads/artifact/expire/9999-01-01/00.00+0000/foo') not in calls


def test_remote_flush_meta_for_commit(monkeypatch):
    sha1 = 'a' * 40
    sha2 = 'b' * 40
    calls = []

    class Dummy:
        def cmd(self, *a, **k):
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
