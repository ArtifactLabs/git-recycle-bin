"""Download command for retrieving artifacts."""
from printer import printer


def download_command(args, rbgit, remote_bin_name):
    """Execute download command to retrieve artifacts from repository."""
    for artifact in args.artifacts:
        try:
            rbgit.cmd("fetch", remote_bin_name, artifact)
        except RuntimeError as e:
            error_msg = str(e)
            # Handle "not our ref" errors gracefully - artifact may have expired
            if "not our ref" in error_msg or "upload-pack: not our ref" in error_msg:
                printer.error(f"Artifact {artifact} not found (possibly expired or cleaned up)")
                continue  # Skip this artifact and continue with others
            else:
                # Re-raise other fetch errors
                printer.error(f"Failed to fetch artifact {artifact}: {e}")
                return 1
                
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
