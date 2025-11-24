import json
from dataclasses import dataclass

from git_recycle_bin.rbgit import RbGit
from git_recycle_bin.printer import printer
from git_recycle_bin.utils.extern import exec, jq
from git_recycle_bin.utils.string import sanitize_branch_name
from git_recycle_bin.utils.string import sanitize_branch_name
from git_recycle_bin.query import Query, RelPathQuery, PathQuery, NameQuery, JqQuery, AndQuery
from git_recycle_bin.commit_msg import parse_commit_msg


@dataclass
class ListResult:
    meta_sha: str
    artifact_sha: str
    meta_data: dict[str, str]


# query
def remote_artifacts(rbgit: RbGit,
                     remote_bin_name: str,
                     query: Query | None,
                     sha: str | None = None,
                     all_shas: bool = False) -> list[str, str]:
    """
    Returns a list of all of pairs of (metadata sha, artifact sha) for which
    query is valid
    """

    artifacts = remote_artifacts_unfiltered(rbgit, remote_bin_name, sha=sha, all_shas=all_shas)

    if query is None:
        return artifacts

    printer.debug(f"Filtering artifacts by {query.__class__.name} with {{ {query.query()} }}")

    return filter_artifacts(artifacts, query)

def filter_artifacts(artifacts: list[ListResult], query) -> list[ListResult]:
    filter_func = query_to_fun(query)
    return [
        artifact
        for artifact in artifacts
        if filter_func(artifact)
    ]

def remote_artifacts_unfiltered(rbgit: RbGit,
                                remote_bin_name: str,
                                all_shas: bool = False,
                                sha: str | None = None
                                ) -> list[str, str]:
    """
    Fetch all artifacts from the remote repository.
    artifacts is a pair of the meta_data_sha and the artifact sha it references
    If all_shas is True, fetch all artifacts artifact sha will be <src_sha>/<artifact_sha>
    O.w. <artifact_sha>.
    If sha is given, only fetch artifacts for that specific commit sha.
    """
    refs = refs_path(sha=sha, all_shas=all_shas)
    lines = rbgit.cmd("ls-remote", "--refs", remote_bin_name, f"{refs}*").splitlines()
    printer.debug(f"{lines}")
    artifacts = []
    for line in lines:
        meta_sha, artifact_sha = line.split()
        artifact_sha = artifact_sha.strip()[len(refs):]
        artifacts.append(ListResult(
            meta_sha=meta_sha,
            artifact_sha=artifact_sha,
            meta_data=meta_data(rbgit, remote_bin_name, meta_sha)
        ))
    return artifacts

def refs_path(sha: str | None = None, all_shas: bool = False):
    """
    Return appropriate refs path based on the given parameters. I.e. the prefix for the
    glob used in ls-remote. if all_shas is set we want all meta-for-commit refs. if sha is specified
    we want only that specific commit. Otherwise we want the current HEAD commit.
    Meta-data is stored at: refs/artifact/meta-for-commit/{src_sha}/{artifact_sha}
    So we either search for refs/artifact/meta-for-commit/ or refs/artifact/meta-for-commit/{sha}/
    """
    if all_shas:
        return "refs/artifact/meta-for-commit/"
    if sha is not None:
        return f"refs/artifact/meta-for-commit/{sha}/"

    src_sha = exec(["git", "rev-parse", "HEAD"])
    return f"refs/artifact/meta-for-commit/{src_sha}/"

def query_to_fun(query: Query):
    if isinstance(query, PathQuery):
        return lambda m: filter_artifact_by_path(m, query.query())
    if isinstance(query, RelPathQuery):
        return lambda m: filter_artifact_by_relpath(m, query.query())
    if isinstance(query, NameQuery):
        return lambda m: filter_artifact_by_name(m, query.query())
    if isinstance(query, JqQuery):
        return lambda m: jq_filter(m, query.query())
    if isinstance(query, AndQuery):
        queries = [query_to_fun(q) for q in query.queries]
        def _and(meta_data):
            return all(q(meta_data) for q in queries)
        return _and

def filter_artifact_by_name(result: ListResult, query: str):
    return result.meta_data['artifact-name'] == sanitize_branch_name(query)

def filter_artifact_by_path(result: ListResult, query: str):
    return result.meta_data['artifact-tree-prefix'] == query

def filter_artifact_by_relpath(result: ListResult, query: str):
    return result.meta_data['src-git-relpath'] == query

def jq_filter(result: ListResult, query: str):
    meta_data_json = json.dumps(result.meta_data)
    jq_res = jq([query], input=meta_data_json)
    printer.debug(f"jq result: {jq_res}")
    json_value = js.loads(meta_data_json)
    return bool(json_value)


def meta_data(rbgit, remote_bin_name, meta_data_commit):
    data = rbgit.fetch_cat_pretty(remote_bin_name, meta_data_commit)
    return parse_commit_msg(data)
