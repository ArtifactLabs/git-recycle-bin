from git_recycle_bin.printer import printer

def download(args, rbgit, remote_bin_name):
    for artifact in args.artifacts:
        rbgit.cmd("fetch", remote_bin_name, artifact)
        if args.force:
            rbgit.cmd("checkout", "-f", artifact)
        else:
            # dont fail with python stack trace if file already exists
            try:
                rbgit.cmd("checkout", artifact)
            except RuntimeError as e:
                printer.error(e)
                printer.error("Use --force to overwrite local files.")
                return 1
