import pytest

from rbgit import RbGit

class DummyRbGit:
    def cmd(self, *args, **kwargs):
        if args[:2] == ("ls-tree", "-lr"):
            return (
                "100644 blob aaaaaa 123\tfile1\n"
                "100644 blob bbbbbb 456\tfile2\n"
            )
        raise RuntimeError("Unexpected command")

def test_tree_size_sum():
    dummy = DummyRbGit()
    size = RbGit.tree_size(dummy, "HEAD")
    assert size == 579


def test_remote_already_has_ref():
    class D:
        def cmd(self, *args):
            if args[0] == 'ls-remote':
                return 'sha\tref' if args[-1] == 'ref' else ''
            raise RuntimeError('bad')

    dummy = D()
    assert RbGit.remote_already_has_ref(dummy, 'origin', 'ref') is True
    assert RbGit.remote_already_has_ref(dummy, 'origin', 'missing') is False


def test_fetch_current_tag_value():
    class D:
        def cmd(self, *args):
            if args[:3] == ('ls-remote', '--tags', 'origin'):
                return 'a1\trefs/tags/v1\nb2\trefs/tags/v2'
            raise RuntimeError('bad')

    dummy = D()
    assert RbGit.fetch_current_tag_value(dummy, 'origin', 'v2') == 'b2'


def test_fetch_cat_pretty():
    calls = []

    class D:
        def cmd(self, *args, **kwargs):
            calls.append(args)
            if args[0] == 'fetch':
                return ''
            if args[:2] == ('cat-file', '-p'):
                return 'content'
            raise RuntimeError('bad')

    dummy = D()
    res = RbGit.fetch_cat_pretty(dummy, 'origin', 'ref')
    assert calls[0] == ('fetch', 'origin', 'ref')
    assert res == 'content'


def test_add_no_changes(tmp_path):
    path = tmp_path / 'file'
    path.write_text('data')

    calls = []

    class D:
        def cmd(self, *args, **kwargs):
            calls.append(args)
            if args[0] == 'diff-index':
                return ''
            return ''

    dummy = D()
    res = RbGit.add(dummy, str(path))
    assert res is False
    assert ('add', str(path)) in calls


def test_add_changes_force(tmp_path):
    path = tmp_path / 'file'
    path.write_text('data')

    calls = []

    class D:
        def cmd(self, *args, **kwargs):
            calls.append(args)
            if args[0] == 'diff-index':
                raise RuntimeError('changed')
            return ''

    dummy = D()
    res = RbGit.add(dummy, str(path), force=True)
    assert res is True
    assert ('add', '--force', str(path)) in calls


def test_add_remote_idempotent_adds():
    calls = []

    class D:
        def cmd(self, *args, **kwargs):
            calls.append(args)
            return ''

    dummy = D()
    RbGit.add_remote_idempotent(dummy, 'origin', 'url')
    assert calls == [('remote', 'add', 'origin', 'url')]


def test_add_remote_idempotent_set_url():
    calls = []

    class D:
        def cmd(self, *args, **kwargs):
            calls.append(args)
            if args[:2] == ('remote', 'add'):
                raise RuntimeError('exists')
            return ''

    dummy = D()
    RbGit.add_remote_idempotent(dummy, 'origin', 'url')
    assert ('remote', 'set-url', 'origin', 'url') in calls


def test_fetch_only_tags_and_set_tag():
    calls = []

    class D:
        def cmd(self, *args, **kwargs):
            calls.append(args)
            return ''

    dummy = D()
    RbGit.fetch_only_tags(dummy, 'origin')
    RbGit.set_tag(dummy, 'v1', 'sha')
    assert ('fetch', 'origin', 'refs/tags/*:refs/tags/*') in calls
    assert ('tag', '--force', 'v1', 'sha') in calls
