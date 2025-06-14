import sys
import argparse
import pytest
import arg_parser


def run_parse_args(argv):
    old = sys.argv
    sys.argv = ['prog'] + argv
    try:
        return arg_parser.parse_args()
    finally:
        sys.argv = old


def test_str2bool():
    assert arg_parser.str2bool('yes') is True
    assert arg_parser.str2bool('no') is False
    with pytest.raises(argparse.ArgumentTypeError):
        arg_parser.str2bool('maybe')


def test_tuple1():
    f = arg_parser.tuple1('key')
    assert f('val') == ('key', 'val')


def test_parse_args_push():
    args = run_parse_args(['push', 'https://example.com', '--path', '/tmp/foo', '--name', 'bar'])
    assert args.command == 'push'
    assert args.remote == 'https://example.com'
    assert args.path == '/tmp/foo'
    assert args.name == 'bar'


def test_parse_args_force_tag_requires_force_branch():
    res = run_parse_args(['push', 'https://example.com', '--path', '/tmp/foo', '--name', 'bar', '--force-tag'])
    assert res is None


def test_parse_args_list_name():
    args = run_parse_args(['list', 'https://example.com', '--name', 'foo'])
    assert args.command == 'list'
    assert args.query == ('name', 'foo')


def test_parse_args_missing_remote():
    with pytest.raises(SystemExit):
        run_parse_args(['list'])
