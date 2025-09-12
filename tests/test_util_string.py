import pytest
from git_recycle_bin.utils.string import (
    remove_empty_lines,
    sanitize_slashes,
    sanitize_branch_name,
    trim_all_lines,
    prefix_lines,
    string_trunc_ellipsis,
    url_redact,
    str2bool,
)
def test_str2bool():
    assert str2bool('yes') is True
    assert str2bool('no') is False
    with pytest.raises(ValueError):
        str2bool('maybe')

def test_remove_empty_lines():
    s = 'a\n\n b\n'
    assert remove_empty_lines(s) == 'a\n b'


def test_sanitize_slashes():
    assert sanitize_slashes('foo/bar') == 'foo_bar'


def test_sanitize_branch_name():
    assert sanitize_branch_name('foo bar') == 'foo_bar'
    assert sanitize_branch_name('/start') == '_start'
    assert sanitize_branch_name('foo..bar') == 'foo.bar'


def test_trim_all_lines():
    inp = '  a\n b  '
    expected = 'a\nb'
    assert trim_all_lines(inp) == expected


def test_prefix_lines():
    text = 'a\nb'
    assert prefix_lines(text, 'p: ') == 'p: a\np: b'


def test_string_trunc_ellipsis():
    long = 'abcdefg'
    assert string_trunc_ellipsis(10, long) == long
    assert string_trunc_ellipsis(5, long) == 'ab...'

def test_url_redact():
    assert url_redact(url="https://foo:pass@service/my/repo.git", replacement="REDACTED") == "https://foo:REDACTED@service/my/repo.git"
    assert url_redact(url="https://foo@service/my/repo.git", replacement="REDACTED")      == "https://foo@service/my/repo.git"
    assert url_redact(url="https://service/my/repo.git", replacement="REDACTED")          == "https://service/my/repo.git"
    assert url_redact(url="https://service/my/re:po.git", replacement="REDACTED")         == "https://service/my/re:po.git"
    assert url_redact(url="https://service/my/re:po@hmm.git", replacement="REDACTED")     == "https://service/my/re:po@hmm.git"

    assert url_redact(url="ssh://foo:pass@service/my/repo.git", replacement="REDACTED")   == "ssh://foo:REDACTED@service/my/repo.git"
    assert url_redact(url="ssh://foo@service/my/repo.git", replacement="REDACTED")        == "ssh://foo@service/my/repo.git"
    assert url_redact(url="ssh://service/my/repo.git", replacement="REDACTED")            == "ssh://service/my/repo.git"
    assert url_redact(url="ssh://service/my/re:po.git", replacement="REDACTED")           == "ssh://service/my/re:po.git"
    assert url_redact(url="ssh://service/my/re:po@hmm.git", replacement="REDACTED")       == "ssh://service/my/re:po@hmm.git"

    assert url_redact(url="foo:pass@service/my/repo.git", replacement="REDACTED") == "foo:pass@service/my/repo.git"
    assert url_redact(url="foo@service/my/repo.git", replacement="REDACTED")      == "foo@service/my/repo.git"
    assert url_redact(url="service/my/repo.git", replacement="REDACTED")          == "service/my/repo.git"
    assert url_redact(url="service/my/re:po.git", replacement="REDACTED")         == "service/my/re:po.git"
    assert url_redact(url="service/my/re:po@hmm.git", replacement="REDACTED")     == "service/my/re:po@hmm.git"
