#!/usr/bin/env python3
import sys

from .utils.extern import exec
from .printer import printer
from .arg_parser import parse_args
from .rbgit import create_rbgit

# commands
from . import (
    show_remote_artifacts,
    push,
    clean,
    download
)


def main() -> int:
    # TODO: Add --add-submodule to add src-git as a {update=none, shallow, nonrecursive} submodule in artifact-commit.

    args = parse_args()
    if args is None:
        return 1

    printer.debug("Arguments:")
    for arg in vars(args):
        printer.debug(f"  '{arg}': '{getattr(args, arg)}'")

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

    with create_rbgit(src_tree_root, path, clean=args.rm_tmp) as rbgit:
        if args.user_name:
            rbgit.cmd("config", "--local", "user.name", args.user_name)
        if args.user_email:
            rbgit.cmd("config", "--local", "user.email", args.user_email)

        if args.remote:
            rbgit.add_remote_idempotent(name=remote_bin_name, url=args.remote)


        commands = {
            "push": lambda: push(args, rbgit, remote_bin_name, path),
            "clean": lambda: clean(rbgit, remote_bin_name),
            "list": lambda: show_remote_artifacts(args, rbgit, remote_bin_name),
            "download": lambda: download(args, rbgit, remote_bin_name),
        }

        run = commands[args.command]
        exitcode = run()

    return exitcode


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
