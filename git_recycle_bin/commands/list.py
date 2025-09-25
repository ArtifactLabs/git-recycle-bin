from git_recycle_bin.rbgit import RbGit
from git_recycle_bin.printer import printer
from git_recycle_bin.utils.extern import exec
from git_recycle_bin.utils.string import sanitize_branch_name
from git_recycle_bin.commit_msg import parse_commit_msg
from git_recycle_bin.utils.string import sanitize_branch_name


# Queries is a type -> querystring product
Query = tuple[str, str]

# query
def remote_artifacts(rbgit: RbGit,
                     remote_bin_name: str,
                     query: Query,
                     all_shas: bool = False) -> list[str, str]:
    """
    Returns a list of all of pairs of (metadata sha, artifact sha) for which
    query is valid
    """
    query_type = query[0]
    query_str  = query[1]

    artifacts = remote_artifacts_unfiltered(rbgit, remote_bin_name)

    filters = {
        'name': filter_artifacts_by_name,
        'path': filter_artifacts_by_path,
        'none': lambda _meta_data, _query: True,
    }
    filter_func = filters[query_type]

    if query_type != "none":
        printer.debug(f"Filtering artifacts by {query_type}={query_str}")

    return filter_artifacts(rbgit, remote_bin_name, query_str, artifacts, filter_func)

def remote_artifacts_unfiltered(rbgit: RbGit,
                                remote_bin_name: str,
                                all_shas: bool = False
                                ) -> list[str, str]:
    """
    Fetch all artifacts from the remote repository.
    artifacts is a pair of the meta_data_sha and the artifact sha it references
    """
    if all_shas:
        refs = refs_path_all()
    else:
        # Fetch all artifacts based on refs/artifact/meta-for-commit/{src_sha}/* refspec.
        # This schema makes it easy to query which artifact are available for the given commit.
        # This allows us to drastically reduce the meta-data to search through, which
        # can then further be queried.
        src_sha = exec(["git", "rev-parse", "HEAD"])
        refs = refs_path(src_sha)
    lines = rbgit.cmd("ls-remote", "--refs", remote_bin_name, f"{refs}*").splitlines()
    printer.debug(f"{lines}")
    artifacts = []
    for line in lines:
        cols = line.split()
        meta_sha_blob = cols[0]
        artifact_sha_commit = cols[1].strip()[len(refs):]
        artifacts.append((meta_sha_blob, artifact_sha_commit))
    return artifacts

def refs_path_all():
    return "refs/artifact/meta-for-commit/"

def refs_path(sha):
    return f"refs/artifact/meta-for-commit/{sha}/"

def filter_artifacts(rbgit, remote_bin_name, query, artifacts, filter_func):
    return [
        artifact
        for artifact in artifacts
        if filter_func(meta_data(rbgit, remote_bin_name, artifact[0]), query)
    ]


def filter_artifacts_by_name(meta_data, query: str):
    return meta_data['artifact-name'] == sanitize_branch_name(query)


def filter_artifacts_by_path(meta_data, query: str):
    return meta_data['src-git-relpath'] == query


def meta_data(rbgit, remote_bin_name, meta_data_commit):
    data = rbgit.fetch_cat_pretty(remote_bin_name, meta_data_commit)
    return parse_commit_msg(data)
