"""Tests for artifact-related functionality in git_recycle_bin."""
import datetime

import pytest
import dateparser
from dateutil.tz import tzlocal
import os
from contextlib import contextmanager
import subprocess
from typing import Set

from src import git_recycle_bin as grb  # DUT

def test_trim_all_lines():
    """Test trimming whitespace from all lines."""
    assert grb.trim_all_lines("  hello\n  world\n") == "hello\nworld\n"

def test_prefix_lines():
    """Test adding prefix to all lines."""
    assert grb.prefix_lines("hello\nworld\n", "prefix: ") == "prefix: hello\nprefix: world"

def test_extract_gerrit_change_id():
    """Test extracting Gerrit change ID from commit message."""
    commit_message = "Some changes\n\nChange-Id: I8473b920f2b0d34f2ef5ddbfdf3bea5db12c99d7"
    assert grb.extract_gerrit_change_id(commit_message) == "I8473b920f2b0d34f2ef5ddbfdf3bea5db12c99d7"

def test_string_trunc_ellipsis():
    """Test string truncation with ellipsis."""
    assert grb.string_trunc_ellipsis(5, "hello world") == "he..."

def test_date_formatted2unix():
    """Test converting formatted date to unix timestamp."""
    assert grb.date_formatted2unix("Wed, 21 Jun 2023 14:13:31 +0200", "%a, %d %b %Y %H:%M:%S %z") == 1687349611

def test_absolute_date():
    """Test converting absolute date to expiry format."""
    expected = dateparser.parse("2023-07-27 CEST", settings={"RETURN_AS_TIMEZONE_AWARE": True})
    expected = expected.astimezone(tzlocal()).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("2023-07-27 CEST") == expected

    expected = dateparser.parse("Mon, 1 Feb 1994 21:21:42 GMT", settings={"RETURN_AS_TIMEZONE_AWARE": True})
    expected = expected.astimezone(tzlocal()).strftime(grb.DATE_FMT_EXPIRE)
    assert grb.date_fuzzy2expiryformat("Mon, 1 Feb 1994 21:21:42 GMT") == expected

def test_relative_date():
    """Test converting relative date expressions to expiry format."""
    now_tz = datetime.datetime.now(tzlocal())
    now_expected = now_tz.strftime(grb.DATE_FMT_EXPIRE)
    tomorrow_expected = (now_tz + datetime.timedelta(days=1)).strftime(grb.DATE_FMT_EXPIRE)
    three_weeks_expected = (now_tz + datetime.timedelta(days=21)).strftime(grb.DATE_FMT_EXPIRE)
    thirty_days_expected = (now_tz + datetime.timedelta(days=30)).strftime(grb.DATE_FMT_EXPIRE)

    assert grb.date_fuzzy2expiryformat("now") == now_expected
    assert grb.date_fuzzy2expiryformat("today") == now_expected

    assert grb.date_fuzzy2expiryformat("tomorrow") == tomorrow_expected

    assert grb.date_fuzzy2expiryformat("now in 3 weeks") == three_weeks_expected
    assert grb.date_fuzzy2expiryformat("now in 3 week") == three_weeks_expected
    assert grb.date_fuzzy2expiryformat("now in 3weeks") == three_weeks_expected
    assert grb.date_fuzzy2expiryformat("in 3 weeks") == three_weeks_expected
    assert grb.date_fuzzy2expiryformat("in 3weeks") == three_weeks_expected
    assert grb.date_fuzzy2expiryformat("in 3week") == three_weeks_expected
    assert grb.date_fuzzy2expiryformat("in 3w") == three_weeks_expected

    assert grb.date_fuzzy2expiryformat("in 30 days") == thirty_days_expected
    assert grb.date_fuzzy2expiryformat("in 30 day") == thirty_days_expected
    assert grb.date_fuzzy2expiryformat("in 30days") == thirty_days_expected
    assert grb.date_fuzzy2expiryformat("in 30day") == thirty_days_expected

    assert grb.date_fuzzy2expiryformat("next month") == grb.date_fuzzy2expiryformat("now in 1 month")

def test_invalid_date():
    """Test handling of invalid date expressions."""
    with pytest.raises(ValueError, match="invalid datetime input"):
        grb.date_fuzzy2expiryformat("invalid")
    with pytest.raises(ValueError, match="invalid datetime input"):
        grb.date_fuzzy2expiryformat("Mon, 32 Feb 1994 21:21:42 GMT")

def test_parse_expire_datetime():
    """Test parsing expiry date format strings."""
    p = "artifact/expire/"
    expected_basic = {"date":"2023-07-27", "time":"16.12", "tzoffset":None}
    expected_plus = {"date":"2023-07-27", "time":"16.12", "tzoffset":"+0200"}
    expected_minus = {"date":"2023-07-27", "time":"16.12", "tzoffset":"-0200"}

    assert grb.parse_expire_date(prefix_discard=p,
                                expiry_formatted="artifact/expire/2023-07-27/16.12") == expected_basic
    assert grb.parse_expire_date(prefix_discard=p,
                                expiry_formatted="artifact/expire/2023-07-27/16.12/") == expected_basic
    assert grb.parse_expire_date(prefix_discard=p,
                                expiry_formatted="artifact/expire/2023-07-27/16.12/foo") == expected_basic

    # Test with nested date paths - should use first date/time
    long_path = "artifact/expire/2023-07-27/16.12/2023-08-17/06.02/foo"
    assert grb.parse_expire_date(prefix_discard=p, expiry_formatted=long_path) == expected_basic

    assert grb.parse_expire_date(prefix_discard=p,
                                expiry_formatted="artifact/expire/2023-07-27/16.12+0200") == expected_plus
    assert grb.parse_expire_date(prefix_discard=p,
                                expiry_formatted="artifact/expire/2023-07-27/16.12+0200/") == expected_plus
    assert grb.parse_expire_date(prefix_discard=p,
                                expiry_formatted="artifact/expire/2023-07-27/16.12-0200") == expected_minus

    # Invalid timezone offset should result in None
    assert grb.parse_expire_date(prefix_discard=p,
                                expiry_formatted="artifact/expire/2023-07-27/16.12-03") == expected_basic

    # Test without prefix
    assert grb.parse_expire_date(prefix_discard="",
                                expiry_formatted="2023-07-27/16.12") == expected_basic
    assert grb.parse_expire_date(prefix_discard="",
                                expiry_formatted="2023-07-27/16.12/") == expected_basic

def test_parse_expire_datetime_invalid():
    """Test parsing invalid expiry date formats."""
    expected_invalid = {"date":None, "time":None, "tzoffset":None}
    result = grb.parse_expire_date(prefix_discard="artifact/expire/",
                                  expiry_formatted="artifact/expire/30d/")
    assert result == expected_invalid

def test_url_redact():
    """Test URL redaction functionality for sensitive information."""
    # HTTPS URLs with passwords should be redacted
    result = grb.url_redact(url="https://foo:pass@service/my/repo.git", replacement="REDACTED")
    assert result == "https://foo:REDACTED@service/my/repo.git"
    # HTTPS URLs without passwords should remain unchanged
    result = grb.url_redact(url="https://foo@service/my/repo.git", replacement="REDACTED")
    assert result == "https://foo@service/my/repo.git"
    result = grb.url_redact(url="https://service/my/repo.git", replacement="REDACTED")
    assert result == "https://service/my/repo.git"
    result = grb.url_redact(url="https://service/my/re:po.git", replacement="REDACTED")
    assert result == "https://service/my/re:po.git"
    result = grb.url_redact(url="https://service/my/re:po@hmm.git", replacement="REDACTED")
    assert result == "https://service/my/re:po@hmm.git"

    # SSH URLs with passwords should be redacted
    result = grb.url_redact(url="ssh://foo:pass@service/my/repo.git", replacement="REDACTED")
    assert result == "ssh://foo:REDACTED@service/my/repo.git"
    # SSH URLs without passwords should remain unchanged
    result = grb.url_redact(url="ssh://foo@service/my/repo.git", replacement="REDACTED")
    assert result == "ssh://foo@service/my/repo.git"
    result = grb.url_redact(url="ssh://service/my/repo.git", replacement="REDACTED")
    assert result == "ssh://service/my/repo.git"
    result = grb.url_redact(url="ssh://service/my/re:po.git", replacement="REDACTED")
    assert result == "ssh://service/my/re:po.git"
    result = grb.url_redact(url="ssh://service/my/re:po@hmm.git", replacement="REDACTED")
    assert result == "ssh://service/my/re:po@hmm.git"

    assert grb.url_redact(url="foo:pass@service/my/repo.git", replacement="REDACTED") == "foo:pass@service/my/repo.git"
    assert grb.url_redact(url="foo@service/my/repo.git", replacement="REDACTED")      == "foo@service/my/repo.git"
    assert grb.url_redact(url="service/my/repo.git", replacement="REDACTED")          == "service/my/repo.git"
    assert grb.url_redact(url="service/my/re:po.git", replacement="REDACTED")         == "service/my/re:po.git"
    assert grb.url_redact(url="service/my/re:po@hmm.git", replacement="REDACTED")     == "service/my/re:po@hmm.git"


@pytest.fixture
def temp_git_setup(tmpdir):
    # Create temporary directories
    local_repo = tmpdir.mkdir("local_repo")
    remote_repo = tmpdir.mkdir("remote_repo")
    artifact_repo = tmpdir.mkdir("artifact_repo")

    # Initialize the 'remote' repository
    subprocess.run(['git', 'init', '--bare'], cwd=remote_repo, check=True)

    # Initialize the local repository
    subprocess.run(['git', 'init'], cwd=local_repo, check=True)

    # Initialize the artifact repository
    subprocess.run(['git', 'init', '--bare'], cwd=artifact_repo, check=True)

    # Add the remote
    remote_url = f"file://{remote_repo}"
    subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=local_repo, check=True)

    # add some files to the local repository
    local_file = local_repo.join("example.txt")
    local_file.write("This is a test file.")
    with git_user_info():
        subprocess.run(['git', 'add', 'example.txt'], cwd=local_repo, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=local_repo, check=True)
        subprocess.run(['git', 'push', 'origin', 'master'], cwd=local_repo, check=True)

    # Return both directories as a tuple to be used in tests
    yield (local_repo, remote_repo, artifact_repo, [(local_file, "example.txt")])


@contextmanager
def change_dir(path):
    original_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_dir)

@contextmanager
def git_user_info():
    old_env = os.environ.copy()
    os.environ["GIT_AUTHOR_NAME"] = "mock"
    os.environ["GIT_AUTHOR_EMAIL"] = "mock@mock.mock"
    os.environ["GIT_COMMITTER_NAME"] = "mock"
    os.environ["GIT_COMMITTER_EMAIL"] = "mock@mock.mock"
    try:
        yield
    finally:
        os.environ = old_env


def contains_metas(rbgit: grb.RbGit, remote: str, commit_shas: Set[str]) -> bool:
    metas = rbgit.meta_for_commit_refs(remote)
    assert commit_shas == { meta[-40:] for meta in metas }
    # return True to allow us to do assert contains_metas which reads better than
    # just contains_metas
    return True

def test_flush_meta_for_commit(temp_git_setup):
    local, _, artifact_remote, artifacts = temp_git_setup
    artifact_path, artifact_name = artifacts[0]

    _args = ["push", f"{artifact_remote}",
             "--path", f"{artifact_path}",
             "--name", artifact_name,
             ]
    _dead = _args + ["--expire", "2 hours ago"]
    dead = grb.parse_args(_dead)
    longlived = grb.parse_args(_args + ["--expire", "in 30 days"])
    dead_flush = grb.parse_args(_dead + ["--flush-meta"])
    dead_rm_flush = grb.parse_args(_dead + ["--rm-expired", "--flush-meta"])
    dead_rm = grb.parse_args(_dead + ["--rm-expired"])

    rbgit=grb.create_rbgit(local, dead.path, clean=True)
    rb_remote="rbgit"

    def push(args):
        return grb.push(args, rbgit, rb_remote, artifact_name)['bin_sha_commit']

    with change_dir(local), git_user_info():
        bin_commit = push(dead)
        assert contains_metas(rbgit, rb_remote, {bin_commit})

        # without --remove-expired the refs should still exist
        bin_commit2 = push(dead_flush)
        assert contains_metas(rbgit, rb_remote, {bin_commit, bin_commit2})

        # with --remove-expired the refs should be removed
        push(dead_rm_flush)
        assert contains_metas(rbgit, rb_remote, set())

        # with only --remove-expired the refs should not be removed
        bin_commit = push(dead_rm)
        assert contains_metas(rbgit, rb_remote, {bin_commit})

        # with --flush-meta the new artifact should not be removed but the old one should
        bin_commit = push(dead_flush)
        assert contains_metas(rbgit, rb_remote, {bin_commit})

        # only the longlived artifact should be present
        bin_commit = push(longlived)
        push(dead_rm_flush)
        assert contains_metas(rbgit, rb_remote, {bin_commit})
>>>>>>> db426b4 (metas: Align code for meta handling with schema)
