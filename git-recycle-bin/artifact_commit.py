import os
import sys
from dataclasses import dataclass

from .utils.string import sanitize_branch_name
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
    src_branch_upstream: str
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

    @classmethod
    def from_dict(cls, d: dict[str, str]) -> "ArtifactCommitInfo":
        return cls(**d)

def create_artifact_commit(rbgit, artifact_name: str, binpath: str, expire_branch: str, add_ignored: bool, src_remote_name: str) -> ArtifactCommitInfo:
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

    # Committer time changes every time the commit-SHA changes, for example {rebasing, amending, ...}.
    # Committer time can be set with $GIT_COMMITTER_DATE or `git rebase --committer-date-is-author-date`.
    # Committer time is monotonically increasing but sampled locally, so graph could still be non-monotonic if a collaborator has a very wrong clock.
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
    if changes:
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

    return ArtifactCommitInfo.from_dict(d)
