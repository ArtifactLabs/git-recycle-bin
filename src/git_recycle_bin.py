#!/usr/bin/env python3
import os
import sys
import json
import shutil
import subprocess
from collections import OrderedDict

from rbgit import RbGit
from printer import printer
from util_string import *
from util_file import *
from util_date import *
from util_sysinfo import *
from util import *
from arg_parser import *
from commit_msg import *

# commands
from list import list_command
from download import download_command


def create_artifact_commit(rbgit, artifact_name: str, binpath: str, expire_branch: str, add_ignored: bool, src_remote_name: str) -> dict[str, str]:
    """ Create Artifact: A binary commit, with builtin traceability and expiry """
    if not os.path.exists(binpath):
        raise RuntimeError(f"Artifact '{binpath}' does not exist!")

    artifact_name_sane = sanitize_branch_name(artifact_name)
    if artifact_name != artifact_name_sane:
        printer.always(f"Warning: Sanitized '{artifact_name}' to '{artifact_name_sane}'.", file=sys.stderr)
        artifact_name = artifact_name_sane

    d = {}
    d['artifact_name'] = artifact_name
    d['binpath'] = binpath
    d['bin_branch_expire'] = date_fuzzy2expiryformat(expire_branch)  # also used by --push-note

    d['artifact_mime'] = classify_path(binpath)

    d['src_remote_name']  = src_remote_name
    d['src_sha']          = exec(["git", "rev-parse", "HEAD"])  # Sample the full SHA once
    d['src_sha_short']    = d['src_sha'][:10]  # Do not sample SHA again, as that would be a race
    d['src_sha_msg']      = exec(["git", "show", "--no-patch", "--format=%B", d['src_sha']])
    d['src_sha_title']    = d['src_sha_msg'].split('\n')[0]  # title is first line of commit-msg

    # Author time is when the commit was first committed.
    # Author time is easily set with `git commit --date`.
    d['src_time_author']  = exec(["git", "show", "-s", "--format=%ad", f"--date=format:{DATE_FMT_GIT}", d['src_sha']])

    # Commiter time changes every time the commit-SHA changes, for example {rebasing, amending, ...}.
    # Commiter time can be set with $GIT_COMMITTER_DATE or `git rebase --committer-date-is-author-date`.
    # Commiter time is monotonically increasing but sampled locally, so graph could still be non-monotonic if a collaborator has a very wrong clock.
    d['src_time_commit']  = exec(["git", "show", "-s", "--format=%cd", f"--date=format:{DATE_FMT_GIT}", d['src_sha']])

    d['src_branch']       = exec(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    d['src_repo_url']     = exec(["git", "config", "--get", f"remote.{d['src_remote_name']}.url"])
    d['src_repo']         = os.path.basename(d['src_repo_url'])
    d['src_tree_root']    = exec(["git", "rev-parse", "--show-toplevel"])
    d['src_status']       = exec(["git", "status", "--porcelain=1", "--untracked-files=no"])

    if d['src_branch'] == "HEAD":
        # We are in detached HEAD and thus can't determine the upstream tracking branch
        d['src_branch_upstream'] = ""
        d['src_commits_ahead']   = ""
        d['src_commits_behind']  = ""
    else:
        d['src_branch_upstream'] = exec(["git", "for-each-ref", "--format=%(upstream:short)", f"refs/heads/{d['src_branch']}"])
        if d['src_branch_upstream'] == "":
            d['src_commits_ahead']  = ""
            d['src_commits_behind'] = ""
        else:
            d['src_commits_ahead']   = exec(["git", "rev-list", "--count", f"{d['src_branch_upstream']}..{d['src_branch']}"])
            d['src_commits_behind']  = exec(["git", "rev-list", "--count", f"{d['src_branch']}..{d['src_branch_upstream']}"])

    d['nca_dir'] = nca_path(d['src_tree_root'], binpath)                        # Longest shared path between gitroot and artifact. Is either {gitroot, something outside gitroot}
    d['artifact_relpath_nca'] = rel_dir(pto=binpath, pfrom=d['nca_dir'])        # Relative path to artifact from nca_dir. Artifact is always within nca_dir
    d['artifact_relpath_src'] = rel_dir(pto=binpath, pfrom=d['src_tree_root'])  # Relative path to artifact from src-git-root. Artifact might be outside of source git.

    # 'expire' branch ref will be deleted with '--rm-expired' argument.
    # E.g.: 'artifact/expire/2024-07-20/14.17+0200/project.git@182db9b0696a5e9f97a5800e4866917c5465b2c6/{obj/doc/html}'
    d['bin_branch_name'] = f"artifact/expire/{d['bin_branch_expire']}/{d['src_repo']}@{d['src_sha']}/{{{d['artifact_relpath_nca']}}}"
    # 'latest' tag ref will not expire but is overwritten to point to newer SHA.
    # E.g.: 'artifact/latest/project.git@main/{obj/doc/html}'
    d['bin_tag_name']    = f"artifact/latest/{d['src_repo']}@{d['src_branch']}/{{{d['artifact_relpath_nca']}}}" if d['src_branch'] != "HEAD" else None

    d['bin_commit_msg'] = emit_commit_msg(d)

    rbgit.checkout_orphan_idempotent(d['bin_branch_name'])

    printer.high_level(f"Adding '{binpath}' as '{d['artifact_relpath_nca']}' ...", file=sys.stderr)
    changes = rbgit.add(binpath, force=add_ignored)
    if changes == True:
        # Set {author,committer}-dates: Make our new commit reproducible by copying from the source; do not sample the current time.
        # Sampling the current time would lead to new commit SHA every time, thus not idempotent.
        os.environ['GIT_AUTHOR_DATE'] = d['src_time_author']
        os.environ['GIT_COMMITTER_DATE'] = d['src_time_commit']
        rbgit.cmd("commit", "--file", "-", "--quiet", "--no-status", "--untracked-files=no", input=d['bin_commit_msg'])
        d['bin_sha_commit'] = rbgit.cmd("rev-parse", "HEAD").strip()
    else:
        d['bin_sha_commit'] = rbgit.cmd("rev-parse", "HEAD").strip()  # We already checked-out idempotently
        printer.high_level(f"No changes for the next commit. Already at {d['bin_sha_commit']}", file=sys.stderr)
    d['bin_time_commit'] = rbgit.cmd("show", "-s", "--format=%cd", f"--date=format:{DATE_FMT_EXPIRE}", d['bin_sha_commit']).strip()

    printer.high_level(f"Artifact commit: {d['bin_sha_commit']}", file=sys.stderr)
    printer.high_level(f"Artifact branch: {d['bin_branch_name']}", file=sys.stderr)
    # Now we have a commit, we can set a tag pointing to it
    if d['bin_tag_name']:
        rbgit.set_tag(tag_name=d['bin_tag_name'], tag_val=d['bin_sha_commit'])
        printer.high_level(f"Artifact tag: {d['bin_tag_name']}", file=sys.stderr)

    # Fetching a commit implies fetching its whole tree too, which may be big!
    # We want light-weight access to the meta-data stored in the commit's message, so we
    # copy meta-data to a new object which can be fetched standalone - without downloading the whole tree.
    # NOTE: This meta-data could be augmented with convenient/unstable information - this would not compromise the commit-SHA's stability.
    d['bin_sha_only_metadata'] = rbgit.cmd("hash-object", "--stdin", "-w", input=d['bin_commit_msg']).strip()
    # Create new ref for the artifact-commit, pointing to [Meta data]-only.
    d['bin_ref_only_metadata'] = f"refs/artifact/meta-for-commit/{d['src_sha']}/{d['bin_sha_commit']}"
    rbgit.cmd("update-ref", d['bin_ref_only_metadata'], d['bin_sha_only_metadata'])

    printer.high_level(f"Artifact [meta data]-only ref: {d['bin_ref_only_metadata']}", file=sys.stderr)
    printer.high_level(f"Artifact [meta data]-only obj: {d['bin_sha_only_metadata']}", file=sys.stderr)

    return d

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

    # Artifact may reside within or outside source git's root. E.g. under $GITROOT/obj/ or $GITROOT/../obj/
    nca_dir = nca_path(src_tree_root, path)

    # Place recyclebin-git's root at a stable location, where both source git and artifact can be seen.
    # Placing artifacts here allows for potential merging of artifact commits as paths are fully qualified.
    rbgit_dir=f"{nca_dir}/.rbgit"

    if args.rm_tmp and os.path.exists(rbgit_dir):
        printer.high_level(f"Deleting local bin repo, {rbgit_dir}, to start from clean-slate.", file=sys.stderr)
        shutil.rmtree(rbgit_dir)

    rbgit = RbGit(printer, rbgit_dir=rbgit_dir, rbgit_work_tree=nca_dir)
    if args.user_name:
        rbgit.cmd("config", "--local", "user.name", args.user_name)
    if args.user_email:
        rbgit.cmd("config", "--local", "user.email", args.user_email)

    remote_bin_name = "recyclebin"

    commands = {
        "push": lambda: push_command(args, rbgit, remote_bin_name, path),
        "clean": lambda: clean_command(rbgit, remote_bin_name),
        "list": lambda: list_command(args, rbgit, remote_bin_name),
        "download": lambda: download_command(args, rbgit, remote_bin_name),
    }

    if args.remote:
        rbgit.add_remote_idempotent(name=remote_bin_name, url=args.remote)

    run = commands[args.command]
    rbgit.add_remote_idempotent(name=remote_bin_name, url=args.remote)
    exitcode = run()

    if args.rm_tmp and os.path.exists(rbgit_dir):
        printer.high_level(f"Deleting local bin repo, {rbgit_dir}, to free-up disk-space.", file=sys.stderr)
        shutil.rmtree(rbgit_dir, ignore_errors=True)

    return exitcode


def clean_command(rbgit, remote_bin_name):
    remote_delete_expired_branches(rbgit, remote_bin_name)
    remote_flush_meta_for_commit(rbgit, remote_bin_name)

def push_command(args, rbgit, remote_bin_name, path):
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
        remote_meta = rbgit.fetch_cat_pretty(remote_bin_name, f"refs/artifact/meta-for-commit/{remote_bin_sha_commit}")

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


def remote_delete_expired_branches(rbgit, remote_bin_name):
    """
        Delete refs of expired branches on remote. Artifacts may still be kept alive by other refs, e.g. by latest-tag.
        Reclaiming disk-space on remote, requires running `git gc` or its equivalent -- _Housekeeping_ on GitLab.
        See https://docs.gitlab.com/ee/administration/housekeeping.html
    """
    branch_prefix = "artifact/expire/"
    lines = rbgit.cmd("ls-remote", "--heads", remote_bin_name, f"refs/heads/{branch_prefix}*").splitlines()

    now = datetime.datetime.now(tzlocal())

    for line in lines:
        _, branch = line.split(maxsplit=1)

        # Timezone may be absent, but we insist on date and time
        date_time_tz = parse_expire_date(branch)
        if date_time_tz['date'] == None: continue
        if date_time_tz['time'] == None: continue
        if date_time_tz['tzoffset'] == None:
            date_time_tz['tzoffset'] = datetime.datetime.strftime(now, "%z")

        compliant_expire_string = f"{date_time_tz['date']}/{date_time_tz['time']}{date_time_tz['tzoffset']}"
        expiry = date_parse_formatted(date_string=compliant_expire_string, date_format=DATE_FMT_EXPIRE)
        delta_formatted = format_timespan(dt_from=now, dt_to=expiry)

        if expiry.timestamp() > now.timestamp():
            printer.detail("Active", delta_formatted, branch)
            continue

        printer.high_level("Expired", delta_formatted, branch)
        rbgit.cmd("push", remote_bin_name, "--delete", branch)

def remote_flush_meta_for_commit(rbgit, remote_bin_name):
    """
        Every artifact has traceability metadata in the commit message. However we can not fetch the commit
        message without fetching the whole artifact too. Hence we have meta-for-commit refs, which point to
        blobs of only metadata. This way we can obtain metadata without downloading potentially big artifacts.

        The artifacts are kept clean either by their built-in expiry-dates or by whoever creating the artifact
        maintaining it, but there is no hook to clean the corresponding meta-for-commit ref.

        This subroutine will scan all existing meta-for-commit references and determine if an artifact is still
        available. If not, the metadata commit will be removed.
    """
    meta_set = rbgit.cmd("ls-remote", "--refs", remote_bin_name, "refs/artifact/meta-for-commit/*").splitlines()
    heads    = rbgit.cmd("ls-remote", "--heads", remote_bin_name, "refs/heads/*").splitlines()
    tags     = rbgit.cmd("ls-remote", "--tags", remote_bin_name, "refs/tags/*").splitlines()

    sha_len = 40
    commits = { l[-sha_len:] for l in meta_set }
    commits.difference_update((l[:sha_len] for l in heads))
    commits.difference_update((l[:sha_len] for l in tags))
    branches = ["refs/artifact/meta-for-commit/" + c for c in commits]
    if branches:
        rbgit.cmd("push", remote_bin_name, "--delete", *branches)


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


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
