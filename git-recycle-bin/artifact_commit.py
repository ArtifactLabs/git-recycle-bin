import os
import sys
from dataclasses import dataclass, field

from .utils.string import sanitize_branch_name, trim_all_lines
from .utils.date import (
    date_fuzzy2expiryformat,
    DATE_FMT_GIT,
    DATE_FMT_EXPIRE,
)
from .utils.file import (
    classify_path,
    rel_dir,
    nca_path,
)
from .utils.extern import exec
from .printer import printer
from .commit_msg import emit_commit_msg

@dataclass
class ArtifactCommitInfo:
    """ Class storing information about an artifact commit. """
    artifact_name: str
    binpath: str
    bin_branch_expire: str
    artifact_mime: str
    src_remote_name: str
    src_sha: str
    src_sha_short: str
    src_sha_msg: str
    src_sha_title: str
    src_time_author: str
    src_time_commit: str
    src_branch: str
    src_repo_url: str
    src_repo: str
    src_tree_root: str
    src_status: str
    src_commits_ahead: str
    src_commits_behind: str
    nca_dir: str
    artifact_relpath_nca: str
    artifact_relpath_src: str
    bin_branch_name: str
    bin_tag_name: str | None
    bin_commit_msg: str
    bin_sha_commit: str
    bin_time_commit: str
    bin_sha_only_metadata: str
    bin_ref_only_metadata: str
    custom_trailers: dict[str, str] = field(default_factory=dict)


def create_artifact_commit(rbgit,
                           artifact_name: str,
                           binpath: str,
                           expire_branch: str = "In 30 days",
                           add_ignored: bool = False,
                           src_remote_name: str = "origin",
                           cwd: str | None = None,
                           custom_trailers: dict[str, str] = {}
                           ) -> ArtifactCommitInfo:
    """ Create Artifact: A binary commit, with builtin traceability and expiry """
    if not os.path.exists(binpath):
        raise RuntimeError(f"Artifact '{binpath}' does not exist!")

    artifact_name_sane = sanitize_branch_name(artifact_name)
    if artifact_name != artifact_name_sane:
        printer.always(f"Warning: Sanitized '{artifact_name}' to '{artifact_name_sane}'.", file=sys.stderr)
        artifact_name = artifact_name_sane

    bin_branch_expire = date_fuzzy2expiryformat(expire_branch)

    artifact_mime = classify_path(binpath)
    src_sha = exec(["git", "rev-parse", "HEAD"], cwd=cwd)  # Sample the full SHA once
    src_sha_msg = exec(["git", "show", "--no-patch", "--format=%B", src_sha], cwd=cwd)
    src_sha_title = src_sha_msg.split('\n')[0]  # title is first line of commit-msg

    src_repo_url = exec(["git", "config", "--get", f"remote.{src_remote_name}.url"])
    src_repo = os.path.basename(src_repo_url)

    # Source of artifact relative to source and NCA dir
    src_tree_root = exec(["git", "rev-parse", "--show-toplevel"], cwd=cwd)
    nca_dir = nca_path(src_tree_root, binpath)                        # Longest shared path between gitroot and artifact. Is either {gitroot, something outside gitroot}
    artifact_relpath_nca = rel_dir(pto=binpath, pfrom=nca_dir)        # Artifact is always within nca_dir
    artifact_relpath_src = rel_dir(pto=binpath, pfrom=src_tree_root)  # Relative path to artifact from src-git-root. Artifact might be outside of source git.

    src_branch, src_status, src_ahead, src_behind = src_branch_status(cwd)

    src_time_author, src_time_commit = src_time_info(src_sha, cwd)

    # Commit Message
    commmit_info = {
        'artifact_name': artifact_name,
        'artifact_mime': artifact_mime,
        'artifact_relpath_nca': artifact_relpath_nca,
        'artifact_relpath_src': artifact_relpath_src,
        'src_sha_title': src_sha_title,
        'src_sha': src_sha,
        'src_sha_short': src_sha[:8],
        'src_sha_msg': src_sha_msg,
        'src_time_author': src_time_author,
        'src_time_commit': src_time_commit,
        'src_branch': src_branch,
        'src_repo': src_repo,
        'src_repo_url': src_repo_url,
        'src_commits_ahead': src_ahead,
        'src_commits_behind': src_behind,
        'src_status': src_status,
        'custom_trailers': custom_trailers,
    }

    bin_commit_msg = emit_commit_msg(commmit_info)  # Validate commit-msg generation

    # 'expire' branch ref will be deleted with '--rm-expired' argument.
    # E.g.: 'artifact/expire/2024-07-20/14.17+0200/project.git@182db9b0696a5e9f97a5800e4866917c5465b2c6/{obj/doc/html}'
    bin_branch_name = f"artifact/expire/{bin_branch_expire}/{src_repo}@{src_sha}/{{{artifact_relpath_nca}}}"
    # 'latest' tag ref will not expire but is overwritten to point to newer SHA.
    # E.g.: 'artifact/latest/project.git@main/{obj/doc/html}'
    bin_tag_name = f"artifact/latest/{src_repo}@{src_branch}/{{{artifact_relpath_nca}}}" if src_branch != "HEAD" else None

    rbgit.checkout_orphan_idempotent(bin_branch_name)

    printer.high_level(f"Adding '{binpath}' as '{artifact_relpath_nca}' ...", file=sys.stderr)
    changes = rbgit.add(binpath, force=add_ignored)
    if changes:
        # Set {author,committer}-dates: Make our new commit reproducible by copying from the source; do not sample the current time.
        # Sampling the current time would lead to new commit SHA every time, thus not idempotent.
        os.environ['GIT_AUTHOR_DATE'] = src_time_author
        os.environ['GIT_COMMITTER_DATE'] = src_time_commit
        rbgit.cmd("commit", "--file", "-", "--quiet", "--no-status", "--untracked-files=no", input=bin_commit_msg)
        bin_sha_commit = rbgit.cmd("rev-parse", "HEAD").strip()
    else:
        bin_sha_commit = rbgit.cmd("rev-parse", "HEAD").strip()  # We already checked-out idempotently
        printer.high_level(f"No changes for the next commit. Already at {bin_sha_commit}", file=sys.stderr)
    bin_time_commit = rbgit.cmd("show", "-s", "--format=%cd", f"--date=format:{DATE_FMT_EXPIRE}", bin_sha_commit).strip()

    printer.high_level(f"Artifact commit: {bin_sha_commit}", file=sys.stderr)
    printer.high_level(f"Artifact branch: {bin_branch_name}", file=sys.stderr)
    # Now we have a commit, we can set a tag pointing to it
    if bin_tag_name:
        rbgit.set_tag(tag_name=bin_tag_name, tag_val=bin_sha_commit)
        printer.high_level(f"Artifact tag: {bin_tag_name}", file=sys.stderr)

    # Fetching a commit implies fetching its whole tree too, which may be big!
    # We want light-weight access to the meta-data stored in the commit's message, so we
    # copy meta-data to a new object which can be fetched standalone - without downloading the whole tree.
    # NOTE: This meta-data could be augmented with convenient/unstable information - this would not compromise the commit-SHA's stability.
    bin_sha_only_metadata = rbgit.cmd("hash-object", "--stdin", "-w", input=bin_commit_msg).strip() # TODO: not used elsewhere
    # Create new ref for the artifact-commit, pointing to [Meta data]-only.
    bin_ref_only_metadata = f"refs/artifact/meta-for-commit/{src_sha}/{bin_sha_commit}"
    rbgit.cmd("update-ref", bin_ref_only_metadata, bin_sha_only_metadata)

    printer.high_level(f"Artifact [meta data]-only ref: {bin_ref_only_metadata}", file=sys.stderr)
    printer.high_level(f"Artifact [meta data]-only obj: {bin_sha_only_metadata}", file=sys.stderr)

    return ArtifactCommitInfo(
        artifact_name=artifact_name,
        binpath=binpath,
        bin_branch_expire=bin_branch_expire,
        artifact_mime=artifact_mime,
        src_remote_name=src_remote_name,
        src_sha=src_sha,
        src_sha_short=src_sha[:8],
        src_sha_msg=src_sha_msg,
        src_sha_title=src_sha_title,
        src_time_author=src_time_author,
        src_time_commit=src_time_commit,
        src_branch=src_branch,
        src_repo_url=src_repo_url,
        src_repo=src_repo,
        src_tree_root=src_tree_root,
        src_status=src_status,
        src_commits_ahead=src_ahead,
        src_commits_behind=src_behind,
        nca_dir=nca_dir,
        artifact_relpath_nca=artifact_relpath_nca,
        artifact_relpath_src=artifact_relpath_src,
        bin_branch_name=bin_branch_name,
        bin_tag_name=bin_tag_name,
        bin_commit_msg=bin_commit_msg,
        bin_sha_commit=bin_sha_commit,
        bin_time_commit=bin_time_commit,
        bin_sha_only_metadata=bin_sha_only_metadata,
        bin_ref_only_metadata=bin_ref_only_metadata,
        custom_trailers=custom_trailers
    )

def src_branch_status(cwd):
    src_status = exec(["git", "status", "--porcelain=1", "--untracked-files=no"], cwd=cwd)
    if src_status == "":
        src_status = "clean"
    else:
        src_status = trim_all_lines(src_status)
    src_branch = exec(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
    if src_branch == "HEAD":
        # We are in detached HEAD and thus can't determine the upstream tracking branch
        src_commits_ahead   = ""
        src_commits_behind  = ""
    else:
        src_branch_upstream = exec(["git", "for-each-ref", "--format=%(upstream:short)", f"refs/heads/{src_branch}"], cwd=cwd)
        if src_branch_upstream == "":
            src_commits_ahead = ""
            src_commits_behind = ""
        else:
            src_commits_ahead = exec(["git", "rev-list", "--count", f"{src_branch_upstream}..{src_branch}"], cwd=cwd)
            src_commits_behind = exec(["git", "rev-list", "--count", f"{src_branch}..{src_branch_upstream}"], cwd=cwd)
    src_commits_ahead = src_commits_ahead if src_commits_ahead != "" else "?"
    src_commits_behind = src_commits_behind if src_commits_behind != "" else "?"
    return src_branch, src_status, src_commits_ahead, src_commits_behind

def src_time_info(src_sha, cwd):
    # Author time is when the commit was first committed.
    # Author time is easily set with `git commit --date`.
    src_time_author = exec(["git", "show", "-s", "--format=%ad", f"--date=format:{DATE_FMT_GIT}", src_sha], cwd=cwd)

    # Committer time changes every time the commit-SHA changes, for example {rebasing, amending, ...}.
    # Committer time can be set with $GIT_COMMITTER_DATE or `git rebase --committer-date-is-author-date`.
    # Committer time is monotonically increasing but sampled locally, so graph could still be non-monotonic if a collaborator has a very wrong clock.
    src_time_commit = exec(["git", "show", "-s", "--format=%cd", f"--date=format:{DATE_FMT_GIT}", src_sha], cwd=cwd)

    return src_time_author, src_time_commit
