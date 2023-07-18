#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from itertools import takewhile

from rbgit import RbGit

def trim_all_lines(input_string):
    lines = input_string.split('\n')
    trimmed_lines = [line.strip() for line in lines]
    return '\n'.join(trimmed_lines)


def prefix_lines(lines: str, prefix: str) -> str:
    return "\n".join([prefix+line for line in lines.split('\n')])


def extract_gerrit_change_id(commit_message: str, prefix: str) -> str:
    # Find the Change-Id line(s)
    change_id_lines = [line for line in commit_message.split('\n') if line.startswith("Change-Id:")]

    # Extract the Change ID from the last matching line, if any
    if change_id_lines:
        last_change_id_line = change_id_lines[-1]
        _, change_id = last_change_id_line.split(maxsplit=1)
        return f"{prefix}{change_id}"

    # If there is no Change-Id line, return an empty string
    return ""

def string_trunc_ellipsis(maxlen: int, longstr: str) -> str:
    if len(longstr) <= maxlen:
        return longstr

    shortstr = longstr[:maxlen]
    if len(shortstr) == maxlen:
        return shortstr[:(maxlen-3)] + "..."
    else:
        return shortstr


def exec(command):
    print("Run:", command)
    return subprocess.check_output(command, text=True).strip()


def nca_path(pathA, pathB):
    """ Get nearest common ancestor of two paths """

    # Get absolute paths. Inputs may be relative.
    components1 = os.path.abspath(pathA).split(os.sep)
    components2 = os.path.abspath(pathB).split(os.sep)

    # Use zip to iterate over pairs of components
    # Stop when components differ, thanks to the use of itertools.takewhile
    common_components = list(takewhile(lambda x: x[0]==x[1], zip(components1, components2)))

    # The common path is the joined common components
    common_path = os.sep.join([x[0] for x in common_components])
    return common_path


def rel_dir(context, query):
    """ Get relative path to query from NCA(context,query) """
    abs_context = os.path.abspath(context)
    abs_query = os.path.abspath(query)
    common_path = nca_path(abs_context, abs_query)
    return os.path.relpath(abs_query, common_path)





def create_artifact_commit(artifact_name: str, binpath: str) -> str:
    """ Create Artifact: A binary commit, with builtin traceability and expiry """
    ttl = "30 days"

    # TODO: Test for binpath existence
    src_remote_name = "origin"    # TODO: Expose as argument
    src_sha       = exec(["git", "rev-parse", "HEAD"])  # full sha
    src_sha_short = exec(["git", "rev-parse", "--short", "HEAD"])  # human readable
    src_sha_msg   = exec(["git", "show", "--no-patch", "--format=%B", src_sha])
    src_sha_title = src_sha_msg.split('\n')[0]  # title is first line of commit-msg
    src_branch    = exec(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    src_repo_url  = exec(["git", "config", "--get", f"remote.{src_remote_name}.url"])
    src_repo      = os.path.basename(src_repo_url)
    src_tree_pwd  = os.getcwd()
    src_status    = exec(["git", "status", "--porcelain=1", "--untracked-files=no"])

    branch_name = f"auto/checkpoint/{src_repo}/{src_sha}/{artifact_name}"

    nca_dir     = nca_path(src_tree_pwd, binpath)
    binpath_rel = rel_dir(src_tree_pwd, binpath)

    rbgit = RbGit(rbgit_dir=f"{nca_dir}/.rbgit", rbgit_work_tree=nca_dir)
    rbgit.init_idempotent()
    rbgit.checkout_orphan_idempotent(branch_name)

    print(f"Adding '{binpath}' as '{binpath_rel}' ...", file=sys.stderr)
    changes = rbgit.add(binpath)
    if changes == False:
        print("No changes for the next commit", file=sys.stderr)
        return

    # Preparing commit message
    commit_msg = f"""
        artifact: {src_repo}@{src_sha_short}: {artifact_name} @({string_trunc_ellipsis(30, src_sha_title).strip()})

        This is a (binary) artifact with expiry. Expiry can be changed.
        See https://gitlab.ci.demant.com/csfw/flow/git-recycle-bin

        artifact-scheme-version: 1
        artifact-name: {artifact_name}
        artifact-path: {binpath_rel}
        artifact-time-to-live: {ttl}
        src-git-commit-title: {src_sha_title}
        src-git-commit-sha: {src_sha}
        src-git-branch: {src_branch}
        src-git-repo: {src_repo}
        src-git-repo-url: {src_repo_url}
    """ + extract_gerrit_change_id(src_sha_msg, "src-git-commit-changeid: ") \
        + prefix_lines(prefix="src-git-status: ", lines=src_status)

    # Set {author,committer}-dates: Make our new commit reproducible by copying from the source; do not sample the current time.
    print("Committing", file=sys.stderr)
    os.environ['GIT_AUTHOR_DATE'] = exec(["git", "show", "-s", "--format=%aD", src_sha])
    os.environ['GIT_COMMITTER_DATE'] = exec(["git", "show", "-s", "--format=%cD", src_sha])
    rbgit.cmd("commit", "--file", "-", "--quiet", "--no-status", "--untracked-files=no", input=trim_all_lines(commit_msg))
    print(rbgit.cmd("log", "-1", "HEAD"))






def main():
    parser = argparse.ArgumentParser(description="Create a checkpoint - an artifact which has traceability and expiry")
    parser.add_argument("artifact_name", help="The name of the artifact")
    parser.add_argument("binpath", help="The path to the binary")

    args = parser.parse_args()

    create_artifact_commit(args.artifact_name, args.binpath)

if __name__ == "__main__":
    main()
