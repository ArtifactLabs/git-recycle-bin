import re

from util_string import (
    prefix_lines,
    remove_empty_lines,
    string_trunc_ellipsis,
    trim_all_lines,
    url_redact,
)


def extract_gerrit_change_id(commit_message: str) -> str:
    # Find the Change-Id line(s)
    change_id_lines = [line for line in commit_message.split('\n') if line.startswith("Change-Id:")]

    # Extract the Change ID from the last matching line, if any
    if change_id_lines:
        last_change_id_line = change_id_lines[-1]
        _, change_id = last_change_id_line.split(maxsplit=1)
        return change_id

    # If there is no Change-Id line, return an empty string
    return ""

def parse_commit_msg(commit_msg):
    # Regex breakdown:
    #   ^([\w-]+) matches the key made up of word chars and dashes from line-start, captured in group 1
    #   :         matches the colon delimiter
    #   (.*)      matches the rest of the line as the value, captured in group 2
    pattern = r'^([\w-]+):(.*)'

    ## NOTE: This does not handle multi-line git trailers correctly, e.g. src-git-status
    ret_dict = {}
    for line in commit_msg.strip().splitlines():
        match = re.match(pattern, line)
        if match:
            key, val = match.group(1), match.group(2)
            ret_dict[key.strip()] = val.strip()
    return ret_dict

def emit_commit_msg(d: dict):
    commit_msg_title = f"""
        artifact: {d['src_repo']}@{d['src_sha_short']}: {d['artifact_name']} @({string_trunc_ellipsis(30, d['src_sha_title']).strip()})
    """

    commit_msg_body = """
        This artifact was published by git-recycle-bin - it may expire!
        See https://github.com/ArtifactLabs/git-recycle-bin
    """

    commit_msg_trailers = f"""
        artifact-schema-version: 1
        artifact-name: {d['artifact_name']}
        artifact-mime-type: {d['artifact_mime']}
        artifact-tree-prefix: {d['artifact_relpath_nca']}
        src-git-relpath: {d['artifact_relpath_src']}
        src-git-commit-title: {d['src_sha_title']}
        src-git-commit-sha: {d['src_sha']}
        {prefix_lines(prefix="src-git-commit-changeid: ", lines=extract_gerrit_change_id(d['src_sha_msg']))}
        src-git-commit-time-author: {d['src_time_author']}
        src-git-commit-time-commit: {d['src_time_commit']}
        src-git-branch: {d['src_branch'] if d['src_branch'] != "HEAD" else "Detached HEAD"}
        src-git-repo-name: {d['src_repo']}
        src-git-repo-url: {url_redact(d['src_repo_url'])}
        src-git-commits-ahead: {d['src_commits_ahead'] if d['src_commits_ahead'] != "" else "?"}
        src-git-commits-behind: {d['src_commits_behind'] if d['src_commits_behind'] != "" else "?"}
        {prefix_lines(prefix="src-git-status: ", lines=trim_all_lines(d['src_status'] if d['src_status'] != "" else "clean"))}
    """

    commit_msg = f"""
        {commit_msg_title}

        {commit_msg_body}

        {remove_empty_lines(trim_all_lines(commit_msg_trailers))}
    """

    return trim_all_lines(commit_msg)
