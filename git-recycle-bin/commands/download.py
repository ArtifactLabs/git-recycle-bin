import re

from git_recycle_bin.printer import printer
from git_recycle_bin.commands.list import remote_artifacts, ListResult
from git_recycle_bin.rbgit import create_rbgit, RbGit
from git_recycle_bin.utils.extern import exec
from git_recycle_bin.utils.string import sanitize_slashes


def download_refs(rbgit: RbGit,
             remote_bin_name: str,
             artifacts: list[str],
             force: bool = False,
             rm_tmp: bool = True,
             ):
    """Download artifacts by their refspecs, i.e <src_sha>/<artifact_sha> or <artifact_sha>"""

    artifact_metas = remote_artifacts(rbgit, remote_bin_name, query=None, all_shas=True)
    metas = refspec_map(artifact_metas)
    artifact_data = []
    for artifact in artifacts:
        try:
            artifact_data.append(metas[artifact])
        except KeyError:
            printer.error(f"Artifact {artifact} not found in remote.")
            continue
    return download(rbgit, remote_bin_name, artifact_data, force=force, rm_tmp=rm_tmp)


def download(rbgit: RbGit,
             remote_bin_name: str,
             artifacts: list[ListResult],
             force: bool = False,
             rm_tmp: bool = True,
             ):

    rbgits = {}
    url = rbgit.get_remote_url(remote_bin_name)

    err = None
    try:
        for artifact in artifacts:
            rel_path = artifact.meta_data['src-git-relpath']
            tree_prefix = artifact.meta_data['artifact-tree-prefix']
            name = sanitize_slashes(tree_prefix)

            tmp_rbgit = create_rbgit(artifact_path=rel_path, clean=False)
            rbgits[tmp_rbgit.rbgit_work_tree] = tmp_rbgit
            tmp_rbgit.add_remote_idempotent(name=name, url=url)
            err = download_single(tmp_rbgit, name, artifact.artifact_sha, path=tree_prefix, force=force)
            if err is not None:
                break
    finally:
        if rm_tmp:
            for path, tmp_rbgit in rbgits.items():
                if path != rbgit.rbgit_work_tree:
                    tmp_rbgit.cleanup()
    return err


def download_single(rbgit: RbGit, remote_bin_name: str, artifact_sha: str,
                    path: str | None = None,
                    force: bool = False):
    rbgit.cmd("fetch", remote_bin_name, artifact_sha)
    if force:
        if path:
            rbgit.cmd("checkout", "-f", artifact_sha, path)
        else:
            rbgit.cmd("checkout", "-f", artifact_sha)
        return None
    else:
        # dont fail with python stack trace if file already exists
        try:
            if path:
                rbgit.cmd("checkout", artifact_sha, path)
            else:
                rbgit.cmd("checkout", artifact_sha)
        except RuntimeError as e:
            printer.error(e)
            printer.error("Use --force to overwrite local files.")
            return 1


def refspec_map(artifacts: list[ListResult]) -> dict[str, ListResult]:
    """
    Given an iterable of tuples (meta_sha, refspec), convert into a map of
    {
        "<src_sha>/<artifact_sha>": (meta_sha_blob, artifact_sha),
        "artifact_sha": (meta_sha_blob, artifact_sha),
    }
    """
    map = {}
    for artifact in artifacts:
        artifact_sha_commit = artifact.artifact_sha.strip()
        _src_sha, artifact_sha = artifact_sha_commit.split('/')
        res = ListResult(
            meta_sha=artifact.meta_sha,
            artifact_sha=artifact_sha,
            meta_data=artifact.meta_data
        )
        map[artifact_sha_commit] = res
        map[artifact_sha] = res
    return map
