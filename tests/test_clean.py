from typing import Set
from git_recycle_bin.rbgit import RbGit, create_rbgit
from git_recycle_bin import push as push_cmd
from git_recycle_bin import (
    remote_flush_meta_for_commit,
    remote_delete_expired_branches
)
from git_recycle_bin.arg_parser import parse_args
from managers import git_user_info, change_dir

def contains_metas(rbgit: RbGit, remote: str, commit_shas: Set[str]) -> bool:
    metas = rbgit.meta_for_commit_refs(remote)
    assert commit_shas == { meta[-40:] for meta in metas }
    # return True to allow us to do assert contains_metas which reads better than
    # just contains_metas
    return True

def test_flush_meta_for_commit(temp_git_setup):
    local, _, artifact_remote, artifacts = temp_git_setup
    artifact_path, artifact_name = artifacts[0]

    _args = ["push", f"{artifact_remote}",
             "--path", f"{artifact_path}",
             "--name", artifact_name,
             ]
    _dead = _args + ["--expire", "2 hours ago"]
    dead = parse_args(_dead)
    longlived = parse_args(_args + ["--expire", "in 30 days"])

    rbgit=create_rbgit(local, dead.path, clean=True)
    rb_remote="rbgit"

    def push(args):
        return push_cmd(rbgit, rb_remote, artifact_name, args).bin_sha_commit

    with change_dir(local), git_user_info():
        bin_commit = push(dead)
        assert contains_metas(rbgit, rb_remote, {bin_commit})

        # without --remove-expired the refs should still exist
        bin_commit2 = push(dead)
        remote_flush_meta_for_commit(rbgit, rb_remote)
        assert contains_metas(rbgit, rb_remote, {bin_commit, bin_commit2})

        # with --remove-expired the refs should be removed
        push(dead)
        remote_delete_expired_branches(rbgit, rb_remote)
        remote_flush_meta_for_commit(rbgit, rb_remote)
        assert contains_metas(rbgit, rb_remote, set())

        # with only --remove-expired the refs should not be removed
        bin_commit = push(dead)
        remote_delete_expired_branches(rbgit, rb_remote)
        assert contains_metas(rbgit, rb_remote, {bin_commit})

        # with --flush-meta the new artifact should not be removed but the old one should
        bin_commit = push(dead)
        remote_flush_meta_for_commit(rbgit, rb_remote)
        assert contains_metas(rbgit, rb_remote, {bin_commit})

        # only the longlived artifact should be present
        bin_commit = push(longlived)
        remote_delete_expired_branches(rbgit, rb_remote)
        remote_flush_meta_for_commit(rbgit, rb_remote)
        assert contains_metas(rbgit, rb_remote, {bin_commit})
