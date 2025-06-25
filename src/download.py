"""Download command for retrieving artifacts."""
from printer import printer


def download_command(args, rbgit, remote_bin_name):
    """Execute download command to retrieve artifacts from repository."""
    for artifact in args.artifacts:
        rbgit.cmd("fetch", remote_bin_name, artifact)
        if args.force:
            rbgit.cmd("checkout", "-f", artifact)
        else:
            # don't fail with python stack trace if file already exists
            try:
                rbgit.cmd("checkout", artifact)
            except RuntimeError as e:
                printer.error(e)
                printer.error("Use --force to overwrite local files.")
                return 1
    return 0
