"""Tests for argument parser functionality."""

import sys
import argparse
import pytest

from git_recycle_bin import arg_parser


def run_parse_args(argv):
    """Helper function to run arg parser with test arguments."""
    old = sys.argv
    sys.argv = ['prog'] + argv
    try:
        return arg_parser.parse_args()
    finally:
        sys.argv = old


def test_str2bool():
    """Test string to boolean conversion function."""
    assert arg_parser.str2bool('yes') is True
    assert arg_parser.str2bool('no') is False
    with pytest.raises(argparse.ArgumentTypeError):
        arg_parser.str2bool('maybe')


def test_tuple1():
    """Test tuple1 function for key-value pair creation."""
    f = arg_parser.tuple1('key')
    assert f('val') == ('key', 'val')


def test_parse_args_push():
    """Test push command argument parsing."""
    args = run_parse_args(['push', 'https://example.com', '--path', '/tmp/foo', '--name', 'bar'])
    assert args.command == 'push'
    assert args.remote == 'https://example.com'
    assert args.path == '/tmp/foo'
    assert args.name == 'bar'


def test_parse_args_force_tag_requires_force_branch():
    """Test that force-tag requires force-branch option."""
    res = run_parse_args(['push', 'https://example.com', '--path', '/tmp/foo', '--name', 'bar', '--force-tag'])
    assert res is None


def test_parse_args_list_name():
    """Test list command with name query argument parsing."""
    args = run_parse_args(['list', 'https://example.com', '--name', 'foo'])
    assert args.command == 'list'
    assert args.query == ('name', 'foo')


def test_parse_args_missing_remote():
    """Test that missing remote argument causes system exit."""
    with pytest.raises(SystemExit):
        run_parse_args(['list'])
