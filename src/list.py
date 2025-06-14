from printer import printer
from util import exec
from util_string import sanitize_branch_name
from commit_msg import parse_commit_msg


def list_command(args, rbgit, remote_bin_name):
    artifacts = remote_artifacts(rbgit, remote_bin_name)
    func = filter_funcs[args.query[0]] # query is a tuple of (flag, value) default is ("all", None)
    if args.query[0] != "all":
        printer.debug(f"Filtering artifacts by {args.query[0]}={args.query[1]}")
    artifacts = filter_artifacts(rbgit, remote_bin_name, args.query[1], artifacts, func)
    for artifact in artifacts:
        print(artifact[1])


def remote_artifacts(rbgit, remote_bin_name):
    # Fetch all artifacts based on refs/artifact/meta-for-commit/{src_sha}/* refspec.
    # This schema makes it easy to query which artifact are available for the given commit.
    # This allows us to drastically reduce the meta-data to search through, which
    # can then further be queried.
    src_sha = exec(["git", "rev-parse", "HEAD"])
    search_path = f"refs/artifact/meta-for-commit/{src_sha}/"
    lines = rbgit.cmd("ls-remote", "--refs", remote_bin_name, f"{search_path}*").splitlines()
    artifacts = []
    for line in lines:
        cols = line.split()
        meta_sha_blob = cols[0]
        artifact_sha_commit = cols[1].strip()[len(search_path):]
        artifacts.append((meta_sha_blob, artifact_sha_commit))
    return artifacts


def filter_artifacts(rbgit, remote_bin_name, query, artifacts, filter_func):
    return [
        artifact
        for artifact in artifacts
        if filter_func(artifact, rbgit=rbgit, remote_bin_name=remote_bin_name, query=query)
    ]


def filter_artifacts_by_name(artifact, **kwargs):
    rbgit = kwargs['rbgit']
    remote_bin_name = kwargs['remote_bin_name']
    data = rbgit.fetch_cat_pretty(remote_bin_name, artifact[0])
    return parse_commit_msg(data)['artifact-name'] == sanitize_branch_name(kwargs['query'])


def filter_artifacts_by_path(artifact, **kwargs):
    rbgit = kwargs['rbgit']
    remote_bin_name = kwargs['remote_bin_name']
    data = rbgit.fetch_cat_pretty(remote_bin_name, artifact[0])
    return parse_commit_msg(data)['src-git-relpath'] == kwargs['query']


filter_funcs = {
    'name': filter_artifacts_by_name,
    'path': filter_artifacts_by_path,
    'all': lambda artifact, **kwargs: True,
}
