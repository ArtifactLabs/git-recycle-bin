from util_string import (
    remove_empty_lines,
    sanitize_slashes,
    sanitize_branch_name,
    trim_all_lines,
    prefix_lines,
    string_trunc_ellipsis,
)


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
