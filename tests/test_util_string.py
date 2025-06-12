from util_string import remove_empty_lines, sanitize_slashes, sanitize_branch_name


def test_remove_empty_lines():
    s = 'a\n\n b\n'
    assert remove_empty_lines(s) == 'a\n b'


def test_sanitize_slashes():
    assert sanitize_slashes('foo/bar') == 'foo_bar'


def test_sanitize_branch_name():
    assert sanitize_branch_name('foo bar') == 'foo_bar'
    assert sanitize_branch_name('/start') == '_start'
    assert sanitize_branch_name('foo..bar') == 'foo.bar'
