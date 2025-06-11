import os
import tempfile
import pytest

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import util_file
import util_string
from commit_msg import parse_commit_msg


def test_nca_and_rel_dir():
    assert util_file.nca_path('/tmp/a/b/c', '/tmp/a/b/d') == '/tmp/a/b'
    assert util_file.rel_dir('/tmp/a', '/tmp/a/b/c') == 'b/c'


def test_classify_path_variants():
    fd, fp = tempfile.mkstemp()
    os.close(fd)
    try:
        assert isinstance(util_file.classify_path(fp), tuple)
    finally:
        os.unlink(fp)

    with tempfile.TemporaryDirectory() as d:
        assert util_file.classify_path(d) == 'directory'

    with tempfile.TemporaryDirectory() as d:
        link = os.path.join(d, 'broken')
        os.symlink('does-not-exist', link)
        assert util_file.classify_path(link) == 'link'


def test_sanitize_branch_name_complex():
    dirty = '/../foo..bar@{baz}?* '
    assert util_string.sanitize_branch_name(dirty) == '_./foo.bar@{baz}___'


def test_parse_commit_msg_simple():
    msg = 'key1: value1\nkey-two: value two\nother line'
    assert parse_commit_msg(msg) == {'key1': 'value1', 'key-two': 'value two'}

