from types import SimpleNamespace
from download import download_command

class DummyRbGit:
    def __init__(self):
        self.calls = []
    def cmd(self, *args):
        self.calls.append(args)
        if args[0] == 'checkout' and args[-1] == 'fail' and '-f' not in args:
            raise RuntimeError('exists')


def test_download_force_false_error(capsys):
    rbgit = DummyRbGit()
    args = SimpleNamespace(artifacts=['fail'], force=False)
    ret = download_command(args, rbgit, 'remote')
    assert ret == 1
    assert ('fetch', 'remote', 'fail') in rbgit.calls
    assert ('checkout', 'fail') in rbgit.calls


def test_download_force_true():
    rbgit = DummyRbGit()
    args = SimpleNamespace(artifacts=['ok'], force=True)
    ret = download_command(args, rbgit, 'remote')
    assert ret is None
    assert rbgit.calls == [('fetch', 'remote', 'ok'), ('checkout', '-f', 'ok')]
