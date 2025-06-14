import subprocess
from util import exec, exec_nostderr


def test_exec_env(monkeypatch):
    called = {}

    def fake_check_output(cmd, env=None, text=None, stderr=None):
        called['cmd'] = cmd
        called['env'] = env
        called['stderr'] = stderr
        return 'out'

    monkeypatch.setattr(subprocess, 'check_output', fake_check_output)
    res = exec(['echo', 'hi'], env={'FOO': 'BAR'})
    assert res == 'out'
    assert called['cmd'] == ['echo', 'hi']
    assert called['env']['FOO'] == 'BAR'
    assert called['stderr'] is None


def test_exec_nostderr(monkeypatch):
    called = {}

    def fake_check_output(cmd, env=None, text=None, stderr=None):
        called['stderr'] = stderr
        return ''

    monkeypatch.setattr(subprocess, 'check_output', fake_check_output)
    exec_nostderr(['echo'])
    assert called['stderr'] is subprocess.DEVNULL
