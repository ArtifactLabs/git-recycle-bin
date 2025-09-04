from types import SimpleNamespace
import git_recycle_bin.commands.list as list_mod


def test_remote_artifacts(monkeypatch):
    # patch util.exec to return known sha
    monkeypatch.setattr(list_mod, 'exec', lambda cmd: 'abcd')

    def fake_cmd(*args, **kwargs):
        if args[:3] == ('ls-remote', '--refs', 'remote'):
            return 'm1 refs/artifact/meta-for-commit/abcd/sha1\nm2 refs/artifact/meta-for-commit/abcd/sha2\n'
        raise AssertionError('unexpected')

    dummy = SimpleNamespace(cmd=fake_cmd)
    res = list_mod.remote_artifacts_unfiltered(dummy, 'remote')
    assert res == [('m1', 'sha1'), ('m2', 'sha2')]


def test_filter_artifacts_by_name_and_path(monkeypatch):
    msgs = {
        'm1': 'artifact-name: foo\nsrc-git-relpath: path1',
        'm2': 'artifact-name: bar\nsrc-git-relpath: path2',
    }

    def fake_fetch(remote, ref):
        return msgs[ref]

    dummy = SimpleNamespace(
        fetch_cat_pretty=lambda r, ref: fake_fetch(r, ref)
    )
    artifacts = [('m1', 'sha1'), ('m2', 'sha2')]

    filtered = list_mod.filter_artifacts(
        dummy, 'r', 'foo', artifacts, list_mod.filter_artifacts_by_name
    )
    assert filtered == [('m1', 'sha1')]

    filtered = list_mod.filter_artifacts(
        dummy, 'r', 'path2', artifacts, list_mod.filter_artifacts_by_path
    )
    assert filtered == [('m2', 'sha2')]
