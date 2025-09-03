import pytest
from types import SimpleNamespace
import git_recycle_bin as grb
from git_recycle_bin.artifact_commit import create_artifact_commit


def test_create_artifact_commit_missing(tmp_path):
    missing = tmp_path / "nope.bin"
    with pytest.raises(RuntimeError):
        create_artifact_commit(SimpleNamespace(), 'name', str(missing), '1d', False, 'origin')


def test_create_artifact_commit_sanitizes_name(tmp_path, monkeypatch):
    path = tmp_path / "file.txt"
    path.write_text('data')

    def fake_exec(cmd):
        if cmd[:3] == ['git', 'rev-parse', 'HEAD']:
            return 'sha'
        if '--format=%B' in cmd:
            return 'msg\n'
        if '--format=%ad' in cmd or '--format=%cd' in cmd:
            return 'Wed, 01 Jan 2020 00:00:00 +0000'
        if cmd[:3] == ['git', 'rev-parse', '--abbrev-ref']:
            return 'main'
        if cmd[:3] == ['git', 'config', '--get']:
            return 'https://example.com/repo.git'
        if cmd[:3] == ['git', 'rev-parse', '--show-toplevel']:
            return '/src/root'
        if cmd[:2] == ['git', 'status']:
            return ''
        if cmd and cmd[1] == 'for-each-ref':
            return 'origin/main'
        if cmd and cmd[0:2] == ['git', 'rev-list']:
            return '0'
        return ''

    ns = grb.artifact_commit
    monkeypatch.setattr(ns, 'exec', fake_exec)
    monkeypatch.setattr(ns, 'classify_path', lambda p: 'file')
    monkeypatch.setattr(ns, 'nca_path', lambda a, b: '/nca')
    monkeypatch.setattr(ns, 'rel_dir', lambda **k: 'rel')
    monkeypatch.setattr(ns, 'date_fuzzy2expiryformat', lambda x: '2024-01-01/00.00+0000')
    monkeypatch.setattr(ns, 'emit_commit_msg', lambda d: 'commit msg')
    monkeypatch.setattr(ns, 'printer', SimpleNamespace(always=lambda *a, **k: None,
                                                       high_level=lambda *a, **k: None,
                                                       detail=lambda *a, **k: None,
                                                       debug=lambda *a, **k: None))

    class Dummy:
        def __init__(self):
            self.calls = []
            self.rbgit_dir = '/rbgit'
        def checkout_orphan_idempotent(self, b):
            self.calls.append(('checkout', b))
        def add(self, p, force):
            self.calls.append(('add', p, force))
            return True
        def cmd(self, *a, input=None, capture_output=True):
            self.calls.append(('cmd', a))
            if a[:2] == ('rev-parse', 'HEAD'):
                return 'sha'
            if a[0] == 'hash-object':
                return 'hash'
            return 'out'
        def set_tag(self, *, tag_name, tag_val):
            self.calls.append(('set_tag', tag_name, tag_val))

    rbgit = Dummy()
    d = ns.create_artifact_commit(rbgit, 'bad name?', str(path), 'tomorrow', False, 'origin')

    assert d['artifact_name'] == 'bad_name_'
    assert any(c[0] == 'set_tag' for c in rbgit.calls)


def test_push_command(monkeypatch):
    calls = []

    def fake_create(r, name, path, expire, add_ignored, src_remote):
        calls.append(('create', name, path, expire, add_ignored, src_remote))
        return {
            'bin_branch_name': 'b',
            'bin_ref_only_metadata': 'm',
            'bin_tag_name': 't',
            'src_commits_ahead': '',
            'bin_sha_commit': 'sha',
            'src_time_commit': 'time',
        }

    ns = grb.commands.push
    monkeypatch.setattr(ns, 'create_artifact_commit', fake_create)
    monkeypatch.setattr(ns, 'push_branch', lambda a, b, c, d: calls.append('push_branch'))
    monkeypatch.setattr(ns, 'push_tag', lambda a, b, c, d: calls.append('push_tag'))
    monkeypatch.setattr(ns, 'note_append_push', lambda a, b: calls.append('note'))
    monkeypatch.setattr(ns, 'remote_delete_expired_branches', lambda c, d: calls.append('rm_expired'))
    monkeypatch.setattr(ns, 'remote_flush_meta_for_commit', lambda c, d: calls.append('flush_meta'))
    monkeypatch.setattr(ns, 'printer', SimpleNamespace(high_level=lambda *a, **k: None, detail=lambda *a, **k: None))

    class DummyRb:
        def __init__(self):
            self.calls = []
            self.rbgit_dir = '/r'
        def add_remote_idempotent(self, name, url):
            calls.append(('add_remote', name, url))
        def cmd(self, *a, **k):
            calls.append(('cmd', a))
            return ''

    args = SimpleNamespace(name='n', expire='e', add_ignored=False, src_remote_name='origin',
                           push_tag=True, push_note=True, rm_expired=True, flush_meta=True,
                           remote='r')

    grb.push(args, DummyRb(), 'bin', '/p')

    assert ('add_remote', 'bin', 'r') in calls
    for op in ['push_branch', 'push_tag', 'note', 'rm_expired', 'flush_meta']:
        assert op in calls
