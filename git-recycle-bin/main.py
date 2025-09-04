#!/usr/bin/env python3
import sys

from .utils.extern import exec
from .printer import printer
from .arg_parser import parse_args
from .rbgit import create_rbgit

# commands
from . import (
    remote_artifacts,
    push,
    clean,
    remote_delete_expired_branches,
    remote_flush_meta_for_commit,
    download,
    cat_metas
)


def main() -> int:
    # TODO: Add --add-submodule to add src-git as a {update=none, shallow, nonrecursive} submodule in artifact-commit.

    args = parse_args()
    if args is None:
        return 1

    printer.debug("Arguments:", file=sys.stderr)
    for arg in vars(args):
        printer.debug(f"  '{arg}': '{getattr(args, arg)}'", file=sys.stderr)

    if args.remote == ".":
        src_git_dir = exec(["git", "rev-parse", "--absolute-git-dir"])
        printer.high_level(f"Will push artifact to local src-git, {src_git_dir}. Mostly used for testing.", file=sys.stderr)
        args.remote = src_git_dir

    # Source git's root, fully qualified path.
    # --show-toplevel: "Show the (by default, absolute) path of the top-level directory of the working tree."
    src_tree_root = exec(["git", "rev-parse", "--show-toplevel"])

    # only some commands require path. All other cases, the git root suffices.
    try:
        path = args.path if args.path else src_tree_root
    except AttributeError:
        path = src_tree_root


    remote_bin_name = "recyclebin"
    commit_info = None

    with create_rbgit(src_tree_root, path, clean=args.rm_tmp) as rbgit:

        # setup
        if args.user_name:
            rbgit.cmd("config", "--local", "user.name", args.user_name)
        if args.user_email:
            rbgit.cmd("config", "--local", "user.email", args.user_email)

        if args.remote:
            rbgit.add_remote_idempotent(name=remote_bin_name, url=args.remote)


        # main command
        if args.command == "push":
            commit_info = push(args, rbgit, remote_bin_name, path)
        if args.command == "clean":
            clean(rbgit, remote_bin_name)
        if args.command == "list":
            for _, artifact_sha in remote_artifacts(rbgit, remote_bin_name,
                                                    args.query,
                                                    args.list_all_shas
                                                    ):
                print(artifact_sha)
        if args.command == "download":
            download(args, rbgit, remote_bin_name)
        if args.command == "cat-meta":
            cat_metas(rbgit, remote_bin_name, args.commits)

        # garbage collection
        if args.rm_expired:
            remote_delete_expired_branches(rbgit, remote_bin_name)
        if args.flush_meta:
            remote_flush_meta_for_commit(rbgit, remote_bin_name)

    # if we have pushed and we want to print the commit do it last
    if args.command == "push" and not args.no_print_commit:
        print(commit_info.bin_sha_commit)

    return 0


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
