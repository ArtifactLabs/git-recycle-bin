from git_recycle_bin.rbgit import RbGit

def cat_metas(rbgit: RbGit,
              remote_bin_name: str,
              commits: list[str]) -> None:
    for sha, content in metas_for_commits(rbgit, remote_bin_name, commits).items():
        print(f"--- {sha} ---")
        print(content)

def metas_for_commits(rbgit: RbGit,
                      remote_bin_name: str,
                      commits: list[str]) -> dict[str, str]:
    meta_datas = {}
    for commit in commits:
        content = rbgit.fetch_cat_pretty(remote_bin_name, commit)
        meta_datas[commit] = content
    return meta_datas
