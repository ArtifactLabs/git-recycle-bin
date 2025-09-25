"""File path utilities for finding common ancestors and classifying paths."""
import os
import mimetypes
from itertools import takewhile


def nca_path(path_a, path_b):
    """Get nearest common ancestor of two paths.
    
    :param path_a: First path
    :param path_b: Second path
    :returns: Nearest common ancestor path
    """
    # Get absolute paths. Inputs may be relative.
    components1 = os.path.abspath(path_a).split(os.sep)
    components2 = os.path.abspath(path_b).split(os.sep)

    # Use zip to iterate over pairs of components
    # Stop when components differ, thanks to the use of itertools.takewhile
    common_components = list(
        takewhile(lambda x: x[0] == x[1], zip(components1, components2))
    )

    # The common path is the joined common components
    common_path = os.sep.join([x[0] for x in common_components])
    return common_path


def rel_dir(pfrom, pto):
    """Get relative path to `pto` from `pfrom`.
    
    :param pfrom: Source path
    :param pto: Target path
    :returns: Relative path from pfrom to pto
    """
    abs_pfrom = os.path.abspath(pfrom)
    abs_pto = os.path.abspath(pto)
    return os.path.relpath(abs_pto, abs_pfrom)


def classify_path(binpath: str) -> str:
    """Determine what the path is, a file or directory. If file, what type.
    
    :param binpath: Path to classify
    :returns: MIME type for files, or type description for other paths
    """
    if os.path.isfile(binpath):
        mimetype, _ = mimetypes.guess_type(binpath)
        return mimetype or "unknown"
    if os.path.isdir(binpath):
        return "directory"
    if os.path.islink(binpath):
        return "link"
    if os.path.ismount(binpath):
        return "mount"
    return "unknown"
