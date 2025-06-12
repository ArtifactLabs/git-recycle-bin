import datetime
import re
from commit_msg import extract_gerrit_change_id, parse_commit_msg, emit_commit_msg


def test_extract_gerrit_change_id():
    msg = "Change-Id: Iabc\nChange-Id: Idef"
    assert extract_gerrit_change_id(msg) == "Idef"


def test_parse_commit_msg():
    msg = "key1: val1\nkey2: val2\nignored"
    assert parse_commit_msg(msg) == {"key1": "val1", "key2": "val2"}


def test_emit_commit_msg_redacts_url():
    d = {
        "artifact_name": "artifact",
        "src_repo": "repo.git",
        "src_sha_short": "abcdef1234",
        "src_sha_title": "Commit title",
        "artifact_mime": "text/plain",
        "artifact_relpath_nca": "path/to",
        "artifact_relpath_src": "path/to",
        "src_sha": "abcdef1234567890",
        "src_sha_msg": "Commit title\n\nChange-Id: Ideadbeef",
        "src_time_author": "Thu, 01 Jan 1970 00:00:00 +0000",
        "src_time_commit": "Thu, 01 Jan 1970 00:00:00 +0000",
        "src_branch": "main",
        "src_repo_url": "https://user:pass@host/repo.git",
        "src_commits_ahead": "1",
        "src_commits_behind": "0",
        "src_status": "",
    }
    msg = emit_commit_msg(d)
    assert "artifact: repo.git@abcdef1234: artifact @(Commit title)" in msg
    assert "src-git-repo-url: https://user:REDACTED@host/repo.git" in msg
