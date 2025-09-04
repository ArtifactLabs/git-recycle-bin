import re

from git_recycle_bin.printer import printer
from git_recycle_bin.commands.list import remote_artifacts_unfiltered, meta_data
from git_recycle_bin.rbgit import create_rbgit, RbGit
from git_recycle_bin.utils.extern import exec


def download(rbgit: RbGit,
             remote_bin_name: str,
             artifacts: list[str],
             force: bool = False,
             rm_tmp: bool = False,
             ):
    artifact_metas = remote_artifacts_unfiltered(rbgit, remote_bin_name, all_shas=True)
    metas = refspec_map(artifact_metas)
    for artifact in artifacts:
        meta_sha, artifact_sha  = metas.get(artifact.strip())
        meta = meta_data(rbgit, remote_bin_name, meta_sha)
        rel_path = meta['src-git-relpath']
        url = rbgit.cmd('remote', 'get-url', remote_bin_name).strip()
        # TODO: not ideal to create and remove all the time.
        with create_rbgit(artifact_path=rel_path, clean=rm_tmp) as rbgit:
            rbgit.add_remote_idempotent(name=remote_bin_name, url=url)
            rbgit.cmd("fetch", remote_bin_name, artifact_sha)
            if force:
                rbgit.cmd("checkout", "-f", artifact_sha)
            else:
                # dont fail with python stack trace if file already exists
                try:
                    rbgit.cmd("checkout", artifact_sha)
                except RuntimeError as e:
                    printer.error(e)
                    printer.error("Use --force to overwrite local files.")
                    return 1

def refspec_map(artifacts):
    """
    Given an iterable of tuples (meta_sha, refspec), convert into a map of
    {
        "<src_sha>/<artifact_sha>": (meta_sha_blob, artifact_sha),
        "artifact_sha": (meta_sha_blob, artifact_sha),
    }
    """
    map = {}
    for artifact in artifacts:
        meta_sha, artifact_sha = artifact
        artifact_sha_commit = artifact_sha.strip()
        _src_sha, artifact_sha = artifact_sha.split('/')
        map[artifact_sha_commit] = (meta_sha, artifact_sha)
        map[artifact_sha] = (meta_sha, artifact_sha)
    return map
