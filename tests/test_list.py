from types import SimpleNamespace
from copy import deepcopy
import git_recycle_bin.commands.list as list_mod
from git_recycle_bin.query import NameQuery, RelPathQuery

### SETUP
list_results = [
    list_mod.ListResult(
        meta_sha='m1',
        artifact_sha='sha1',
        meta_data={'artifact-name': 'foo', 'src-git-relpath': 'path1'}
    ),
    list_mod.ListResult(
        meta_sha='m2',
        artifact_sha='sha2',
        meta_data={'artifact-name': 'bar', 'src-git-relpath': 'path2'}
    ),
    list_mod.ListResult(
        meta_sha='m3',
        artifact_sha='sha3',
        meta_data={'artifact-name': 'baz', 'src-git-relpath': 'path3'}
    ),
]
def fake_sha(i):
    return 'abcd' if i < 2 else 'efgh'

def as_ls_remote(list_results, ref):
    ref = ref.rstrip('*')
    lines = []
    for i, r in enumerate(list_results):
        sha = fake_sha(i)
        if ref.endswith(f"/{sha}/") or ref == 'refs/artifact/meta-for-commit/':
            lines.append(f"{r.meta_sha} refs/artifact/meta-for-commit/{sha}/{r.artifact_sha}")
    print(lines)
    return '\n'.join(lines) + '\n'

def map_src_sha(list_results):
    results = []
    for i, r in enumerate(list_results):
        sha = fake_sha(i)
        new_result = deepcopy(r)
        new_result.artifact_sha = f"{sha}/{r.artifact_sha}"
        results.append(new_result)
    return results

def as_messages(list_results):
    msgs = {}
    for r in list_results:
        msgs[r.meta_sha] = f"artifact-name: {r.meta_data['artifact-name']}\nsrc-git-relpath: {r.meta_data['src-git-relpath']}"
    return msgs

### TESTS

def test_remote_artifacts(monkeypatch):
    # patch util.exec to return known sha
    monkeypatch.setattr(list_mod, 'exec', lambda cmd: 'abcd')

    def fake_cmd(*args, **kwargs):
        if args[:3] == ('ls-remote', '--refs', 'remote'):
            return as_ls_remote(list_results, args[3])
        raise AssertionError('unexpected')

    msgs = as_messages(list_results)

    def fake_fetch(remote, ref):
        return msgs[ref]

    dummy = SimpleNamespace(cmd=fake_cmd, fetch_cat_pretty=fake_fetch)
    res = list_mod.remote_artifacts_unfiltered(dummy, 'remote')
    assert res == list_results[:2]  # only first two have sha 'abcd'

    res = list_mod.remote_artifacts_unfiltered(dummy, 'remote', sha='abcd')
    assert res == list_results[:2]  # only first two have sha 'abcd'

    res = list_mod.remote_artifacts_unfiltered(dummy, 'remote', all_shas=True)
    assert res == map_src_sha(list_results)




def test_filter_artifacts_by_name_and_path(monkeypatch):
    filtered = list_mod.filter_artifacts(list_results, NameQuery('foo'))
    assert filtered == [list_results[0]]

    and_query = list_mod.AndQuery(NameQuery('foo'), RelPathQuery('path1'))
    filtered = list_mod.filter_artifacts(list_results, and_query)
    assert filtered == [list_results[0]]

    filtered = list_mod.filter_artifacts(list_results, RelPathQuery('path2'))
    assert filtered == [list_results[1]]
