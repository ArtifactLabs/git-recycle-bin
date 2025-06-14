import os
from util_file import nca_path, rel_dir, classify_path


def test_nca_and_rel(tmp_path):
    a = tmp_path / 'a'
    b = tmp_path / 'a' / 'b'
    b.mkdir(parents=True)
    assert nca_path(a, b) == str(a.resolve())
    assert rel_dir(a, b) == 'b'


def test_classify_path(tmp_path):
    f = tmp_path / 'file.txt'
    f.write_text('hi')
    assert classify_path(str(f)) == ('text/plain', None)
    assert classify_path(str(tmp_path)) == 'directory'
    assert classify_path(str(tmp_path / 'missing')) == 'unknown'
