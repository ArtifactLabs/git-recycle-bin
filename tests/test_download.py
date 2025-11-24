from types import SimpleNamespace
import git_recycle_bin.commands.download as download_mod
from git_recycle_bin.commands.list import ListResult

class DummyRbGit:
    def __init__(self, rbgit_work_tree=None):
        self.calls = []
        self.rbgit_work_tree = rbgit_work_tree

    def cmd(self, *args):
        self.calls.append(args)
        if args[0] == 'checkout' and args[-1] == 'fail' and '-f' not in args:
            raise RuntimeError('exists')

    def get_remote_url(self, remote_bin_name):
        self.calls.append(('get_remote_url', remote_bin_name))
        return 'dummy_url'

    def add_remote_idempotent(self, name, url):
        self.calls.append(('add_remote_idempotent', name, url))

    def cleanup(self):
        self.calls.append(('cleanup'))


def test_download_single_force_false_error(capsys):
    rbgit = DummyRbGit()
    ret = download_mod.download_single(rbgit, 'remote', 'fail')
    assert ret == 1
    assert ('fetch', 'remote', 'fail') in rbgit.calls
    assert ('checkout', 'fail') in rbgit.calls


def test_download_single_force_true():
    rbgit = DummyRbGit()
    ret = download_mod.download_single(rbgit, 'remote', 'ok', force=True)
    assert ret is None
    assert rbgit.calls == [('fetch', 'remote', 'ok'), ('checkout', '-f', 'ok')]

def test_download_single_path_specified():
    rbgit = DummyRbGit()
    ret = download_mod.download_single(rbgit, 'remote', 'ok', path='some/path')
    assert ret is None
    assert rbgit.calls == [('fetch', 'remote', 'ok'), ('checkout', 'ok', 'some/path')]

def test_download_function(monkeypatch):
    """Test the main download function with multiple branches"""
    rbgit = DummyRbGit()
    intermediary_rbgits = []
    def mock_create_rbgit(artifact_path, *args, **kwargs):
        rbgit = DummyRbGit(artifact_path)
        intermediary_rbgits.append(rbgit)
        return rbgit
    monkeypatch.setattr(download_mod, 'create_rbgit', mock_create_rbgit)

    artifacts = [
        ListResult(meta_sha='meta1',
                   artifact_sha='branch1',
                   meta_data={'src-git-relpath': 'path1',
                              'artifact-tree-prefix': 'prefix1'}),
        ListResult(meta_sha='meta2',
                     artifact_sha='branch2',
                     meta_data={'src-git-relpath': 'path2',
                                'artifact-tree-prefix': 'prefix2'}),
    ]
    # Test successful download of multiple branches
    result = download_mod.download(rbgit, 'remote', artifacts, force=False, rm_tmp=True)

    assert result is None
    assert [('get_remote_url', 'remote')] == rbgit.calls

    for irbgit, artifact in zip(intermediary_rbgits, artifacts):
        remote_name = artifact.meta_data['artifact-tree-prefix']
        expected_calls = [
            ('add_remote_idempotent', remote_name, 'dummy_url'),
            ('fetch', remote_name, artifact.artifact_sha),
            ('checkout', artifact.artifact_sha, remote_name),
            ('cleanup')
        ]
        assert expected_calls == irbgit.calls
    # TODO test result of intermediary rbgit instances
