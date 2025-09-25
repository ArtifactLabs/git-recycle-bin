import sys
import subprocess
import json
from collections import OrderedDict

from git_recycle_bin.printer import printer
from git_recycle_bin.artifact_commit import create_artifact_commit
from git_recycle_bin.commit_msg import parse_commit_msg
from git_recycle_bin.utils.extern import exec, exec_nostderr
from git_recycle_bin.utils.date import (
    date_formatted2unix,
    DATE_FMT_GIT,
    DATE_FMT_EXPIRE,
)
from git_recycle_bin.utils.sysinfo import get_user, get_hostname
from git_recycle_bin.utils.string import sanitize_branch_name, sanitize_slashes
from .clean import remote_delete_expired_branches, remote_flush_meta_for_commit


def push(args, rbgit, remote_bin_name, path) -> dict[str, str]:
    printer.high_level(f"Making local commit of artifact {path} in artifact-repo at {rbgit.rbgit_dir}", file=sys.stderr)
    d = create_artifact_commit(rbgit, args.name, path, args.expire, args.add_ignored, args.src_remote_name)
    printer.detail(rbgit.cmd("branch", "-vv"))
    printer.detail(rbgit.cmd("log", "-1", d['bin_branch_name']))

    rbgit.add_remote_idempotent(name=remote_bin_name, url=args.remote)
    push_branch(args, d, rbgit, remote_bin_name)
    if args.push_tag:
        push_tag(args, d, rbgit, remote_bin_name)
    if args.push_note:
        note_append_push(args, d)
    if args.rm_expired:
        remote_delete_expired_branches(rbgit, remote_bin_name)
    if args.flush_meta:
        remote_flush_meta_for_commit(rbgit, remote_bin_name)
    return d


def push_branch(args, d, rbgit, remote_bin_name):
    """
        Push branch to binary remote.

        Push branch first, then meta-data (we don't want meta-data to be pushed if branch push fails).
        Branch might exist already upstream.
        Pushing may take long, so always show stdout and stderr without capture.
    """
    printer.high_level(f"Pushing to remote artifact-repo: Artifact data on branch {d['bin_branch_name']}", file=sys.stderr)
    if args.force_branch:
        rbgit.cmd("push", "--force", remote_bin_name, d['bin_branch_name'], capture_output=False)
    else:
        if rbgit.remote_already_has_ref(remote_bin_name, d['bin_branch_name']):
            printer.always(f"Remote artifact-repo already has {d['bin_branch_name']} -- and we won't force push.")
        else:
            rbgit.cmd("push",        remote_bin_name, d['bin_branch_name'], capture_output=False)

    printer.high_level(f"Pushing to remote artifact-repo: Artifact meta-data {d['bin_ref_only_metadata']}", file=sys.stderr)
    if args.force_branch:
        rbgit.cmd("push", "--force", remote_bin_name, d['bin_ref_only_metadata'], capture_output=False)
    else:
        if rbgit.remote_already_has_ref(remote_bin_name, d['bin_ref_only_metadata']):
            printer.always(f"Remote artifact-repo already has {d['bin_ref_only_metadata']} -- and we won't force push.")
        else:
            rbgit.cmd("push",        remote_bin_name, d['bin_ref_only_metadata'], capture_output=False)


def push_tag(args, d, rbgit, remote_bin_name):
    """
        Push tag to binary remote.
    """
    if not d['bin_tag_name']:
        printer.error("Error: You are in Detached HEAD, so you can't push 'latest' tag to bin-remote with name of your source branch.", file=sys.stderr)
        return

    if d['src_commits_ahead'] != "" and int(d['src_commits_ahead']) >= 1:
        printer.error(f"Error: Your local branch is ahead by {d['src_commits_ahead']} commits of its upstream authoritative branch. Won't push tag to bin-remote.", file=sys.stderr)
        return

    remote_bin_sha_commit = rbgit.fetch_current_tag_value(remote_bin_name, d['bin_tag_name'])
    if remote_bin_sha_commit:
        printer.high_level(f"Bin-remote already has a tag named {d['bin_tag_name']} pointing to {remote_bin_sha_commit[:8]}.", file=sys.stderr)
        remote_meta = rbgit.fetch_cat_pretty(remote_bin_name, d['bin_ref_only_metadata'])

        commit_time_theirs = parse_commit_msg(remote_meta)['src-git-commit-time-commit']
        commit_time_ours = d['src_time_commit']
        commit_time_theirs_u = date_formatted2unix(commit_time_theirs, DATE_FMT_GIT)
        commit_time_ours_u = date_formatted2unix(commit_time_ours, DATE_FMT_GIT)
        printer.high_level(f"Our artifact {d['bin_sha_commit'][:8]} has src committer-time:   {commit_time_ours} ({commit_time_theirs_u})", file=sys.stderr)
        printer.high_level(f"Their artifact {remote_bin_sha_commit[:8]} has src committer-time: {commit_time_theirs} ({commit_time_ours_u})", file=sys.stderr)

        if commit_time_ours_u > commit_time_theirs_u:
            printer.high_level(f"Our artifact is newer than theirs. Updating...", file=sys.stderr)
            rbgit.cmd("push", "--force", remote_bin_name, d['bin_tag_name'])  # Push with force is necessary to update existing tag
        else:
            if not args.force_tag:
                printer.high_level(f"Our artifact is not newer than theirs. Leaving remote tag as-is.", file=sys.stderr)
            else:
                printer.high_level(f"Our artifact is not newer than theirs. Forcing update to remote tag.", file=sys.stderr)
                rbgit.cmd("push", "--force", remote_bin_name, d['bin_tag_name'])  # Push with force is necessary to update existing tag

    else:
        printer.high_level(f"Bin-remote does not have a tag named {d['bin_tag_name']} -- we'll publish it.", file=sys.stderr)
        rbgit.cmd("push", remote_bin_name, d['bin_tag_name'])  # Create new tag; push with force is not necessary


def note_append_push(args, d):
    """
        Add a git-note to local src repository, and push it to src remote.
        The note contains a single line of JSON pointing to the newly pushed artifact.
        Such notes makes it discoverable, by simple git-log, where and what artifacts exist.
    """

    # Ensure we don't get additional directory levels in note refspec
    bin_remote_sane = sanitize_slashes(args.remote)
    name_sane = sanitize_slashes(args.name)

    # Workspace may have modified tracked files - if so, SHA can't be trusted
    work_state = "clean" if d['src_status'] == "" else "dirty"

    # This note refspec has some design properties:
    # - The "notes/artifact/"-prefix permits scoped {ignore,only} fetch of artifact notes.
    # - The "notes/artifact/{bin_remote_sane}"-prefix permits fetch of only artifacts published on certain binary remotes,
    #   this reduces git-log spam if some remotes only hold documentation and others hold built images.
    # - The "notes/artifact/{bin_remote_sane}/{name_sane}"-prefix allows scoping to certain artifacts.
    # - The final bin_sha_commit level detaches us from retention policy; if all is expired we can delete the note-ref.
    git_notes_ref = sanitize_branch_name(f"refs/notes/artifact/{bin_remote_sane}/{name_sane}/{d['bin_sha_commit']}-{work_state}")

    # git-notes assumes refs/notes/commits by default, which we don't want to interfere with,
    # so we tell git to manipulate our refspec, by the GIT_NOTES_REF environment variable.
    gitenv = {"GIT_NOTES_REF": git_notes_ref}
    # Many CI systems do not have author configured, and we want to be non-destructive, so use env
    if args.user_name:
        gitenv['GIT_AUTHOR_NAME'] = args.user_name
        gitenv['GIT_COMMITTER_NAME'] = args.user_name
    if args.user_email:
        gitenv['GIT_AUTHOR_EMAIL'] = args.user_email
        gitenv['GIT_COMMITTER_EMAIL'] = args.user_email

    # Ensure dumped json is specifically ordered - humans won't look till end of line.
    # OK to duplicate data from the git note refspec, as either may change.
    linedata = OrderedDict([
        # Traceability {what, when, who, from where} published
        ("date",   d['bin_time_commit']),  # sort chronologically
        ("name",   args.name),             # sort similar/rebuilt artifacts together
        ("user",   get_user()),
        ("host",   get_hostname()),

        # Retention policy
        ("expire", d['bin_branch_expire']),

        # Fully qualified 'pointer' to artifact on binary remote
        ("remote", args.remote),
        ("commit", d['bin_sha_commit']),  # we only need the artifact commit SHA, not any (expired) branches that point to it
    ])
    msg = json.dumps(linedata, separators=(', ', ':'))

    def notes_fetch_resolve():
        """ Fetch notes in source repo and bring our local copy up to date """
        try:
            exec_nostderr(["git", "fetch", args.src_remote_name, git_notes_ref], env=gitenv)
            exec(["git", "notes", "merge", "--strategy", "cat_sort_uniq", "-v", "FETCH_HEAD"], env=gitenv)
        except subprocess.CalledProcessError:
            pass  # fetch above fails with no prior refs to fetch, that's OK

    notes_fetch_resolve()
    exec(["git", "notes", "append", "-m", msg, "HEAD"], env=gitenv)

    tries = 10
    while tries > 0:
        try:
            tries -= 1
            exec(["git", "push", args.src_remote_name, git_notes_ref], env=gitenv)
            break
        except RuntimeError:
            notes_fetch_resolve()
